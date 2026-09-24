"""Job details — behaviour over screens/job_details_map.py (modules 03 and 04-order-details).

What the tree cannot say is decided by pixels: the "Updated" banner (fill #B80B22, as on the list
card) is not an element; "Check in fully on screen" is the button's rect inside the window.
"""

import time

import allure

from helpers import pixels, waits
from pages.base_page import BasePage, normalized
from pages.jobs_list_page import UPDATED_RGB, UPDATED_SHARE
from screens.job_details_map import JOB_DETAILS

BANNER_WATCH = 2.0  # seconds a "no Updated banner" check keeps looking (the banner lives ~0.3 s)


class JobDetailsPage(BasePage):
    screen = JOB_DETAILS

    def expect_header(self, title_line: str, timeout: float | None = None) -> None:
        """The app bar shows '<jobId> - <title>' of the job that was opened."""
        self.visible("header", timeout, text=title_line)

    def expect_field(self, alias: str, text: str, timeout: float | None = None) -> None:
        """A text field of the details (status, date, PF name …) shows exactly ``text``."""
        self.scroll_to(alias, text=text)
        self.visible(alias, timeout, text=text)

    def expect_description(self, text: str, timeout: float | None = None) -> None:
        """The description shows ``text`` — every line, in order (one element, recon 5)."""
        first = text.split("\n")[0]
        with allure.step("expect job-details.description = the whole description"):
            shown = self.visible("description", timeout, text=first).get_attribute("name") or ""
            assert normalized(shown) == normalized(text), f"description is {shown!r}"

    def expect_check_in_on_screen(self) -> None:
        """``Check in`` is enabled and lies wholly inside the window — no scrolling needed."""
        height = self.driver.get_window_size()["height"]
        with allure.step("expect Check in enabled and fully on screen"):
            self.expect_enabled("check-in")
            rect = self.rect("check-in")
            bottom = rect["y"] + rect["height"]
            assert rect["y"] >= 0 and bottom <= height, (
                f"Check in at y={rect['y']}..{bottom}, screen height {height}"
            )

    def expect_read_only(self) -> None:
        """No text field or text view anywhere on the screen (CHK-ORDD-010)."""
        with allure.step("expect no editable element on the details"):
            count = len(self.driver.find_elements(*self.locator("any-editable")))
            assert count == 0, f"{count} editable element(s) on the details"

    def pull_to_refresh(self) -> None:
        """The ``swipe job-details.root down`` step: pull the details content down, release."""
        size = self.driver.get_window_size()
        to_y = int(size["height"] * 0.8)
        with allure.step("pull to refresh (job-details)"):
            if self.platform != "ios":
                self._drag(250, to_y)
                return
            # iOS: the native press-then-drag the Flutter scroll views follow (as the Jobs list)
            self.driver.execute_script(
                "mobile: dragFromToForDuration",
                {"duration": 0.3, "fromX": size["width"] // 2, "fromY": 250,
                 "toX": size["width"] // 2, "toY": to_y},
            )  # fmt: skip

    def expect_no_updated_banner(self, seconds: float = BANNER_WATCH) -> None:
        """No "Updated" banner fill on screen during ``seconds`` (pixels — not in the tree)."""
        with allure.step(f"expect no 'Updated' banner on the details for {seconds}s (pixels)"):
            end = time.monotonic() + seconds
            shares = []
            while time.monotonic() < end:
                png = self.driver.get_screenshot_as_png()
                shares.append(pixels.colour_share(png, UPDATED_RGB))
                if shares[-1] >= UPDATED_SHARE:
                    allure.attach(png, name=f"'Updated' banner drawn ({shares[-1]:.4f})",
                                  attachment_type=allure.attachment_type.PNG)  # fmt: skip
                    raise AssertionError(f"'Updated' banner drawn (fill {shares[-1]:.4f})")
            assert shares, "no screenshot taken"

    def open_attachments(self, timeout: float | None = None) -> None:
        self.scroll_to("attachments")
        self.tap("attachments", timeout)

    def wait_checking_in(self, timeout: float | None = None) -> None:
        """The Check in button turned into the disabled 'Checking in' (the flow started)."""
        with allure.step("expect 'Checking in' (disabled)"):
            waits.wait_until(
                self.driver,
                lambda _d: self.is_visible("checking-in", 0),
                timeout,
                "the button did not turn into 'Checking in'",
            )
            self.expect_disabled("checking-in")
