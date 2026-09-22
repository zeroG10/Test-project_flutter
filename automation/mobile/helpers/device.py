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
