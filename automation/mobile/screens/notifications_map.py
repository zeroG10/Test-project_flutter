"""Notifications — root only (module 11-notifications extends it). Source: recon 4."""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

NOTIFICATIONS = Screen(
    id="notifications",
    anchor="root",
    elements={
        "root": El(
            ios=(
                AppiumBy.IOS_PREDICATE,
                "type == 'XCUIElementTypeOther' AND name == 'Notification list'",
            )
        ),
    },
)
