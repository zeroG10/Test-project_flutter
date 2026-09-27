"""Profile (module 12-profile, SRS §3.1.5). Source: recon 4 (root) and recon 13
(qa/shared/recon-dumps/ios-2026-09-24/recon13_*.xml).

The tab is named 'Profile\\nTab 3 of 3', so the screen title is matched by type and exact name. The
user card is ONE element named '<first last>\\n<phone>\\n<email>'; its Edit button has no name (the
unnamed button at the card's top right). App theme is a row named 'App theme (<mode>)' with a
'Show menu' button; its menu offers Auto / Light / Dark.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "

PROFILE = Screen(
    id="profile",
    anchor="root",
    elements={
        "root": El(
            ios=(AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeOther' AND name == 'Profile'")
        ),
        "card": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name CONTAINS '@' AND rect.y < 200"),
            note="'<first last>\\n<phone>\\n<email>' — read by the page",
        ),
        "edit": El(
            ios=(_P, _BUTTON + "rect.x > 330 AND rect.y < 200 AND rect.width < 40"),
            note="unnamed, at the card's top right (@346,142 32x32) — testability defect",
        ),
        "theme": El(
            ios=(_P, "name BEGINSWITH 'App theme ('"), note="'App theme (Auto|Light|Dark)'"
        ),
        "theme-menu": El(ios=(_P, _BUTTON + "name == 'Show menu'")),
        "privacy": El(ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Privacy Policy'")),
        "terms": El(ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Terms & Conditions'")),
        "logout": El(ios=(_P, "type == 'XCUIElementTypeImage' AND name == 'Log out'")),
        "version": El(ios=(_P, _TEXT + "name BEGINSWITH 'v'"), note="'v<version> (<build>)'"),
    },
)

THEME_MENU = Screen(
    id="theme-menu",
    anchor="auto",
    elements={
        "auto": El(ios=(_P, _BUTTON + "name == 'Auto'")),
        "light": El(ios=(_P, _BUTTON + "name == 'Light'")),
        "dark": El(ios=(_P, _BUTTON + "name == 'Dark'")),
    },
)

LOGOUT_DIALOG = Screen(
    id="logout-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Log out'")),
        "message": El(ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want to log out?'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "confirm": El(ios=(_P, _BUTTON + "name == 'Log out'")),
    },
)
