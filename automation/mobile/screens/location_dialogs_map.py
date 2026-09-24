"""The location prompts and alerts of a check-in / check-out (modules 04 and 05).

Source: recon 5 / 5b (qa/shared/recon-dumps/ios-2026-09-24/recon5b_checkin_os_prompt.xml,
recon5b_checkin_after_dont_allow.xml). The first one is the SYSTEM permission alert: it is in the
page source only while the session setting ``respectSystemAlerts`` is on
(pages/location_dialogs_page.py). The others are the app's own dialogs (recon 6 / 6c).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
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

LOCATION_PROMPT = Screen(
    id="location-prompt",
    anchor="title",
    elements={
        "title": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeStaticText' AND name CONTAINS 'to use your location'",
            ),
            note="system alert 'Allow “<app name>” to use your location?' (app name per flavor)",
        ),
        "message": El(
            ios=(_A, LOCATION_PROMPT_MESSAGE),
            note="the app's usage description, shown by the system prompt (recon 5b)",
        ),
        "allow-while-using": El(ios=(_P, _BUTTON + "name == 'Allow While Using App'")),
        "dont-allow": El(
            ios=(_P, _BUTTON + "name BEGINSWITH 'Don' AND name ENDSWITH 'Allow'"),
            note="'Don’t Allow' — the typographic apostrophe is matched around, not typed",
        ),
    },
)

LOCATION_DISABLED = Screen(
    id="location-disabled",
    anchor="title",
    elements={
        "title": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Location disabled'")
        ),
        "message": El(ios=(_A, LOCATION_DISABLED_MESSAGE)),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "go-to-settings": El(ios=(_P, _BUTTON + "name == 'Go to settings'")),
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
            )
        ),
        "message": El(ios=(_A, NOT_AT_SITE_MESSAGE)),
        "got-it": El(ios=(_P, _BUTTON + "name == 'Got it'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
    },
)

MOCK_LOCATION = Screen(
    id="mock-location",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Location could not be trusted'")),
        "message": El(ios=(_A, MOCK_LOCATION_MESSAGE)),
        "got-it": El(ios=(_P, _BUTTON + "name == 'Got it'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
    },
)
