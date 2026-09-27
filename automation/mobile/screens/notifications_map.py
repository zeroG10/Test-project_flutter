"""Notifications (module 11-notifications, SRS §3.1.4). Source: recon 4 (root) and recon 12
(qa/shared/recon-dumps/ios-2026-09-24/recon12_*.xml).

A notification row is ONE element named '<M/d/yyyy>\\n<h:mm a>\\n<description>': an Other when the
job can be opened, an Image when it cannot (D-NOTIF-2). The icon and the chevron are unnamed Images
inside the row; the unread red dot is not in the tree (pixels — pages/notifications_page.py). The
push banner is one Image whose name joins its three texts; "Go to Settings" is not an element of its
own — the page taps its line. The ``visible`` attribute is wrong for part of a long list, so the
page reads rows from the page source by their rect.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "

NOTIFICATIONS = Screen(
    id="notifications",
    anchor="root",
    elements={
        "root": El(ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Notification list'")),
        "empty-title": El(ios=(_P, _TEXT + "name == 'No notifications yet'")),
        "empty-text": El(
            ios=(_P, _TEXT + "name BEGINSWITH 'You' AND name ENDSWITH 'about your jobs here.'"),
            note='"You\'ll see updates about your jobs here."',
        ),
        "row": El(
            ios=(
                _P,
                "(type == 'XCUIElementTypeOther' OR type == 'XCUIElementTypeImage') "
                "AND name CONTAINS {text}",
            ),
            note="'<date>\\n<time>\\n<description>' — found by a part of the description; "
            "Image = the job cannot be opened",
        ),
        "chevron": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND rect.x > 340 AND rect.width < 30"),
            note="unnamed, at the row's right end (x 366, 20x20) — paired with its row by the page",
        ),
        "banner": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND name BEGINSWITH 'Turn on push'"),
            note="'Turn on push notifications\\nTurn on push notifications to get alerts for job "
            "updates.\\nGo to Settings' — one element at the top",
        ),
        "go-to-settings": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND name ENDSWITH 'Go to Settings'"),
            note="the banner itself: 'Go to Settings' is its last line, tapped by position",
        ),
    },
)
