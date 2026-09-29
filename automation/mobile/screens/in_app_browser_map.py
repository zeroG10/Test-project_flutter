"""The in-app browser the app opens for "On map" (module 04-order-details, TC-ORDD-003).

Source: recon 5 (qa/shared/recon-dumps/ios-2026-09-24/recon5_maps.xml): with Google Maps not
installed the app opens maps.apple.com in the system in-app browser (SFSafariViewController) —
the app stays in the foreground (D-ORDD-4). Its controls carry system labels. Once the page
has loaded (run 1: up to ~10 s; recon 5 saw it blank) it shows a place card for the address.

Android (recon A1): "On map" does NOT use this screen — it opens the Google Maps APP
(qa/shared/recon-dumps/android-2026-09-29/maps_app.xml, maps_app_first_run.xml), a different,
unmapped screen (report below, no alias invented here per the task brief). This screen's Android
column instead serves the Chrome Custom Tab the app opens for Privacy Policy / SMS Terms
(pages/in_app_browser_page.py is reused there — tests/shared/test_profile.py,
sms_terms flow): qa/shared/recon-dumps/android-2026-09-29/browser_privacy.xml, browser_terms.xml,
package com.android.chrome.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_ID = AppiumBy.ID

IN_APP_BROWSER = Screen(
    id="in-app-browser",
    anchor="close",
    elements={
        "close": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Close' AND rect.y < 120"),
            android=(_ID, "com.android.chrome:id/close_button"),
            note="the browser's own Close in its top bar (y 62) — the Maps page has a 'Close' too. "
            "Android: Chrome Custom Tabs' close button, content-desc 'Close tab' (recon A1)",
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
            android=(_ID, "com.android.chrome:id/url_bar"),
            note="the address bar; its value is the host shown (e.g. '\\u200emaps.apple.com'). "
            "Android: Chrome's url_bar, text 'concerttech.com' (recon A1) — its host is read from "
            "the ``text`` attribute, not ``value``; in_app_browser_page.py::shown_host() calls "
            "get_attribute('value') unconditionally, report to the main session",
        ),
    },
)

# "On map" opens the Google Maps app on Android (not this screen) — Maps has no alias here per the
# task brief (do not invent aliases for Maps); the search box is
# com.google.android.apps.maps:id/search_omnibox_text_box, desc = the job address (recon A1
# maps_app.xml). "loaded" has no Android twin: Chrome shows no equivalent marker — the page waits
# for url_bar / the page text instead (recon-2026-09-29-android.md §04/06).
ANDROID_WITHOUT = {
    "in-app-browser.loaded": "no Android twin (Chrome Custom Tabs has no 'page loaded' marker "
    "like SFSafariViewController's IsPageLoaded) — the page should wait for url_bar / the page "
    "text instead",
    "in-app-browser.place": "'On map' on Android opens the Google Maps app, not this in-app "
    "browser (recon A1 maps_app.xml) — when this screen is used on Android (Chrome Custom Tabs "
    "for Privacy/Terms) there is no address place card",
}
