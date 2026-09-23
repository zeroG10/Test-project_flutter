"""Welcome — first screen of a signed-out app (module 02-authentication).

Source: Appium tree qa/shared/recon-dumps/ios-2026-09-23/welcome.xml (recon 2026-09-23).
The app ships no ``Semantics(identifier:)`` (audit): locators are the visible texts, by
owner decision 2026-09-23. Android locators come with step 7.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

WELCOME = Screen(
    id="welcome",
    anchor="root",
    elements={
        # The title wraps: name is "Welcome to Concert\nTechnologies' Field Force" (D-1 wording).
        "root": El(ios=(_P, "name BEGINSWITH 'Welcome to Concert'")),
        "title": El(ios=(_P, "name BEGINSWITH 'Welcome to Concert'")),
        "subtitle": El(
            ios=(AppiumBy.ACCESSIBILITY_ID, "Create an account or log in to get started.")
        ),
        # Type-qualified: the Login screen has a *text* "Sign up" too.
        "sign-up": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Sign up'")),
        "login": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Login'")),
        # Asserted HIDDEN (CHK-AUTH-003): a Flutter back button is labelled "Back" on other
        # screens and unnamed on OTP / SMS Terms — neither may show here.
        "back": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeButton' AND (name == 'Back' OR name == nil OR name == '')",
            ),
            note="any back control; used only for expect-hidden",
        ),
        "logo": El(
            ios=(_P, "type == 'XCUIElementTypeImage'"),
            note="unlabelled image — TD-AUTH-001; logo checks stay manual (partial)",
        ),
    },
)
