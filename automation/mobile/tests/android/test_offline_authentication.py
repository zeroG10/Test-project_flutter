"""Authentication — Android offline (step 5): TC-AUTH-015…018.

Source: qa/mobile/02-authentication/android/authentication-test-cases.md (owner-validated
2026-10-01; D-OFF-1…9 answered, no remarks on the TCs). Android only: these four checks need
network control the iOS simulator does not have — CHK-AUTH-124 (login), CHK-AUTH-070
(registration), CHK-AUTH-099/-100 (OTP offline + retry), CHK-AUTH-098 (OTP, slow network).

TC-AUTH-017's last step (tap otp.verify once back online → jobs-list) is the SRS expectation
(FR-OTP-12 "allow retry") and is EXPECTED TO FAIL on this app today — Resolved D-OFF-1 (owner,
2026-10-01): treated as a bug (S3), filed once this automated run shows it. The assertion stays
exactly as the test case asks for; it is not worked around or loosened.

Every expected text goes through ``expected(...)`` (--prove-red breaks it).
"""

import allure
import pytest

from pages.android.offline_page import OfflineBanner
from pages.jobs_list_page import JobsListPage
from pages.login_page import LoginPage
from pages.otp_page import OtpPage
from pages.registration_page import RegistrationPage
from pages.welcome_page import WelcomePage

SERVER = 20.0  # an answer from the DEV API (weak server)
SLOW = 90.0  # throttled network (emulator: gsm speed, gprs delay) on top of the server's own time

LOGIN_OFFLINE_ERROR = "An unexpected error occurred. Please try logging in again."
REGISTRATION_OFFLINE_ERROR = "No internet connection"
OTP_OFFLINE_ERROR = "No internet connection"


@pytest.fixture
def pages(driver, platform):
    class Pages:
        welcome = WelcomePage(driver, platform)
        login = LoginPage(driver, platform)
        otp = OtpPage(driver, platform)
        registration = RegistrationPage(driver, platform)
        jobs = JobsListPage(driver, platform)
        offline = OfflineBanner(driver, platform)

    return Pages


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-AUTH-015")
@pytest.mark.chk("CHK-AUTH-124")
@allure.tag("CHK-AUTH-124")
@allure.title(
    "TC-AUTH-015 Login offline shows the generic connectivity error and blocks navigation; "
    "back online, Continue retries without reopening the screen"
)
def test_login_offline_then_retry_online(logged_out_app, network, pages, tech, expected, evidence):
    pages.welcome.open_login()  # open login
    network.off()  # open device.network off
    pages.login.type("identifier", tech.email)  # fill login.identifier {{tech.email}}
    pages.login.submit()  # click login.continue — attempted while offline

    # recon A2 row 2: the Login-screen message shows ~3 s right after Continue, then
    # disappears — checked first, before the longer-lived app-wide banner (recon A2 row 1)
    pages.login.expect_error(expected(LOGIN_OFFLINE_ERROR), 5)  # expect-visible login.error
    pages.offline.expect_shown()  # expect-visible offline-banner.message
    evidence.checkpoint("login-offline-error")
    pages.login.assert_open(2)  # expect-visible login.root — still on Login, no OTP navigation

    network.on()  # open device.network on
    pages.login.submit()  # click login.continue — retry without reopening the screen
    pages.otp.assert_open(SERVER)  # expect-visible otp.root — the retry succeeded (FR-LOG-09)


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-AUTH-016")
@pytest.mark.chk("CHK-AUTH-070")
@allure.tag("CHK-AUTH-070")
@allure.title(
    "TC-AUTH-016 Registration offline shows the error and keeps the form; back online, "
    "Continue retries and reaches OTP"
)
def test_registration_offline_then_retry_online(
    new_user, logged_out_app, network, pages, expected, evidence
):
    reg = pages.registration
    pages.welcome.open_sign_up()  # open registration
    reg.fill_form(new_user.first_name, new_user.last_name, new_user.phone_national, new_user.email)
    reg.choose_channel("email")  # click registration.channel-email

    network.off()  # open device.network off
    reg.submit()  # click registration.continue — attempted while offline
    # registration.snackbar (recon A2, code-only) resolves to the form-error alias already in
    # the map — the same parametrised pattern already used for login.error / TC-AUTH-014
    reg.visible("form-error", 10, text=expected(REGISTRATION_OFFLINE_ERROR))
    evidence.checkpoint("registration-offline-error")
    with allure.step("expect the typed values preserved"):
        # the form has scrolled: Flutter hands Android only the on-screen fields, so each field
        # is scrolled to before it is read (offline run 01021112-r1: First name was above the top)
        for alias, value in (
            ("first-name", new_user.first_name),
            ("last-name", new_user.last_name),
            ("email", new_user.email),
        ):
            reg.scroll_to(alias)
            assert reg.field_value(reg.find(alias)) == expected(value), alias

    network.on()  # open device.network on
    reg.submit()  # click registration.continue — retry without reopening the screen
    pages.otp.assert_open(SERVER)  # expect-visible otp.root — Email address verification


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-AUTH-017")
@pytest.mark.chk("CHK-AUTH-099", "CHK-AUTH-100")
@allure.tag("CHK-AUTH-099", "CHK-AUTH-100")
@allure.title(
    "TC-AUTH-017 OTP offline shows 'No internet connection' under the code field; the "
    "owner's retry (tap Verify) once back online"
)
def test_otp_offline_then_verify_retry(logged_out_app, network, pages, tech, expected, evidence):
    pages.welcome.open_login()  # open login
    pages.login.type("identifier", tech.email)  # fill login.identifier {{tech.email}}
    pages.login.submit()  # click login.continue — OTP requested
    pages.otp.assert_open(SERVER)  # expect-visible otp.root

    network.off()  # open device.network off
    pages.otp.enter_code(tech.otp)  # fill otp.code {{tech.otp}} — submits automatically, offline
    # expect-visible otp.error "No internet connection" — resolved to the network-error alias
    pages.otp.expect_text("network-error", expected(OTP_OFFLINE_ERROR), 10)
    pages.offline.expect_shown()  # expect-visible offline-banner.message (recon A2 row 1)
    evidence.checkpoint("otp-offline-error")

    network.on()  # open device.network on
    pages.otp.tap("verify")  # click otp.verify — the owner's expected retry (CHK-AUTH-100)
    # expect-visible jobs-list.root — SRS FR-OTP-12 "allow retry"; expected RED today.
    # Resolved D-OFF-1 (owner, 2026-10-01): a bare Verify tap does not resume the offline
    # attempt once back online — treated as a bug (S3), filed once this run confirms it. Kept
    # exactly as the test case asks for; do not retry, skip or loosen this assertion.
    pages.jobs.assert_open(SERVER)


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-AUTH-018")
@pytest.mark.chk("CHK-AUTH-098")
@allure.tag("CHK-AUTH-098")
@allure.title(
    "TC-AUTH-018 OTP verification on a slow network: one verification pass, one navigation "
    "to the Jobs list, no duplicate OTP screen in the back stack"
)
def test_otp_slow_network_single_transition(logged_out_app, network, pages, tech, expected):
    pages.welcome.open_login()  # open login
    pages.login.type("identifier", tech.email)  # fill login.identifier {{tech.email}}
    pages.login.submit()  # click login.continue — OTP requested
    pages.otp.assert_open(SERVER)  # expect-visible otp.root

    network.slow()  # open device.network slow (emulator: gsm speed, gprs delay)
    pages.otp.enter_code(tech.otp)  # fill otp.code {{tech.otp}} — submits automatically, slow

    pages.jobs.assert_open(SLOW)  # wait-for jobs-list.root — a single transition, not several
    pages.otp.wait_gone("root", 2)  # expect-hidden otp.root — exactly one OTP screen existed
    pages.jobs.go_back()  # back — system Back from the Jobs list
    pages.otp.wait_gone("root", 2)  # expect-hidden otp.root — no duplicate screen in the back stack
