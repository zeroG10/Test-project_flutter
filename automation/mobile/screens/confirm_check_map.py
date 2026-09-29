"""The check-in / check-out confirmation screens (module 05-check-in-out, SRS §3.1.3.3).

Source: recon 6c (qa/shared/recon-dumps/ios-2026-09-24/recon6c_site_1.xml, recon6c_co_1.xml) and
Figma `Job details_Confirm check in` 2451:83073 / `…_Confirm check out` 2451:83083 — the same
layout for both: app-bar title (Header), a picture, a primary message, a supporting text, Cancel
and Confirm. The X is an IconButton without a label — the only unnamed button of the app bar.

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/confirm_check_in.xml,
confirm_check_out.xml): same layout and texts, content-desc based. Only three Buttons on screen
(close, Cancel, Confirm) — close is unlabelled and first in document order.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_HEADER = "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND "
_U = AppiumBy.ANDROID_UIAUTOMATOR
_A = AppiumBy.ACCESSIBILITY_ID

CONFIRM_CHECK = Screen(
    id="confirm-check",
    anchor="confirm",
    elements={
        "title": El(
            ios=(_P, _HEADER + "name == {text}"),
            android=(_A, "{text}"),
            note="'Confirm check in' / 'Confirm check out'",
        ),
        "primary": El(
            ios=(_P, _TEXT + "name == {text}"),
            android=(_A, "{text}"),
            note="'Check in and start' / 'Check out and finish'",
        ),
        "supporting": El(
            ios=(_P, _TEXT + "name == {text}"),
            android=(_A, "{text}"),
            note="'Confirm you are on site to begin the job.' / '… ready to finish the job.'",
        ),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'"), android=(_A, "Cancel")),
        "confirm": El(ios=(_P, _BUTTON + "name == 'Confirm'"), android=(_A, "Confirm")),
        "close": El(
            ios=(_P, _BUTTON + "(name == nil OR name == '') AND rect.y < 140"),
            android=(
                _U,
                'new UiSelector().className("android.widget.Button").clickable(true).instance(0)',
            ),
            note="the X has no label (app code audit §3): the only unnamed app-bar button. "
            "Android: same unlabelled X (no content-desc/resource-id, recon A1) — position-based, "
            "the first clickable Button in document order, before Cancel/Confirm",
        ),
    },
)
