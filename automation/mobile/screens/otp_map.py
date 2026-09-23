"""OTP — "Email address verification" / "Phone number verification" (module 02-authentication).

Source: recon 2026-09-23 (passes 3b, 3c) — the screen was driven through Appium, but its tree
was NOT saved, so only these facts are confirmed: the title texts, the hidden 1×1 code field
(the four cells are drawn), auto-submit after the 4th digit (D-5), ``Incorrect code.`` kept in
the tree while hidden (assert VISIBILITY only), an unnamed back button, the ``1:00`` timer.
Elements marked UNCONFIRMED use the checklist / test-case wording; recon 3d confirms them.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_TITLE = (
    "type == 'XCUIElementTypeStaticText' AND "
    "(name == 'Email address verification' OR name == 'Phone number verification')"
)

OTP = Screen(
    id="otp",
    anchor="root",
    elements={
        "root": El(ios=(_P, _TITLE)),
        "title": El(ios=(_P, _TITLE)),
        "instruction": El(
            ios=(_P, "name BEGINSWITH 'Enter the 4-digit code'"),
            note="UNCONFIRMED wording (TC-AUTH-005) — recon 3d",
        ),
        "destination": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name CONTAINS {text}"),
            note="parametrised by the address / last digits the code was sent to",
        ),
        "code": El(
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="hidden 1×1 field, no label — the only input; TD-AUTH-002",
        ),
        "verify": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Verify'"),
            note="UNCONFIRMED name — recon 3d",
        ),
        "error": El(
            ios=(_A, "Incorrect code."),
            note="present in the tree while hidden — expect-visible / expect-hidden only",
        ),
        "resend": El(
            ios=(_P, "name CONTAINS 'request a new code'"),
            note="UNCONFIRMED wording (TC-AUTH-009, countdown) — recon 3d",
        ),
    },
)
