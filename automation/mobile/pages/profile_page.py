"""Profile — behaviour over screens/profile_map.py (module 12, recon 13).

The card is one element: '<first last>\\n<phone>\\n<email>' — parsed here. The Edit button has no
name: it is found by its place (the card's top right). The theme is decided by the screenshot's
mean brightness (recon 13: light ~246, dark ~39).
"""

from dataclasses import dataclass

import allure

from helpers import pixels
from pages.base_page import BasePage
from screens.profile_map import LOGOUT_DIALOG, PROFILE, THEME_MENU

DARK_BELOW = 100.0
LIGHT_ABOVE = 180.0


@dataclass
class Card:
    name: str
    phone: str
    email: str


class ThemeMenu(BasePage):
    screen = THEME_MENU


class LogoutDialog(BasePage):
    screen = LOGOUT_DIALOG


class ProfilePage(BasePage):
    screen = PROFILE

    def card(self, timeout: float | None = None) -> Card:
        lines = self.label_of(self.visible("card", timeout)).split("\n")
        lines += [""] * (3 - len(lines))
        return Card(*lines[:3])

    def theme(self) -> str:
        """'Auto' / 'Light' / 'Dark' from 'App theme (<mode>)'."""
        label = self.label_of(self.visible("theme", 5))
        return label.removeprefix("App theme (").removesuffix(")")

    def set_theme(self, mode: str) -> None:
        """'Auto' / 'Light' / 'Dark' through the ⋮ menu."""
        menu = ThemeMenu(self.driver, self.platform)
        with allure.step(f"App theme → {mode}"):
            self.tap("theme-menu", 5)
            menu.assert_open(5)
            menu.tap(mode.lower())
            menu.wait_gone("auto", 5)

    def brightness(self) -> float:
        return pixels.mean_brightness(self.driver.get_screenshot_as_png())

    def expect_dark(self, dark: bool = True) -> None:
        state = "dark" if dark else "light"
        with allure.step(f"expect the screen {state} (mean brightness)"):
            value = self.brightness()
            if dark:
                assert value < DARK_BELOW, f"mean brightness {value:.1f}, dark is < {DARK_BELOW}"
            else:
                assert value > LIGHT_ABOVE, f"mean brightness {value:.1f}, light is > {LIGHT_ABOVE}"

    def log_out(self, confirm: bool) -> None:
        dialog = LogoutDialog(self.driver, self.platform)
        with allure.step(f"Log out → {'Log out' if confirm else 'Cancel'}"):
            self.tap("logout", 5)
            dialog.assert_open(5)
            dialog.tap("confirm" if confirm else "cancel")
            dialog.wait_gone("title", 5)
