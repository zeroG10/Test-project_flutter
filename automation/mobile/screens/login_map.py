"""Login — email or phone, then an OTP (module 02-authentication).

Source: Appium tree qa/shared/recon-dumps/ios-2026-09-23/login.xml (recon 2026-09-23).
Visible texts as locators (owner decision 2026-09-23). Android locators come with step 7.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE

LOGIN = Screen(
    id="login",
    anchor="root",
    elements={
        # The subtitle is unique to Login; "Log in" also appears on Registration (its link).
        "root": El(ios=(_A, "Good to see you! Let's get you logged in.")),
        "title": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Log in'")),
        "subtitle": El(ios=(_A, "Good to see you! Let's get you logged in.")),
        "helper": El(ios=(_A, "Enter the email or phone number you used during registration")),
        "identifier": El(
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'Phone number / Email'")
        ),
        "format-hint": El(ios=(_A, "Format: +1234567890 or name@example.com")),
        "continue": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Continue'")),
        "privacy-link": El(ios=(_P, "type == 'XCUIElementTypeLink' AND name == 'Privacy Policy'")),
        "terms-link": El(
            ios=(_P, "type == 'XCUIElementTypeLink' AND name == 'Terms & Conditions'")
        ),
        "sign-up-link": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Sign up'")),
        "text-fields": El(
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="all inputs — for 'the only input on the screen' (count)",
        ),
        # Validation and server messages: texts from the checklist (live-app wording, D-8).
        # Where they are drawn (inside the field / a banner) — UNCONFIRMED until recon 3d.
        "error": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == {text}"),
            note="parametrised by the expected message; position UNCONFIRMED (recon 3d)",
        ),
    },
)
