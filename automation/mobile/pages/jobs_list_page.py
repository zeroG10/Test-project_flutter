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

from helpers import pixels, waits
from pages.base_page import BasePage
from screens import locator_for
from screens.jobs_calendar_map import JOBS_CALENDAR
from screens.jobs_list_map import JOBS_LIST

_CARD_START = re.compile(r"^(Updated\n)?\d{1,2} [A-Z][a-z]{2} \d{4}\n\d{2}:\d{2}\n")
_CARD_TYPES = ("XCUIElementTypeStaticText", "XCUIElementTypeImage")
REFRESH_SETTLE = 8.0  # a pull-to-refresh against the weak DEV server
SCAN_LIMIT = 8  # drags while collecting every card of the list
CARD_BOTTOM_MARGIN = 130  # the bottom tab bar covers the lowest ~125 pt (y 750 of 874, recon 4)
UPDATED_RGB = (0xB8, 0x0B, 0x22)  # the "Updated" banner fill: app theme `tertiary`
UPDATED_SHARE = 0.005  # calibrated 2026-09-24: 0.016–0.027 with a banner in view, 0.000 without


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


def cards_in_tree(page_source: str) -> list[Card]:
    """Every card node of one page-source read, visible or not. After a back navigation the tree
    reports drawn cards ``visible=false`` (run 2, 2026-09-24: TD-JOBS-003) — presence is what a
    count can rely on; a short list (≤ ~8 cards) is built completely, so no scrolling is needed."""
    return [
        parse_card(node.attrib["name"])
        for node in ET.fromstring(page_source).iter()
        if node.tag in _CARD_TYPES and is_card(node.attrib.get("name"))
    ]


class JobsViewMixin:
    """What list and calendar mode share: cards, pull-to-refresh (mixed into a BasePage)."""

    def _drag_at(
        self, x: int, from_y: int, to_x_or_y: int, *, horizontal_y: int | None = None
    ) -> None:
        """A drag from (x, from_y) to (x, to_y) — or, with ``horizontal_y``, from (x, y) to
        (to_x, y). iOS: the native press-then-drag (``mobile: dragFromToForDuration``), which the
        Flutter lists and the calendar's page view follow (recon 4); a W3C drag with a hold before
        the release did not turn the week (run 1). Android: a W3C drag."""
        if horizontal_y is None:
            start, end = (x, from_y), (x, to_x_or_y)
        else:
            start, end = (x, horizontal_y), (to_x_or_y, horizontal_y)
        if self.platform == "ios":
            self.driver.execute_script(
                "mobile: dragFromToForDuration",
                {
                    "duration": 0.3,
                    "fromX": start[0],
                    "fromY": start[1],
                    "toX": end[0],
                    "toY": end[1],
                },
            )
            return
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(
            self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "finger"), duration=300
        )
        pointer = actions.w3c_actions.pointer_action
        pointer.move_to_location(*start).pointer_down()
        pointer.move_to_location(*end).release()
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

    def open_card(self, job_id: str) -> None:
        """Tap a job's card only once it is still and wholly above the bottom tab bar: a tap on a
        list that is still coasting after a drag, or on a card half under the tab bar, does not
        open the job (module 05 run 1, the 5th of 8 cards)."""
        self.scroll_to("card", text=job_id)
        self._settle(3.0)
        limit = self.driver.get_window_size()["height"] - CARD_BOTTOM_MARGIN
        rect = self.find("card", text=job_id).rect
        if rect["y"] + rect["height"] > limit:
            width = self.driver.get_window_size()["width"]
            self._drag_at(width // 2, limit - 20, limit - 20 - rect["height"])
            self._settle(3.0)
        self.tap("card", text=job_id)

    def expect_card_field(self, job_id: str, field: str, value: str) -> None:
        with allure.step(f"expect {self.screen.id}.card[{job_id}].{field} = {value!r}"):
            actual = getattr(self.card(job_id), field)
            assert actual == value, f"card {job_id}: {field} is {actual!r}, expected {value!r}"

    def expect_updated(self, job_id: str, shown: bool) -> None:
        """``card[...].updated`` decided by the tree AND the drawn screen: after a back navigation
        the tree has contradicted the screen (recon 4 vs runs 1–2, TD-JOBS-003). The pixels look
        for the banner fill anywhere on the screen with the card in view — in the seed only the
        card under test can carry it. Tree and screen must both agree with ``shown``."""
        state = "shows" if shown else "does not show"
        with allure.step(
            f"expect {self.screen.id}.card[{job_id}] {state} 'Updated' (tree + pixels)"
        ):
            in_tree = self.card(job_id).updated
            png = self.driver.get_screenshot_as_png()
            share = pixels.colour_share(png, UPDATED_RGB)
            drawn = share >= UPDATED_SHARE
            allure.attach(png, name=f"{job_id}: tree updated={in_tree}, banner fill {share:.4f}",
                          attachment_type=allure.attachment_type.PNG)  # fmt: skip
            assert in_tree == shown and drawn == shown, (
                f"card {job_id}: 'Updated' in the tree {in_tree}, drawn {drawn} "
                f"(banner fill {share:.4f}); expected {shown}"
            )

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

    def wait_content(self, timeout: float | None = None) -> None:
        """Cards or the empty state are in the tree (the view has loaded or finished a move)."""

        def shown(driver) -> bool:
            source = driver.page_source
            return "No jobs" in source or bool(cards_in_tree(source))

        waits.wait_until(self.driver, shown, timeout, "neither job cards nor 'No jobs' on screen")

    def all_cards(self) -> list[Card]:
        """Every card of the scrolled content, top → bottom: wait for the content, scroll to the
        top, then collect while scrolling down (run 1: counting mid-scroll right after a back
        navigation saw no card at all)."""
        self.wait_content()
        height = self.driver.get_window_size()["height"]
        up, down = int(height * 0.75), int(height * 0.35)
        for _ in range(SCAN_LIMIT):  # to the top: drag the content down until it stops moving
            first = self.visible_cards()[:1]
            self._drag_at(10, down, up)
            if self.visible_cards()[:1] == first:
                break
        self.wait_content()
        seen: list[Card] = []
        for _ in range(SCAN_LIMIT):
            fresh = [c for c in self.visible_cards() if c not in seen]
            if not fresh:
                break
            seen += fresh
            self._drag_at(10, up, down)
        # a "no such card" built on a tree that hides every card would pass vacuously
        assert seen or not cards_in_tree(self.driver.page_source), (
            "the tree holds job cards but reports none visible (TD-JOBS-003) — cannot decide"
        )
        return seen

    def card_count(self, job_id: str) -> int:
        """How many cards of ``job_id`` the view holds — one page-source read, visibility ignored
        (see ``cards_in_tree``)."""
        self.wait_content()
        return sum(1 for c in cards_in_tree(self.driver.page_source) if c.job_id == job_id)


class JobsListPage(JobsViewMixin, BasePage):
    screen = JOBS_LIST

    def wait_loaded(self, timeout: float | None = None) -> None:
        """List loaded — a tap on the toggle while it is still loading is ignored (recon 4)."""
        with allure.step("wait for the Jobs list to load"):
            self.wait_content(timeout)

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
