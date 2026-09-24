"""Bottom tab bar — Jobs / Notifications / Profile (shared by the signed-in screens).

Source: recon 3b and recon 4. Tabs are Images named '<label>\\nTab N of 3'; the Notifications
label carries a counter ('8\\nNotifications\\nTab 2 of 3'), so the stable tail is matched. The
selected tab has ``traits="Selected, Image"`` in the page source (read by pages/tabbar_page.py).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE

TABBAR = Screen(
    id="tabbar",
    anchor="jobs",
    elements={
        "jobs": El(ios=(_P, "name ENDSWITH 'Tab 1 of 3'")),
        "notifications": El(ios=(_P, "name ENDSWITH 'Tab 2 of 3'")),
        "profile": El(ios=(_P, "name ENDSWITH 'Tab 3 of 3'")),
    },
)
