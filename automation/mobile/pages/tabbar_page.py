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
        """The tab whose page-source ``traits`` contain ``Selected`` (recon 4); Android: the tab
        node with ``selected="true"`` (recon A1)."""
        if self.platform == "android":
            for n in self.nodes():
                for tail, tab in _TABS.items():
                    if n.label.endswith(tail) and n.selected:
                        return tab
            return None
        for node in ET.fromstring(self.driver.page_source).iter():
            name = node.attrib.get("name") or ""
            for tail, tab in _TABS.items():
                if name.endswith(tail) and "Selected" in (node.attrib.get("traits") or ""):
                    return tab
        return None

    def notifications_count(self) -> int:
        """The unread count on the Notifications tab — the first line of its label
        ('3\nNotifications\nTab 2 of 3'; no number = 0, recon 12). Android: the same label, in
        ``content-desc`` (recon A1)."""
        if self.platform == "android":
            for n in self.nodes():
                if n.label.endswith("Tab 2 of 3"):
                    first = n.label.split("\n")[0]
                    return int(first) if first.isdigit() else 0
            raise AssertionError("no Notifications tab in the page source")
        for node in ET.fromstring(self.driver.page_source).iter():
            name = node.attrib.get("name") or ""
            if name.endswith("Tab 2 of 3"):
                first = name.split("\n")[0]
                return int(first) if first.isdigit() else 0
        raise AssertionError("no Notifications tab in the page source")

    def expect_selected(self, tab: str) -> None:
        with allure.step(f"expect the {tab} tab selected"):
            actual = self.selected()
            assert actual == tab, f"selected tab is {actual!r}, expected {tab!r}"
