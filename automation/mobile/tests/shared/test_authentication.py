"""Authentication pilot (module 02) — TC-AUTH-001…014.

Source of every step and expectation: qa/mobile/02-authentication/authentication-test-cases.md
(owner-validated 2026-09-23; D-1…D-12 accepted — the tests assert the live app).
Locators: screens/*_map.py only. App state: fixtures/app_state.py. Serial on purpose
(weak DEV server): the order below keeps UI logins and OTP requests to a minimum, and the
only wrong OTP of the run is in TC-AUTH-008 (FR-OTP-13 lockout).

Every expected text goes through ``expected(...)`` — ``--prove-red`` breaks them all.
"""

import re

import allure
import pytest

from fixtures import test_data
from helpers import waits
from pages.jobs_list_page import JobsListPage
from pages.login_page import LoginPage
from pages.otp_page import OtpPage
from pages.registration_page import RegistrationPage
from pages.sms_terms_page import SmsTermsPage
from pages.welcome_page import WelcomePage

LANDING = 30.0  # cold start of the DEV debug build + first frame
SERVER = 20.0  # an answer from the DEV API (weak server)

UNREGISTERED_EMAIL = "This email is not registered yet. Create an account to get started."
UNREGISTERED_PHONE = "This phone number is not registered yet. Create an account to get started."
DUPLICATE_PHONE = "An account with this phone number already exists. Please log in to continue."


def digits(text: str | None) -> str:
    return re.sub(r"\D", "", text or "")


@pytest.fixture
def pages(driver, platform):
    class Pages:
        welcome = WelcomePage(driver, platform)
        login = LoginPage(driver, platform)
        otp = OtpPage(driver, platform)
        jobs = JobsListPage(driver, platform)
        registration = RegistrationPage(driver, platform)
        sms_terms = SmsTermsPage(driver, platform)

    return Pages


# --------------------------------------------------------------------------------------
# Login
# --------------------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-005")
@pytest.mark.chk(
    "CHK-AUTH-110", "CHK-AUTH-115", "CHK-AUTH-117", "CHK-AUTH-119",
    "CHK-AUTH-073", "CHK-AUTH-074", "CHK-AUTH-075", "CHK-AUTH-088", "CHK-AUTH-089",
    "CHK-ORDL-001",  # module 03: the Jobs list is the landing screen (owner, 2026-09-24)
)  # fmt: skip
@allure.tag(
    "CHK-AUTH-110", "CHK-AUTH-115", "CHK-AUTH-117", "CHK-AUTH-119",
    "CHK-AUTH-073", "CHK-AUTH-074", "CHK-AUTH-075", "CHK-AUTH-088", "CHK-AUTH-089",
    "CHK-ORDL-001",  # module 03: the Jobs list is the landing screen (owner, 2026-09-24)
)  # fmt: skip
@allure.title("TC-AUTH-005 Login with email and the OTP opens the Jobs list")
def test_login_with_email(logged_out_app, pages, tech, expected, evidence):
    pages.welcome.open_login()
    pages.login.expect_text("title", expected("Log in"))
    pages.login.type("identifier", tech.email)
    pages.login.expect_enabled("continue")
    evidence.checkpoint("login-filled")
    pages.login.submit()

    pages.otp.expect_text("title", expected("Email address verification"), SERVER)
    pages.otp.expect_text(
        "instruction", expected("Enter the 4-digit code sent to your email address")
    )
    pages.otp.expect_sent_to(tech.email)
    evidence.checkpoint("otp-screen")
    pages.otp.enter_code(tech.otp)  # submits by itself after the 4th digit (D-5)

    pages.jobs.assert_open(LANDING)
    evidence.checkpoint("jobs-list")


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-003")
@pytest.mark.chk("CHK-AUTH-002")
@allure.tag("CHK-AUTH-002")
@allure.title("TC-AUTH-003 A valid session skips Welcome and opens the Jobs list on relaunch")
def test_session_skips_welcome(ui_login, pages, expected):
    pages.jobs.expect_text("root", expected("Jobs list"))
    ui_login.relaunch()
    pages.jobs.assert_open(LANDING)
    pages.welcome.wait_gone("root", 2)


# --------------------------------------------------------------------------------------
# Welcome
# --------------------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-002")
@pytest.mark.chk("CHK-AUTH-009", "CHK-AUTH-010", "CHK-AUTH-016", "CHK-AUTH-103")
@allure.tag("CHK-AUTH-009", "CHK-AUTH-010", "CHK-AUTH-016", "CHK-AUTH-103")
@allure.title("TC-AUTH-002 Welcome actions open Registration and Login")
def test_welcome_actions(logged_out_app, pages, expected):
    pages.welcome.assert_open()
    pages.welcome.open_sign_up()
    pages.registration.expect_text("title", expected("Registration"), LANDING)
    # Welcome opens Registration with context.go (a route REPLACE): there is no back stack,
    # so no system back to Welcome by design (run 1, 2026-09-23). A cold start returns to it.
    logged_out_app.relaunch()
    pages.welcome.assert_open(LANDING)
    pages.welcome.open_login()
    pages.login.expect_text("title", expected("Log in"), 10)


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-001")
@pytest.mark.chk(
    "CHK-AUTH-001", "CHK-AUTH-003", "CHK-AUTH-004", "CHK-AUTH-005", "CHK-AUTH-007", "CHK-AUTH-008"
)
@allure.tag(
    "CHK-AUTH-001", "CHK-AUTH-003", "CHK-AUTH-004", "CHK-AUTH-005", "CHK-AUTH-007", "CHK-AUTH-008"
)
@allure.title(
    "TC-AUTH-001 Welcome shows the header, subtext and both actions, without back navigation"
)
def test_welcome_screen(logged_out_app, pages, expected, evidence):
    welcome = pages.welcome
    welcome.visible("root")
    welcome.expect_text("title", expected("Welcome to Concert Technologies' Field Force"))  # D-1
    welcome.expect_centred("title")
    welcome.expect_text("subtitle", expected("Create an account or log in to get started."))
    welcome.expect_below("subtitle", "title")
    welcome.visible("sign-up")
    welcome.expect_in_bottom_area("sign-up")
    welcome.visible("login")
    welcome.expect_below("login", "sign-up")
    welcome.wait_gone("back", 2)
    evidence.checkpoint("welcome")


# --------------------------------------------------------------------------------------
# Login screen content and validation
# --------------------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-004")
@pytest.mark.chk(
    "CHK-AUTH-104", "CHK-AUTH-105", "CHK-AUTH-106", "CHK-AUTH-107", "CHK-AUTH-108", "CHK-AUTH-109"
)
@allure.tag(
    "CHK-AUTH-104", "CHK-AUTH-105", "CHK-AUTH-106", "CHK-AUTH-107", "CHK-AUTH-108", "CHK-AUTH-109"
)
@allure.title(
    "TC-AUTH-004 Login shows its content and keeps Continue disabled while the field is empty"
)
def test_login_screen_content(logged_out_app, pages, expected):
    pages.welcome.open_login()
    login = pages.login
    login.expect_text("title", expected("Log in"))
    login.expect_text("subtitle", expected("Good to see you! Let's get you logged in."))  # D-4
    login.expect_text(
        "helper", expected("Enter the email or phone number you used during registration")
    )
    login.visible("identifier")
    with allure.step("expect login.identifier to be the only input on the screen"):
        assert login.count_visible("text-fields") == 1
    login.expect_disabled("continue")
    login.visible("privacy-link")
    login.visible("terms-link")
    login.visible("sign-up-link")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-006")
@pytest.mark.chk("CHK-AUTH-111", "CHK-AUTH-116", "CHK-AUTH-118", "CHK-AUTH-072", "CHK-AUTH-096")
@allure.tag("CHK-AUTH-111", "CHK-AUTH-116", "CHK-AUTH-118", "CHK-AUTH-072", "CHK-AUTH-096")
@allure.title(
    "TC-AUTH-006 Login with a phone number opens Phone verification and completes sign-in"
)
def test_login_with_phone(logged_out_app, pages, tech, expected):
    pages.welcome.open_login()
    pages.login.expect_text("title", expected("Log in"))  # before any server call
    pages.login.type("identifier", tech.phone)  # E.164, as the field's hint asks (Q-A1)
    pages.login.expect_enabled("continue")
    pages.login.submit()
    pages.otp.expect_text("title", expected("Phone number verification"), SERVER)
    pages.otp.expect_sent_to(tech.phone_last4)
    pages.otp.enter_code(tech.otp)
    pages.jobs.assert_open(LANDING)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-007")
@pytest.mark.chk("CHK-AUTH-114", "CHK-AUTH-121", "CHK-AUTH-123", "CHK-AUTH-125")
@allure.tag("CHK-AUTH-114", "CHK-AUTH-121", "CHK-AUTH-123", "CHK-AUTH-125")
@allure.title(
    "TC-AUTH-007 Login rejects an invalid format and an unregistered email, retry in place"
)
def test_login_rejects_invalid_and_unregistered_email(logged_out_app, pages, expected):
    login = pages.login
    pages.welcome.open_login()
    for invalid in ("abc@", "12ab"):
        login.type("identifier", invalid)
        # D-12 (owner, 2026-09-23): no message — only the format hint and a disabled Continue
        login.expect_text("format-hint", expected("Format: +1234567890 or name@example.com"))
        login.expect_disabled("continue")

    email = test_data.unregistered_email()
    login.type("identifier", email)
    login.expect_enabled("continue")  # the invalid state is cleared (CHK-AUTH-114)
    login.submit()
    login.expect_error(expected(UNREGISTERED_EMAIL), SERVER)  # red banner, ~4 s
    login.expect_text("identifier", email)  # value preserved (CHK-AUTH-121)

    retry = test_data.unregistered_email()
    login.type("identifier", retry)  # retry without reopening the screen (CHK-AUTH-125)
    login.submit()
    login.expect_error(expected(UNREGISTERED_EMAIL), SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-007")
@pytest.mark.chk("CHK-AUTH-122")
@allure.tag("CHK-AUTH-122")
@allure.title("TC-AUTH-007 Login rejects an unregistered phone number")
@allure.link("qa/mobile/02-authentication/bugs/BUG-AUTH-001.md", name="BUG-AUTH-001")
@allure.label("bug", "BUG-AUTH-001")
def test_login_rejects_unregistered_phone(logged_out_app, field_services_api, pages, expected):
    # BUG-AUTH-001 (S3, filed 2026-09-23): the app shows "An unexpected error occurred. Please
    # try logging in again." for an unregistered phone. The test stays RED against the checklist
    # until the bug is fixed — it is the regression check (prompts/08).
    login = pages.login
    pages.welcome.open_login()
    login.expect_text("title", expected("Log in"))  # before any server call
    phone = f"+1{test_data.free_fictional_national(field_services_api)}"
    login.type("identifier", phone)
    login.expect_enabled("continue")
    login.submit()
    login.expect_error(expected(UNREGISTERED_PHONE), SERVER)
    login.expect_text("identifier", phone)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-009")
@pytest.mark.chk("CHK-AUTH-077", "CHK-AUTH-078", "CHK-AUTH-080", "CHK-AUTH-097", "CHK-AUTH-126")
@allure.tag("CHK-AUTH-077", "CHK-AUTH-078", "CHK-AUTH-080", "CHK-AUTH-097", "CHK-AUTH-126")
@allure.title(
    "TC-AUTH-009 OTP: Verify disabled below 4 digits, resend locked during the countdown, "
    "back returns to Login without signing in"
)
def test_otp_partial_code_countdown_and_back(logged_out_app, pages, tech, expected):
    pages.welcome.open_login()
    pages.login.expect_text("title", expected("Log in"))  # before any server call
    pages.login.request_code(tech.email)
    otp = pages.otp
    otp.expect_text("title", expected("Email address verification"), SERVER)
    otp.enter_code("123")
    otp.expect_disabled("verify")
    otp.expect_text("resend", expected("You can request a new code in"))
    first = otp.countdown_seconds()
    with allure.step(f"expect the countdown to go down from {first}s"):
        waits.wait_until(otp.driver, lambda _d: otp.countdown_seconds() < first, 5)
    otp.go_back()  # iOS: edge swipe (recon 3d)
    pages.login.assert_open(10)
    logged_out_app.relaunch()
    pages.welcome.assert_open(LANDING)  # no session without a verified code


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-008")
@pytest.mark.chk("CHK-AUTH-090", "CHK-AUTH-091")
@allure.tag("CHK-AUTH-090", "CHK-AUTH-091")
@allure.title(
    "TC-AUTH-008 An incorrect OTP shows a visible error and the code stays editable; "
    "the correct code then signs in"
)
def test_wrong_otp_then_correct(logged_out_app, pages, tech, expected, evidence):
    pages.welcome.open_login()
    pages.login.expect_text("title", expected("Log in"))  # before any OTP is requested
    pages.login.request_code(tech.email)
    otp = pages.otp
    otp.expect_text("title", expected("Email address verification"), SERVER)
    # The tree reports "Incorrect code." visible even when it is not drawn (TD-AUTH-008):
    # shown / hidden is decided by the pixels inside its bounds.
    otp.expect_error_shown(False, 5)
    otp.enter_code(test_data.wrong_otp(tech.otp))  # the ONLY wrong OTP of the run
    otp.expect_error_shown(True, SERVER)
    evidence.checkpoint("otp-incorrect-code")
    otp.assert_open(2)  # still on the OTP screen: not signed in
    otp.enter_code(tech.otp)
    pages.jobs.assert_open(LANDING)


# --------------------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-010")
@pytest.mark.chk(
    "CHK-AUTH-017", "CHK-AUTH-018", "CHK-AUTH-019", "CHK-AUTH-020", "CHK-AUTH-021",
    "CHK-AUTH-022", "CHK-AUTH-023", "CHK-AUTH-024", "CHK-AUTH-035",
)  # fmt: skip
@allure.tag(
    "CHK-AUTH-017", "CHK-AUTH-018", "CHK-AUTH-019", "CHK-AUTH-020", "CHK-AUTH-021",
    "CHK-AUTH-022", "CHK-AUTH-023", "CHK-AUTH-024", "CHK-AUTH-035",
)  # fmt: skip
@allure.title(
    "TC-AUTH-010 Registration shows its fields and sections in order, the +1 prefix, "
    "and Continue disabled by default"
)
def test_registration_form_layout(logged_out_app, pages, expected, evidence):
    pages.welcome.open_sign_up()
    reg = pages.registration
    reg.expect_text("title", expected("Registration"), LANDING)
    reg.expect_text("subtitle", expected("Good to see you! Let's get you registered."))
    reg.visible("first-name")
    reg.expect_below("last-name", "first-name")
    reg.expect_below("phone", "last-name")
    reg.expect_below("email", "phone")
    with allure.step("expect the phone prefix +1 (CLIENT_BUILD=true)"):
        assert reg.phone_prefix() == expected("+1")
    reg.expect_below("channel-section", "email")
    reg.visible("channel-options")
    with allure.step("expect SMS and Email options"):
        assert reg.selected_channel() is None  # both radios found, none selected
    # The consent switch is disabled here, and a disabled switch is reported not visible by
    # the tree: it is asserted drawn (pixels) and placed below the channel section.
    reg.visible("sms-consent-label")
    reg.expect_below("sms-consent-label", "channel-options")
    reg.expect_drawn("sms-consent")
    evidence.checkpoint("registration-top")
    reg.scroll_to("continue")
    reg.expect_disabled("continue")
    reg.scroll_to("privacy-link")
    reg.expect_below("privacy-link", "continue")
    reg.visible("terms-link")
    reg.visible("log-in-link")
    reg.expect_in_bottom_area("log-in-link")


REQUIRED = object()  # "(typed, then cleared)"
CAPPED = object()  # longer than the field allows: capped, no message
VALID = {
    "first-name": "Alex",
    "last-name": "Smith",
    "phone": "2025550123",
    "email": "qa-auto@example.com",
}
VALIDATION_ROWS = [
    # field, value, expected message (None = no error), id
    ("first-name", REQUIRED, "Field is required.", "first-required"),
    ("first-name", "A", "2 characters minimum.", "first-1-char"),
    ("first-name", "Al", None, "first-2-chars"),
    ("first-name", "a" * 50, None, "first-50-chars"),  # BUG-AUTH-002: SRS says 100
    ("first-name", "a" * 51, CAPPED, "first-51-chars"),  # current app limit, D-14
    ("first-name", "Ann3", "Has invalid characters.", "first-digit"),
    ("first-name", "An@n", "Has invalid characters.", "first-special"),
    ("last-name", REQUIRED, "Field is required.", "last-required"),
    ("last-name", "B", "2 characters minimum.", "last-1-char"),
    ("last-name", "Bo", None, "last-2-chars"),
    ("last-name", "B3", "Has invalid characters.", "last-digit"),
    ("phone", REQUIRED, "Phone number is required", "phone-required"),
    ("phone", "123", "Enter a valid phone number", "phone-malformed"),
    ("phone", "2025550123", None, "phone-valid"),
    ("email", REQUIRED, "Field is required.", "email-required"),
    ("email", "abc@", "Email format is incorrect.", "email-malformed"),
    ("email", "qa-auto@example.com", None, "email-valid"),
]


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-011")
@pytest.mark.chk(
    "CHK-AUTH-026", "CHK-AUTH-027", "CHK-AUTH-028", "CHK-AUTH-029", "CHK-AUTH-030",
    "CHK-AUTH-031", "CHK-AUTH-032", "CHK-AUTH-033", "CHK-AUTH-034", "CHK-AUTH-041",
    "CHK-AUTH-043", "CHK-AUTH-044", "CHK-AUTH-045", "CHK-AUTH-046", "CHK-AUTH-047",
)  # fmt: skip
@allure.tag(
    "CHK-AUTH-026", "CHK-AUTH-027", "CHK-AUTH-028", "CHK-AUTH-029", "CHK-AUTH-030",
    "CHK-AUTH-031", "CHK-AUTH-032", "CHK-AUTH-033", "CHK-AUTH-034", "CHK-AUTH-041",
    "CHK-AUTH-043", "CHK-AUTH-044", "CHK-AUTH-045", "CHK-AUTH-046", "CHK-AUTH-047",
)  # fmt: skip
@allure.title("TC-AUTH-011 Registration validates {field}: {row_id}")
@pytest.mark.parametrize(
    ("field", "value", "message", "row_id"),
    VALIDATION_ROWS,
    ids=[row[-1] for row in VALIDATION_ROWS],
)
def test_registration_field_validation(
    logged_out_app, pages, expected, field, value, message, row_id
):
    pages.welcome.open_sign_up()
    reg = pages.registration
    reg.expect_text("title", expected("Registration"), LANDING)

    if value is REQUIRED:
        reg.fill(field, VALID[field][:2])
        reg.clear(field)
    else:
        reg.fill(field, value)

    if message is None:
        reg.expect_no_field_error(field)
        if field == "phone":
            reg.expect_text("phone", expected("(202) 555-0123"))  # formatted as typed
        return
    if message is CAPPED:
        reg.expect_no_field_error(field)
        with allure.step("expect the input capped at 50 characters (D-14)"):
            assert len(reg.find(field).get_attribute("value") or "") == 50
        return

    reg.expect_field_error(field, expected(message))
    reg.fill(field, VALID[field])  # correction
    reg.expect_no_field_error(field)  # cleared dynamically


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-012")
@pytest.mark.chk(
    "CHK-AUTH-049", "CHK-AUTH-053", "CHK-AUTH-055", "CHK-AUTH-056", "CHK-AUTH-060", "CHK-AUTH-061"
)
@allure.tag(
    "CHK-AUTH-049", "CHK-AUTH-053", "CHK-AUTH-055", "CHK-AUTH-056", "CHK-AUTH-060", "CHK-AUTH-061"
)
@allure.title("TC-AUTH-012 Choosing the SMS channel requires accepting the SMS Terms")
def test_sms_channel_requires_terms_and_consent(logged_out_app, pages, expected, evidence):
    user = test_data.new_user()  # nothing is submitted: no API cleanup needed
    pages.welcome.open_sign_up()
    reg = pages.registration
    reg.expect_text("title", expected("Registration"), LANDING)
    reg.fill_form(user.first_name, user.last_name, user.phone_national, user.email)

    reg.choose_channel("sms")  # opens the SMS Terms (D-9)
    pages.sms_terms.expect_text("title", expected("SMS Messaging Terms & Conditions"), 10)
    evidence.checkpoint("sms-terms")
    pages.sms_terms.accept()

    reg.assert_open(10)
    reg.expect_channel("sms")
    reg.scroll_to("sms-consent-text")
    reg.expect_below("sms-consent-text", "sms-consent")
    reg.expect_enabled("sms-consent")
    reg.scroll_to("continue")
    reg.expect_disabled("continue")  # SMS chosen, consent not given
    reg.set_sms_consent(True)
    reg.expect_enabled("continue")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-AUTH-014")
@pytest.mark.chk("CHK-AUTH-068", "CHK-AUTH-069", "CHK-AUTH-071")
@allure.tag("CHK-AUTH-068", "CHK-AUTH-069", "CHK-AUTH-071")
@allure.title(
    "TC-AUTH-014 Registering with an already registered phone shows an error, keeps the values "
    "and allows a retry"
)
def test_registration_duplicate_phone(new_user, logged_out_app, pages, tech, expected):
    # new_user: if the duplicate check ever let the form through, the API teardown removes it
    pages.welcome.open_sign_up()
    reg = pages.registration
    reg.expect_text("title", expected("Registration"), LANDING)
    reg.fill_form(new_user.first_name, new_user.last_name, tech.phone_national, new_user.email)
    reg.choose_channel("email")
    reg.submit()
    reg.visible("form-error", SERVER, text=expected(DUPLICATE_PHONE))  # red banner (D-7)
    reg.scroll_to("phone")
    with allure.step("expect the phone value preserved"):
        assert digits(reg.find("phone").get_attribute("value")) == tech.phone_national
    reg.fill("phone", new_user.phone_national)  # retry without reopening the screen
    reg.scroll_to("continue")
    reg.expect_enabled("continue")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.e2e
@pytest.mark.tc("TC-AUTH-013")
@pytest.mark.chk("CHK-AUTH-050", "CHK-AUTH-062", "CHK-AUTH-063", "CHK-AUTH-064", "CHK-AUTH-066")
@allure.tag("CHK-AUTH-050", "CHK-AUTH-062", "CHK-AUTH-063", "CHK-AUTH-064", "CHK-AUTH-066")
@allure.title(
    "TC-AUTH-013 Registering with the Email channel verifies the email and opens the Jobs list"
)
def test_registration_with_email_channel(new_user, logged_out_app, pages, tech, expected, evidence):
    pages.welcome.open_sign_up()
    reg = pages.registration
    reg.expect_text("title", expected("Registration"), LANDING)
    reg.fill_form(new_user.first_name, new_user.last_name, new_user.phone_national, new_user.email)
    reg.choose_channel("email")
    reg.expect_channel("email")
    reg.scroll_to("continue")
    reg.expect_enabled("continue")
    evidence.checkpoint("registration-filled")
    reg.submit()

    pages.otp.expect_text("title", expected("Email address verification"), SERVER)
    pages.otp.expect_sent_to(new_user.email)
    evidence.checkpoint("otp-new-user")
    pages.otp.enter_code(tech.otp)  # the DEV code is the same for every account

    pages.jobs.assert_open(LANDING)  # no onboarding after registration (Q-A2)
    evidence.checkpoint("jobs-list-new-user")
    # teardown (new_user): DELETE /user/full-delete/{id}, verified gone; app data cleared
