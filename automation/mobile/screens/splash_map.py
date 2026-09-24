"""Splash — the start-up screen (module 01-splash).

Source: recon 4 (2026-09-24, qa/shared/recon-dumps/ios-2026-09-24/splash_*_tree_*.xml): while the
splash is up the tree holds **no** text, button or field at all — there is nothing to anchor a
locator to. The splash is decided by pixels (brand colour #782A2A of Figma `Spalsh` 2451:82537,
the white logo) in pages/splash_page.py; the only entries here are the application itself and
the element kinds that must be absent (CHK-SPL-005).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

SPLASH = Screen(
    id="splash",
    anchor="root",
    elements={
        "root": El(
            ios=(_P, "type == 'XCUIElementTypeApplication'"),
            note="the app itself — the splash has no element of its own; "
            "SplashPage decides 'splash shown' by pixels",
        ),
        "interactive": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeStaticText' OR type == 'XCUIElementTypeButton' OR "
                "type == 'XCUIElementTypeTextField' OR type == 'XCUIElementTypeLink' OR "
                "type == 'XCUIElementTypeSwitch'",
            ),
            note="anything a user could read or press — must be absent during the splash",
        ),
    },
)
