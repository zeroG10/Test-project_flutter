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
        """Terminate the app and wipe its data (signed out, first-launch state)."""
        key = "appId" if self.platform == "android" else "bundleId"
        with allure.step("app: clear data"):
            self.driver.execute_script("mobile: clearApp", {key: self.app_id})

    def reinstall(self) -> None:
        """Remove and install the build from .env — slower than clear_data, always clean."""
        path = settings.app_path(self.platform)
        with allure.step(f"app: reinstall from {path.name}"):
            self.driver.remove_app(self.app_id)
            self.driver.install_app(str(path))
