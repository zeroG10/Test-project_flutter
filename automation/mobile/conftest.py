"""pytest wiring for the mobile stack. Run matrix and conventions: README.md.

What this file enforces (QA Doctrine, CLAUDE.md):
* ``--platform`` is android | ios only — Flutter is ``APP_KIND`` in .env.
* Tests marked ``android`` / ``ios`` / ``flutter`` are DESELECTED when they do not match the
  run (platform / app kind). Deselection is visible in the summary and leaves pytest exit 5
  when nothing is left, so an empty run is red, not green.
* Every ``@pytest.mark.chk(...)`` id must look like ``CHK-<FEATURE>-<NNN>``; a malformed id
  would never be traced (silently "not run"), so collection fails instead.
* A missing build or an unreachable Appium server is reported as ``Blocked: ...``.
* CI strict-skip: with ``CI`` (or ``QA_STRICT_SKIPS=1``) set, a run that skipped any test
  exits 1 — a skip is Blocked and must not vote green in a gate (GATES.md rule 2).
"""

import contextlib
import os
import re

import allure
import pytest
from appium import webdriver

from config.capabilities import get_capabilities
from config.settings import normalize_platform, settings

CHK_ID = re.compile(r"^CHK-[A-Z]{2,5}-\d{3,}$")
PLATFORM_MARKERS = frozenset({"android", "ios"})
PLATFORM_KEY = pytest.StashKey[str]()


def pytest_addoption(parser):
    parser.addoption(
        "--platform",
        action="store",
        default=None,
        help="android | ios (Flutter is APP_KIND in .env)",
    )


def pytest_configure(config):
    raw = config.getoption("--platform") or settings.platform
    try:
        config.stash[PLATFORM_KEY] = normalize_platform(raw)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc


def pytest_report_header(config):
    flutter_driver = settings.flutter_driver if settings.is_flutter else "-"
    return (
        f"mobile: platform={config.stash[PLATFORM_KEY]} app_kind={settings.app_kind} "
        f"flutter_driver={flutter_driver} appium={settings.appium_url}"
    )


def pytest_collection_modifyitems(config, items):
    platform = config.stash[PLATFORM_KEY]
    invalid: list[str] = []
    kept: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        # 1. CHK ids: validate and expose to JUnit (<property name="chk">) for trace_results.py
        for marker in item.iter_markers("chk"):
            if not marker.args:
                invalid.append(f"{item.nodeid}: @pytest.mark.chk without an id")
            for chk_id in marker.args:
                if isinstance(chk_id, str) and CHK_ID.match(chk_id):
                    item.user_properties.append(("chk", chk_id))
                else:
                    invalid.append(f"{item.nodeid}: {chk_id!r}")

        # 2. Scope by platform / app kind
        wanted = {m.name for m in item.iter_markers() if m.name in PLATFORM_MARKERS}
        out_of_scope = (bool(wanted) and platform not in wanted) or (
            item.get_closest_marker("flutter") is not None and not settings.is_flutter
        )
        (deselected if out_of_scope else kept).append(item)

    if invalid:
        raise pytest.UsageError(
            "Invalid @pytest.mark.chk id(s) — expected CHK-<FEATURE>-<NNN>:\n  "
            + "\n  ".join(invalid)
        )
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept


@pytest.fixture(scope="session")
def platform(request) -> str:
    """OS under test for this run: android | ios."""
    return request.config.stash[PLATFORM_KEY]


@pytest.fixture
def driver(platform):
    app = settings.app_path(platform)
    if not app.exists():
        pytest.fail(f"Blocked: build not found at {app} — see builds/README.md", pytrace=False)
    try:
        drv = webdriver.Remote(settings.appium_url, options=get_capabilities(platform))
    except Exception as exc:  # any session-creation failure is Blocked, never a silent skip
        pytest.fail(
            f"Blocked: no Appium session at {settings.appium_url} "
            f"({type(exc).__name__}: {exc}). Is scripts/start_appium.sh running? "
            "Run scripts/doctor.sh.",
            pytrace=False,
        )
    # No implicit wait on purpose: it silently stacks on explicit waits. Use helpers/waits.py.
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            with contextlib.suppress(Exception):
                allure.attach(
                    drv.get_screenshot_as_png(),
                    name="screenshot-on-failure",
                    attachment_type=allure.attachment_type.PNG,
                )
                allure.attach(
                    drv.page_source,
                    name="page-source",
                    attachment_type=allure.attachment_type.XML,
                )


# --------------------------------------------------------------------------- #
# CI strict-skip (GATES.md rule 2): a skip is Blocked, never green
# --------------------------------------------------------------------------- #
# pytest exits 0 when every test that ran either passed or was skipped. In a gate that
# would let a skipped (= Blocked, still owed) check vote green. When CI is set — or
# QA_STRICT_SKIPS=1 locally — a run that skipped anything exits 1 and lists the skips.
# xfail is not a skip: an expected failure proves a known defect (bug id in the reason).

_SKIPPED_IN_RUN: list[str] = []


def _strict_skips_enabled() -> bool:
    if os.environ.get("QA_STRICT_SKIPS", "").strip().lower() in {"1", "true", "yes"}:
        return True
    return os.environ.get("CI", "").strip().lower() in {"1", "true", "yes"}


def pytest_runtest_logreport(report):
    if report.skipped and not hasattr(report, "wasxfail"):
        reason = ""
        if isinstance(report.longrepr, tuple) and len(report.longrepr) == 3:
            reason = str(report.longrepr[2])
        _SKIPPED_IN_RUN.append(f"{report.nodeid}: {reason or 'skipped'}")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not _SKIPPED_IN_RUN:
        return
    if _strict_skips_enabled():
        mode = "STRICT (exit 1)"
    else:
        mode = "advisory (set CI or QA_STRICT_SKIPS=1 to fail)"
    terminalreporter.write_sep("=", f"Blocked: {len(_SKIPPED_IN_RUN)} skipped test(s) — {mode}")
    for line in _SKIPPED_IN_RUN:
        terminalreporter.write_line(f"  {line}")
    terminalreporter.write_line(
        "A skip is Blocked, never Passed (CLAUDE.md doctrine rule 3). Configure what is missing "
        "or quarantine the test with a BUG id (.github/GATES.md)."
    )


def pytest_sessionfinish(session, exitstatus):
    if _SKIPPED_IN_RUN and _strict_skips_enabled() and int(exitstatus) == 0:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
