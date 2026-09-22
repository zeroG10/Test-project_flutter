"""Example page object for the login screen. Copy this pattern for real screens.

The page holds behaviour only; every locator lives in ``screens/login_map.py``.
"""

import allure

from pages.base_page import BasePage
from screens.login_map import LOGIN


class LoginPage(BasePage):
    screen = LOGIN

    def login(self, email: str, password: str) -> None:
        with allure.step(f"login as {email}"):
            self.type("email", email)
            self.type("password", password)
            self.hide_keyboard()
            self.tap("submit")

    def error_message(self) -> str:
        return self.text("error")
