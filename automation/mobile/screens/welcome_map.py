"""Welcome — first screen of a signed-out app (module 02-authentication).

Source: Appium tree qa/shared/recon-dumps/ios-2026-09-23/welcome.xml (recon 2026-09-23).
The app ships no ``Semantics(identifier:)`` (audit): locators are the visible texts, by
owner decision 2026-09-23. Android: qa/shared/recon-dumps/android-2026-09-29/welcome.xml
(recon A1) — same texts as iOS (content-desc, newlines included).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR

WELCOME = Screen(
    id="welcome",
    anchor="root",
    elements={
        # The title wraps: name is "Welcome to Concert\nTechnologies' Field Force" (D-1 wording).
        "root": El(
            android=(_A, "Welcome to Concert\nTechnologies' Field Force"),
            ios=(_P, "name BEGINSWITH 'Welcome to Concert'"),
        ),
        "title": El(
            android=(_A, "Welcome to Concert\nTechnologies' Field Force"),
            ios=(_P, "name BEGINSWITH 'Welcome to Concert'"),
        ),
        "subtitle": El(
            android=(_A, "Create an account or log in to get started."),
            ios=(AppiumBy.ACCESSIBILITY_ID, "Create an account or log in to get started."),
        ),
        # Type-qualified: the Login screen has a *text* "Sign up" too.
        "sign-up": El(
            android=(_A, "Sign up"),
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Sign up'"),
        ),
        "login": El(
            android=(_A, "Login"),
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Login'"),
        ),
        # Asserted HIDDEN (CHK-AUTH-003): a Flutter back button is labelled "Back" on other
        # screens and unnamed on OTP / SMS Terms — neither may show here.
        "back": El(
            android=(_A, "Back"),
            ios=(
                _P,
                "type == 'XCUIElementTypeButton' AND (name == 'Back' OR name == nil OR name == '')",
            ),
            note="any back control; used only for expect-hidden — on Android 'Back' (matches "
            "nothing here, confirmed absent in welcome.xml, recon A1)",
        ),
        "logo": El(
            android=(_U, 'new UiSelector().className("android.widget.ImageView")'),
            ios=(_P, "type == 'XCUIElementTypeImage'"),
            note="unlabelled image — TD-AUTH-001; logo checks stay manual (partial); Android: "
            "the only ImageView on this screen (position-based, recon A1)",
        ),
    },
)
