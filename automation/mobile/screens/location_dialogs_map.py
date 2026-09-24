"""The location prompts of a check-in start (module 04-order-details, TC-ORDD-005).

Source: recon 5 / 5b (qa/shared/recon-dumps/ios-2026-09-24/recon5b_checkin_os_prompt.xml,
recon5b_checkin_after_dont_allow.xml). The first one is the SYSTEM permission alert: it is in the
page source only while the session setting ``respectSystemAlerts`` is on
(pages/location_dialogs_page.py). The second one is the app's own dialog.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "

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
