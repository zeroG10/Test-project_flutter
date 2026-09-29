"""Jobs — weekly calendar mode, behaviour over screens/jobs_calendar_map.py (module 03).

Day cells are texts named by the full date; the week changes by a horizontal swipe on the strip
(no arrows — D-ORDL-7); the selected day keeps its weekday after a swipe (D-ORDL-12). The
calendar keeps its own copy of the jobs: a list refresh does not reach it (BUG-ORDL-001), so
tests pull to refresh here before reading cards.
"""

import re
import xml.etree.ElementTree as ET
from datetime import date

import allure

from helpers import waits
from pages.base_page import BasePage
from pages.jobs_list_page import JobsViewMixin
from screens.jobs_calendar_map import JOBS_CALENDAR

_DAY_CELL = re.compile(r"^[A-Za-z]+day, [A-Za-z]+ \d+, \d+$")


def day_cell_name(day: date) -> str:
    """'Thursday, September 24, 2026' — the accessibility name of a day cell."""
    return f"{day:%A}, {day:%B} {day.day}, {day.year}"


def day_title(day: date) -> str:
    """'Thursday, 24 September' — the title of the selected day (EEEE, d MMMM)."""
    return f"{day:%A}, {day.day} {day:%B}"


class JobsCalendarPage(JobsViewMixin, BasePage):
    screen = JOBS_CALENDAR

    def week_days(self) -> list[str]:
        """Names of the day cells, left → right (one page-source read)."""
        if self.platform == "android":
            shown = [(n.x, n.label) for n in self.nodes() if n.visible and _DAY_CELL.match(n.label)]
            return [name for _, name in sorted(shown)]
        cells = []
        for node in ET.fromstring(self.driver.page_source).iter():
            a = node.attrib
            name = a.get("name") or ""
            if a.get("visible") == "true" and _DAY_CELL.match(name):
                cells.append((int(a.get("x", 0)), name))
        return [name for _, name in sorted(cells)]

    def expect_week(self, days: list[date]) -> None:
        wanted = [day_cell_name(d) for d in days]
        with allure.step(f"expect the week {wanted[0]} … {wanted[-1]}"):
            waits.wait_until(
                self.driver,
                lambda _d: self.week_days() == wanted,
                message=f"week strip is {self.week_days()}, expected {wanted}",
            )

    def select_day(self, day: date) -> None:
        self.tap("day", text=day_cell_name(day))

    def swipe_week(self, direction: str) -> None:
        """``left`` → next week, ``right`` → previous week (a drag across the day strip)."""
        if direction not in ("left", "right"):
            raise ValueError("direction must be left or right")
        before = self.week_days()
        strip = self.visible("week").rect
        y = strip["y"] + strip["height"] // 2
        width = self.driver.get_window_size()["width"]
        start, end = (0.85, 0.15) if direction == "left" else (0.15, 0.85)
        with allure.step(f"swipe the week strip {direction}"):
            self._drag_at(int(width * start), 0, int(width * end), horizontal_y=y)
            waits.wait_until(
                self.driver,
                lambda _d: self.week_days() != before,
                message="the week strip did not change after the swipe",
            )
