"""The system dialer a phone link opens on Android: the test checks the number, it never places
a call. iOS: Blocked — the simulator has no Phone app.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

DIALER_PACKAGE = "com.google.android.dialer"

DIALER = Screen(
    id="dialer",
    anchor="number",
    elements={
        "number": El(
            android=(AppiumBy.ID, f"{DIALER_PACKAGE}:id/digits"),
            note="Android only: the number field, e.g. '+1 202-555-0147' (dialer.xml)",
        ),
    },
)
