"""The app-wide offline banner and the "Connection restored" dialog — behaviour over
screens/offline_banner_map.py (Android stage, step 5; recon A2)."""

import allure
from selenium.common.exceptions import TimeoutException

from helpers import waits
from pages.base_page import BasePage
from screens import APP_BAR_BOTTOM_ANDROID
from screens.offline_banner_map import CONNECTION_RESTORED, OFFLINE_BANNER

BANNER_WAIT = 15.0  # s: the banner follows the connectivity change within a few seconds
COMPACT_WAIT = 10.0  # s: the long text turns into "No internet connection." + Try again after ~5 s
RESTORED_WAIT = 45.0  # s: the dialog came ~15 s after the network returned (recon A2 row 12)
CLOSE_FROM_RIGHT = 84  # px: the ✕ centre from the right edge (recon A2: [954,288][1038,372])
CLOSE_BELOW_BAR = 50  # px below the app bar: inside the ✕ of both banner heights
CLOSE_IF_SHOWN_WAIT = 25.0  # s: the dialog came ~15 s after the network returned (recon A2)


class OfflineBanner(BasePage):
    screen = OFFLINE_BANNER

    def expect_shown(self, timeout: float = BANNER_WAIT) -> None:
        self.visible("message", timeout)

    def close(self) -> None:
        """The ✕ (no name, TD in the map) — the banner covers the top of the content until it is
        closed (D-OFF-7). Compact banner: right of Try again. The long text can stay well past its
        ~5 s (after a cold start offline, module 07 offline run 1): then the ✕ at the right end of
        the strip under the app bar (recon A2: ✕ x 954–1038, y 288–409)."""
        with allure.step("tap offline-banner.close"):
            self.expect_shown()
            width = self.driver.get_window_size()["width"]
            if self.is_visible("try-again", COMPACT_WAIT):
                link = self.find("try-again").rect
                right = link["x"] + link["width"]
                self.tap_xy(right + (width - right) / 2, link["y"] + link["height"] / 2)
            else:
                self.tap_xy(width - CLOSE_FROM_RIGHT, APP_BAR_BOTTOM_ANDROID + CLOSE_BELOW_BAR)
            self.wait_gone("message", 5)


class ConnectionRestoredDialog(BasePage):
    screen = CONNECTION_RESTORED

    def wait_open(self, timeout: float = RESTORED_WAIT) -> None:
        self.assert_open(timeout)

    def dismiss(self, timeout: float = RESTORED_WAIT) -> None:
        """Network back while an In progress job is cached: after the sync the dialog comes on
        the TAB screens (Jobs, Notifications, Profile) — over a pushed screen (job details, a
        deliverable) it waits until the user is back on a tab (app_shell.dart; module 07 offline
        run 1). Cancel closes it (its own check is TC-DLV-009)."""
        with allure.step("Connection restored dialog → Cancel"):
            self.wait_open(timeout)
            self.tap("cancel")
            self.wait_gone("title", 5)

    def close_if_shown(self, timeout: float = CLOSE_IF_SHOWN_WAIT) -> bool:
        """On a tab screen after the network returns: Cancel the dialog if it comes within
        ``timeout``. It names every In progress job of the app's details cache — also earlier
        tests' jobs deleted on the server since (D-OFF-10) — and lies over the screen, which then
        leaves the tree (full run offline-all-r1: TC-ORDL-018, TC-NOTIF-007)."""
        with allure.step(f"Connection restored dialog within {timeout:.0f} s → Cancel (if shown)"):
            if not self.shows(timeout):
                return False
            allure.attach(
                self.label_of(self.find("message")),
                name="Connection restored — message",
                attachment_type=allure.attachment_type.TEXT,
            )
            self.tap("cancel")
            self.wait_gone("title", 5)
            return True

    def shows(self, timeout: float) -> bool:
        try:
            waits.wait_visible(self.driver, self.locator("title"), timeout)
        except TimeoutException:
            return False
        return True
