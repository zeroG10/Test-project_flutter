"""Device / driver utilities: adb, simctl and session introspection."""

import subprocess

from appium.webdriver.webdriver import WebDriver

from config.settings import normalize_platform
from helpers import waits
from helpers.android.device import Adb


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


# Android: the driver's own check after ``am force-stop`` lists the app's processes from
# ActivityManager — and a stale record with pid 0 (``ProcessRecord{… 0:<package>/u0a219}``, seen
# after the module 01+03 runs on 2026-09-29) never goes away, so it waits in vain ("[12799,0] ->
# [0]", even with 10 s; run 2). So: force-stop without the driver's check, then wait until ``pidof``
# finds no process (it ignores pid 0). Measured: gone 0.3 s (foreground) / 0.64 s (background)
# after force-stop, adb included; the ceiling below only matters on a stuck device.
TERMINATE_TIMEOUT_ANDROID = 10.0


def terminate_app(driver: WebDriver, app_id: str) -> None:
    """Stop ``app_id`` and wait until its process is gone (iOS: the driver's own wait)."""
    if platform_of(driver) != "android":
        driver.terminate_app(app_id)
        return
    driver.execute_script("mobile: terminateApp", {"appId": app_id, "timeout": 0})
    adb = Adb.of(driver)
    waits.wait_until(
        driver,
        lambda _d: not adb.shell(f"pidof {app_id}", check=False, timeout=20).strip(),
        TERMINATE_TIMEOUT_ANDROID,
        f"{app_id} still has a process {TERMINATE_TIMEOUT_ANDROID:.0f} s after force-stop",
    )
