"""Login — behaviour over screens/login_map.py."""

import allure

from pages.base_page import BasePage
from screens.login_map import LOGIN


class LoginPage(BasePage):
    screen = LOGIN

    def request_code(self, identifier: str) -> None:
        """Email or phone (E.164, as the field's hint says) → Continue → an OTP is requested."""
        with allure.step(f"Login: request a code for {identifier}"):
            self.type("identifier", identifier)
            self.submit()

    def submit(self) -> None:
        """Hide the keyboard, then Continue: the server's message is a banner at the bottom for
        ~4 s, and an open software keyboard hides it (final run 1, 2026-09-27)."""
        with allure.step("hide the keyboard, tap login.continue"):
            self.hide_keyboard()
            self.tap("continue")

    def expect_error(self, text: str, timeout: float | None = None) -> None:
        """A validation / server message with exactly this text is visible."""
        self.visible("error", timeout, text=text)

    def expect_no_error(self, text: str, timeout: float | None = None) -> None:
        self.wait_gone("error", timeout, text=text)
