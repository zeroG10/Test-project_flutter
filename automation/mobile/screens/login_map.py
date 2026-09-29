"""Login — email or phone, then an OTP (module 02-authentication).

Source: Appium tree qa/shared/recon-dumps/ios-2026-09-23/login.xml (recon 2026-09-23).
Visible texts as locators (owner decision 2026-09-23). Android:
qa/shared/recon-dumps/android-2026-09-29/login.xml, login_invalid.xml (recon A1) — same
texts; the identifier field is an EditText, its label only in ``hint`` (TD-A1).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR

LOGIN = Screen(
    id="login",
    anchor="root",
    elements={
        # The subtitle is unique to Login; "Log in" also appears on Registration (its link).
        "root": El(
            android=(_A, "Good to see you! Let's get you logged in."),
            ios=(_A, "Good to see you! Let's get you logged in."),
        ),
        "title": El(
            android=(_A, "Log in"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Log in'"),
        ),
        "subtitle": El(
            android=(_A, "Good to see you! Let's get you logged in."),
            ios=(_A, "Good to see you! Let's get you logged in."),
        ),
        "helper": El(
            android=(_A, "Enter the email or phone number you used during registration"),
            ios=(_A, "Enter the email or phone number you used during registration"),
        ),
        "identifier": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.EditText").instance(0)',
            ),
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'Phone number / Email'"),
            note="Android: the only EditText on the screen, hint 'Phone number / Email' — "
            "TD-A1 (UiSelector cannot match a hint)",
        ),
        "format-hint": El(
            android=(_A, "Format: +1234567890 or name@example.com"),
            ios=(_A, "Format: +1234567890 or name@example.com"),
        ),
        "continue": El(
            android=(_A, "Continue"),
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Continue'"),
        ),
        "privacy-link": El(
            android=(_A, "Privacy Policy"),
            ios=(_P, "type == 'XCUIElementTypeLink' AND name == 'Privacy Policy'"),
        ),
        "terms-link": El(
            android=(_A, "Terms & Conditions"),
            ios=(_P, "type == 'XCUIElementTypeLink' AND name == 'Terms & Conditions'"),
        ),
        "sign-up-link": El(
            android=(_A, "Sign up"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Sign up'"),
        ),
        "text-fields": El(
            android=(_U, 'new UiSelector().className("android.widget.EditText")'),
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="all inputs — for 'the only input on the screen' (count)",
        ),
        # Server messages (not registered): a red banner at the bottom for ~4 s, exposed as an
        # element of type Other named by its text (recon 3d) — hence no type in the predicate.
        # The Login screen shows NO format message at all: an invalid value only keeps
        # Continue disabled (recon 3d; question D-12).
        "error": El(
            android=(_A, "{text}"),
            ios=(_P, "name == {text}"),
            note="parametrised by the expected message; a transient banner (recon 3d); "
            "Android: same convention, content-desc equals the message (not in recon A1, "
            "parametrised so unverified offline by design)",
        ),
    },
)
