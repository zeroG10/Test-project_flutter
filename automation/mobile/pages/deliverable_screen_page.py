"""Survey / Photo report / Notes screens — behaviour over screens/deliverable_screens_map.py."""

import contextlib

import allure
from selenium.common.exceptions import TimeoutException, WebDriverException

from helpers import waits
from pages.base_page import BasePage
from screens.deliverable_screens_map import DELIVERABLE_SCREEN

# Android: the app bar ends at 283 px (recon A1). A deliverable screen's title sits in it
# (survey_short.xml, notes.xml, photo_report.xml: y 173–246); the job details list rows with the
# very same labels lower down (y ≥ 378) — module 06 Android run 1, TC-ORDP-005.
APP_BAR_BOTTOM_ANDROID = 283


class DeliverableScreenPage(BasePage):
    screen = DELIVERABLE_SCREEN

    def expect_open(self, title: str, timeout: float | None = None) -> None:
        if self.platform != "android":
            self.visible("title", timeout, text=title)
            return
        with allure.step(f"expect the {title} screen open (its title in the app bar)"):
            waits.wait_until(
                self.driver,
                lambda _d: self._title_in_app_bar(title),
                timeout,
                f"no {title!r} title in the app bar",
            )

    def shows(self, title: str, timeout: float) -> bool:
        """Non-raising probe: the screen named ``title`` opened within ``timeout``."""
        if self.platform != "android":
            return self.is_visible("title", timeout, text=title)
        try:
            waits.wait_until(self.driver, lambda _d: self._title_in_app_bar(title), timeout)
        except TimeoutException:
            return False
        return True

    def _title_in_app_bar(self, title: str) -> bool:
        for element in waits.find_all(self.driver, self.locator("title", text=title)):
            with contextlib.suppress(WebDriverException):
                if element.is_displayed() and element.rect["y"] < APP_BAR_BOTTOM_ANDROID:
                    return True
        return False
