"""Jobs list — behaviour over screens/jobs_list_map.py (module 03-order-list).

A card is one element whose name is the whole card (recon 4):
``[Updated\\n]<d MMM y>\\n<HH:mm>\\n<status>\\n<jobId> - <title>\\n<address>``.
``parse_card`` turns it into fields; assertions compare fields, never substrings of the whole
card (the address "New York" contains "New"). The calendar shows the same cards
(pages/jobs_calendar_page.py).
"""

import contextlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import allure
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from helpers import waits
from pages.base_page import BasePage
from screens import locator_for
from screens.jobs_calendar_map import JOBS_CALENDAR
from screens.jobs_list_map import JOBS_LIST

_CARD_START = re.compile(r"^(Updated\n)?\d{1,2} [A-Z][a-z]{2} \d{4}\n\d{2}:\d{2}\n")
_CARD_TYPES = ("XCUIElementTypeStaticText", "XCUIElementTypeImage")
REFRESH_SETTLE = 8.0  # a pull-to-refresh against the weak DEV server
SCAN_LIMIT = 8  # drags while collecting every card of the list


@dataclass(frozen=True)
class Card:
    updated: bool
    date: str
    time: str
    status: str
    title: str  # "<jobId> - <title>"
    address: str

    @property
    def job_id(self) -> str:
        return self.title.split(" - ", 1)[0]


def is_card(name: str | None) -> bool:
    return bool(name) and bool(_CARD_START.match(name))


def parse_card(name: str) -> Card:
    """Fields of a card from its accessibility name (format above)."""
    lines = name.split("\n")
    updated = lines[0] == "Updated"
    if updated:
        lines = lines[1:]
    if len(lines) < 5:
        raise ValueError(f"not a job card: {name!r}")
    date, time, status, title = lines[:4]
    return Card(updated, date, time, status, title, "\n".join(lines[4:]))


def cards_on_screen(page_source: str) -> list[tuple[Card, int]]:
    """Visible cards of one page-source read, with their top y, top → bottom."""
    found = []
    for node in ET.fromstring(page_source).iter():
        a = node.attrib
        if node.tag in _CARD_TYPES and a.get("visible") == "true" and is_card(a.get("name")):
            found.append((parse_card(a["name"]), int(a.get("y", 0))))
    return sorted(found, key=lambda pair: pair[1])


class JobsViewMixin:
    """What list and calendar mode share: cards, pull-to-refresh (mixed into a BasePage)."""

    def _drag_at(self, x: int, from_y: int, to_y: int, hold: float = 0.3) -> None:
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(
            self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "finger"), duration=300
        )
        pointer = actions.w3c_actions.pointer_action
        pointer.move_to_location(x, from_y).pointer_down()
        pointer.move_to_location(x, to_y).pause(hold).release()
        actions.perform()

    def _settle(self, timeout: float = REFRESH_SETTLE) -> None:
        """Wait until two page-source reads in a row are equal: the refresh has landed."""
        last: list[str] = []

        def stable(driver) -> bool:
            with contextlib.suppress(WebDriverException):
                last.append(driver.page_source)
            return len(last) >= 2 and last[-1] == last[-2]

        with contextlib.suppress(TimeoutException):
            waits.wait_until(self.driver, stable, timeout)

    def pull_to_refresh(self) -> None:
        """The ``swipe <root> down`` step: pull from below the header down, release, settle."""
        with allure.step(f"pull to refresh ({self.screen.id})"):
            size = self.driver.get_window_size()
            self._drag_at(size["width"] // 2, 300, int(size["height"] * 0.8))
            self._settle()

    def card(self, job_id: str) -> Card:
        """The card of ``job_id``, scrolled into view and parsed."""
        self.scroll_to("card", text=job_id)
        return parse_card(self.find("card", text=job_id).get_attribute("name"))

    def expect_card_field(self, job_id: str, field: str, value: str) -> None:
        with allure.step(f"expect {self.screen.id}.card[{job_id}].{field} = {value!r}"):
            actual = getattr(self.card(job_id), field)
            assert actual == value, f"card {job_id}: {field} is {actual!r}, expected {value!r}"

    def expect_no_card(self, job_id: str) -> None:
        """``expect-hidden card[...]``: not found anywhere in the (scrolled) list."""
        with allure.step(f"expect no card {job_id} in {self.screen.id}"):
            titles = [c.job_id for c in self.all_cards()]
            assert job_id not in titles, f"{job_id} is shown ({titles})"

    def visible_cards(self) -> list[Card]:
        return [card for card, _ in cards_on_screen(self.driver.page_source)]

    def expect_no_cards(self) -> None:
        with allure.step(f"expect no job card in {self.screen.id}"):
            shown = [c.job_id for c in self.visible_cards()]
            assert not shown, f"cards shown: {shown}"

    def all_cards(self) -> list[Card]:
        """Every card of the scrolled content, top → bottom; scrolls back the same distance."""
        height = self.driver.get_window_size()["height"]
        up, down = int(height * 0.75), int(height * 0.35)
        seen: list[Card] = []
        drags = 0
        while drags < SCAN_LIMIT:
            fresh = [c for c in self.visible_cards() if c not in seen]
            if not fresh:
                break
            seen += fresh
            self._drag_at(10, up, down)
            drags += 1
        for _ in range(drags):
            self._drag_at(10, down, up)
        return seen

    def card_count(self, job_id: str) -> int:
        return sum(1 for c in self.all_cards() if c.job_id == job_id)


class JobsListPage(JobsViewMixin, BasePage):
    screen = JOBS_LIST

    def wait_loaded(self, timeout: float | None = None) -> None:
        """List loaded = its empty state or at least one card is on screen (a tap on the toggle
        while the list is still loading is ignored by the app — recon 4)."""

        def loaded(driver) -> bool:
            source = driver.page_source
            return "No jobs" in source or bool(cards_on_screen(source))

        with allure.step("wait for the Jobs list to load"):
            waits.wait_until(self.driver, loaded, timeout, "the Jobs list did not load")

    def to_calendar(self) -> None:
        """Tap the toggle → calendar mode (day cells visible)."""
        self.wait_loaded()
        with allure.step("toggle → calendar"):
            self.tap("view-toggle")
            waits.wait_visible(self.driver, locator_for(JOBS_CALENDAR, self.platform, "root"))

    def to_list(self) -> None:
        """Tap the toggle → list mode (no day cells)."""
        with allure.step("toggle → list"):
            self.tap("view-toggle")
            waits.wait_gone(self.driver, locator_for(JOBS_CALENDAR, self.platform, "root"))
