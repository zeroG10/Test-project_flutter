"""Splash — the start-up screen (module 01-splash).

Source: recon 4 (2026-09-24, qa/shared/recon-dumps/ios-2026-09-24/splash_*_tree_*.xml): while the
splash is up the tree holds **no** text, button or field at all — there is nothing to anchor a
locator to. The splash is decided by pixels (brand colour #782A2A of Figma `Spalsh` 2451:82537,
the white logo) in pages/splash_page.py; the only entries here are the application itself and
the element kinds that must be absent (CHK-SPL-005).

Android (recon A1, 2026-09-29, D-SPL-A1): a **system** splash (Android 12+, white, ≈ 3 s) shows
first, then the same Flutter brand splash. No dump exists for either — both are transient and,
like on iOS, the tree is unreadable/empty while they are up; no Android recon dumps directory
holds a splash tree. SplashPage decides "shown" by pixels on both platforms (unchanged), so
no locator is needed here — see ANDROID_WITHOUT below.
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

ANDROID_WITHOUT = {
    "splash.root": "no Android recon dump of the splash exists (system splash + brief Flutter "
    "brand splash, both transient); SplashPage decides 'shown' by pixels on both platforms, "
    "same as iOS — no locator needed (D-SPL-A1, owner 2026-09-29)",
    "splash.interactive": "same as splash.root — 'no interactive element' is decided by pixels "
    "(brand-colour share), not by counting tree nodes, on Android too; no dump to verify a "
    "structural locator against",
}
