"""Survey / Photo report / Notes screens — behaviour over screens/deliverable_screens_map.py."""

from pages.base_page import BasePage
from screens.deliverable_screens_map import DELIVERABLE_SCREEN


class DeliverableScreenPage(BasePage):
    screen = DELIVERABLE_SCREEN

    def expect_open(self, title: str, timeout: float | None = None) -> None:
        self.visible("title", timeout, text=title)
