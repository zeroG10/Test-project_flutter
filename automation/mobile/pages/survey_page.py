"""The survey form — behaviour over screens/survey_map.py and screens/survey_photo_map.py
(module 08).

What the tree does not give is resolved here, each with its testability defect:
- the visible questions are the numbered titles parsed from the card labels (TD-SRV-001);
- a field is "the n-th of its kind in form order" (``nth``): off-screen elements are in the tree
  with an empty rect, so the page scrolls towards the n-th by comparing it with the ones on screen;
- a text field is tapped in its input area — a loose card's text field is the whole card
  (TD-SRV-002);
- a gallery photo is chosen by its grid position in the system picker (TD-SRV-003).
"""

import re
import time
import xml.etree.ElementTree as ET

import allure
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from helpers import waits
from pages.base_page import BasePage
from screens.survey_map import (
    SURVEY,
    SURVEY_DATE_PICKER,
    SURVEY_DELETE_DIALOG,
    SURVEY_TIME_PICKER,
)
from screens.survey_photo_map import PHOTO_EDITOR, PHOTO_METADATA, PHOTO_PICKER

TITLE = re.compile(r"(\d+)\. \n(.+?)(?=\n|$)")
TOP, BOTTOM = 125, 770  # the form's visible band: below the app bar, above the Save button
NTH_DRAGS = 30
PICKER_WAIT = 10.0  # the system photo picker takes a few seconds to appear (recon 8)
LOGIC_WAIT = 5.0  # the form re-renders at once after an answer; the wait only absorbs the redraw


class SurveyDatePicker(BasePage):
    screen = SURVEY_DATE_PICKER


class SurveyTimePicker(BasePage):
    screen = SURVEY_TIME_PICKER


class SurveyDeleteDialog(BasePage):
    screen = SURVEY_DELETE_DIALOG


class PhotoPicker(BasePage):
    screen = PHOTO_PICKER


class PhotoEditor(BasePage):
    screen = PHOTO_EDITOR


class PhotoMetadata(BasePage):
    screen = PHOTO_METADATA


def titles_in(source: str) -> list[str]:
    """The numbered question titles in a page source, by number (TD-SRV-001)."""
    by_number: dict[int, str] = {}
    for el in ET.fromstring(source).iter():
        for number, title in TITLE.findall(el.attrib.get("name") or ""):
            by_number.setdefault(int(number), title)
    return [by_number[n] for n in sorted(by_number)]


class SurveyPage(BasePage):
    screen = SURVEY

    # --- what is on the form -----------------------------------------------------------

    def titles(self) -> list[str]:
        return titles_in(self.driver.page_source)

    def expect_titles(self, expected: list[str], timeout: float = LOGIC_WAIT) -> None:
        """The form renders exactly ``expected`` questions, in this order (a logic-table row)."""
        with allure.step(f"expect the visible questions: {expected}"):
            try:
                waits.wait_until(self.driver, lambda _d: self.titles() == expected, timeout)
            except TimeoutException:
                raise AssertionError(
                    f"visible questions {self.titles()}, expected {expected}"
                ) from None

    def labels(self) -> list[str]:
        """The raw card labels that carry question titles (for "no required marker")."""
        return [el.attrib.get("name") or "" for el in ET.fromstring(self.driver.page_source).iter()
                if TITLE.search(el.attrib.get("name") or "")]  # fmt: skip

    def count(self, alias: str, **params: object) -> int:
        """How many ``alias`` the form renders now (on screen or not)."""
        return len(self.driver.find_elements(*self.locator(alias, **params)))

    def names(self, alias: str, **params: object) -> list[str]:
        return [
            e.get_attribute("name") or ""
            for e in self.driver.find_elements(*self.locator(alias, **params))
        ]

    # --- the n-th element of a kind ---------------------------------------------------

    def nth(self, alias: str, n: int, **params: object) -> WebElement:
        """The ``n``-th (0-based) ``alias`` in form order, scrolled wholly into the visible band."""
        height = self.driver.get_window_size()["height"]
        down = True
        for _ in range(NTH_DRAGS):
            found = self.driver.find_elements(*self.locator(alias, **params))
            if len(found) <= n:
                raise AssertionError(
                    f"{self._name(alias, params)}: {len(found)} on the form, wanted #{n}"
                )
            shown = []
            for k, el in enumerate(found):
                try:
                    r = el.rect
                    if el.is_displayed() and r["y"] >= TOP and r["y"] + r["height"] <= BOTTOM:
                        shown.append(k)
                except StaleElementReferenceException:
                    continue
            if n in shown:
                return found[n]
            if shown:
                down = n > max(shown)
            if down:
                self._drag(int(height * 0.62), int(height * 0.34))
            else:
                self._drag(int(height * 0.34), int(height * 0.62))
        raise AssertionError(f"{self._name(alias, params)} #{n} not brought on screen")

    def tap_nth(self, alias: str, n: int = 0, **params: object) -> None:
        with allure.step(f"tap {self._name(alias, params)} #{n + 1}"):
            self.nth(alias, n, **params).click()
            time.sleep(0.3)  # the tap's own redraw; the next read waits on its condition

    def is_selected(self, alias: str, n: int = 0, **params: object) -> bool:
        return (self.nth(alias, n, **params).get_attribute("value") or "") == "1"

    def expect_selected(
        self, alias: str, n: int = 0, selected: bool = True, **params: object
    ) -> None:
        state = "selected" if selected else "not selected"
        with allure.step(f"expect {self._name(alias, params)} #{n + 1} {state}"):
            assert self.is_selected(alias, n, **params) == selected, (
                f"{self._name(alias, params)} #{n + 1} is not {state}"
            )

    # --- text, date, time -------------------------------------------------------------

    def hide_keyboard(self) -> None:
        """Tap the app bar title: dismisses the keyboard without touching a field."""
        self.tap("header")
        time.sleep(0.5)

    def _focus_text(self, n: int) -> WebElement:
        el = self.nth("text", n)
        r = el.rect
        y = r["y"] + r["height"] - 70 if r["height"] > 200 else r["y"] + r["height"] // 2
        self.driver.execute_script("mobile: tap", {"x": r["x"] + r["width"] // 2, "y": y})
        time.sleep(0.8)  # the field re-renders on focus: type into the focused one (recon 8)
        return self.driver.switch_to.active_element

    def fill_text(self, n: int, text: str) -> None:
        with allure.step(
            f"fill survey.text #{n + 1}: {text[:40]!r}{'…' if len(text) > 40 else ''}"
        ):
            self._focus_text(n).send_keys(text)
            self.hide_keyboard()

    def clear_text(self, n: int) -> None:
        with allure.step(f"clear survey.text #{n + 1}"):
            self._focus_text(n).clear()
            self.hide_keyboard()

    def text_value(self, n: int) -> str:
        return self.nth("text", n).get_attribute("value") or ""

    def set_date(self, day: int, n: int = 0) -> None:
        """The n-th EMPTY date field → day ``day`` of the month the picker opens on → OK."""
        picker = SurveyDatePicker(self.driver, self.platform)
        with allure.step(f"set survey.date #{n + 1} to day {day}"):
            self.tap_nth("date", n)
            picker.tap("day", 10, text=f"{day}, ")
            picker.tap("ok")
            picker.wait_gone("ok", 5)

    def set_time(self, hour: int, minute: int, n: int = 0) -> None:
        """The n-th EMPTY time field → text input mode (the dial is not in the tree) → OK."""
        picker = SurveyTimePicker(self.driver, self.platform)
        with allure.step(f"set survey.time #{n + 1} to {hour:02d}:{minute:02d}"):
            self.tap_nth("time", n)
            picker.tap("text-mode", 10)
            for alias, value in (("hour", hour), ("minute", minute)):
                waits.wait_until(self.driver, lambda _d, a=alias: picker.is_visible(a, 0), 5)
                time.sleep(0.5)  # the field is rebuilt once after the mode switch (recon 8: stale)
                picker.tap(alias)
                field = self.driver.switch_to.active_element
                field.clear()
                field.send_keys(f"{value:02d}")
            picker.tap("ok")
            picker.wait_gone("ok", 5)

    # --- photos -----------------------------------------------------------------------

    def add_photo(self, n: int, cell: int, description: str) -> None:
        """``survey.upload-photo`` #n → gallery cell ``cell`` (newest first) → ✓ → description →
        Save."""
        picker = PhotoPicker(self.driver, self.platform)
        editor, meta = (
            PhotoEditor(self.driver, self.platform),
            PhotoMetadata(self.driver, self.platform),
        )
        with allure.step(
            f"add photo #{cell} of the gallery to survey.upload-photo #{n + 1}: {description!r}"
        ):
            self.tap_nth("upload-photo", n)
            if not picker.is_open(PICKER_WAIT):
                # the first tap after a keyboard can go to the keyboard's dismissal (recon 8)
                self.tap_nth("upload-photo", n)
                picker.assert_open(PICKER_WAIT)
            grid = picker.visible("grid", 5).rect
            size = grid["width"] / 3
            x = grid["x"] + size * (cell % 3 + 0.5)
            y = grid["y"] + size * (cell // 3 + 0.5)
            self.driver.execute_script("mobile: tap", {"x": x, "y": y})
            editor.assert_open(15)
            editor.tap("done")
            meta.assert_open(15)
            if description:
                meta.tap("description")
                time.sleep(0.5)
                self.driver.switch_to.active_element.send_keys(description)
            meta.tap("save")
            self.assert_open(15)
            if description:
                self.visible("thumbnail", 15, text=description)

    # --- repeatable sections ----------------------------------------------------------

    def entry_headers(self, section: str) -> list[str]:
        """The headers of a repeatable section's entries, in order: '<section>', '<section> 2', …"""
        return [name.split("\n")[0] for name in self.names("entry-headers", text=section)]

    def delete_entry(self, n: int, confirm: bool | None) -> None:
        """Tap the n-th entry's trash; ``confirm`` True / False answers the dialog, None = no
        dialog expected."""
        dialog = SurveyDeleteDialog(self.driver, self.platform)
        with allure.step(f"delete entry (trash #{n + 1}), dialog: {confirm}"):
            self.tap_nth("delete-entry", n)
            if confirm is None:
                assert not dialog.is_visible("title", 2), "a dialog opened for an empty entry"
                return
            dialog.visible("title", 5)
            dialog.tap("delete" if confirm else "cancel")
            dialog.wait_gone("title", 5)

    # --- save -------------------------------------------------------------------------

    def save(self, timeout: float = 20.0) -> None:
        """Tap Save; "Survey saved" appears (the app then shows the job's details)."""
        with allure.step("tap survey.save → 'Survey saved'"):
            self.tap("save")
            self.visible("saved", timeout)
