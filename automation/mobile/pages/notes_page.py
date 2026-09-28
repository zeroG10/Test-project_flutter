"""Notes — behaviour over screens/notes_map.py (module 10).

A note row is one element whose label joins the date, the text and 'Show menu' (TD-NOTE-001): the
page parses the rows from the page source in list order and opens the ⋮ menu with a tap on the row's
right end.
"""

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import allure

from helpers import waits
from pages.base_page import BasePage
from screens.notes_map import (
    NOTE_DELETE_DIALOG,
    NOTE_EDITOR,
    NOTE_MENU,
    NOTE_UNSAVED_DIALOG,
    NOTES,
)

TOAST = 8.0  # a toast stays ~3 s
SAVE_WAIT = 20.0
MENU_X_FROM_RIGHT = 28  # the ⋮ sits at the row's right end (recon 10: 374 of 402)


@dataclass(frozen=True)
class NoteRow:
    date: str
    text: str
    x: int
    y: int
    width: int
    height: int


def rows_in(source: str) -> list[NoteRow]:
    """The note rows of a page source, top to bottom."""
    rows = []
    for el in ET.fromstring(source).iter("XCUIElementTypeImage"):
        a = el.attrib
        parts = (a.get("name") or "").split("\n")
        if len(parts) >= 3 and parts[-1] == "Show menu":
            rows.append(NoteRow(parts[0], "\n".join(parts[1:-1]), int(a["x"]), int(a["y"]),
                                int(a["width"]), int(a["height"])))  # fmt: skip
    return sorted(rows, key=lambda r: r.y)


class NoteMenu(BasePage):
    screen = NOTE_MENU


class NoteEditor(BasePage):
    screen = NOTE_EDITOR

    def text(self) -> str:
        """The field's current text."""
        return self.find("field").get_attribute("value") or ""

    def type_text(self, text: str) -> None:
        with allure.step(f"fill note-editor.field: {text[:40]!r}{'…' if len(text) > 40 else ''}"):
            self.tap("field")
            time.sleep(0.6)  # the field re-renders on focus: type into the focused one
            waits.focused(self.driver).send_keys(text)

    def counter(self) -> str:
        return self.find("counter").get_attribute("name") or ""


class NoteDeleteDialog(BasePage):
    screen = NOTE_DELETE_DIALOG


class NoteUnsavedDialog(BasePage):
    screen = NOTE_UNSAVED_DIALOG


class NotesPage(BasePage):
    screen = NOTES

    def rows(self) -> list[NoteRow]:
        return rows_in(self.driver.page_source)

    def texts(self) -> list[str]:
        return [r.text for r in self.rows()]

    def expect_texts(self, expected: list[str], timeout: float = 10.0) -> None:
        with allure.step(f"expect the notes (newest first): {expected}"):
            end = time.monotonic() + timeout
            while self.texts() != expected and time.monotonic() < end:
                time.sleep(0.5)
            assert self.texts() == expected, f"notes {self.texts()}, expected {expected}"

    def wait_toast_gone(self) -> None:
        self.wait_gone("toast", TOAST)

    def start_add(self) -> NoteEditor:
        """The bottom "Add note" (there are two in the empty state) → "Add note"."""
        with allure.step("tap notes.add-note"):
            self.wait_toast_gone()  # a toast of the last save lies over the screen
            buttons = self.driver.find_elements(*self.locator("add-note"))
            max(buttons, key=lambda b: b.rect["y"]).click()
            editor = NoteEditor(self.driver, self.platform)
            editor.visible("add-title", 10)
            return editor

    def add_note(self, text: str) -> None:
        editor = self.start_add()
        editor.type_text(text)
        editor.tap("save")
        self.assert_open(SAVE_WAIT)
        self.wait_toast_gone()

    def open_menu(self, n: int) -> NoteMenu:
        """Tap the ⋮ of the n-th (0-based) note row."""
        with allure.step(f"tap notes.menu #{n + 1}"):
            self.wait_toast_gone()
            row = self.rows()[n]
            x = row.x + row.width - MENU_X_FROM_RIGHT
            self.driver.execute_script("mobile: tap", {"x": x, "y": row.y + row.height / 2})
            menu = NoteMenu(self.driver, self.platform)
            menu.assert_open(5)
            return menu

    def edit(self, n: int) -> NoteEditor:
        self.open_menu(n).tap("edit")
        editor = NoteEditor(self.driver, self.platform)
        editor.visible("edit-title", 10)
        return editor

    def delete_from_menu(self, n: int, confirm: bool) -> None:
        dialog = NoteDeleteDialog(self.driver, self.platform)
        self.open_menu(n).tap("delete")
        dialog.assert_open(5)
        dialog.tap("delete" if confirm else "cancel")
        dialog.wait_gone("title", 5)
