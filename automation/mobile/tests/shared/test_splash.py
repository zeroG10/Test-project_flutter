"""Splash (module 01) — TC-SPL-001…003, TC-SPL-005, TC-SPL-006.

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
@pytest.mark.chk("CHK-SPL-001", "CHK-SPL-002", "CHK-SPL-003", "CHK-SPL-011")
@allure.tag("CHK-SPL-001", "CHK-SPL-002", "CHK-SPL-003", "CHK-SPL-011")
@allure.title(
    "TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo, then "
    "opens Welcome by itself"
)
def test_cold_start_splash_then_welcome(app, driver, pages, expected):
    """Split on the owner's word (2026-10-01): the interaction checks are TC-SPL-005 (one red item —
    the system Back, BUG-SPL-002 — no longer turns these red too) and the tree check is TC-SPL-006
    (a tree read that misses the ~1-s Android splash no longer Blocks these four)."""
    splash = pages.splash.use_colour(pixels.hex_to_rgb(expected(BRAND)))
    app.clear_data()  # signed out and not running → the next launch is a cold start
    idle = driver.get_settings().get("waitForIdleTimeout")
    driver.update_settings({"waitForIdleTimeout": 0})  # return from launch before the app idles
    try:
        app.launch()
        first = splash.expect_shown_after_system_splash()  # iOS: the first frame (unchanged)
        if app.platform == "android":
            # the brand splash is up for about a second after the system one (module 01+03
            # Android runs 3–5): the logo on the first brand frame
            splash.expect_logo_centred(first)
        else:
            shown = splash.expect_shown("splash before the logo check")  # debug build: ~8 s
            splash.expect_logo_centred(shown)
    except SplashMissed as exc:
        pytest.skip(f"Blocked: timing — {exc}; the splash could not be observed in time")
    finally:
        if idle is not None:
            driver.update_settings({"waitForIdleTimeout": idle})
    pages.welcome.expect_text("title", expected(WELCOME_TITLE), LANDING)  # Welcome, not Login
    pages.login.wait_gone("root", 2)


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-SPL-006")
@pytest.mark.chk("CHK-SPL-005")
@allure.tag("CHK-SPL-005")
@allure.title(
    "TC-SPL-006 The splash offers nothing to interact with: no text, button, link or field"
)
def test_splash_has_nothing_to_interact_with(app, driver, pages, expected):
    """CHK-SPL-005 on its own (split from TC-SPL-001, owner 2026-10-01). Android: the tree must be
    read inside a splash of about a second — the tree proves by itself whether it was (the Welcome
    title in it → Blocked, timing; never Passed)."""
    splash = pages.splash.use_colour(pixels.hex_to_rgb(expected(BRAND)))
    app.clear_data()
    idle = driver.get_settings().get("waitForIdleTimeout")
    driver.update_settings({"waitForIdleTimeout": 0})
    try:
        app.launch()
        splash.expect_shown_after_system_splash()
        splash.expect_no_interactive_elements()
    except SplashMissed as exc:
        pytest.skip(f"Blocked: timing — {exc}; the splash could not be observed in time")
    finally:
        if idle is not None:
            driver.update_settings({"waitForIdleTimeout": idle})
    pages.welcome.expect_text("title", expected(WELCOME_TITLE), LANDING)


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-SPL-005")
@pytest.mark.chk("CHK-SPL-007")
@allure.tag("CHK-SPL-007")
@allure.title(
    "TC-SPL-005 A tap and a back on the splash change nothing; the app goes on to Welcome by itself"
)
def test_splash_ignores_interaction(app, driver, pages, expected):
    """CHK-SPL-007 on its own (split from TC-SPL-001, owner 2026-10-01). Android: red against
    BUG-SPL-002 — the system Back on the splash leaves the app."""
    splash = pages.splash.use_colour(pixels.hex_to_rgb(expected(BRAND)))
    app.clear_data()
    idle = driver.get_settings().get("waitForIdleTimeout")
    driver.update_settings({"waitForIdleTimeout": 0})
    try:
        app.launch()
        splash.expect_shown_after_system_splash()
        if app.platform == "android":
            # start 1 — the system Back right after the first brand frame (the splash lasts about
            # a second after the system one on this host) — it does not depend on how fast the
            # tree is read, so it goes first (01-split-r1: the tap's tree read came too late and
            # the whole TC was Blocked before the Back was tried);
            # start 2 — a tap, then the tree: still the splash's, nothing opened by the tap
            pages.welcome.go_back()  # the system Back
            app.expect_stays_in_front("a back on the splash changes nothing")
            app.terminate()
            app.launch()
            splash.expect_shown_after_system_splash()
            splash.tap_centre()
            splash.expect_no_interactive_elements()
        else:
            splash.tap_centre()
            pages.welcome.go_back()  # edge swipe
            splash.expect_shown("splash after a tap and an edge swipe")
    except SplashMissed as exc:
        # Gone because the Back left the app (Android, Q-SPL-A2) is a verdict, not timing
        app.expect_stays_in_front("a back on the splash changes nothing", hold=0)
        pytest.skip(f"Blocked: timing — {exc}; the splash could not be observed in time")
    finally:
        if idle is not None:
            driver.update_settings({"waitForIdleTimeout": idle})
    # the frame right after the back can still show the splash while Android is already
    # leaving the app (Q-SPL-A2), so: over a window (iOS: the edge swipe)
    app.expect_stays_in_front("a back on the splash changes nothing")
    pages.welcome.expect_text("title", expected(WELCOME_TITLE), LANDING)  # went on by itself


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
