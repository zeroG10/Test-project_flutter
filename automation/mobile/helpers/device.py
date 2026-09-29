"""Device / driver utilities: adb, simctl and session introspection."""

import subprocess

from appium.webdriver.webdriver import WebDriver

from config.settings import normalize_platform


def adb(*args: str) -> str:
    return subprocess.check_output(["adb", *args], text=True)


def adb_install(apk_path: str) -> None:
    subprocess.check_call(["adb", "install", "-r", apk_path])


def adb_uninstall(package: str) -> None:
    subprocess.call(["adb", "uninstall", package])


def xcrun_simctl(*args: str) -> str:
    return subprocess.check_output(["xcrun", "simctl", *args], text=True)


def platform_of(driver: WebDriver) -> str:
    """OS of a live session (android | ios), read from the capabilities the server returned."""
    return normalize_platform(str(driver.capabilities.get("platformName", "")))


# Android: after ``am force-stop`` the driver waits only 500 ms by default for the process to go.
# Measured on the Pixel 7 emulator (2026-09-29): gone after 0.3 s from the foreground and 0.64 s
# from the background, adb round-trips included — over the default on a busy host (module 01+03
# Android run 1: 16 set-ups errored with "still running after 500ms timeout"). The wait ends as
# soon as the process is gone, so a high ceiling costs nothing on a healthy device.
TERMINATE_TIMEOUT_MS_ANDROID = 10_000


def terminate_app(driver: WebDriver, app_id: str) -> None:
    """Stop ``app_id`` and wait until its process is gone (iOS: the driver's own wait)."""
    if platform_of(driver) == "android":
        driver.execute_script(
            "mobile: terminateApp", {"appId": app_id, "timeout": TERMINATE_TIMEOUT_MS_ANDROID}
        )
        return
    driver.terminate_app(app_id)
