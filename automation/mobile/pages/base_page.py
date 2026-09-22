"""Base page object: alias-level actions over a screen map, with explicit waits only.

Pages never hold locators. A page names its ``screen`` (``screens/<x>_map.py``) and acts on
element aliases; the map resolves each alias to a ``(strategy, value)`` for the platform of
the live session. Every action waits explicitly (helpers/waits.py) — no sleeps, no implicit wait.
"""

import contextlib

import allure
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import WebDriverException

from config.settings import normalize_platform
from helpers import waits
from helpers.device import platform_of
from helpers.waits import Locator
from screens import Screen, locator_for


class BasePage:
    screen: Screen  # set by every subclass

    def __init__(self, driver: WebDriver, platform: str | None = None):
        if getattr(self, "screen", None) is None:
            raise TypeError(f"{type(self).__name__} must set `screen` to a Screen map")
        self.driver = driver
        self.platform = normalize_platform(platform) if platform else platform_of(driver)

    # --- resolution -------------------------------------------------------------------

    def locator(self, alias: str) -> Locator:
        return locator_for(self.screen, self.platform, alias)

    def find(self, alias: str, timeout: float | None = None) -> WebElement:
        """Element is present (may be hidden)."""
        return waits.wait_present(self.driver, self.locator(alias), timeout)

    def visible(self, alias: str, timeout: float | None = None) -> WebElement:
        """Element is displayed — the ``expect-visible`` step."""
        return waits.wait_visible(self.driver, self.locator(alias), timeout)

    # --- actions ----------------------------------------------------------------------

    def tap(self, alias: str, timeout: float | None = None) -> None:
        with allure.step(f"tap {self.screen.qualified(alias)}"):
            waits.wait_clickable(self.driver, self.locator(alias), timeout).click()

    def type(self, alias: str, text: str, timeout: float | None = None) -> None:
        with allure.step(f"fill {self.screen.qualified(alias)}"):
            element = self.visible(alias, timeout)
            element.clear()
            element.send_keys(text)

    def hide_keyboard(self) -> None:
        """Best effort: iOS raises when no keyboard is shown, which is not a failure."""
        with contextlib.suppress(WebDriverException):
            self.driver.hide_keyboard()

    # --- expectations -----------------------------------------------------------------

    def text(self, alias: str, timeout: float | None = None) -> str:
        return self.visible(alias, timeout).text

    def expect_text(self, alias: str, text: str, timeout: float | None = None) -> None:
        with allure.step(f"expect {self.screen.qualified(alias)} contains {text!r}"):
            waits.wait_text(self.driver, self.locator(alias), text, timeout)

    def is_visible(self, alias: str, timeout: float | None = None) -> bool:
        """Non-raising probe for branching. For assertions use ``visible`` / ``wait_gone``."""
        return waits.is_visible(self.driver, self.locator(alias), timeout)

    def wait_gone(self, alias: str, timeout: float | None = None) -> None:
        """The ``expect-hidden`` step: raises if the element is still visible."""
        with allure.step(f"expect {self.screen.qualified(alias)} gone"):
            waits.wait_gone(self.driver, self.locator(alias), timeout)

    def assert_open(self, timeout: float | None = None) -> None:
        """The screen's anchor element is visible; raises TimeoutException otherwise."""
        if self.screen.anchor is None:
            raise ValueError(f"screen {self.screen.id!r} defines no anchor")
        with allure.step(f"expect screen {self.screen.id} open"):
            self.visible(self.screen.anchor, timeout)

    def is_open(self, timeout: float | None = None) -> bool:
        if self.screen.anchor is None:
            raise ValueError(f"screen {self.screen.id!r} defines no anchor")
        return self.is_visible(self.screen.anchor, timeout)
