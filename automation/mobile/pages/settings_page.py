"""The iOS Settings app — the app's notification permission (module 11, TC-NOTIF-005; recon 12).

Settings is started fresh (terminated first) so every run walks the same path from its root:
Apps → the app → NOTIFICATIONS → the switch. Switching the permission may restart the app under
test (recon 12: it came back on the Jobs list), so callers open the tab they need again.
"""

import contextlib

import allure
from selenium.common.exceptions import WebDriverException

from helpers import waits
from pages.base_page import BasePage
from screens.settings_map import SETTINGS

SETTINGS_APP = "com.apple.Preferences"
SWITCH_FROM_RIGHT = 30  # the switch itself — a tap on its label does not toggle it (recon 12)
SCROLLS = 15  # the app sits at the end of Settings → Apps ('[DEV] …' sorts after the letters)


class SystemSettingsPage(BasePage):
    screen = SETTINGS

    def _reach(self, alias: str) -> None:
        """Scroll down until ``alias`` is displayed, then tap it (run 1: six scrolls were not
        enough to reach the app in the Apps list)."""
        size = self.driver.get_window_size()
        for _ in range(SCROLLS):
            shown = [e for e in self.driver.find_elements(*self.locator(alias)) if e.is_displayed()]
            if shown:
                shown[0].click()
                return
            self.driver.execute_script("mobile: dragFromToForDuration", {
                "duration": 0.3, "fromX": size["width"] // 2, "fromY": int(size["height"] * 0.7),
                "toX": size["width"] // 2, "toY": int(size["height"] * 0.35)})  # fmt: skip
        raise AssertionError(f"settings.{alias} not found after {SCROLLS} scrolls")

    def is_foreground(self) -> bool:
        return self.driver.query_app_state(SETTINGS_APP) == 4

    def set_app_notifications(self, allowed: bool, app_id: str) -> None:
        """Allow Notifications on / off for the app under test, then bring the app back."""
        state = "on" if allowed else "off"
        with allure.step(f"Settings: Apps → the app → Notifications → Allow Notifications {state}"):
            with contextlib.suppress(WebDriverException):
                self.driver.terminate_app(SETTINGS_APP)
            self.driver.activate_app(SETTINGS_APP)
            self.assert_open(15)
            self._reach("apps")
            self._reach("app-row")
            self.tap("notifications", 10)
            switch = self.visible("allow-notifications", 10)
            want = "1" if allowed else "0"
            if switch.get_attribute("value") != want:
                r = switch.rect
                self.driver.execute_script("mobile: tap", {
                    "x": r["x"] + r["width"] - SWITCH_FROM_RIGHT,
                    "y": r["y"] + r["height"] / 2})  # fmt: skip
            waits.wait_until(
                self.driver,
                lambda _d: self.find("allow-notifications").get_attribute("value") == want,
                10,
                f"Allow Notifications did not turn {state}",
            )
            self.driver.activate_app(app_id)
