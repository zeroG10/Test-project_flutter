"""System dialogs that exist only on Android (recon A1, 2026-09-29;
qa/shared/recon-2026-09-29-android.md).

Other apps' UI: stable resource ids of the permission controller, Google Play services and the
system ANR dialog. The iOS counterparts are system alerts answered by ``autoAcceptAlerts``.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_ID = AppiumBy.ID
_U = AppiumBy.ANDROID_UIAUTOMATOR
_PC = "com.android.permissioncontroller:id/"
_GMS = 'new UiSelector().packageName("com.google.android.gms")'

NOTIFICATION_PERMISSION = Screen(
    id="notification-permission",
    anchor="allow",
    elements={
        "message": El(
            android=(_ID, f"{_PC}permission_message"),
            note="Android only: 'Allow [DEV] CT Mobile to send you notifications?' — asked after "
            "the first sign-in (Android 13+ POST_NOTIFICATIONS; perm_notifications.xml)",
        ),
        "allow": El(android=(_ID, f"{_PC}permission_allow_button"), note="Android only: Allow"),
        "deny": El(android=(_ID, f"{_PC}permission_deny_button"), note="Android only: Don't allow"),
    },
)

LOCATION_ACCURACY = Screen(
    id="location-accuracy",
    anchor="turn-on",
    elements={
        "message": El(
            android=(_ID, "com.google.android.gms:id/message"),
            note="Android only: Google Play services 'For a better experience, your device will "
            "need to use Location Accuracy' before the first fix (gms_location_accuracy.xml)",
        ),
        "turn-on": El(
            android=(_U, _GMS + '.text("Turn on")'),
            note="Android only: android:id/button1 of the Play-services dialog",
        ),
        "no-thanks": El(
            android=(_U, _GMS + '.text("No thanks")'),
            note="Android only: android:id/button2 of the Play-services dialog",
        ),
    },
)

ANR_DIALOG = Screen(
    id="anr-dialog",
    anchor="wait",
    elements={
        "title": El(
            android=(_ID, "android:id/alertTitle"),
            note="Android only: '[DEV] CT Mobile isn't responding' — a starved emulator (recon A1, "
            "Fable's analysis): Blocked, never Failed",
        ),
        "wait": El(android=(_ID, "android:id/aerr_wait"), note="Android only: Wait"),
        "close-app": El(android=(_ID, "android:id/aerr_close"), note="Android only: Close app"),
    },
)
