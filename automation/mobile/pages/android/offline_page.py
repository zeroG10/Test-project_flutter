"""The app-wide offline banner and the "Connection restored" dialog — behaviour over
screens/offline_banner_map.py (Android stage, step 5; recon A2)."""

import allure
from selenium.common.exceptions import TimeoutException

from helpers import waits
from pages.base_page import BasePage
from screens.offline_banner_map import CONNECTION_RESTORED, OFFLINE_BANNER

BANNER_WAIT = 15.0  # s: the banner follows the connectivity change within a few seconds
COMPACT_WAIT = 10.0  # s: the long text turns into "No internet connection." + Try again after ~5 s
RESTORED_WAIT = 45.0  # s: the dialog came ~15 s after the network returned (recon A2 row 12)


class OfflineBanner(BasePage):
    screen = OFFLINE_BANNER

    def expect_shown(self, timeout: float = BANNER_WAIT) -> None:
        self.visible("message", timeout)

    def close(self) -> None:
        """The ✕ (no name, TD in the map): once the banner is compact, tap right of Try again —
        the banner covers the top of the content until it is closed (D-OFF-7)."""
        with allure.step("tap offline-banner.close (right of Try again)"):
            link = self.visible("try-again", COMPACT_WAIT).rect
            width = self.driver.get_window_size()["width"]
            right = link["x"] + link["width"]
            self.tap_xy(right + (width - right) / 2, link["y"] + link["height"] / 2)
            self.wait_gone("message", 5)


class ConnectionRestoredDialog(BasePage):
    screen = CONNECTION_RESTORED

    def wait_open(self, timeout: float = RESTORED_WAIT) -> None:
        self.assert_open(timeout)

    def dismiss(self, timeout: float = RESTORED_WAIT) -> None:
        """Network back on an unfinished In progress job: the dialog comes and lies over the
        screen; Cancel closes it (its own check is TC-DLV-009)."""
        with allure.step("Connection restored dialog → Cancel"):
            self.wait_open(timeout)
            self.tap("cancel")
            self.wait_gone("title", 5)

    def shows(self, timeout: float) -> bool:
        try:
            waits.wait_visible(self.driver, self.locator("title"), timeout)
        except TimeoutException:
            return False
        return True
