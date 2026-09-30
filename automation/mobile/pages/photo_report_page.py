"""The Photo report — behaviour over screens/photo_report_map.py and screens/survey_photo_map.py
(module 09).

What the tree does not give is resolved here: a photo's delete icon has no name (TD-PHR-001), so the
page pairs every grid photo with the unnamed button inside its top-right corner, in grid order; a
gallery photo is chosen by its grid position in the system picker (TD-SRV-003, as the survey).
"""

import time
import xml.etree.ElementTree as ET

import allure

from helpers import waits
from pages.base_page import BasePage
from screens.photo_report_map import (
    PHOTO_ADD_SHEET,
    PHOTO_DELETE_DIALOG,
    PHOTO_REPORT,
    PHOTO_UNSAVED_DIALOG,
)
from screens.survey_photo_map import PHOTO_EDITOR, PHOTO_METADATA, PHOTO_PICKER

PICKER_WAIT = 10.0  # the system photo picker takes a few seconds to appear (recon 8 / 9)
TOAST = 8.0  # the save toast stays 3 s
SAVE_WAIT = 30.0  # Save uploads the photo before it returns (D-PHR-5)
GRID_MIN_WIDTH = 150  # grid photos are ~189 pt wide; the preview on the metadata page is 156
# Android (px, recon A1): a grid tile is ~509 px wide, its delete icon a 105-px unlabelled
# ImageView at the tile's top right; picker cells are labelled "Photo taken on <date>".
GRID_MIN_WIDTH_ANDROID = 400
DELETE_MAX_WIDTH_ANDROID = 150
PICKER_CELL_PREFIX = "Photo taken on"


class PhotoAddSheet(BasePage):
    screen = PHOTO_ADD_SHEET


class PhotoDeleteDialog(BasePage):
    screen = PHOTO_DELETE_DIALOG


class PhotoUnsavedDialog(BasePage):
    screen = PHOTO_UNSAVED_DIALOG


class PhotoPicker(BasePage):
    screen = PHOTO_PICKER


class PhotoEditor(BasePage):
    screen = PHOTO_EDITOR


class PhotoMetadata(BasePage):
    screen = PHOTO_METADATA

    def is_edit(self, timeout: float | None = None) -> bool:
        return self.is_visible("edit-title", timeout)

    def hide_keyboard(self) -> None:
        """Tap the page's left margin: the page drops the focus on a tap outside the field. (The
        field's label scrolls away under a long description — module 09 run 1.)"""
        height = self.driver.get_window_size()["height"]
        self.tap_xy(6, int(height * 0.3))
        time.sleep(0.5)

    def fill_description(self, text: str) -> None:
        with allure.step(f"fill photo-metadata.description: {text[:40]!r}"):
            self.tap("description")
            time.sleep(0.6)  # the field re-renders on focus: type into the focused one
            waits.focused(self.driver).send_keys(text)
            self.hide_keyboard()

    def description(self) -> str:
        return self.field_value(self.find("description"))

    def counter(self) -> str:
        return self.label_of(self.find("counter"))

    def tap(self, alias: str, timeout: float | None = None, **params: object) -> None:
        # Android: a 500-character description pushes the tags below the screen, and Android
        # shows only on-screen nodes (module 09 Android run 1, TC-PHR-002)
        if alias == "tag" and self.platform == "android":
            self.scroll_to("tag", **params)
        super().tap(alias, timeout, **params)

    def is_tag_selected(self, tag: str) -> bool:
        if self.platform == "android":
            self.scroll_to("tag", text=tag)
        return self.value("tag", text=tag) == "1"

    def expect_tag(self, tag: str, selected: bool = True) -> None:
        state = "selected" if selected else "not selected"
        with allure.step(f"expect photo-metadata.tag[{tag}] {state}"):
            assert self.is_tag_selected(tag) == selected, f"tag {tag!r} is not {state}"


class PhotoReportPage(BasePage):
    screen = PHOTO_REPORT

    def photos(self) -> list[dict]:
        """The grid's photos in grid order (rows, then columns), as page-source attributes, each
        with ``delete``: the rect of its delete icon (TD-PHR-001)."""
        if self.platform == "android":
            return self._photos_android()
        root = ET.fromstring(self.driver.page_source)
        images, buttons = [], []
        for el in root.iter():
            a = el.attrib
            if el.tag == "XCUIElementTypeImage" and int(a.get("width") or 0) > GRID_MIN_WIDTH:
                images.append(dict(a))
            elif (
                el.tag == "XCUIElementTypeButton"
                and not a.get("name")
                and 0 < int(a.get("width") or 0) < 50
            ):
                buttons.append(dict(a))
        images.sort(key=lambda a: (int(a["y"]), int(a["x"])))
        for image in images:
            x, y, w = int(image["x"]), int(image["y"]), int(image["width"])
            image["delete"] = next(
                (
                    b
                    for b in buttons
                    if x + w / 2 < int(b["x"]) < x + w and y <= int(b["y"]) < y + 80
                ),
                None,
            )
        return images

    def _photos_android(self) -> list[dict]:
        """The same shape as on iOS (``name``, ``x``/``y``/``width``/``height``, ``delete``)."""
        nodes = self.nodes()

        def attrs(n) -> dict:
            return {"name": n.label, "x": n.x, "y": n.y, "width": n.width, "height": n.height}

        # a photo without description and tag is an ImageView with NO label (module 09 Android
        # run 1, TC-PHR-003: the first of three photos was not counted) — by size, as on iOS
        tiles = [
            attrs(n)
            for n in nodes
            if n.kind == "ImageView"
            and n.width > GRID_MIN_WIDTH_ANDROID
            and not n.clickable
            and n.label != "Add photo"
        ]
        icons = [
            attrs(n)
            for n in nodes
            if n.kind == "ImageView" and not n.label and 0 < n.width < DELETE_MAX_WIDTH_ANDROID
        ]
        tiles.sort(key=lambda a: (a["y"], a["x"]))
        for t in tiles:
            x, y, w = t["x"], t["y"], t["width"]
            t["delete"] = next(
                (i for i in icons if x + w / 2 < i["x"] < x + w and y <= i["y"] < y + 200), None
            )
        return tiles

    def descriptions(self) -> list[str]:
        """Each grid photo's description (the first line of its name; '' without one)."""
        return [(p.get("name") or "").split("\n")[0] for p in self.photos()]

    def expect_photo_count(self, count: int, timeout: float = 10.0) -> None:
        with allure.step(f"expect {count} photo(s) in the grid"):
            end = time.monotonic() + timeout
            while len(self.photos()) != count and time.monotonic() < end:
                time.sleep(0.5)
            assert len(self.photos()) == count, f"{len(self.photos())} photos in the grid"

    def _tap_rect(self, a: dict) -> None:
        x = int(a["x"]) + int(a["width"]) / 2
        y = int(a["y"]) + int(a["height"]) / 2
        self.tap_xy(x, y)

    def open_photo(self, n: int) -> None:
        """Tap the n-th (0-based) grid photo → "Edit photo"."""
        with allure.step(f"tap photo-report.photo #{n + 1}"):
            self._tap_rect(self.photos()[n])
            PhotoMetadata(self.driver, self.platform).visible("edit-title", 10)

    def tap_delete(self, n: int) -> None:
        """Tap the n-th (0-based) grid photo's delete icon."""
        with allure.step(f"tap photo-report.delete #{n + 1}"):
            icon = self.photos()[n]["delete"]
            assert icon, f"no delete icon on photo #{n + 1}"
            self._tap_rect(icon)

    def delete_photo(self, n: int) -> None:
        """Delete icon → "Delete photo" → Delete."""
        dialog = PhotoDeleteDialog(self.driver, self.platform)
        self.tap_delete(n)
        dialog.visible("title", 5)
        dialog.tap("delete")
        dialog.wait_gone("title", 5)

    def start_add_photo(self) -> None:
        """The bottom "Add photo" (two in the empty state) → the Camera / Gallery sheet."""
        with allure.step("tap photo-report.add-photo"):
            self.wait_gone("toast", TOAST)  # the save toast lies over the button for 3 s
            buttons = self.driver.find_elements(*self.locator("add-photo"))
            bottom = max(buttons, key=lambda b: b.rect["y"])
            bottom.click()
            PhotoAddSheet(self.driver, self.platform).assert_open(10)

    def pick_from_gallery(self, cell: int) -> None:
        """The sheet's Gallery → the system picker's cell ``cell`` (newest first) → the editor."""
        sheet, picker = (
            PhotoAddSheet(self.driver, self.platform),
            PhotoPicker(self.driver, self.platform),
        )
        with allure.step(f"Gallery → photo #{cell} of the gallery"):
            sheet.tap("gallery")
            picker.assert_open(PICKER_WAIT)
            if self.platform == "android":  # Android Photo picker: cells are in the tree
                cells = sorted(
                    (n for n in self.nodes() if n.label.startswith(PICKER_CELL_PREFIX)),
                    key=lambda n: (n.y, n.x),
                )
                assert len(cells) > cell, f"the picker shows {len(cells)} photo(s), need #{cell}"
                c = cells[cell]
                self.tap_xy(c.x + c.width / 2, c.y + c.height / 2)
                PhotoEditor(self.driver, self.platform).assert_open(15)
                return
            grid = picker.visible("grid", 5).rect
            size = grid["width"] / 3
            x = grid["x"] + size * (cell % 3 + 0.5)
            y = grid["y"] + size * (cell // 3 + 0.5)
            self.tap_xy(x, y)
            PhotoEditor(self.driver, self.platform).assert_open(15)

    def add_photo(self, cell: int = 1, description: str = "", tags: tuple[str, ...] = ()) -> None:
        """The whole add flow: sheet → gallery → editor ✓ → metadata → Save → back on the report."""
        editor, meta = (
            PhotoEditor(self.driver, self.platform),
            PhotoMetadata(self.driver, self.platform),
        )
        with allure.step(f"add a photo (cell {cell}): {description!r}, tags {list(tags)}"):
            self.start_add_photo()
            self.pick_from_gallery(cell)
            editor.tap("done")
            meta.assert_open(15)
            if description:
                meta.fill_description(description)
            for tag in tags:
                meta.tap("tag", text=tag)
            meta.tap("save")
            self.assert_open(SAVE_WAIT)
