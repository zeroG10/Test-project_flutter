"""Splash (module 01) — TC-SPL-001…003.

Source of every step and expectation: qa/mobile/01-splash/splash-test-cases.md (D-SPL-1…4 accepted
by the owner; recon 4, 2026-09-24). The splash has no labelled element: it is decided by pixels
(pages/splash_page.py). A splash check that comes too late is Blocked (timing), never Passed.
TC-SPL-003 is red today — BUG-SPL-001 — and stays red as the regression check (owner, 2026-09-24).

Every expected text / colour goes through ``expected(...)`` — ``--prove-red`` breaks them all.
"""

import allure
import pytest

from helpers import pixels, waits
from pages.jobs_list_page import JobsListPage
from pages.login_page import LoginPage
from pages.otp_page import OtpPage
from pages.registration_page import RegistrationPage
from pages.splash_page import SplashMissed, SplashPage
from pages.tabbar_page import TabBarPage
from pages.welcome_page import WelcomePage

LANDING = 30.0  # the DEV debug build needs ~10 s to its first screen (recon 4)
SERVER = 20.0
BRAND = "#782A2A"  # Figma `Spalsh` 2451:82537 fill = the app theme's primary colour (D-SPL-2)
WELCOME_TITLE = "Welcome to Concert Technologies' Field Force"  # D-1


@pytest.fixture
def pages(driver, platform):
    class Pages:
        splash = SplashPage(driver, platform)
        welcome = WelcomePage(driver, platform)
        login = LoginPage(driver, platform)
        otp = OtpPage(driver, platform)
        registration = RegistrationPage(driver, platform)
        jobs = JobsListPage(driver, platform)
        tabbar = TabBarPage(driver, platform)

    return Pages


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-SPL-001")
@pytest.mark.chk(
    "CHK-SPL-001", "CHK-SPL-002", "CHK-SPL-003", "CHK-SPL-005", "CHK-SPL-007", "CHK-SPL-011"
)  # fmt: skip
@allure.tag(
    "CHK-SPL-001", "CHK-SPL-002", "CHK-SPL-003", "CHK-SPL-005", "CHK-SPL-007", "CHK-SPL-011"
)  # fmt: skip
@allure.title(
    "TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and "
    "nothing to interact with, then opens Welcome by itself"
)
def test_cold_start_splash_then_welcome(app, driver, pages, expected):
    splash = pages.splash.use_colour(pixels.hex_to_rgb(expected(BRAND)))
    app.clear_data()  # signed out and not running → the next launch is a cold start
    idle = driver.get_settings().get("waitForIdleTimeout")
    driver.update_settings({"waitForIdleTimeout": 0})  # return from launch before the app idles
    try:
        app.launch()
        splash.expect_shown_after_system_splash()  # iOS: the first frame (unchanged)
        splash.expect_no_interactive_elements()
        splash.tap_centre()
        pages.welcome.go_back()  # iOS: edge swipe; Android: the system Back
        shown = splash.expect_shown("splash after a tap and an edge swipe")
        splash.expect_logo_centred(shown)
    except SplashMissed as exc:
        pytest.skip(f"Blocked: timing — {exc}; the splash could not be observed in time")
    finally:
        if idle is not None:
            driver.update_settings({"waitForIdleTimeout": idle})
    # CHK-SPL-007: the back changed nothing — on Android the frame right after the system Back
    # still shows the splash while the app is already being left (Q-SPL-A2), so: over a window
    app.expect_stays_in_front("a back on the splash changes nothing")
    pages.welcome.expect_text("title", expected(WELCOME_TITLE), LANDING)  # Welcome, not Login
    pages.login.wait_gone("root", 2)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SPL-002")
@pytest.mark.chk("CHK-SPL-008", "CHK-SPL-012")
@allure.tag("CHK-SPL-008", "CHK-SPL-012")
@allure.title(
    "TC-SPL-002 With a valid session, the splash hands over to the Jobs list "
    "and Welcome never appears"
)
def test_session_hands_over_to_jobs(ui_login, app, driver, pages, expected):
    pages.jobs.assert_open()
    app.terminate()
    app.launch()

    def jobs_without_welcome(_driver) -> bool:
        assert not pages.welcome.is_open(0), "Welcome appeared although a session exists"
        return pages.jobs.is_open(0)

    with allure.step("wait for the Jobs list; Welcome must never show meanwhile"):
        waits.wait_until(driver, jobs_without_welcome, LANDING, "the Jobs list did not open")
    pages.jobs.expect_text("root", expected("Jobs list"))
    pages.tabbar.visible("jobs")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.e2e
@pytest.mark.tc("TC-SPL-003")
@pytest.mark.chk("CHK-SPL-009")
@allure.tag("CHK-SPL-009")
@allure.title(
    "TC-SPL-003 A session whose account was deleted on the server ends on Welcome "
    "after a cold start"
)
def test_deleted_account_session_ends(
    new_user, field_services_api, logged_out_app, app, pages, tech, expected, evidence
):
    # precondition: a new technician registered through the UI and signed in (TC-AUTH-013 flow)
    with allure.step("precondition: register a new technician and sign in"):
        pages.welcome.open_sign_up()
        reg = pages.registration
        reg.assert_open(LANDING)
        reg.fill_form(
            new_user.first_name, new_user.last_name, new_user.phone_national, new_user.email
        )
        reg.choose_channel("email")
        reg.submit()
        pages.otp.enter_code(tech.otp)
        pages.jobs.assert_open(LANDING)
    app.terminate()
    with allure.step("precondition: delete the account on the server"):
        deleted = field_services_api.full_delete_test_user(new_user.email)
        assert deleted, "the new technician was not found for deletion"

    app.launch()
    try:
        pages.welcome.expect_text("title", expected(WELCOME_TITLE), LANDING)
    finally:
        evidence.checkpoint("after-cold-start-deleted-account")
    pages.jobs.wait_gone("root", 2)
    app.relaunch()
    pages.welcome.expect_text("title", expected(WELCOME_TITLE), LANDING)
