"""The iOS Settings app — only the path to the app's notification permission (module 11, recon 12).

Settings → Apps (``com.apple.settings.apps``) → the app's row → NOTIFICATIONS → the switch
``ALLOW_NOTIFICATIONS_ID`` (value '1' / '0'). A tap on the switch's label does not toggle it; the
page taps the switch itself, at the right end of the row. iOS only: Android is the emulator's own
settings (Android stage).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

SETTINGS = Screen(
    id="settings",
    anchor="root",
    elements={
        "root": El(ios=(_P, "type == 'XCUIElementTypeNavigationBar'")),
        "apps": El(ios=(_P, "name == 'com.apple.settings.apps'")),
        "app-row": El(
            ios=(_P, "name CONTAINS 'CT Mobile'"),
            note="the app in Settings → Apps ('[DEV] CT Mobile')",
        ),
        "notifications": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'NOTIFICATIONS'")
        ),
        "allow-notifications": El(
            ios=(_P, "type == 'XCUIElementTypeSwitch' AND name == 'ALLOW_NOTIFICATIONS_ID'"),
            note="value '1' on / '0' off",
        ),
    },
)
