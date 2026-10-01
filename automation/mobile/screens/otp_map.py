"""OTP — "Email address verification" / "Phone number verification" (module 02-authentication).

Source: Appium trees qa/shared/recon-dumps/ios-2026-09-23/recon3d_otp*.xml (recon 3d,
2026-09-23). Confirmed: title, instruction, destination (the full email), the hidden 1×1 code
field (typed digits appear as texts "1", "2", "3" in the drawn cells), ``Verify`` disabled below
4 digits, the resend text with an m:ss countdown, a back button labelled ``Back``.

⚠️ ``Incorrect code.`` is in the tree AND reported ``visible=true`` before any input, while the
screenshot shows nothing there (recon 3d) — neither presence nor Appium visibility may decide
"the error is shown". See OtpPage.error_rendered(); TC-AUTH-008 needs that oracle.

Android: qa/shared/recon-dumps/android-2026-09-29/otp.xml (recon A1) — same trap ("Incorrect
code." in the tree before any input); the hidden field is an EditText with no hint (no label at
all, not even in ``hint``) — the four digit boxes are unlabelled clickable Views, not aliased
(mirrors the iOS map, which does not alias the drawn cells either).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR
_TITLE = (
    "type == 'XCUIElementTypeStaticText' AND "
    "(name == 'Email address verification' OR name == 'Phone number verification')"
)
_TITLE_ANDROID = (
    'new UiSelector().descriptionMatches("Email address verification|Phone number verification")'  # noqa: E501
)

OTP = Screen(
    id="otp",
    anchor="root",
    elements={
        "root": El(android=(_U, _TITLE_ANDROID), ios=(_P, _TITLE)),
        "title": El(android=(_U, _TITLE_ANDROID), ios=(_P, _TITLE)),
        "instruction": El(
            android=(_A, "Enter the 4-digit code sent to your email address"),
            ios=(_A, "Enter the 4-digit code sent to your email address"),
        ),
        "destination": El(
            android=(_U, "new UiSelector().descriptionContains({text})"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name CONTAINS {text}"),
            note="parametrised by the address / last digits the code was sent to",
        ),
        "code": El(
            android=(_U, 'new UiSelector().className("android.widget.EditText")'),
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="hidden 1×1 field, no label — the only input; TD-AUTH-002. Android: the only "
            "EditText on the screen, no hint either (recon A1)",
        ),
        "verify": El(
            android=(_A, "Verify"),
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Verify'"),
        ),
        "back": El(
            android=(_A, "Back"),
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Back'"),
        ),
        "error": El(
            android=(_A, "Incorrect code."),
            ios=(_A, "Incorrect code."),
            note="in the tree and 'visible' even when not drawn — "
            "decide by OtpPage.error_rendered() (Android: same trap, recon A1)",
        ),
        "network-error": El(
            android=(_A, "No internet connection"),
            note="Android only (step 5): under the code field when the check fails offline "
            "(recon A2 row 3, otp_offline_8s.xml)",
        ),
        # "Didn't receive the code? You can request a new code in 0:59"
        "resend": El(
            android=(_U, 'new UiSelector().descriptionContains("You can request a new code in")'),
            ios=(_P, "name CONTAINS 'You can request a new code in'"),
        ),
    },
)
