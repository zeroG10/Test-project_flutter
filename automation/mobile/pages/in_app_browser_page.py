"""The in-app browser "On map" opens — behaviour over screens/in_app_browser_map.py.

Android (recon A1): Privacy / Terms open in Chrome Custom Tabs (``url_bar`` holds the host, Close
works as an ordinary tap); "On map" opens the Google Maps app instead of this browser (D-ORDD-A1)
— ``expect_map`` / ``close_map`` take either road.
"""

import allure

from config.settings import settings
from helpers import waits
from pages.base_page import BasePage, normalized
from screens.in_app_browser_map import IN_APP_BROWSER


class InAppBrowserPage(BasePage):
    screen = IN_APP_BROWSER

    def shown_host(self) -> str:
        """The host in the address bar, without the direction marks iOS puts around it."""
        value = self.field_value(self.find("url"))
        return normalized(value.replace("‎", "").replace("‏", ""))

    def expect_host(self, host: str, timeout: float | None = None) -> None:
        with allure.step(f"expect the in-app browser to show {host!r}"):
            waits.wait_until(
                self.driver,
                lambda _d: self.shown_host() == host,
                timeout,
                f"in-app browser shows {self.shown_host()!r}, expected {host!r}",
            )

    def expect_map(self, host: str, place: str, host_timeout: float, place_timeout: float) -> None:
        """ "On map": iOS — the browser on ``host`` showing ``place``; Android — Google Maps whose
        search holds ``place`` (the same address part)."""
        if self.platform == "android":
            from pages.android.system_pages import MapsAppPage

            maps = MapsAppPage(self.driver, self.platform)
            maps.expect_place(place, host_timeout + place_timeout)
            return
        self.expect_host(host, host_timeout)
        self.visible("place", place_timeout, text=place)

    def close_map(self) -> None:
        """Back to the app: iOS closes the browser; Android brings the app back over Maps."""
        if self.platform == "android":
            with allure.step("back to the app from Google Maps"):
                self.driver.activate_app(settings.app_id("android"))
            return
        self.close()

    def close(self, timeout: float = 30.0) -> None:
        """Close once the page has loaded, by a tap at the button's centre. Module 12 runs 1–2:
        an element click on Close left the browser open (the address bar's button lies over it,
        26…376 × 62…106); a tap at Close's centre closes it at once."""
        if self.platform == "android":  # Chrome Custom Tabs: loaded = the address bar shows a host
            with allure.step("tap in-app-browser.close once the address bar shows a host"):
                waits.wait_until(self.driver, lambda _d: self.shown_host() != "", timeout,
                                 "the Custom Tab shows no address")  # fmt: skip
                self.tap("close", 5)
                self.wait_gone("close", 10)
            return
        with allure.step("tap in-app-browser.close (its centre) once the page has loaded"):
            self.find("loaded", timeout)
            r = self.visible("close", 5).rect
            self.tap_xy(r["x"] + r["width"] / 2, r["y"] + r["height"] / 2)
            self.wait_gone("close", 10)
