"""Job details — behaviour over screens/job_details_map.py (modules 03 and 04-order-details).

What the tree cannot say is decided by pixels: the "Updated" banner (fill #B80B22, as on the list
card) is not an element; "Check in fully on screen" is the button's rect inside the window.
"""

import contextlib
import re
import time
from collections.abc import Iterator
from datetime import UTC, datetime

import allure
from selenium.common.exceptions import TimeoutException

from helpers import pixels, waits
from pages.base_page import BasePage, normalized
from pages.jobs_list_page import UPDATED_RGB, UPDATED_SHARE
from pages.submit_dialog_page import SETTLE, Submission, SubmitDialog, snackbars, watch_submission
from screens.job_details_map import JOB_DETAILS

TIMER = re.compile(r"(\d\d):(\d\d):(\d\d)")
TIMER_READ = 5.0  # seconds to catch a clean timer name between digit roll-overs
TIMER_TOLERANCE = 2.0  # whole seconds shown (±1) + the time a tree read takes (up to ~0.5 s)
BANNER_WATCH = 2.0  # seconds a "no Updated banner" check keeps looking (the banner lives ~0.3 s)
SNACKBAR = 10.0  # seconds for an earlier snackbar to leave the bottom action (recon 11: ~4 s)


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
            shown = self.label_of(self.visible("description", timeout, text=first))
            assert normalized(shown) == normalized(text), f"description is {shown!r}"

    def timer_seconds(self, timeout: float = TIMER_READ) -> int:
        """The In progress stopwatch in seconds. Its name holds the digits and colons on separate
        lines; while a digit rolls over the name briefly carries both digits (recon 7:
        '0\\n0\\n:\\n0\\n0\\n:\\n4\\n1\\n2'), so the read waits for a clean HH:MM:SS."""
        seen: list[str] = []

        def clean(_driver) -> tuple[int, int, int] | None:
            found = self.driver.find_elements(*self.locator("timer"))
            name = self.label_of(found[0]) if found else ""
            seen.append(name)
            match = TIMER.fullmatch(name.replace("\n", ""))
            return tuple(int(g) for g in match.groups()) if match else None

        try:
            hours, minutes, seconds = waits.wait_until(self.driver, clean, timeout, poll=0.1)
        except TimeoutException:
            last = seen[-3:]
            raise AssertionError(f"the timer is not HH:MM:SS within {timeout}s: {last}") from None
        return hours * 3600 + minutes * 60 + seconds

    def expect_timer_running(self, gap: float = 3.0) -> None:
        """The stopwatch shows HH:MM:SS and moves with the clock: two reads ``gap`` s apart differ
        by the time between them (± TIMER_TOLERANCE)."""
        with allure.step(f"expect the timer HH:MM:SS and running ({gap:.0f}s)"):
            first, start = self.timer_seconds(), time.monotonic()
            time.sleep(gap)  # the observation window of the check itself, not a sync wait
            second, elapsed = self.timer_seconds(), time.monotonic() - start
            assert abs((second - first) - elapsed) <= TIMER_TOLERANCE, (
                f"timer {first}s → {second}s in {elapsed:.1f}s"
            )

    def expect_deliverable_row(self, name: str) -> None:
        """A deliverable row ``name`` with two images inside it: the icon on the left, the
        chevron on the right (CHK-ORDP-005; recon 7 — the images have no names)."""
        with allure.step(f"expect {self.screen.id}.deliverable[{name}] with icon and chevron"):
            self.scroll_to("deliverable", text=name)
            row = self.visible("deliverable", text=name).rect
            inside = [
                im.rect for im in self.driver.find_elements(*self.locator("images"))
                if row["y"] <= im.rect["y"] + im.rect["height"] / 2 <= row["y"] + row["height"]
            ]  # fmt: skip
            xs = sorted(r["x"] + r["width"] / 2 for r in inside)
            third = row["width"] / 3
            assert len(xs) == 2 and xs[0] < row["x"] + third and xs[1] > row["x"] + 2 * third, (
                f"row {name!r} {row}: images at x={xs}, expected an icon left and a chevron right"
            )

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

    def open_submit_dialog(self) -> SubmitDialog:
        """Tap "Submit deliverables" → the confirmation dialog. A snackbar of an earlier save
        ("Survey saved") lies over the button for ~4 s and takes the tap (run 1): it must be gone
        first — the button itself reads as visible under it."""
        with allure.step("tap job-details.submit-deliverables → submit-dialog"):
            self.visible("submit-deliverables", SNACKBAR)
            gone = lambda d: not snackbars(d.page_source, self.platform)  # noqa: E731
            waits.wait_until(self.driver, gone, SNACKBAR)
            self.tap("submit-deliverables")
            dialog = SubmitDialog(self.driver, self.platform)
            dialog.assert_open(10)
            return dialog

    def retry_submission(self, settle: float = SETTLE) -> Submission:
        """Tap the failed submission's Retry, then watch as ``SubmitDialog.submit`` does."""
        with allure.step("tap job-details.retry and watch the submission"):
            seen = Submission(tapped_at=datetime.now(UTC))
            self.tap("retry", 2)
            return watch_submission(self.driver, seen, settle=settle)

    def open_attachments(self, timeout: float | None = None) -> None:
        self.scroll_to("attachments")
        self.tap("attachments", timeout)

    def wait_checking_in(self, timeout: float | None = None) -> None:
        """The Check in button turned into the disabled 'Checking in' (the flow started).

        Android: the location prompt opens at once in a window of its own, and UiAutomator2
        reads only the active window — the button under it is found with ``enableMultiWindows``
        for this step only (module 04 Android run 1: the prompt over 'Checking in')."""
        with allure.step("expect 'Checking in' (disabled)"), self._all_windows():
            waits.wait_until(
                self.driver,
                lambda _d: self.is_visible("checking-in", 0),
                timeout,
                "the button did not turn into 'Checking in'",
            )
            self.expect_disabled("checking-in")

    @contextlib.contextmanager
    def _all_windows(self) -> Iterator[None]:
        if self.platform != "android":
            yield
            return
        self.driver.update_settings({"enableMultiWindows": True})
        try:
            yield
        finally:
            with contextlib.suppress(Exception):
                self.driver.update_settings({"enableMultiWindows": False})
