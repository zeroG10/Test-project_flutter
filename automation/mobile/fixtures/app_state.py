"""App-state and test-data fixtures (pytest plugin, registered in conftest.py).

The ``App state`` / ``Preconditions`` rows of a test case map to these fixtures:

| Test-case precondition                         | Fixture          |
|------------------------------------------------|------------------|
| cold start; app data reset (logged out)        | ``logged_out_app`` |
| signed in as ``{{tech.*}}``                    | ``ui_login``     |
| ``{{tech.*}}``                                 | ``tech``         |
| ``{{new_user.*}}`` + API delete in ``finally`` | ``new_user``     |
| named screenshots at checkpoints               | ``evidence``     |

Session model (README "Session model"): one Appium session per run; login through the UI
only when the app has no session — on DEV that is once per run unless a test signs out
(FR-OTP-13 lockout, weak DEV server). There is no token injection on mobile: the token
lives in the iOS keychain.

A precondition that cannot be established is ``Blocked`` (pytest skip with a
``Blocked: …`` reason — trace_results.py reads a skip as Blocked), never a product Failed.
Pages the fixtures drive (step 5 implements them, aliases from the Auth test cases):
``WelcomePage.open_login()``, ``LoginPage.request_code(identifier)``,
``OtpPage.enter_code(code)``, ``JobsListPage`` / ``WelcomePage`` anchors.
"""

import dataclasses

import allure
import pytest
from selenium.common.exceptions import TimeoutException

from fixtures import test_data
from helpers.app import AppControl
from helpers.evidence import Evidence
from helpers.field_services_api import ApiBlocked, FieldServicesApi
from helpers.waits import wait_any

# Cold start of a DEV debug build on the simulator: splash + first frame + session check.
LANDING_TIMEOUT = 30.0


def _pages(driver, platform):
    # Imported lazily: screen maps and pages are generated in step 5, after this harness.
    from pages.jobs_list_page import JobsListPage
    from pages.welcome_page import WelcomePage

    return WelcomePage(driver, platform), JobsListPage(driver, platform)


def _landing(driver, platform) -> str:
    """Which screen the app shows after a (re)launch: ``welcome`` | ``jobs-list``."""
    welcome, jobs = _pages(driver, platform)
    try:
        return wait_any(
            driver,
            {"welcome": lambda: welcome.is_open(0), "jobs-list": lambda: jobs.is_open(0)},
            LANDING_TIMEOUT,
        )
    except TimeoutException:
        return "unknown"


@pytest.fixture
def app(driver, platform) -> AppControl:
    """Lifecycle calls for the app under test: launch / relaunch / clear data / reinstall."""
    return AppControl(driver, platform)


@pytest.fixture
def evidence(driver) -> Evidence:
    """``evidence.checkpoint("otp-screen")`` — a named screenshot in the report."""
    return Evidence(driver)


@pytest.fixture(scope="session")
def tech() -> test_data.Tech:
    """``{{tech.*}}`` — the registered DEV test technician from .env (read-only)."""
    try:
        return test_data.tech()
    except LookupError as exc:
        pytest.skip(str(exc))


@pytest.fixture
def logged_out_app(app, driver, platform) -> AppControl:
    """Cold start with app data reset: signed out, Welcome on screen."""
    with allure.step("precondition: app data reset, cold start → Welcome"):
        app.clear_data()
        app.launch()
        landed = _landing(driver, platform)
        if landed != "welcome":
            # iOS: clearApp empties the data container but not the keychain; the app wipes
            # keychain tokens on a first-launch start. If that did not happen, reinstall.
            with allure.step(f"clear data landed on {landed!r}, not Welcome → reinstall"):
                app.reinstall()
                app.launch()
                landed = _landing(driver, platform)
        if landed != "welcome":
            pytest.skip(
                f"Blocked: no signed-out Welcome after clear data + reinstall (landed on {landed})"
            )
    return app


@pytest.fixture
def ui_login(app, driver, platform, tech) -> AppControl:
    """Signed in as the test technician, Jobs list on screen, after a cold start.

    Reuses a live session; signs in through the UI (email + DEV OTP) only when the app
    shows Welcome. Proving login itself is TC-AUTH-005's job — here a failed login is a
    precondition that could not be met, so the dependent test is Blocked.
    """
    with allure.step("precondition: signed in as the test technician → Jobs list"):
        app.relaunch()
        landed = _landing(driver, platform)
        if landed == "jobs-list":
            return app
        if landed != "welcome":
            pytest.skip(f"Blocked: cold start landed on {landed}, neither Welcome nor Jobs list")
        from pages.login_page import LoginPage
        from pages.otp_page import OtpPage

        welcome, jobs = _pages(driver, platform)
        try:
            with allure.step(f"UI login as {tech.email}"):
                welcome.open_login()
                LoginPage(driver, platform).request_code(tech.email)
                OtpPage(driver, platform).enter_code(tech.otp)
                jobs.assert_open(LANDING_TIMEOUT)
        except TimeoutException as exc:
            pytest.skip(f"Blocked: UI login precondition failed ({exc.msg or 'timeout'})")
    return app


@pytest.fixture(scope="session")
def field_services_api():
    """Admin API client for setup/cleanup; signs in once, when the first test needs it."""
    try:
        api = FieldServicesApi()
        api.find_technicians_by_email("qa-auto+probe@example.com")  # sign-in + read check
    except (ApiBlocked, OSError) as exc:
        pytest.skip(f"Blocked: Field Services API unavailable — {exc}")
    yield api
    api.close()


@pytest.fixture
def new_user(field_services_api, app):
    """``{{new_user.*}}`` — unique technician data; whatever the test registers under it is
    deleted through the API afterwards, pass or fail (teardown = ``finally``).

    The app is then reset too: it may still hold a session of the deleted user.
    A failed delete is a harness error with the user id in the message (manual recovery).
    """
    user = dataclasses.replace(
        test_data.new_user(), phone_national=test_data.free_fictional_national(field_services_api)
    )
    allure.attach(
        f"first name: {user.first_name}\nlast name: {user.last_name}\n"
        f"email: {user.email}\nphone: {user.phone}",
        name="generated new_user",
        attachment_type=allure.attachment_type.TEXT,
    )
    try:
        yield user
    finally:
        try:
            field_services_api.full_delete_test_user(user.email)
        finally:
            app.clear_data()
