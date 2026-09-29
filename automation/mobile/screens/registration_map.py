"""Registration — self sign-up of a technician (module 02-authentication).

Source: Appium trees qa/shared/recon-dumps/ios-2026-09-23/registration_*.xml (recon 3c,
2026-09-23). The lower half (Continue, links) is off-screen until scrolled: ``scroll_to``.
Android: qa/shared/recon-dumps/android-2026-09-29/registration.xml, registration_bottom.xml,
registration_sms_accepted.xml (recon A1) — same texts and behaviour (SMS choice opens SMS
Terms, consent checkbox disabled until SMS chosen); the four name/contact fields are
EditTexts with the label only in ``hint`` (TD-A1); the two channel controls are
``android.widget.RadioButton`` and the consent is an ``android.widget.CheckBox``.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import EditTextByHint, El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR


def _field(label: str) -> El:
    return El(ios=(_P, f"type == 'XCUIElementTypeTextField' AND name == '{label}'"))


REGISTRATION = Screen(
    id="registration",
    anchor="root",
    elements={
        # The screen container (named by its trailing text): stays visible when the form scrolls,
        # unlike the subtitle (recon 3d).
        "root": El(
            android=(_A, "Already have an account?"),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Already have an account?'"),
        ),
        "title": El(
            android=(_A, "Registration"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Registration'"),
        ),
        "subtitle": El(
            android=(_A, "Good to see you! Let's get you registered."),
            ios=(_A, "Good to see you! Let's get you registered."),
        ),
        "first-name": El(
            android=EditTextByHint(0, "First name"),
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'First name'"),
            note="Android: EditText instance(0), hint 'First name' — TD-A1 (found by hint)",
        ),
        "last-name": El(
            android=EditTextByHint(1, "Last name"),
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'Last name'"),
            note="Android: EditText instance(1), hint 'Last name' — TD-A1 (found by hint)",
        ),
        "phone": El(
            android=EditTextByHint(2, "Phone number"),
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'Phone number'"),
            note="Android: EditText instance(2), hint 'Phone number' — TD-A1 (found by hint)",
        ),
        "email": El(
            android=EditTextByHint(3, "Email"),
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'Email'"),
            note="Android: EditText instance(3), hint 'Email' — TD-A1 (found by hint)",
        ),
        # Country picker: name "United States + 1\n+ 1" (spoken label + the visible "+ 1").
        "phone-prefix": El(
            android=(_A, "United States + 1\n+ 1"),
            ios=(_P, "type == 'XCUIElementTypeButton' AND name BEGINSWITH 'United States'"),
        ),
        "channel-section": El(
            android=(_A, "Preferred channel for job notifications"),
            ios=(_A, "Preferred channel for job notifications"),
        ),
        # Container of the two radios; its name is the two captions "SMS\nEmail".
        "channel-options": El(
            android=(_A, "SMS\nEmail"),
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' "
                "AND name BEGINSWITH 'SMS' AND name ENDSWITH 'Email'",
            ),
            note="anchor for the unnamed radios: SMS = left half, Email = right half — TD-AUTH-003",
        ),
        "channel-radios": El(
            android=(_U, 'new UiSelector().className("android.widget.RadioButton")'),
            ios=(_P, "type == 'XCUIElementTypeButton' AND (name == nil OR name == '')"),
            note="both unnamed radios (value '1' = selected); the page tells them apart by "
            "position inside channel-options — TD-AUTH-003. Android: both RadioButtons "
            "(checked='true' when selected), same position rule (recon A1)",
        ),
        "sms-consent": El(
            android=(_U, 'new UiSelector().className("android.widget.CheckBox")'),
            ios=(_P, "type == 'XCUIElementTypeSwitch'"),
            note="the only switch; unnamed, value 0/1, disabled until SMS is chosen — TD-AUTH-004."
            " Android: the only CheckBox, unnamed, enabled only once SMS is chosen (recon A1)",
        ),
        "sms-consent-label": El(
            android=(
                _A,
                "I agree to receive automated SMS messages from Concert Technologies Group, "
                "Inc., including one-time passwords (OTPs), job notifications, and account "
                "alerts.",
            ),
            ios=(_P, "name BEGINSWITH 'I agree to receive automated SMS messages'"),
        ),
        "sms-consent-text": El(
            android=(
                _U,
                "new UiSelector().descriptionStartsWith("
                '"Checking this box you agree to receive SMS messages")',
            ),
            ios=(_P, "name BEGINSWITH 'Checking this box you agree to receive SMS'"),
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
        "log-in-link": El(
            android=(_A, "Log in"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Log in'"),
        ),
        "logo": El(
            android=(_U, 'new UiSelector().className("android.widget.ImageView")'),
            ios=(_P, "type == 'XCUIElementTypeImage'"),
            note="unlabelled image — TD-AUTH-001; logo checks stay manual (partial); Android: "
            "the only ImageView, visible only at the top before scrolling (recon A1)",
        ),
        # Server-side error after Continue (duplicate phone, TC-AUTH-014), wording from the
        # checklist (D-7). Login shows its server errors as a banner of type Other (recon 3d),
        # so the predicate names no type.
        "form-error": El(
            android=(_A, "{text}"),
            ios=(_P, "name == {text}"),
            note="parametrised by the expected message; Android: same convention as "
            "login.error, content-desc equals the message (parametrised, unverified offline "
            "by design)",
        ),
    },
)
