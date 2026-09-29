"""Job-link dialogs (module 03-order-list, SRS §3.1.2.0 / FR-ORD-01-1).

Source: recon 4 (qa/shared/recon-dumps/ios-2026-09-24/recon4c_*.xml, recon4b_link_https_*.xml)
and Figma `Basic dialog/True` 2451:82555. Both are app dialogs (not system alerts); texts are
the app's wording (D-ORDL-9, accepted).

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/link_expired.xml, phone_mismatch.xml):
same texts and shape — an app dialog (content-desc "Dismiss" full-window barrier under it, as
submit-dialog.layer). Unlike the iOS simulator, the mismatch dialog does NOT close itself on
Android (Q-ORDL-A2, recon-2026-09-29-android.md) — report to the main session, no map change.
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
        "title": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Link expired'"),
            android=(_A, "Link expired"),
        ),
        "message": El(
            ios=(_A, "This link is no longer valid."),
            android=(_A, "This link is no longer valid."),
        ),
        "ok": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'OK'"), android=(_A, "OK")),
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
            ),
            android=(_A, "Assigned to a different phone number"),
        ),
        "message": El(ios=(_A, MISMATCH_MESSAGE), android=(_A, MISMATCH_MESSAGE)),
        "cancel": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Cancel'"), android=(_A, "Cancel")
        ),
        "log-out": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Log out'"),
            android=(_A, "Log out"),
        ),
    },
)
