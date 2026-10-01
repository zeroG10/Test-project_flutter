"""Notifications (module 11-notifications, SRS §3.1.4). Source: recon 4 (root) and recon 12
(qa/shared/recon-dumps/ios-2026-09-24/recon12_*.xml).

A notification row is ONE element named '<M/d/yyyy>\\n<h:mm a>\\n<description>': an Other when the
job can be opened, an Image when it cannot (D-NOTIF-2). The icon and the chevron are unnamed Images
inside the row; the unread red dot is not in the tree (pixels — pages/notifications_page.py). The
push banner is one Image whose name joins its three texts; "Go to Settings" is not an element of its
own — the page taps its line. The ``visible`` attribute is wrong for part of a long list, so the
page reads rows from the page source by their rect.

Android: qa/shared/recon-dumps/android-2026-09-29/notifications.xml, notifications_banner.xml
(recon A1) — same row format and kind rule (View = openable, ImageView = not, D-NOTIF-2); the
icon and chevron are two unlabelled ImageViews per openable row (not individually
distinguishable without position — mirrors the iOS map's structural locator); "No notifications
yet" was not reached (the test account already had notifications) — ANDROID_UNVERIFIED below,
same Flutter text assumed. "Go to Settings" on Android opens the app's own notification page
directly (D-NOTIF-A2) — see screens/settings_map.py.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR
_TEXT = "type == 'XCUIElementTypeStaticText' AND "

NOTIFICATIONS = Screen(
    id="notifications",
    anchor="root",
    elements={
        "root": El(
            android=(_A, "Notification list"),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Notification list'"),
        ),
        "empty-title": El(
            android=(_A, "No notifications yet"),
            ios=(_P, _TEXT + "name == 'No notifications yet'"),
        ),
        "empty-text": El(
            android=(
                _U,
                'new UiSelector().descriptionMatches("You.*about your jobs here\\.")',
            ),
            ios=(_P, _TEXT + "name BEGINSWITH 'You' AND name ENDSWITH 'about your jobs here.'"),
            note='"You\'ll see updates about your jobs here."',
        ),
        "row": El(
            android=(_U, "new UiSelector().descriptionContains({text})"),
            ios=(
                _P,
                "(type == 'XCUIElementTypeOther' OR type == 'XCUIElementTypeImage') "
                "AND name CONTAINS {text}",
            ),
            note="'<date>\\n<time>\\n<description>' — found by a part of the description; "
            "Image = the job cannot be opened. Android: descriptionContains matches both "
            "View (openable) and ImageView (not) rows, same as iOS (recon A1)",
        ),
        "chevron": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.ImageView").clickable(false)',
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND rect.x > 340 AND rect.width < 30"),
            note="unnamed, at the row's right end (x 366, 20x20) — paired with its row by the "
            "page. Android: every non-clickable ImageView — a row's icon and chevron (no "
            "content-desc at all, which no description selector matches; 01+03 run 3); the page "
            "tells them apart by x (recon A1)",
        ),
        "banner": El(
            android=(
                _A,
                "Turn on push notifications\nTurn on push notifications to get alerts for job "
                "updates.\nGo to Settings",
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND name BEGINSWITH 'Turn on push'"),
            note="'Turn on push notifications\\nTurn on push notifications to get alerts for job "
            "updates.\\nGo to Settings' — one element at the top",
        ),
        "offline-title": El(
            android=(_A, "No internet connection"),
            note="Android only (step 5): the list's offline state — notifications are not cached "
            "(D-OFF-4, recon A2 row 14); no final period, unlike the app-wide banner",
        ),
        "offline-text": El(
            android=(
                _A,
                "Slow or no internet connection. Check the Internet settings and try again",
            ),
            note="Android only (step 5): under offline-title (recon A2 row 14)",
        ),
        "try-again": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.Button").description("Try again")',
            ),
            note="Android only (step 5): the offline state's Button; the banner's link is a View",
        ),
        "go-to-settings": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.ImageView")'
                '.descriptionContains("Go to Settings")',
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND name ENDSWITH 'Go to Settings'"),
            note="the banner itself: 'Go to Settings' is its last line, tapped by position. "
            "Android: descriptionMatches ends-with over the multi-line content-desc (recon A1)",
        ),
    },
)

ANDROID_UNVERIFIED = {
    "notifications.empty-title": "not reached in recon A1 (the test account already had "
    "notifications) — same Flutter text as iOS; confirm in step 4",
    "notifications.empty-text": "not reached in recon A1 — same Flutter text as iOS; confirm "
    "in step 4",
}
