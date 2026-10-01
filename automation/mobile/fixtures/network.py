"""Network control for the Android offline tests (step 5, recon A2): the device's Wi-Fi + mobile
data and the emulator's speed. Whatever a test does — also when it fails — the network is ON, at
full speed and resolving names again when it ends, so the next test starts online."""

from collections.abc import Iterator

import allure
import pytest

from helpers.android.device import Adb


class Network:
    def __init__(self, adb: Adb):
        self.adb = adb

    def off(self) -> None:
        self.adb.set_network(False)

    def on(self) -> None:
        self.adb.set_network(True)

    def slow(self, speed: str = "gsm", delay: str = "gprs") -> None:
        """GSM speed, GPRS delay (emulator console) until the test ends."""
        with allure.step(f"device: network SLOW (speed {speed}, delay {delay})"):
            self.adb.run("emu", "network", "speed", speed)
            self.adb.run("emu", "network", "delay", delay)


@pytest.fixture
def network(driver, platform) -> Iterator[Network]:
    if platform != "android":
        pytest.skip("Blocked: the iOS simulator's network cannot be switched off (android-stage)")
    adb = Adb.of(driver)
    try:
        yield Network(adb)
    finally:
        with allure.step("cleanup: network ON, full speed"):
            adb.run("emu", "network", "speed", "full", check=False)
            adb.run("emu", "network", "delay", "none", check=False)
            adb.set_network(True, check=False)
