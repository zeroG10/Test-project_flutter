"""Bottom tab bar — Jobs / Notifications / Profile (shared by the signed-in screens).

Source: recon 3b and recon 4. Tabs are Images named '<label>\\nTab N of 3'; the Notifications
label carries a counter ('8\\nNotifications\\nTab 2 of 3'), so the stable tail is matched. The
selected tab has ``traits="Selected, Image"`` in the page source (read by pages/tabbar_page.py).

Android: qa/shared/recon-dumps/android-2026-09-29/jobs_list.xml, notifications.xml, profile.xml
(recon A1) — same three ImageViews, content-desc '<label>\\nTab N of 3' (Notifications carries
the same unread-count prefix, e.g. '5\\nNotifications\\nTab 2 of 3'); the selected tab has
``selected="true"`` in the page source, not ``traits`` — pages/tabbar_page.py needs an Android
branch (see final report).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR

TABBAR = Screen(
    id="tabbar",
    anchor="jobs",
    elements={
        "jobs": El(android=(_A, "Jobs\nTab 1 of 3"), ios=(_P, "name ENDSWITH 'Tab 1 of 3'")),
        "notifications": El(
            android=(_U, 'new UiSelector().descriptionMatches(".*Tab 2 of 3")'),
            ios=(_P, "name ENDSWITH 'Tab 2 of 3'"),
            note="Android: descriptionMatches (no descriptionEndsWith in UiAutomator) — matches "
            "with or without the unread-count prefix (recon A1)",
        ),
        "profile": El(android=(_A, "Profile\nTab 3 of 3"), ios=(_P, "name ENDSWITH 'Tab 3 of 3'")),
    },
)
