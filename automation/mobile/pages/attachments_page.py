"""Attachments and the file viewers — behaviour over screens/attachments_map.py (module 04).

Photo thumbnails are not in the tree (TD-ORDD-002): the Photos grid is judged by pixels — two
cells side by side under the tabs, each covered by a picture (ink), not by the small error icon
the app draws when a photo fails to load (recon 5b: ink 0.007 per cell). The PDF page is judged
by the colour block our test PDF carries on its first page (fixtures/media/qa_auto_2_pages.pdf).
"""

import io

import allure

from helpers import pixels, waits
from pages.base_page import BasePage
from screens.attachments_map import ATTACHMENTS, PDF_VIEWER, PHOTO_VIEWER

PAGE_BLOCK_RGB = (120, 42, 42)  # the block on page 1 of the test PDF (#782A2A)
PAGE_BLOCK_SHARE = 0.01  # calibrated 2026-09-24: 0.0001–0.0015 on screens without the page
PHOTO_INK = 0.10  # a loaded thumbnail covers its cell; the error icon covers ~0.7 %
PDF_TIMEOUT = 20.0
PHOTO_TIMEOUT = 20.0


def grid_cells(window_width: int, top: int, columns: int = 2, gap: int = 16) -> list[dict]:
    """Inner boxes (points) of the first row of the Photos grid: ``columns`` cells of aspect
    3:4 (attachments_page.dart) under ``top``, shrunk to their middle 60 % so rounded corners and
    spacing never count."""
    width = (window_width - gap * (columns + 1)) / columns
    height = width * 4 / 3
    cells = []
    for i in range(columns):
        x = gap + i * (width + gap)
        cells.append({"x": x + width * 0.2, "y": top + gap + height * 0.2,
                      "width": width * 0.6, "height": height * 0.6})  # fmt: skip
    return cells


class AttachmentsPage(BasePage):
    screen = ATTACHMENTS

    @property
    def _gap(self) -> int:
        """The grid's spacing: 16 pt on iOS, 42 px on Android (tiles [42,451]–[519,1087] of a
        1080-px screen, recon A1 — the same 3:4 cells)."""
        return 42 if self.platform == "android" else 16

    def selected_tab(self) -> str:
        """'Documents' or 'Photos' — the label of the tab whose traits contain 'Selected'."""
        return self.label_of(self.find("selected-tab")).split("\n")[0]

    def expect_selected_tab(self, label: str, timeout: float | None = None) -> None:
        with allure.step(f"expect the selected tab to be {label!r}"):
            waits.wait_until(
                self.driver,
                lambda _d: self.selected_tab() == label,
                timeout,
                f"selected tab is {self.selected_tab()!r}, expected {label!r}",
            )

    def tab_names(self) -> list[str]:
        """Names of the tabs, left → right: '<label>\nTab N of M' (recon 5b)."""
        tabs = [e for e in self.driver.find_elements(*self.locator("tabs")) if e.is_displayed()]
        return [self.label_of(e) for e in sorted(tabs, key=lambda e: e.rect["x"])]

    def open_tab(self, label: str) -> None:
        self.tap("tab", text=label)
        self.expect_selected_tab(label)

    def cell_inks(self) -> list[float]:
        png = self.driver.get_screenshot_as_png()
        width = self.driver.get_window_size()["width"]
        scale = pixels.Image.open(io.BytesIO(png)).width / width
        tabs = self.find("tab", text="Photos").rect
        top = tabs["y"] + tabs["height"]
        inks = [pixels.ink_ratio(png, box, scale) for box in grid_cells(width, top, gap=self._gap)]
        allure.attach(png, name=f"photos grid (cell ink {[round(i, 3) for i in inks]})",
                      attachment_type=allure.attachment_type.PNG)  # fmt: skip
        return inks

    def expect_thumbnails_drawn(self, count: int = 2, timeout: float = PHOTO_TIMEOUT) -> None:
        """The first ``count`` grid cells each show a picture (not the error icon)."""
        last: list[list[float]] = []

        def drawn(_driver) -> bool:
            last.append(self.cell_inks()[:count])
            return all(ink >= PHOTO_INK for ink in last[-1])

        with allure.step(f"expect {count} photo thumbnails drawn side by side (pixels)"):
            waits.wait_until(self.driver, drawn, timeout, "thumbnails not drawn (cell inks above)")

    def tap_cell(self, index: int) -> None:
        """Tap the ``index``-th (0-based) cell of the first grid row — cells have no element."""
        width = self.driver.get_window_size()["width"]
        tabs = self.find("tab", text="Photos").rect
        box = grid_cells(width, tabs["y"] + tabs["height"], gap=self._gap)[index]
        x, y = round(box["x"] + box["width"] / 2), round(box["y"] + box["height"] / 2)
        with allure.step(f"tap photo cell {index + 1} at ({x}, {y})"):
            self.driver.tap([(x, y)])


class PdfViewerPage(BasePage):
    screen = PDF_VIEWER

    def expect_page_drawn(self, timeout: float = PDF_TIMEOUT) -> None:
        """The first page of the test PDF is on screen: its colour block is drawn."""
        last: list[float] = []

        def drawn(_driver) -> bool:
            png = self.driver.get_screenshot_as_png()
            last.append(pixels.colour_share(png, PAGE_BLOCK_RGB))
            return last[-1] >= PAGE_BLOCK_SHARE

        with allure.step("expect the first PDF page drawn (pixels: its colour block)"):
            try:
                waits.wait_until(self.driver, drawn, timeout, "PDF page not drawn (colour block)")
            finally:
                allure.attach(self.driver.get_screenshot_as_png(),
                              name=f"pdf viewer (block share {last[-1] if last else '-'})",
                              attachment_type=allure.attachment_type.PNG)  # fmt: skip

    def close(self) -> None:
        """Tap X — the right-most unnamed app-bar button (the download icon sits left of it
        once the PDF has loaded; run 1, 2026-09-24)."""
        buttons = self.driver.find_elements(*self.locator("close"))
        assert buttons, "no unnamed app-bar button in the PDF viewer"
        with allure.step(f"tap pdf-viewer.close (right-most of {len(buttons)} unnamed buttons)"):
            max(buttons, key=lambda b: b.rect["x"]).click()

    def expect_read_only(self) -> None:
        with allure.step("expect no editable element in the viewer"):
            count = len(self.driver.find_elements(*self.locator("any-editable")))
            assert count == 0, f"{count} editable element(s) in the PDF viewer"


class PhotoViewerPage(BasePage):
    screen = PHOTO_VIEWER

    def expect_photo_fills_width(self, timeout: float = PHOTO_TIMEOUT) -> None:
        """A picture covers the middle band of the screen, edge to edge (pixels)."""
        last: list[float] = []

        def drawn(_driver) -> bool:
            png = self.driver.get_screenshot_as_png()
            size = self.driver.get_window_size()
            scale = pixels.Image.open(io.BytesIO(png)).width / size["width"]
            band = {"x": 0, "y": size["height"] * 0.4, "width": size["width"],
                    "height": size["height"] * 0.2}  # fmt: skip
            last.append(pixels.ink_ratio(png, band, scale))
            return last[-1] >= PHOTO_INK

        with allure.step("expect the photo drawn across the screen width (pixels)"):
            waits.wait_until(self.driver, drawn, timeout,
                             f"photo not drawn: band ink {last[-1] if last else '-'}")  # fmt: skip
