"""Registration — self sign-up of a technician (module 02-authentication).

Source: Appium trees qa/shared/recon-dumps/ios-2026-09-23/registration_*.xml (recon 3c,
2026-09-23). The lower half (Continue, links) is off-screen until scrolled: ``scroll_to``.
Android locators come with step 7.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE


def _field(label: str) -> El:
    return El(ios=(_P, f"type == 'XCUIElementTypeTextField' AND name == '{label}'"))


REGISTRATION = Screen(
    id="registration",
    anchor="root",
    elements={
        # The screen container (named by its trailing text): stays visible when the form scrolls,
        # unlike the subtitle (recon 3d).
        "root": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Already have an account?'")
        ),
        "title": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Registration'")),
        "subtitle": El(ios=(_A, "Good to see you! Let's get you registered.")),
        "first-name": _field("First name"),
        "last-name": _field("Last name"),
        "phone": _field("Phone number"),
        "email": _field("Email"),
        # Country picker: name "United States + 1\n+ 1" (spoken label + the visible "+ 1").
        "phone-prefix": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name BEGINSWITH 'United States'")
        ),
        "channel-section": El(ios=(_A, "Preferred channel for job notifications")),
        # Container of the two radios; its name is the two captions "SMS\nEmail".
        "channel-options": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' "
                "AND name BEGINSWITH 'SMS' AND name ENDSWITH 'Email'",
            ),
            note="anchor for the unnamed radios: SMS = left half, Email = right half — TD-AUTH-003",
        ),
        "channel-radios": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND (name == nil OR name == '')"),
            note="both unnamed radios (value '1' = selected); the page tells them apart by "
            "position inside channel-options — TD-AUTH-003",
        ),
        "sms-consent": El(
            ios=(_P, "type == 'XCUIElementTypeSwitch'"),
            note="the only switch; unnamed, value 0/1, disabled until SMS is chosen — TD-AUTH-004",
        ),
        "sms-consent-label": El(
            ios=(_P, "name BEGINSWITH 'I agree to receive automated SMS messages'")
        ),
        "sms-consent-text": El(
            ios=(_P, "name BEGINSWITH 'Checking this box you agree to receive SMS'")
        ),
        "continue": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Continue'")),
        "privacy-link": El(ios=(_P, "type == 'XCUIElementTypeLink' AND name == 'Privacy Policy'")),
        "terms-link": El(
            ios=(_P, "type == 'XCUIElementTypeLink' AND name == 'Terms & Conditions'")
        ),
        "log-in-link": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Log in'")),
        "logo": El(
            ios=(_P, "type == 'XCUIElementTypeImage'"),
            note="unlabelled image — TD-AUTH-001; logo checks stay manual (partial)",
        ),
        # Server-side error after Continue (duplicate phone, TC-AUTH-014), wording from the
        # checklist (D-7). Login shows its server errors as a banner of type Other (recon 3d),
        # so the predicate names no type.
        "form-error": El(
            ios=(_P, "name == {text}"),
            note="parametrised by the expected message",
        ),
    },
)
