"""Job-link dialogs (module 03-order-list, SRS §3.1.2.0 / FR-ORD-01-1).

Source: recon 4 (qa/shared/recon-dumps/ios-2026-09-24/recon4c_*.xml, recon4b_link_https_*.xml)
and Figma `Basic dialog/True` 2451:82555. Both are app dialogs (not system alerts); texts are
the app's wording (D-ORDL-9, accepted).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "

MISMATCH_MESSAGE = (
    "The jobs you are trying to access are assigned to a different phone number. "
    "To continue, please log out and sign in with the phone number linked to this job."
)

LINK_EXPIRED = Screen(
    id="link-expired",
    anchor="title",
    elements={
        "title": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Link expired'")),
        "message": El(ios=(_A, "This link is no longer valid.")),
        "ok": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'OK'")),
    },
)

PHONE_MISMATCH = Screen(
    id="phone-mismatch",
    anchor="title",
    elements={
        "title": El(
            ios=(
                _P,
                _TEXT + "name == 'Assigned to a different phone number'",
            )
        ),
        "message": El(ios=(_A, MISMATCH_MESSAGE)),
        "cancel": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Cancel'")),
        "log-out": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Log out'")),
    },
)
