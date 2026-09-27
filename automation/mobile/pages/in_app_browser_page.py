"""The in-app browser "On map" opens — behaviour over screens/in_app_browser_map.py."""

import allure

from helpers import waits
from pages.base_page import BasePage, normalized
from screens.in_app_browser_map import IN_APP_BROWSER


class InAppBrowserPage(BasePage):
    screen = IN_APP_BROWSER

    def shown_host(self) -> str:
        """The host in the address bar, without the direction marks iOS puts around it."""
        value = self.find("url").get_attribute("value") or ""
        return normalized(value.replace("‎", "").replace("‏", ""))

    def expect_host(self, host: str, timeout: float | None = None) -> None:
        with allure.step(f"expect the in-app browser to show {host!r}"):
            waits.wait_until(
                self.driver,
                lambda _d: self.shown_host() == host,
                timeout,
                f"in-app browser shows {self.shown_host()!r}, expected {host!r}",
            )

    def close(self, timeout: float = 30.0) -> None:
        """Close once the page has loaded — a Close tapped while it loads is ignored (module 12
        run 1: the browser stayed open)."""
        with allure.step("tap in-app-browser.close once the page has loaded"):
            self.find("loaded", timeout)
            self.tap("close")
            self.wait_gone("close", 10)
