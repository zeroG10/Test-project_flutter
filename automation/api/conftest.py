import os
import re
from pathlib import Path

from dotenv import load_dotenv

# Load automation/api/.env into os.environ BEFORE anything imports `config.settings`,
# so pydantic-settings and any direct `os.getenv(...)` in a test see the same values.
# override=False (default): a real environment variable (e.g. a CI secret) always wins
# over the file.
load_dotenv(Path(__file__).parent / ".env")

import allure  # noqa: E402
import pytest  # noqa: E402

from clients.base_client import ApiClient  # noqa: E402
from config.settings import settings  # noqa: E402

# Canonical CHK id (automation/README.md → IDs and tags). Same pattern in
# automation/mobile/conftest.py and automation/tools/trace_results.py — a malformed id
# would never be traced (silently "not run"), so collection fails instead.
CHK_ID = re.compile(r"^CHK-[A-Z]{2,5}-\d{3,}$")


def pytest_collection_modifyitems(config, items):
    invalid: list[str] = []
    for item in items:
        for marker in item.iter_markers("chk"):
            if not marker.args:
                invalid.append(f"{item.nodeid}: @pytest.mark.chk without an id")
            for chk_id in marker.args:
                if isinstance(chk_id, str) and CHK_ID.match(chk_id):
                    item.user_properties.append(("chk", chk_id))
                else:
                    invalid.append(f"{item.nodeid}: {chk_id!r}")
    if invalid:
        raise pytest.UsageError(
            "Invalid @pytest.mark.chk id(s) — expected CHK-<FEATURE>-<NNN>:\n  "
            + "\n  ".join(invalid)
        )


def pytest_sessionstart(session):
    """Fail closed before a single request: no target, no run (doctrine rule 3).
    Mirrors automation/web/playwright.config.ts, which throws without BASE_URL."""
    target = (settings.api_base_url or "").strip()
    if not target or target.startswith("<") or "api.example.com" in target:
        raise pytest.UsageError(
            "API_BASE_URL is not set (or still the <…> placeholder) — copy automation/api/"
            ".env.example to .env and set the dev/staging target. Blocked, not green: "
            "a run without a target is not a run."
        )
    if not target.startswith(("http://", "https://")):
        raise pytest.UsageError(f"API_BASE_URL is not a URL: {target!r}")


@pytest.fixture(scope="session", autouse=True)
def _env_label():
    allure.dynamic.label("env", settings.api_env)
    allure.dynamic.label("base_url", settings.api_base_url)


@pytest.fixture
def api() -> ApiClient:
    with ApiClient() as client:
        yield client


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        allure.attach(
            f"Test: {item.nodeid}\nFailed at: {report.longrepr}",
            name="failure-context",
            attachment_type=allure.attachment_type.TEXT,
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
