"""Google Maps — what "On map" opens on Android (recon A1; D-ORDD-A1, CHK-ORDD-012 allows an
external maps app). On iOS the same step opens the in-app browser on maps.apple.com.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

MAPS_PACKAGE = "com.google.android.apps.maps"

MAPS_APP = Screen(
    id="maps-app",
    anchor="search",
    elements={
        "search": El(
            android=(AppiumBy.ID, f"{MAPS_PACKAGE}:id/search_omnibox_text_box"),
            note="Android only: the search box; its content-desc is the job's address "
            "(maps_app.xml)",
        ),
        "skip": El(
            android=(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Skip")'),
            note="Android only: 'Make it your map' first-run sign-in offer "
            "(maps_app_first_run.xml)",
        ),
    },
)
