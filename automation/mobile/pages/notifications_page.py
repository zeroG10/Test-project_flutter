"""Notifications — behaviour over screens/notifications_map.py (module 11, recon 12).

What the tree does not say is read another way:
- rows come from the page source by their rect (the ``visible`` attribute is wrong for part of a
  long list);
- the unread red dot is pixels: ``#EB0101`` (theme ``error``) in a 16-pt box at the top right of
  the icon. The icon is centred in the row's height (recon 12: 6.8 % of the box when unread, 0 %
  when read);
- "Go to Settings" is the last line of the banner's single element, tapped by position.
"""

import contextlib
import io
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import allure
from PIL import Image
from selenium.common.exceptions import TimeoutException, WebDriverException

from helpers import pixels, waits
from pages.base_page import BasePage
from screens.notifications_map import NOTIFICATIONS

DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")  # 'M/d/yyyy' (recon 12: '9/26/2026')
TIME = re.compile(r"^\d{1,2}:\d{2}\s?[AP]M$")  # 'h:mm a' (the space may be U+202F)
UNREAD_RGB = (0xEB, 0x01, 0x01)
UNREAD_SHARE = 0.03  # calibrated on recon 12 screenshots: 0.068 unread, 0.000 read
ICON_CENTRE_X = 40  # the icon glyph (x 28, 24 pt) inside the 48-pt circle from x 16
GO_TO_SETTINGS = (127, 24)  # the line's centre: x in points, y above the banner's bottom
SETTLE = 8.0


@dataclass
class NotificationRow:
    kind: str  # "Other" = the job can be opened, "Image" = it cannot (D-NOTIF-2)
    date: str
    time: str
    description: str
    x: int
    y: int
    width: int
    height: int
    chevron: bool


def rows_in(source: str) -> list[NotificationRow]:
    """Every notification row of a page source, top to bottom, with its chevron."""
    nodes = list(ET.fromstring(source).iter())
    chevrons = [
        n.attrib
        for n in nodes
        if n.tag.endswith("Image") and not n.attrib.get("name") and int(n.attrib.get("x", 0)) > 340
    ]
    rows = []
    for node in nodes:
        kind = node.tag.replace("XCUIElementType", "")
        lines = (node.attrib.get("name") or "").split("\n")
        if kind not in ("Other", "Image") or len(lines) < 3:
            continue
        if not (DATE.match(lines[0]) and TIME.match(lines[1])):
            continue
        a = node.attrib
        x, y, w, h = (int(a.get(k, 0)) for k in ("x", "y", "width", "height"))
        chevron = any(
            y <= int(c.get("y", 0)) + int(c.get("height", 0)) / 2 <= y + h for c in chevrons
        )
        rows.append(NotificationRow(kind, lines[0], lines[1], "\n".join(lines[2:]), x, y, w, h,
                                    chevron))  # fmt: skip
    return sorted(rows, key=lambda r: r.y)


class NotificationsPage(BasePage):
    screen = NOTIFICATIONS

    def rows(self) -> list[NotificationRow]:
        return rows_in(self.driver.page_source)

    def descriptions(self) -> list[str]:
        return [r.description for r in self.rows()]

    def row(self, part: str, timeout: float = 10.0) -> NotificationRow:
        """The row whose description contains ``part``."""
        end = time.monotonic() + timeout
        while True:
            found = [r for r in self.rows() if part in r.description]
            if found or time.monotonic() > end:
                break
            time.sleep(0.5)
        assert found, f"no notification row with {part!r}: {self.descriptions()}"
        return found[0]

    def _settle(self, timeout: float = SETTLE) -> None:
        """Two page-source reads in a row are equal: the list has landed."""
        last: list[str] = []

        def stable(driver) -> bool:
            with contextlib.suppress(WebDriverException):
                last.append(driver.page_source)
            return len(last) >= 2 and last[-1] == last[-2]

        with contextlib.suppress(TimeoutException):
            waits.wait_until(self.driver, stable, timeout)

    def refresh(self) -> None:
        """The ``swipe notifications.root down`` step: pull the list down, release, settle."""
        size = self.driver.get_window_size()
        with allure.step("pull to refresh (notifications)"):
            self.driver.execute_script("mobile: dragFromToForDuration", {
                "duration": 0.3, "fromX": size["width"] // 2, "fromY": 300,
                "toX": size["width"] // 2, "toY": int(size["height"] * 0.8)})  # fmt: skip
            self._settle()

    def scroll_down(self) -> None:
        size = self.driver.get_window_size()
        self.driver.execute_script("mobile: dragFromToForDuration", {
            "duration": 0.3, "fromX": size["width"] // 2, "fromY": int(size["height"] * 0.7),
            "toX": size["width"] // 2, "toY": int(size["height"] * 0.3)})  # fmt: skip
        self._settle()

    def tap_row(self, part: str) -> None:
        with allure.step(f"tap notifications.row[{part}]"):
            r = self.row(part)
            self.driver.execute_script(
                "mobile: tap", {"x": r.x + r.width / 2, "y": r.y + r.height / 2}
            )

    def unread_share(self, part: str) -> float:
        """Share of the unread red in the dot's box of the row with ``part`` (pixels)."""
        r = self.row(part)
        png = self.driver.get_screenshot_as_png()
        scale = Image.open(io.BytesIO(png)).width / self.driver.get_window_size()["width"]
        cx, cy = r.x + ICON_CENTRE_X, r.y + r.height / 2
        box = {"x": cx + 8, "y": cy - 24, "width": 16, "height": 16}
        return pixels.box_colour_share(png, box, scale, UNREAD_RGB)

    def expect_unread(self, part: str, unread: bool = True) -> None:
        state = "unread (red dot)" if unread else "read (no red dot)"
        with allure.step(f"expect notifications.row[{part}] {state} — pixels"):
            share = self.unread_share(part)
            if unread:
                assert share >= UNREAD_SHARE, f"no red dot: {share:.4f} < {UNREAD_SHARE}"
            else:
                assert share < UNREAD_SHARE / 3, f"red dot drawn: {share:.4f}"

    def banner_lines(self) -> list[str]:
        return (self.visible("banner", 10).get_attribute("name") or "").split("\n")

    def tap_go_to_settings(self) -> None:
        with allure.step("tap notifications.go-to-settings (the banner's last line)"):
            r = self.visible("go-to-settings", 10).rect
            x, above = GO_TO_SETTINGS
            self.driver.execute_script(
                "mobile: tap", {"x": r["x"] + x, "y": r["y"] + r["height"] - above}
            )
