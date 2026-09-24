"""The in-app browser the app opens for "On map" (module 04-order-details, TC-ORDD-003).

Source: recon 5 (qa/shared/recon-dumps/ios-2026-09-24/recon5_maps.xml): with Google Maps not
installed the app opens maps.apple.com in the system in-app browser (SFSafariViewController) —
the app stays in the foreground (D-ORDD-4). Its controls carry system labels.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

IN_APP_BROWSER = Screen(
    id="in-app-browser",
    anchor="close",
    elements={
        "close": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Close'")),
        "url": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'URL'"),
            note="the address bar; its value is the host shown (e.g. '\\u200emaps.apple.com')",
        ),
    },
)
