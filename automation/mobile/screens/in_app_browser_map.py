"""The in-app browser the app opens for "On map" (module 04-order-details, TC-ORDD-003).

Source: recon 5 (qa/shared/recon-dumps/ios-2026-09-24/recon5_maps.xml): with Google Maps not
installed the app opens maps.apple.com in the system in-app browser (SFSafariViewController) —
the app stays in the foreground (D-ORDD-4). Its controls carry system labels. Once the page
has loaded (run 1: up to ~10 s; recon 5 saw it blank) it shows a place card for the address.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

IN_APP_BROWSER = Screen(
    id="in-app-browser",
    anchor="close",
    elements={
        "close": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Close' AND rect.y < 120"),
            note="the browser's own Close in its top bar (y 62) — the Maps page has a 'Close' too",
        ),
        "place": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == {text}"),
            note="the place card of maps.apple.com: the street line (run 1, 2026-09-24)",
        ),
        "loaded": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name CONTAINS 'IsPageLoaded=true'"),
            note="'BrowserView?IsPageLoaded=true&…' — a Close tapped before this is ignored "
            "(module 12 run 1)",
        ),
        "url": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'URL'"),
            note="the address bar; its value is the host shown (e.g. '\\u200emaps.apple.com')",
        ),
    },
)
