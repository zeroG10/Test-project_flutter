"""The app's "Enter location manually" dialog (recon A1): shown when no GPS fix comes in time
(``location_flow_cubit.dart``). Unreachable on the iOS simulator, which always reports a
location; CHK-ORDD-036…042 and CHK-CHIO-013/019/024…026 become Android tests (owner, Q-ORDD-A3).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID

LOCATION_MANUAL = Screen(
    id="location-manual",
    anchor="title",
    elements={
        "title": El(android=(_A, "Enter location manually"), note="Android only: dialog title"),
        "message": El(
            android=(_A, "We can't detect your location automatically. Please, enter it manually."),
            note="Android only: dialog text (location_manual_entry.xml)",
        ),
        "address": El(
            android=(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("android.widget.EditText").instance(0)',
            ),
            note="Android only: hint 'Job site address', pre-filled with the job's address. "
            "TD-A1: Flutter text field without label/id — UiSelector cannot match a hint",
        ),  # fmt: skip
        "cancel": El(android=(_A, "Cancel"), note="Android only: Cancel"),
        "confirm": El(android=(_A, "Confirm"), note="Android only: Confirm"),
    },
)
