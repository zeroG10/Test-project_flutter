"""The iOS Settings app — only the path to the app's notification permission (module 11, recon 12).

Settings → Apps (``com.apple.settings.apps``) → the app's row → NOTIFICATIONS → the switch
``ALLOW_NOTIFICATIONS_ID`` (value '1' / '0'). A tap on the switch's label does not toggle it; the
page taps the switch itself, at the right end of the row. iOS only: Android is the emulator's own
settings (Android stage).

Android (D-NOTIF-A2, recon A1 qa/shared/recon-dumps/android-2026-09-29/android_settings.xml):
"Go to Settings" opens the app's own notification page directly — activity
``com.android.settings/.Settings$AppNotificationSettingsActivity`` — skipping the
Apps-list / app-row / NOTIFICATIONS navigation entirely (ANDROID_WITHOUT below). The switch is
``android:id/switch_widget`` (checked=true/false), labelled by
``com.android.settings:id/switch_text`` "All [DEV] CT Mobile notifications".
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_ID = AppiumBy.ID

SETTINGS = Screen(
    id="settings",
    anchor="root",
    elements={
        "root": El(
            android=(_ID, "com.android.settings:id/collapsing_toolbar"),
            ios=(_P, "type == 'XCUIElementTypeNavigationBar'"),
            note="Android: the app-notifications page's toolbar (content-desc '[DEV] CT "
            "Mobile') — the page is reached directly, no navigation bar concept carried over "
            "(recon A1)",
        ),
        "apps": El(ios=(_P, "name == 'com.apple.settings.apps'")),
        "app-row": El(
            ios=(_P, "name CONTAINS 'CT Mobile'"),
            note="the app in Settings → Apps ('[DEV] CT Mobile')",
        ),
        "notifications": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'NOTIFICATIONS'")
        ),
        "allow-notifications": El(
            android=(_ID, "android:id/switch_widget"),
            ios=(_P, "type == 'XCUIElementTypeSwitch' AND name == 'ALLOW_NOTIFICATIONS_ID'"),
            note="value '1' on / '0' off. Android: checked=true/false; labelled by "
            "com.android.settings:id/switch_text 'All [DEV] CT Mobile notifications' "
            "(recon A1)",
        ),
    },
)

ANDROID_WITHOUT = {
    "settings.apps": "Android: 'Go to Settings' opens the app's notification page directly "
    "(Settings$AppNotificationSettingsActivity) — no Apps-list step (D-NOTIF-A2, recon A1)",
    "settings.app-row": "Android: no app-row step — opens straight to the app's own "
    "notification page (D-NOTIF-A2, recon A1)",
    "settings.notifications": "Android: no NOTIFICATIONS tap — the notification page is the "
    "one that opens (D-NOTIF-A2, recon A1)",
}
