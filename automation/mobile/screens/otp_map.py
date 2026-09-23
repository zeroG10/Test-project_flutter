"""OTP — "Email address verification" / "Phone number verification" (module 02-authentication).

Source: Appium trees qa/shared/recon-dumps/ios-2026-09-23/recon3d_otp*.xml (recon 3d,
2026-09-23). Confirmed: title, instruction, destination (the full email), the hidden 1×1 code
field (typed digits appear as texts "1", "2", "3" in the drawn cells), ``Verify`` disabled below
4 digits, the resend text with an m:ss countdown, a back button labelled ``Back``.

⚠️ ``Incorrect code.`` is in the tree AND reported ``visible=true`` before any input, while the
screenshot shows nothing there (recon 3d) — neither presence nor Appium visibility may decide
"the error is shown". See OtpPage.error_rendered(); TC-AUTH-008 needs that oracle.
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
        "instruction": El(ios=(_A, "Enter the 4-digit code sent to your email address")),
        "destination": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name CONTAINS {text}"),
            note="parametrised by the address / last digits the code was sent to",
        ),
        "code": El(
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="hidden 1×1 field, no label — the only input; TD-AUTH-002",
        ),
        "verify": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Verify'")),
        "back": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Back'")),
        "error": El(
            ios=(_A, "Incorrect code."),
            note="in the tree and 'visible' even when not drawn — "
            "decide by OtpPage.error_rendered()",
        ),
        # "Didn't receive the code? You can request a new code in 0:59"
        "resend": El(ios=(_P, "name CONTAINS 'You can request a new code in'")),
    },
)
