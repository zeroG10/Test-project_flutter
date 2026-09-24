"""Check-in / check-out confirmation — behaviour over screens/confirm_check_map.py (module 05)."""

import allure

from pages.base_page import BasePage
from screens.confirm_check_map import CONFIRM_CHECK


class ConfirmCheckPage(BasePage):
    screen = CONFIRM_CHECK

    def expect_screen(self, title: str, primary: str, supporting: str, timeout=None) -> None:
        """The confirmation screen with its three texts, both buttons and the X."""
        with allure.step(f"expect the confirmation screen {title!r}"):
            self.visible("title", timeout, text=title)
            self.visible("primary", text=primary)
            self.visible("supporting", text=supporting)
            self.visible("cancel")
            self.visible("confirm")
            self.visible("close")

    def double_tap_confirm(self) -> None:
        """Two quick taps on Confirm (one native double tap at its centre)."""
        rect = self.rect("confirm")
        x, y = rect["x"] + rect["width"] // 2, rect["y"] + rect["height"] // 2
        with allure.step(f"double-tap confirm-check.confirm at ({x}, {y})"):
            if self.platform == "ios":
                self.driver.execute_script("mobile: doubleTap", {"x": x, "y": y})
            else:
                self.driver.execute_script("mobile: doubleClickGesture", {"x": x, "y": y})
