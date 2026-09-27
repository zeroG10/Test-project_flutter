"""App lifecycle on the live session: cold start, relaunch, clear data, reinstall.

One Appium session serves the whole run (conftest.py ``driver``); tests get the app into
the state they need through these calls, wrapped by the fixtures in fixtures/app_state.py.
Every call is an Allure step, so a report shows how the starting state was produced.

Clearing data = signing out, on both OSes:
* Android — ``mobile: clearApp`` is ``pm clear``: app data incl. the secure storage goes.
* iOS simulator — ``mobile: clearApp`` empties the app's data container. The session token
  lives in the keychain, which survives that, but the app itself deletes keychain tokens on
  a "fresh install" launch (``TokenStorage.clearIosKeychainTokensOnFreshInstall`` — a flag in
  the app's preferences, which are in the container). Real devices do not support
  clearApp; there the only way is a reinstall.
"""

import contextlib
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import allure
from appium.webdriver.webdriver import WebDriver

from config.settings import normalize_platform, settings


class AppControl:
    def __init__(self, driver: WebDriver, platform: str):
        self.driver = driver
        self.platform = normalize_platform(platform)
        self.app_id = settings.app_id(self.platform)

    def launch(self) -> None:
        """Bring the app to the foreground; a cold start when it is not running."""
        with allure.step(f"app: launch {self.app_id}"):
            self.driver.activate_app(self.app_id)

    def terminate(self) -> None:
        with allure.step(f"app: terminate {self.app_id}"):
            self.driver.terminate_app(self.app_id)

    def relaunch(self) -> None:
        """Terminate, then launch — the ``open app: terminate, then cold start`` step."""
        with allure.step("app: relaunch (cold start)"):
            self.terminate()
            self.launch()

    def background(self, seconds: float) -> None:
        """Send the app to the background for ``seconds``, then bring it back."""
        with allure.step(f"app: background for {seconds}s"):
            self.driver.background_app(seconds)

    def clear_data(self) -> None:
        """Terminate the app and wipe its data (signed out, first-launch state).

        iOS: a reinstall from the build, NOT ``mobile: clearApp``. On the iOS 26 simulator
        clearApp also deletes the container's hidden ``.com.apple.mobile_container_manager
        .metadata.plist``; the first launch after it works, but when the system photo picker hands
        a photo to the app, iOS resets the container — Documents and the app's database are gone
        and every later local write fails ("savePhoto failed"; final runs 1 and 2, 2026-09-27,
        TC-PHR-001 after the Auth tests). A reinstall gives the true fresh-install state."""
        with allure.step("app: clear data"):
            if self.platform == "ios":
                with contextlib.suppress(Exception):
                    self.driver.terminate_app(self.app_id)
                self.reinstall()
                self._first_launch()
                return
            self.driver.execute_script("mobile: clearApp", {"appId": self.app_id})

    FIRST_LAUNCH_WAIT = 10.0  # seconds for the notification prompt of a fresh install

    def _first_launch(self) -> None:
        """After a reinstall: launch once, allow the system notification prompt, stop the app —
        the state ``mobile: clearApp`` used to leave (signed out, permission kept, not running).
        Without it the prompt lies over the next cold start (stable run 1: TC-SPL-001 saw the
        splash under it and was Blocked)."""
        with allure.step("app: first launch after the reinstall — allow notifications, stop"):
            self.driver.activate_app(self.app_id)
            end = time.monotonic() + self.FIRST_LAUNCH_WAIT
            while time.monotonic() < end:
                with contextlib.suppress(Exception):
                    self.driver.execute_script("mobile: alert", {"action": "accept"})
                    break
                if "Welcome to Concert" in self.driver.page_source:
                    break  # no prompt (already accepted by autoAcceptAlerts)
                time.sleep(0.5)
            self.driver.terminate_app(self.app_id)

    def reinstall(self) -> None:
        """Remove and install the build from .env — slower than clear_data, always clean."""
        path = settings.app_path(self.platform)
        with allure.step(f"app: reinstall from {path.name}"):
            self.driver.remove_app(self.app_id)
            self.driver.install_app(str(path))

    def reset_location_permission(self) -> None:
        """Location permission back to "not determined", so the next check-in asks again
        (module 04, TC-ORDD-005; recon 5b). The app is terminated first — relaunch it after.

        iOS simulator: ``xcrun simctl privacy <udid> reset location <bundle>``. Android:
        ``mobile: changePermissions`` revoke (a revoked runtime permission is asked again)."""
        with allure.step("app: reset the location permission (not determined)"):
            self.terminate()
            if self.platform == "android":
                self.driver.execute_script("mobile: changePermissions", {
                    "permissions": ["android.permission.ACCESS_FINE_LOCATION",
                                    "android.permission.ACCESS_COARSE_LOCATION"],
                    "appPackage": self.app_id, "action": "revoke"})  # fmt: skip
                return
            udid = self.driver.capabilities.get("udid") or "booted"
            subprocess.run(
                ["xcrun", "simctl", "privacy", udid, "reset", "location", self.app_id],
                check=True,
                capture_output=True,
                timeout=30,
            )

    # --- device location and the app's location switches (module 05; recon 6 / 6c) ---------

    MOCK_SWITCH = "flutter.mock_location_override_enabled"
    THEME_KEY = "flutter.theme_mode"  # ThemeCubit: system / light / dark

    def _simctl(self, *args: str) -> subprocess.CompletedProcess:
        udid = self.driver.capabilities.get("udid") or "booted"
        return subprocess.run(
            ["xcrun", "simctl", *[udid if a == "{udid}" else a for a in args]],
            check=True, capture_output=True, text=True, timeout=60,
        )  # fmt: skip

    def set_location(self, latitude: float, longitude: float) -> None:
        """The device's location (iOS simulator: ``simctl location set``; Android: geo fix)."""
        with allure.step(f"device location → {latitude:.6f}, {longitude:.6f}"):
            if self.platform == "android":
                self.driver.set_location(latitude, longitude, 0)
                return
            self._simctl("location", "{udid}", "set", f"{latitude},{longitude}")

    def grant_location_permission(self) -> None:
        """Location permission granted up front — no system prompt (iOS: ``simctl privacy``)."""
        with allure.step("app: location permission granted"):
            if self.platform == "android":
                self.driver.execute_script("mobile: changePermissions", {
                    "permissions": ["android.permission.ACCESS_FINE_LOCATION",
                                    "android.permission.ACCESS_COARSE_LOCATION"],
                    "appPackage": self.app_id, "action": "grant"})  # fmt: skip
                return
            self._simctl("privacy", "{udid}", "grant", "location", self.app_id)

    def set_mock_location_allowed(self, allowed: bool) -> None:
        """The app's own debug preference that lets a simulated fix through (owner, Q-CHIO-5).

        iOS simulator only: every simulator fix is reported as mocked and refused (recon 6 / 6b).
        Written into the app's preferences while the app is closed (the app reads it at start);
        code and build unchanged. Android emulator fixes are not needed to pass through it."""
        if self.platform != "ios":
            return
        state = "ON" if allowed else "OFF"
        with allure.step(f"app: mock-location switch {state} (app preference)"):
            self.terminate()
            data = self._simctl("get_app_container", "{udid}", self.app_id, "data").stdout.strip()
            plist = f"{data}/Library/Preferences/{self.app_id}"
            self._simctl("spawn", "{udid}", "defaults", "write", plist, self.MOCK_SWITCH,
                         "-bool", "YES" if allowed else "NO")  # fmt: skip
            read = self._simctl("spawn", "{udid}", "defaults", "read", plist, self.MOCK_SWITCH)
            if read.stdout.strip() != ("1" if allowed else "0"):
                raise RuntimeError(f"mock-location switch not written: {read.stdout!r}")

    def reset_theme(self) -> None:
        """App theme back to Auto (the app's ``theme_mode`` preference = 'system'), written while
        the app is closed — the undo of a theme test that failed half way (module 12). iOS only
        for now: the Android stage adds its own."""
        if self.platform != "ios":
            return
        with allure.step("app: theme preference → Auto (system)"):
            self.terminate()
            data = self._simctl("get_app_container", "{udid}", self.app_id, "data").stdout.strip()
            plist = f"{data}/Library/Preferences/{self.app_id}"
            self._simctl("spawn", "{udid}", "defaults", "write", plist, self.THEME_KEY,
                         "-string", "system")  # fmt: skip

    def add_media(self, *paths: Path) -> None:
        """Put photos into the device gallery; the last one becomes the newest (iOS simulator:
        ``simctl addmedia``). Android: the Android stage adds its own (adb push + media scan)."""
        if self.platform != "ios":
            raise NotImplementedError("add_media: iOS simulator only for now")
        with allure.step(f"device gallery: add {', '.join(p.name for p in paths)}"):
            self._simctl("addmedia", "{udid}", *(str(p) for p in paths))

    def in_foreground(self, bundle_or_package: str) -> bool:
        """Whether another app (e.g. Settings) is in the foreground now (state 4)."""
        return self.driver.query_app_state(bundle_or_package) == 4

    # --- job links (module 03; recon 4, 2026-09-24) -----------------------------------------

    def open_link(self, url: str) -> None:
        """Open a job link the way a tap in an SMS / email does: as a universal link (iOS) or an
        App Link (Android). The app's own scheme ``ctflutter://jobs/<key>`` does not carry the key
        (recon 4), so tests always use the https link from ``POST /job/assign/{phone}``.

        iOS simulator: ``xcrun simctl openurl`` (``mobile: deepLink`` did not deliver the link to
        the app in recon 4). Android: ``mobile: deepLink`` = ``am start -a VIEW -d <url>``.
        """
        with allure.step(f"open job link {url}"):
            if self.platform == "android":
                self.driver.execute_script("mobile: deepLink", {"url": url, "package": self.app_id})
                return
            udid = self.driver.capabilities.get("udid") or "booted"
            subprocess.run(
                ["xcrun", "simctl", "openurl", udid, url],
                check=True,
                capture_output=True,
                timeout=30,
            )

    @contextlib.contextmanager
    def alerts_left_alone(self) -> Iterator[None]:
        """Switch the session's alert auto-accept off for a few steps (iOS). ``autoAcceptAlerts``
        exists for the OS permission prompts, but WDA may also press a button of an app dialog
        — a link dialog must be answered by the test itself (recon 4)."""
        if self.platform != "ios":
            yield
            return
        self.driver.update_settings({"defaultAlertAction": ""})
        try:
            yield
        finally:
            with contextlib.suppress(Exception):
                self.driver.update_settings({"defaultAlertAction": "accept"})
