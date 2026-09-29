"""Profile (module 12-profile, SRS §3.1.5). Source: recon 4 (root) and recon 13
(qa/shared/recon-dumps/ios-2026-09-24/recon13_*.xml).

The tab is named 'Profile\\nTab 3 of 3', so the screen title is matched by type and exact name. The
user card is ONE element named '<first last>\\n<phone>\\n<email>'; its Edit button has no name (the
unnamed button at the card's top right). App theme is a row named 'App theme (<mode>)' with a
'Show menu' button; its menu offers Auto / Light / Dark.

Android: qa/shared/recon-dumps/android-2026-09-29/profile.xml, theme_menu.xml,
logout_dialog.xml (recon A1) — the card is an unlabelled ``android.view.View`` (content-desc
contains '@', redacted in the dump); Edit is the first unlabelled clickable ImageView; theme
menu items and Log out are ImageViews; the logout dialog's title 'Log out' (a View) and its
confirm button 'Log out' (a Button) share the same content-desc — disambiguated by className.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "

PROFILE = Screen(
    id="profile",
    anchor="root",
    elements={
        "root": El(
            android=(_A, "Profile"),
            ios=(AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeOther' AND name == 'Profile'"),
        ),
        "card": El(
            android=(_U, 'new UiSelector().descriptionContains("@")'),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name CONTAINS '@' AND rect.y < 200"),
            note="'<first last>\\n<phone>\\n<email>' — read by the page. Android: the only "
            "element whose content-desc contains '@' on this screen (recon A1)",
        ),
        "edit": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.ImageView")'
                ".clickable(true).instance(0)",
            ),
            ios=(_P, _BUTTON + "rect.x > 330 AND rect.y < 200 AND rect.width < 40"),
            note="unnamed, at the card's top right (@346,142 32x32) — testability defect. "
            "Android: the first clickable ImageView (the tabs come after it, recon A1); it has no "
            "content-desc at all, which no description selector matches (01+03 run 3)",
        ),
        "theme": El(
            android=(_U, 'new UiSelector().descriptionStartsWith("App theme (")'),
            ios=(_P, "name BEGINSWITH 'App theme ('"),
            note="'App theme (Auto|Light|Dark)'",
        ),
        "theme-menu": El(android=(_A, "Show menu"), ios=(_P, _BUTTON + "name == 'Show menu'")),
        "privacy": El(
            android=(_A, "Privacy Policy"),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Privacy Policy'"),
        ),
        "terms": El(
            android=(_A, "Terms & Conditions"),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Terms & Conditions'"),
        ),
        "logout": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.ImageView").description("Log out")',
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND name == 'Log out'"),
            note="Android: className disambiguates from LOGOUT_DIALOG's Button 'Log out' "
            "(recon A1)",
        ),
        "version": El(
            android=(_U, 'new UiSelector().descriptionStartsWith("v")'),
            ios=(_P, _TEXT + "name BEGINSWITH 'v'"),
            note="'v<version> (<build>)'",
        ),
    },
)

THEME_MENU = Screen(
    id="theme-menu",
    anchor="auto",
    elements={
        "auto": El(android=(_A, "Auto"), ios=(_P, _BUTTON + "name == 'Auto'")),
        "light": El(android=(_A, "Light"), ios=(_P, _BUTTON + "name == 'Light'")),
        "dark": El(android=(_A, "Dark"), ios=(_P, _BUTTON + "name == 'Dark'")),
    },
)

LOGOUT_DIALOG = Screen(
    id="logout-dialog",
    anchor="title",
    elements={
        "title": El(
            android=(
                _U,
                'new UiSelector().className("android.view.View").description("Log out")',
            ),
            ios=(_P, _TEXT + "name == 'Log out'"),
            note="Android: className disambiguates from the Button 'confirm' (recon A1)",
        ),
        "message": El(
            android=(
                _U,
                'new UiSelector().descriptionStartsWith("Are you sure you want to log out?")',
            ),
            ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want to log out?'"),
            note="Android: trailing space after the '?' in the real content-desc (recon A1)",
        ),
        "cancel": El(android=(_A, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "confirm": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.Button").description("Log out")',
            ),
            ios=(_P, _BUTTON + "name == 'Log out'"),
            note="Android: className disambiguates from the dialog's title (recon A1)",
        ),
    },
)
