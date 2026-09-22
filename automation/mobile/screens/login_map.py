"""Login screen map — PLACEHOLDER ids. Replace with the ids from your testability contract.

Native Android ids are ``<package>:id/<name>`` (package from .env). A Flutter app exposes
``Semantics(identifier: "login-email")`` as resource-id ``login-email`` (no package prefix)
on Android and as accessibilityIdentifier on iOS, so its map is simply::

    "email": El(android=(AppiumBy.ID, "login-email"),
                ios=(AppiumBy.ACCESSIBILITY_ID, "login-email"))

Test-case steps address these as ``login.email``, ``login.submit`` ... (screens/README.md).
"""

from appium.webdriver.common.appiumby import AppiumBy

from config.settings import settings
from screens import El, Screen

_PKG = settings.android_app_package

LOGIN = Screen(
    id="login",
    anchor="title",
    elements={
        "title": El(
            android=(AppiumBy.ID, f"{_PKG}:id/login_title"),
            ios=(AppiumBy.ACCESSIBILITY_ID, "login-title"),
        ),
        "email": El(
            android=(AppiumBy.ID, f"{_PKG}:id/login_email"),
            ios=(AppiumBy.ACCESSIBILITY_ID, "login-email"),
        ),
        "password": El(
            android=(AppiumBy.ID, f"{_PKG}:id/login_password"),
            ios=(AppiumBy.ACCESSIBILITY_ID, "login-password"),
        ),
        "submit": El(
            android=(AppiumBy.ACCESSIBILITY_ID, "login-submit"),
            ios=(AppiumBy.ACCESSIBILITY_ID, "login-submit"),
        ),
        "error": El(
            android=(AppiumBy.ID, f"{_PKG}:id/login_error"),
            ios=(AppiumBy.ACCESSIBILITY_ID, "login-error"),
        ),
        # Text fallback: allowed, but only while the id is missing. Log it as a testability
        # defect (docs/requirements/shared/testability-contract.md) and replace when fixed.
        "forgot-password": El(
            android=(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Forgot password?")'),
            ios=(AppiumBy.IOS_PREDICATE, "label == 'Forgot password?'"),
            note="no id yet — text fallback, testability defect TD-LOGIN-001",
        ),
    },
)
