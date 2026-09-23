"""Welcome — behaviour over screens/welcome_map.py."""

import allure

from pages.base_page import BasePage
from screens.welcome_map import WELCOME


class WelcomePage(BasePage):
    screen = WELCOME

    def open_login(self) -> None:
        with allure.step("Welcome → Login"):
            self.tap("login")

    def open_sign_up(self) -> None:
        with allure.step("Welcome → Sign up (Registration)"):
            self.tap("sign-up")
