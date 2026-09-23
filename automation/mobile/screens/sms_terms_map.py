"""SMS Messaging Terms & Conditions — opened by choosing the SMS channel (D-9).

Source: Appium trees registration_sms_selected.xml, sms_terms_bottom.xml (recon 3c,
2026-09-23). The Accept button appears only after scrolling to the end.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE

SMS_TERMS = Screen(
    id="sms-terms",
    anchor="root",
    elements={
        "root": El(ios=(_A, "SMS Messaging Terms & Conditions")),
        "title": El(ios=(_A, "SMS Messaging Terms & Conditions")),
        "accept": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeButton' AND name == 'I Accept SMS Terms & Conditions'",
            )
        ),
        "close": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND (name == nil OR name == '')"),
            note="unnamed close icon, the only unnamed button here — TD-AUTH-005 "
            "(CHK-AUTH-057 deferred)",
        ),
    },
)
