"""Profile — root only (module 12-profile extends it). Source: recon 4.

The tab is named 'Profile\\nTab 3 of 3', so the screen title is matched by type and exact name.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

PROFILE = Screen(
    id="profile",
    anchor="root",
    elements={
        "root": El(
            ios=(AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeOther' AND name == 'Profile'")
        ),
    },
)
