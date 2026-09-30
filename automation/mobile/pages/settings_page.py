"""The system Settings — the app's notification permission (module 11, TC-NOTIF-005; recon 12).

Android (recon A1): "Go to Settings" opens the app's own notification page directly
(``Settings$AppNotificationSettingsActivity``); the page is reached the same way here — the
system intent for the app's notification settings — and the switch is ``android:id/switch_widget``.
The app reads the permission only when it starts (D-NOTIF-A1, owner 2026-09-29: a note, not a
bug), so after allowing push again the app is restarted before the test looks at the banner.

Settings is started fresh (terminated first) so every run walks the same path from its root:
Apps → the app → NOTIFICATIONS → the switch. Switching the permission may restart the app under
test (recon 12: it came back on the Jobs list), so callers open the tab they need again.
"""

import contextlib

import allure
from selenium.common.exceptions import TimeoutException, WebDriverException

from helpers import waits
from helpers.device import terminate_app
from pages.base_page import BasePage
from screens.android.system_dialogs_map import NOTIFICATION_PERMISSION
from screens.settings_map import SETTINGS

SETTINGS_APP = "com.apple.Preferences"
SETTINGS_APP_ANDROID = "com.android.settings"
ANDROID_SWITCH = ("id", "android:id/switch_widget")
SWITCH_FROM_RIGHT = 30  # the switch itself — a tap on its label does not toggle it (recon 12)
SCROLLS = 15  # the app sits at the end of Settings → Apps ('[DEV] …' sorts after the letters)
# Android: switching the permission off in Settings ends the app's process (as for any revoked
# runtime permission); at its next start the signed-in app asks again — the system prompt, which
# iOS never shows twice (module 11 Android run 1, TC-NOTIF-005).
PROMPT_WAIT_ANDROID = 20.0  # s: a cold start, the splash, the session check, then the prompt


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
        package = SETTINGS_APP_ANDROID if self.platform == "android" else SETTINGS_APP
        return self.driver.query_app_state(package) == 4

    def _set_android(self, allowed: bool, app_id: str) -> None:
        state = "on" if allowed else "off"
        with allure.step(f"Settings: the app's notifications → {state}"):
            self.driver.execute_script("mobile: startActivity", {
                "action": "android.settings.APP_NOTIFICATION_SETTINGS",
                "extras": [["s", "android.provider.extra.APP_PACKAGE", app_id]],
            })  # fmt: skip
            switch = waits.wait_visible(self.driver, ANDROID_SWITCH, 15)
            if (switch.get_attribute("checked") == "true") != allowed:
                switch.click()
            waits.wait_until(
                self.driver,
                lambda d: (
                    (d.find_element(*ANDROID_SWITCH).get_attribute("checked") == "true") == allowed
                ),
                10,
                f"the app's notifications did not turn {state}",
            )
            if allowed:  # D-NOTIF-A1: the app sees the new permission only after a restart
                with contextlib.suppress(WebDriverException):
                    terminate_app(self.driver, app_id)
            self.driver.activate_app(app_id)
        if not allowed:
            self._deny_prompt_android()

    def _deny_prompt_android(self) -> None:
        """The user who has just switched push off answers the app's new request "Don't allow"
        (D-NOTIF-A4). Once Android stops showing the prompt (a second refusal), nothing comes."""
        with allure.step("the app asks for notifications again → Don't allow (if it asks)"):
            deny = NOTIFICATION_PERMISSION.locator("android", "deny")
            try:
                waits.wait_clickable(self.driver, deny, PROMPT_WAIT_ANDROID).click()
            except TimeoutException:
                allure.attach(
                    f"no prompt within {PROMPT_WAIT_ANDROID:.0f} s",
                    name="notification prompt",
                    attachment_type=allure.attachment_type.TEXT,
                )
                return
            waits.wait_gone(self.driver, deny, 10)

    def set_app_notifications(self, allowed: bool, app_id: str) -> None:
        """Allow Notifications on / off for the app under test, then bring the app back."""
        if self.platform == "android":
            self._set_android(allowed, app_id)
            return
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
