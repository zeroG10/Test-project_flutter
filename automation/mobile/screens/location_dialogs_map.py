"""The location prompts and alerts of a check-in / check-out (modules 04 and 05).

Source: recon 5 / 5b (qa/shared/recon-dumps/ios-2026-09-24/recon5b_checkin_os_prompt.xml,
recon5b_checkin_after_dont_allow.xml). The first one is the SYSTEM permission alert: it is in the
page source only while the session setting ``respectSystemAlerts`` is on
(pages/location_dialogs_page.py). The others are the app's own dialogs (recon 6 / 6c).

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/perm_location.xml,
perm_location_second.xml, location_disabled.xml, not_at_site.xml, mock_location.xml):
- location-prompt is the real Android permission dialog (package
  com.google.android.permissioncontroller), always in the page source (no respectSystemAlerts
  concept). It has ONE combined text (TextView id permission_message: "Allow [DEV] CT Mobile to
  access this device's location?") where iOS splits title + message — "title" and "message" both
  resolve to it here. "Don't allow" is a different resource-id the second time a permission is
  requested (permission_deny_button → permission_deny_and_dont_ask_again_button) — matched by one
  regex. A third button not modelled on iOS, "Only this time"
  (permission_allow_one_time_button), was seen too — no alias added (unused by any test case).
- not-at-site and mock-location are the app's own dialogs, same texts as iOS (recon A1).
- location-access-required (Android only): after a FIRST refusal Android may still ask again, and
  the app shows "Location access required" / "GPS is required to check in. Enable location
  services to continue." / Cancel / "Enable" — Enable asks the system again (owner-accepted,
  D-CHIO-A3). A refusal the system will not ask about again (iOS: the first one; Android: the
  second, "don't ask again") leads to location-disabled — the SAME app dialog on both platforms
  (`showLocationDisabledDialog` for `permissionDeniedForever`, app code
  location_flow_cubit.dart; module 05 Android, 2026-09-30). The map of step 3 had put the Android
  dialog under the location-disabled aliases; not reached in recon A1, hence listed unverified.
- Two dialogs still have no alias (task brief: report, do not add screens): the "Enter location
  manually" dialog (location_manual_entry.xml — content-desc "Enter location manually" / "We
  can't detect your location automatically. Please, enter it manually." / an EditText, hint "Job
  site address" / Cancel / Confirm) and Google's "Location Accuracy" dialog
  (gms_location_accuracy.xml, package com.google.android.gms, resource-id android:id/button1
  "Turn on" / android:id/button2 "No thanks").
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR
_ID = AppiumBy.ID
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_TEXT = "type == 'XCUIElementTypeStaticText' AND "

LOCATION_PROMPT_MESSAGE = (
    "This app needs your location to verify you are on site when checking in or out of a job."
)
NOT_AT_SITE_MESSAGE = (
    "Your GPS location is accurate, but you don't appear to be at the registered job site. "
    "Please move to the site to check in."
)
MOCK_LOCATION_MESSAGE = (
    "Your device is reporting a simulated (mock) location, so it cannot be used to verify you are "
    "on site. Turn off any mock-location app and try again."
)
LOCATION_DISABLED_MESSAGE = (
    "To use GPS check-in, please enable location services in your device settings. "
    "You can still check in manually if you prefer."
)
# Android, after a refusal the system may still ask again (D-CHIO-A3, recon A1
# location_disabled.xml — the file name is recon's, the dialog is "Location access required").
LOCATION_ACCESS_REQUIRED_MESSAGE = (
    "GPS is required to check in. Enable location services to continue."
)

LOCATION_PROMPT = Screen(
    id="location-prompt",
    anchor="title",
    elements={
        "title": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeStaticText' AND name CONTAINS 'to use your location'",
            ),
            android=(_ID, "com.android.permissioncontroller:id/permission_message"),
            note="system alert 'Allow “<app name>” to use your location?' (app name per flavor). "
            "Android: the real permission dialog has one combined text for title + message "
            "(TextView permission_message, recon A1) — both aliases resolve to it",
        ),
        "message": El(
            ios=(_A, LOCATION_PROMPT_MESSAGE),
            android=(_ID, "com.android.permissioncontroller:id/permission_message"),
            note="the app's usage description, shown by the system prompt (recon 5b). Android: "
            "same element as 'title' — the dialog shows only "
            "\"Allow [DEV] CT Mobile to access this device's location?\" (recon A1), not the app's "
            "custom usage string; expect_text('message', LOCATION_PROMPT_MESSAGE) needs an "
            "Android-specific expected value — report to the main session",
        ),
        "allow-while-using": El(
            ios=(_P, _BUTTON + "name == 'Allow While Using App'"),
            android=(
                _ID,
                "com.android.permissioncontroller:id/permission_allow_foreground_only_button",
            ),
            note="Android: 'While using the app' (recon A1)",
        ),
        "dont-allow": El(
            ios=(_P, _BUTTON + "name BEGINSWITH 'Don' AND name ENDSWITH 'Allow'"),
            android=(
                _U,
                "new UiSelector().resourceIdMatches("
                '"com.android.permissioncontroller:id/permission_deny.*button")',
            ),
            note="'Don’t Allow' — the typographic apostrophe is matched around, not typed. "
            "Android: 'Don’t allow' — the resource-id differs the first time "
            "(permission_deny_button) and the second (permission_deny_and_dont_ask_again_button, "
            "recon A1 perm_location.xml / perm_location_second.xml); one regex matches either",
        ),
    },
)

LOCATION_DISABLED = Screen(
    id="location-disabled",
    anchor="title",
    elements={
        "title": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Location disabled'"),
            android=(_A, "Location disabled"),
            note="the refusal the system will not ask about again — iOS: the first; Android: the "
            "second ('don't ask again'); the same Dart dialog on both",
        ),
        "message": El(ios=(_A, LOCATION_DISABLED_MESSAGE), android=(_A, LOCATION_DISABLED_MESSAGE)),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'"), android=(_A, "Cancel")),
        "go-to-settings": El(
            ios=(_P, _BUTTON + "name == 'Go to settings'"),
            android=(_A, "Go to settings"),
        ),
    },
)

LOCATION_ACCESS_REQUIRED = Screen(
    id="location-access-required",
    anchor="title",
    elements={
        "title": El(
            android=(_A, "Location access required"),
            note="Android only: the app's dialog after a refusal the system may still ask about "
            "again (D-CHIO-A3, recon A1 location_disabled.xml)",
        ),
        "message": El(
            android=(_A, LOCATION_ACCESS_REQUIRED_MESSAGE),
            note="Android only: LOCATION_ACCESS_REQUIRED_MESSAGE (D-CHIO-A3)",
        ),
        "cancel": El(android=(_A, "Cancel"), note="Android only"),
        "enable": El(
            android=(_A, "Enable"),
            note="Android only: asks the system for the permission again (D-CHIO-A3)",
        ),
    },
)

NOT_AT_SITE = Screen(
    id="not-at-site",
    anchor="title",
    elements={
        "title": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeStaticText' AND name == 'You are not at the job site'",
            ),
            android=(_A, "You are not at the job site"),
        ),
        "message": El(ios=(_A, NOT_AT_SITE_MESSAGE), android=(_A, NOT_AT_SITE_MESSAGE)),
        "got-it": El(ios=(_P, _BUTTON + "name == 'Got it'"), android=(_A, "Got it")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'"), android=(_A, "Cancel")),
    },
)

MOCK_LOCATION = Screen(
    id="mock-location",
    anchor="title",
    elements={
        "title": El(
            ios=(_P, _TEXT + "name == 'Location could not be trusted'"),
            android=(_A, "Location could not be trusted"),
        ),
        "message": El(ios=(_A, MOCK_LOCATION_MESSAGE), android=(_A, MOCK_LOCATION_MESSAGE)),
        "got-it": El(ios=(_P, _BUTTON + "name == 'Got it'"), android=(_A, "Got it")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'"), android=(_A, "Cancel")),
    },
)

# Not reached in recon A1 — the Android "don't ask again" path; confirmed by the module 05 runs.
_DENIED_FOREVER = (
    "Android: the dialog after a refusal the system will not ask about again — not reached in "
    "recon A1; the same Dart dialog as iOS (showLocationDisabledDialog)"
)
ANDROID_UNVERIFIED = {
    "location-disabled.title": _DENIED_FOREVER,
    "location-disabled.message": _DENIED_FOREVER,
    "location-disabled.go-to-settings": _DENIED_FOREVER,
}
