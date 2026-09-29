"""SMS Messaging Terms & Conditions — opened by choosing the SMS channel (D-9).

Source: Appium trees registration_sms_selected.xml, sms_terms_bottom.xml (recon 3c,
2026-09-23). The Accept button appears only after scrolling to the end. Android:
qa/shared/recon-dumps/android-2026-09-29/sms_terms.xml, sms_terms_bottom.xml (recon A1) —
same texts; back is an unlabelled Button top-left (not added to the tree until scrolled to
the bottom does the Accept button appear).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR

SMS_TERMS = Screen(
    id="sms-terms",
    anchor="root",
    elements={
        "root": El(
            android=(_A, "SMS Messaging Terms & Conditions"),
            ios=(_A, "SMS Messaging Terms & Conditions"),
        ),
        "title": El(
            android=(_A, "SMS Messaging Terms & Conditions"),
            ios=(_A, "SMS Messaging Terms & Conditions"),
        ),
        "accept": El(
            android=(_A, "I Accept SMS Terms & Conditions"),
            ios=(
                _P,
                "type == 'XCUIElementTypeButton' AND name == 'I Accept SMS Terms & Conditions'",
            ),
        ),
        "close": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.Button").clickable(true).instance(0)',
            ),
            ios=(_P, "type == 'XCUIElementTypeButton' AND (name == nil OR name == '')"),
            note="unnamed close icon, the only unnamed button here — TD-AUTH-005 "
            "(CHK-AUTH-057 deferred). Android: unlabelled Button top-left, position-based "
            "(the first Button in document order — Accept is appended after scrolling, "
            "recon A1)",
        ),
    },
)
