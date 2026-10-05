"""pytest wiring for the mobile stack. Run matrix and conventions: README.md.

What this file enforces (QA Doctrine, CLAUDE.md):
* ``--platform`` is android | ios only — Flutter is ``APP_KIND`` in .env.
* Tests marked ``android`` / ``ios`` / ``flutter`` are DESELECTED when they do not match the
  run (platform / app kind). Deselection is visible in the summary and leaves pytest exit 5
  when nothing is left, so an empty run is red, not green.
* Every ``@pytest.mark.chk(...)`` id must look like ``CHK-<FEATURE>-<NNN>``; a malformed id
  would never be traced (silently "not run"), so collection fails instead.
* Every ``@pytest.mark.tc(...)`` carries exactly one ``TC-<FEATURE>-<NNN>`` id (the test case
  the test implements, qa/mobile/<NN-module>/<module>-test-cases.md).
* A missing build or an unreachable Appium server is reported as ``Blocked: ...``.
* CI strict-skip: with ``CI`` (or ``QA_STRICT_SKIPS=1``) set, a run that skipped any test
  exits 1 — a skip is Blocked and must not vote green in a gate (GATES.md rule 2).

Harness additions for this project (README "Session model", "Evidence", "Allure report"):
* ONE Appium session per run (serial runs on a weak DEV server); app state per test comes
  from fixtures/app_state.py (``logged_out_app``, ``ui_login``, ``new_user`` …).
* Allure grouping Platform › Module (from the CHK code) and a run-context ``env`` label on
  every result; environment.properties + categories.json written at the end of the run.
* Screenshot + page source on a failure or a Blocked setup; screen video only when
  ``EVIDENCE_VIDEO`` asks for it (default off; ``auto`` keeps it for failed or Blocked tests
  and tests marked ``e2e``).
"""

import contextlib
import os
import re
from pathlib import Path

import allure
import pytest
from appium import webdriver
from selenium.common.exceptions import WebDriverException

from config.capabilities import get_capabilities
from config.settings import normalize_platform, settings
from helpers.android.device import Adb
from helpers.evidence import ScreenRecorder
from helpers.reporting import PLATFORM_TITLE, env_label, module_for, write_allure_run_files

pytest_plugins = [
    "fixtures.app_state",
    "fixtures.jobs",
    "fixtures.details",
    "fixtures.check",
    "fixtures.progress",
    "fixtures.survey",
    "fixtures.notifications",
    "fixtures.profile",
    "fixtures.network",
]

CHK_ID = re.compile(r"^CHK-[A-Z]{2,5}-\d{3,}$")
TC_ID = re.compile(r"^TC-[A-Z]{2,5}-\d{3,}$")
PLATFORM_MARKERS = frozenset({"android", "ios"})
PLATFORM_KEY = pytest.StashKey[str]()
REPORTS_KEY = pytest.StashKey[dict]()  # item -> {"setup"|"call"|"teardown": TestReport}


def pytest_addoption(parser):
    parser.addoption(
        "--platform",
        action="store",
        default=None,
        help="android | ios (Flutter is APP_KIND in .env)",
    )
    parser.addoption(
        "--prove-red",
        action="store_true",
        default=False,
        help="break every expected text a test routes through the `expected` fixture: each test "
        "must go red (GATES rule 6). Use a separate --alluredir; never trace this run.",
    )


PROVE_RED_SUFFIX = " «prove-red: deliberately wrong»"


def pytest_configure(config):
    if not config.pluginmanager.has_plugin("anr-blocked"):
        config.pluginmanager.register(AnrBlocked(), "anr-blocked")
    raw = config.getoption("--platform") or settings.platform
    try:
        config.stash[PLATFORM_KEY] = normalize_platform(raw)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    # the platform's own test account and Appium server (PARALLEL-RUNS.md), before any
    # fixture reads them
    settings.apply_platform(config.stash[PLATFORM_KEY])


def pytest_report_header(config):
    flutter_driver = settings.flutter_driver if settings.is_flutter else "-"
    header = (
        f"mobile: platform={config.stash[PLATFORM_KEY]} app_kind={settings.app_kind} "
        f"flutter_driver={flutter_driver} appium={settings.appium_url} "
        f"account={settings.account_key(config.stash[PLATFORM_KEY]) or 'not set'}"
    )
    if config.getoption("--prove-red"):
        header += "\nPROVE-RED RUN: every test must FAIL; a passing test is not proven"
    return header


def skipped_chks(item: pytest.Item, platform: str) -> dict[str, str]:
    """CHK ids the owner decided NOT to check on ``platform`` for this test, with the reason:
    ``@pytest.mark.chk_skipped_on("android", "CHK-ORDD-024", reason="owner, Q-ORDD-A4 …")``.
    On that platform the id carries no tag, so the trace reads it as not run (never Passed, never
    Failed) and the report says why; on the other platform nothing changes."""
    skipped: dict[str, str] = {}
    for marker in item.iter_markers("chk_skipped_on"):
        if marker.args and normalize_platform(str(marker.args[0])) == platform:
            for chk_id in marker.args[1:]:
                skipped[str(chk_id)] = str(marker.kwargs.get("reason", ""))
    return skipped


def pytest_collection_modifyitems(config, items):
    platform = config.stash[PLATFORM_KEY]
    invalid: list[str] = []
    kept: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        # 0. Owner-skipped CHK ids of this platform: a reason, ids of this test, no static tag
        skipped = skipped_chks(item, platform)
        declared_chk = {a for m in item.iter_markers("chk") for a in m.args}
        static_tags = {
            str(t)
            for m in item.iter_markers("allure_label")
            if m.kwargs.get("label_type") == "tag"
            for t in m.args
        }
        for chk_id, reason in skipped.items():
            if not reason.strip():
                invalid.append(f"{item.nodeid}: chk_skipped_on {chk_id} without a reason")
            if chk_id not in declared_chk:
                invalid.append(f"{item.nodeid}: chk_skipped_on {chk_id} is not in its chk(...)")
            if chk_id in static_tags:
                invalid.append(
                    f"{item.nodeid}: {chk_id} is skipped on {platform} but still in @allure.tag"
                )

        # 1. CHK ids: validate and expose to JUnit (<property name="chk">) for trace_results.py
        for marker in item.iter_markers("chk"):
            if not marker.args:
                invalid.append(f"{item.nodeid}: @pytest.mark.chk without an id")
            for chk_id in marker.args:
                if chk_id in skipped:
                    item.user_properties.append(("chk_skipped", f"{chk_id}: {skipped[chk_id]}"))
                elif isinstance(chk_id, str) and CHK_ID.match(chk_id):
                    item.user_properties.append(("chk", chk_id))
                else:
                    invalid.append(f"{item.nodeid}: {chk_id!r}")

        # 1b. TC id: one per test, the test case it implements
        for marker in item.iter_markers("tc"):
            if len(marker.args) != 1 or not (
                isinstance(marker.args[0], str) and TC_ID.match(marker.args[0])
            ):
                invalid.append(
                    f"{item.nodeid}: tc{marker.args!r} — expected one TC-<FEATURE>-<NNN>"
                )
            else:
                item.user_properties.append(("tc", marker.args[0]))

        # 2. Scope by platform / app kind
        wanted = {m.name for m in item.iter_markers() if m.name in PLATFORM_MARKERS}
        out_of_scope = (bool(wanted) and platform not in wanted) or (
            item.get_closest_marker("flutter") is not None and not settings.is_flutter
        )
        (deselected if out_of_scope else kept).append(item)

    if invalid:
        raise pytest.UsageError(
            "Invalid @pytest.mark.chk / @pytest.mark.tc id(s) — expected CHK-<FEATURE>-<NNN> / "
            "TC-<FEATURE>-<NNN>:\n  " + "\n  ".join(invalid)
        )
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept


@pytest.fixture(scope="session")
def platform(request) -> str:
    """OS under test for this run: android | ios."""
    return request.config.stash[PLATFORM_KEY]


@pytest.fixture(scope="session")
def expected(request):
    """Route a test's expected texts through this: ``expected("Log in")``.

    Normal run: the text unchanged. ``--prove-red``: the text made wrong on purpose, so the
    test must fail at its first text expectation — the proof that it can go red.
    """
    if not request.config.getoption("--prove-red"):
        return lambda text: text
    return lambda text: f"{text}{PROVE_RED_SUFFIX}"


@pytest.fixture(scope="session")
def driver(platform):
    """ONE Appium session for the whole run. The session start installs the build from
    .env (a clean app at the start of every run); per-test app state comes from the
    fixtures in fixtures/app_state.py, never from a new session."""
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
    with contextlib.ExitStack() as device:
        if platform == "android":  # a pushed "New job assigned" pop-up covers the app bar
            device.enter_context(Adb.of(drv).heads_up_off())
            Adb.of(drv).remove_test_providers()  # a crashed run may have left mock providers
        yield drv
    with contextlib.suppress(Exception):
        drv.quit()


_ANDROID_MODULES_SEEN: list[str] = []
# What a dead UiAutomator2 server (or a dead session) answers — the session is started anew
_DEAD_SESSION = (
    "socket hang up",
    "instrumentation process is not running",
    "invalid session id",
    "session is either terminated",
    "Could not proxy command",
)


def _new_session(drv, platform: str, why: str) -> None:
    """A fresh Appium session on the same driver object: a new UiAutomator2 server process and
    a fast-reset app (the tests sign in by themselves, as each module did in step 4)."""
    with allure.step(f"Appium: a new session ({why})"):
        with contextlib.suppress(Exception):
            drv.quit()
        drv.start_session(get_capabilities(platform))


@pytest.fixture(scope="module", autouse=True)
def _android_session_per_module(request, driver, platform):
    """Android: one Appium session per test module, as the module runs of step 4. In the first
    full run of step 6 the UiAutomator2 server died after ~40 min of one session ("socket hang
    up") and every later test errored (final-s1: 109 errors); a fresh server per module keeps
    a death inside one module."""
    if platform == "android":
        if _ANDROID_MODULES_SEEN:
            _new_session(driver, platform, f"module {request.module.__name__}")
        _ANDROID_MODULES_SEEN.append(request.module.__name__)
    yield


@pytest.fixture(autouse=True)
def _android_session_alive(driver, platform):
    """Android: before each test, a dead session (UiAutomator2 gone) is started anew — the test
    that was running when it died has its own verdict; the next ones do not inherit it."""
    if platform == "android":
        try:
            driver.get_window_size()
        except WebDriverException as exc:
            if not any(sign in str(exc) for sign in _DEAD_SESSION):
                raise
            _new_session(driver, platform, f"the last one died: {str(exc)[:80]}")
    yield


@pytest.fixture(autouse=True)
def _allure_context(request, platform):
    """Group results Platform › Module and stamp the run configuration on each of them."""
    item = request.node
    chk_ids = [arg for marker in item.iter_markers("chk") for arg in marker.args]
    module = module_for(chk_ids)
    allure.dynamic.parent_suite(PLATFORM_TITLE[platform])
    allure.dynamic.suite(module)
    allure.dynamic.epic(module)
    tc_marker = item.get_closest_marker("tc")
    if tc_marker is not None:
        allure.dynamic.feature(tc_marker.args[0])
        allure.dynamic.tag(tc_marker.args[0])
    # Safety net for trace_results.py: allure-pytest does not turn chk("CHK-…") (a marker
    # with args) into a tag, so a test that forgot its @allure.tag would trace as not run.
    declared = {
        str(tag)
        for marker in item.iter_markers("allure_label")
        if marker.kwargs.get("label_type") == "tag"
        for tag in marker.args
    }
    skipped = skipped_chks(item, platform)
    for chk_id in dict.fromkeys(chk_ids):
        if chk_id in skipped:  # owner decision for this platform: no tag, the reason instead
            allure.dynamic.label("chk_skipped", f"{chk_id} — {skipped[chk_id]}")
        elif chk_id not in declared:
            allure.dynamic.tag(chk_id)
    allure.dynamic.label("env", env_label(platform))
    if request.config.getoption("--prove-red"):
        allure.dynamic.label("run_mode", "prove-red")


@pytest.fixture(autouse=True)
def _screen_video(request, driver, platform):
    """``EVIDENCE_VIDEO=auto|all``: record every test; keep the video for failed or Blocked tests
    and tests marked e2e (``all``: every test). Default ``off``: nothing is recorded."""
    if settings.evidence_video == "off":
        yield
        return
    recorder = ScreenRecorder(driver, platform)
    recorder.start()
    yield
    item = request.node
    went_wrong = any(
        report.failed or (report.skipped and "Blocked:" in _skip_reason(report))
        for report in item.stash.get(REPORTS_KEY, {}).values()
    )
    keep = (
        settings.evidence_video == "all" or went_wrong or item.get_closest_marker("e2e") is not None
    )
    recorder.stop(keep, name=f"video · {item.name}")


def _attach_screen_evidence(item: pytest.Item, label: str) -> None:
    drv = item.funcargs.get("driver")
    if drv is None:
        return
    with contextlib.suppress(Exception):
        allure.attach(
            drv.get_screenshot_as_png(),
            name=f"screenshot-{label}",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            drv.page_source,
            name=f"page-source-{label}",
            attachment_type=allure.attachment_type.XML,
        )


def _skip_reason(report: pytest.TestReport) -> str:
    if isinstance(report.longrepr, tuple) and len(report.longrepr) == 3:
        return str(report.longrepr[2])
    return ""


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    item.stash.setdefault(REPORTS_KEY, {})[report.when] = report
    if report.when in ("setup", "call") and report.failed:
        _attach_screen_evidence(item, f"on-failure-{report.when}")
    elif report.when == "setup" and report.skipped and "Blocked:" in _skip_reason(report):
        _attach_screen_evidence(item, "blocked-setup")


ANR_REASON = (
    "Blocked: the emulator showed '… isn't responding' (ANR) — the emulator was starved of CPU; "
    "not an app verdict (recon A1, Fable's analysis: docs/notes/session-handoff.md §3х). Re-run "
    "on an idle host."
)


class AnrBlocked:
    """Android: a failure with the system ANR dialog on screen is Blocked, never Failed. The
    frozen app is closed so the next test starts it again (no "Wait" loop: every ANR dump
    freezes the app longer). Registered as its own plugin in ``pytest_configure`` — a module
    holds one function per hook name — and innermost, so Allure already records the skip."""

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when not in ("setup", "call") or not report.failed:
            return
        drv, platform = item.funcargs.get("driver"), item.funcargs.get("platform")
        if drv is None or platform != "android":
            return
        with contextlib.suppress(Exception):
            if "android:id/aerr_wait" not in drv.page_source:
                return
            _attach_screen_evidence(item, "anr")
            with contextlib.suppress(Exception):
                drv.find_element("id", "android:id/aerr_close").click()
            report.outcome = "skipped"
            report.longrepr = (str(item.path), item.location[1] or 0, ANR_REASON)


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
    if config.getoption("--prove-red"):
        green = [r.nodeid for r in terminalreporter.stats.get("passed", [])]
        red = len(terminalreporter.stats.get("failed", []))
        terminalreporter.write_sep(
            "=", f"PROVE-RED: {red} test(s) went red, {len(green)} stayed green"
        )
        for nodeid in green:
            terminalreporter.write_line(
                f"  NOT PROVEN (passed with a broken expectation): {nodeid}"
            )
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
    # Run context for the Allure "Environment" widget + failure categories. Not on
    # --collect-only (nothing ran, nothing to describe).
    results_dir = session.config.getoption("allure_report_dir", default=None)
    if results_dir and not session.config.getoption("collectonly"):
        with contextlib.suppress(OSError):
            write_allure_run_files(Path(results_dir), session.config.stash[PLATFORM_KEY])
