"""Appium capabilities per platform.

``platform`` is the OS (android | ios) and picks the option class. The app kind
(native | flutter) changes only the automationName, and only when the Flutter integration
driver is opted in (``APP_KIND=flutter`` + ``FLUTTER_DRIVER=integration``). By default a
Flutter build is driven exactly like a native one.

Client quirk worth knowing: ``AppiumOptions`` stores class defaults (``automationName``,
``platformName``) unprefixed and ``set_capability`` values ``appium:``-prefixed, so assigning
``opts.automation_name`` on a native option class sends TWO automationName keys. The
integration driver therefore gets option subclasses whose *defaults* name it.
"""

from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions
from appium.options.common.automation_name_option import AUTOMATION_NAME
from appium.options.ios import XCUITestOptions

from config.settings import normalize_platform, settings

NATIVE_AUTOMATION = {"android": "UiAutomator2", "ios": "XCUITest"}
FLUTTER_INTEGRATION_AUTOMATION = "FlutterIntegration"


class FlutterIntegrationAndroidOptions(UiAutomator2Options):
    """UiAutomator2 typed caps, driven by appium-flutter-integration-driver."""

    @property
    def default_capabilities(self) -> dict:
        return {**super().default_capabilities, AUTOMATION_NAME: FLUTTER_INTEGRATION_AUTOMATION}


class FlutterIntegrationIOSOptions(XCUITestOptions):
    """XCUITest typed caps, driven by appium-flutter-integration-driver."""

    @property
    def default_capabilities(self) -> dict:
        return {**super().default_capabilities, AUTOMATION_NAME: FLUTTER_INTEGRATION_AUTOMATION}


def automation_name(platform: str) -> str:
    """Driver a session for ``platform`` requests under the current settings."""
    if settings.uses_flutter_integration:
        return FLUTTER_INTEGRATION_AUTOMATION
    return NATIVE_AUTOMATION[normalize_platform(platform)]


def android_caps() -> UiAutomator2Options:
    cls = (
        FlutterIntegrationAndroidOptions
        if settings.uses_flutter_integration
        else UiAutomator2Options
    )
    opts = cls()  # platformName / automationName come from the class defaults
    opts.platform_version = settings.android_platform_version
    opts.device_name = settings.android_device_name
    opts.app = str(settings.app_path("android"))
    opts.app_package = settings.android_app_package
    opts.app_activity = settings.android_app_activity
    opts.auto_grant_permissions = True
    opts.new_command_timeout = settings.new_command_timeout
    # Flutter redraws (spinners, the job timer) keep UiAutomator from ever seeing "idle": without
    # this every action waits the default 10 s for it (recon A1). A busy emulator also needs
    # longer than the default 30 s to start the UiAutomator2 server.
    opts.set_capability("appium:settings[waitForIdleTimeout]", 100)
    opts.set_capability("appium:uiautomator2ServerLaunchTimeout", 90000)
    # The debug APK is 195 MB: its install (re-dexing) and `pm clear` take long on a busy
    # emulator (module 02 run 1: install -r timed out after 60 s, pm clear failed after it).
    opts.set_capability("appium:androidInstallTimeout", 240000)
    opts.set_capability("appium:adbExecTimeout", 120000)
    return opts


def ios_caps() -> XCUITestOptions:
    cls = FlutterIntegrationIOSOptions if settings.uses_flutter_integration else XCUITestOptions
    opts = cls()
    opts.platform_version = settings.ios_platform_version
    opts.device_name = settings.ios_device_name
    opts.app = str(settings.app_path("ios"))
    opts.bundle_id = settings.ios_bundle_id
    # iOS counterpart of Android's auto_grant_permissions: accept native system alerts
    # (notifications, location, camera, photos). Flutter in-app dialogs are not native
    # alerts and are unaffected. A test that checks a denied permission overrides this.
    opts.auto_accept_alerts = True
    opts.new_command_timeout = settings.new_command_timeout
    return opts


def get_capabilities(platform: str) -> AppiumOptions:
    """Options for ``platform``; ValueError for anything but android|ios (incl. "flutter")."""
    platform = normalize_platform(platform)
    return android_caps() if platform == "android" else ios_caps()
