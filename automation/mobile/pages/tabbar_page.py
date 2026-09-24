"""Bottom tab bar — behaviour over screens/tabbar_map.py."""

import xml.etree.ElementTree as ET

import allure

from pages.base_page import BasePage
from screens.tabbar_map import TABBAR

_TABS = {"Tab 1 of 3": "jobs", "Tab 2 of 3": "notifications", "Tab 3 of 3": "profile"}


class TabBarPage(BasePage):
    screen = TABBAR

    def open(self, tab: str) -> None:
        self.tap(tab)

    def selected(self) -> str | None:
        """The tab whose page-source ``traits`` contain ``Selected`` (recon 4)."""
        for node in ET.fromstring(self.driver.page_source).iter():
            name = node.attrib.get("name") or ""
            for tail, tab in _TABS.items():
                if name.endswith(tail) and "Selected" in (node.attrib.get("traits") or ""):
                    return tab
        return None

    def expect_selected(self, tab: str) -> None:
        with allure.step(f"expect the {tab} tab selected"):
            actual = self.selected()
            assert actual == tab, f"selected tab is {actual!r}, expected {tab!r}"
