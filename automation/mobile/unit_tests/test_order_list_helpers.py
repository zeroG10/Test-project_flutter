"""Offline checks of the module 01 / 03 helpers: card parsing, pixel oracles, seed dates.

cd automation/mobile && uv run python -m unittest discover -s unit_tests -v
"""

import io
import unittest
from datetime import date
from unittest import mock

from PIL import Image

from fixtures.jobs import plan_days, week_of
from helpers import pixels
from pages.jobs_calendar_page import day_cell_name, day_title
from pages.jobs_list_page import (
    UPDATED_RGB,
    UPDATED_SHARE,
    JobsViewMixin,
    cards_on_screen,
    is_card,
    parse_card,
)
from pages.link_dialogs_page import DialogMissed, PhoneMismatchDialog

CARD = (
    "24 Sep 2026\n09:00\nNew\nQA-AUTO-R4-0924-0909-NEW - QA-AUTO recon4 new\n"
    "QA test site, 350 5th Ave, New York, NY 10118"
)  # verbatim from recon 4


def png(size: tuple[int, int], fill: tuple[int, int, int], box=None, box_fill=(255, 255, 255)):
    image = Image.new("RGB", size, fill)
    if box:
        image.paste(Image.new("RGB", (box[2], box[3]), box_fill), (box[0], box[1]))
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


class Cards(unittest.TestCase):
    def test_parse_a_recon_card(self):
        card = parse_card(CARD)
        self.assertFalse(card.updated)
        self.assertEqual((card.date, card.time, card.status), ("24 Sep 2026", "09:00", "New"))
        self.assertEqual(card.job_id, "QA-AUTO-R4-0924-0909-NEW")
        self.assertEqual(card.address, "QA test site, 350 5th Ave, New York, NY 10118")

    def test_updated_banner(self):
        card = parse_card("Updated\n" + CARD)
        self.assertTrue(card.updated)
        self.assertEqual(card.status, "New")

    def test_not_a_card(self):
        self.assertFalse(is_card("Jobs list"))
        self.assertFalse(is_card("Thursday, September 24, 2026"))
        with self.assertRaises(ValueError):
            parse_card("24 Sep 2026\n09:00")

    def test_cards_from_page_source(self):
        source = (
            "<AppiumAUT>"
            f'<XCUIElementTypeImage name="Updated&#10;{CARD.replace(chr(10), "&#10;")}" '
            'visible="true" y="300"/>'
            f'<XCUIElementTypeStaticText name="{CARD.replace(chr(10), "&#10;")}" '
            'visible="true" y="118"/>'
            '<XCUIElementTypeStaticText name="No jobs" visible="true" y="400"/>'
            "</AppiumAUT>"
        )
        found = cards_on_screen(source)
        self.assertEqual([c.updated for c, _ in found], [False, True])  # sorted by y

    def test_hidden_cards_never_make_an_empty_scan(self):
        # TD-JOBS-003: every card in the tree but reported visible=false
        hidden = (
            "<AppiumAUT>"
            f'<XCUIElementTypeStaticText name="{CARD.replace(chr(10), "&#10;")}" '
            'visible="false" y="118"/>'
            "</AppiumAUT>"
        )

        class Frozen(JobsViewMixin):
            driver = mock.Mock(page_source=hidden, get_window_size=lambda: {"height": 874})
            wait_content = _drag_at = lambda *_a, **_k: None

        self.assertEqual(cards_on_screen(hidden), [])
        with self.assertRaisesRegex(AssertionError, "cannot decide"):
            Frozen().all_cards()


class Pixels(unittest.TestCase):
    BRAND = pixels.hex_to_rgb("#782A2A")

    def test_hex(self):
        self.assertEqual(self.BRAND, (120, 42, 42))
        with self.assertRaises(ValueError):
            pixels.hex_to_rgb("#782A2A «prove-red: deliberately wrong»")

    def test_brand_share_and_centred_logo(self):
        frame = png((402, 874), self.BRAND, box=(151, 387, 100, 100))
        self.assertGreater(pixels.colour_share(frame, self.BRAND), 0.95)
        dx, dy = pixels.light_blob_offset(frame, 402)
        self.assertLess(abs(dx), 0.02)
        self.assertLess(abs(dy), 0.02)

    def test_off_centre_logo_and_no_logo(self):
        frame = png((402, 874), self.BRAND, box=(20, 387, 100, 100))
        dx, _ = pixels.light_blob_offset(frame, 402)
        self.assertLess(dx, -0.2)
        self.assertIsNone(pixels.light_blob_offset(png((402, 874), self.BRAND), 402))

    def test_welcome_is_not_the_splash(self):
        welcome = png((402, 874), (248, 248, 250))
        self.assertLess(pixels.colour_share(welcome, self.BRAND), 0.1)

    def test_updated_banner_fill(self):
        # a list with one banner (370 x 27 pt, ~2.8 % of the screen) vs the brand-coloured tab
        # indicator and the red notification dot, which must not count as a banner
        white = (248, 248, 250)
        banner = png((402, 874), white, box=(16, 126, 370, 27), box_fill=UPDATED_RGB)
        self.assertGreater(pixels.colour_share(banner, UPDATED_RGB), UPDATED_SHARE)
        tab = png((402, 874), white, box=(40, 750, 60, 4), box_fill=self.BRAND)
        dot = png((402, 874), white, box=(200, 760, 10, 10), box_fill=(0xEB, 0x01, 0x01))
        for frame in (tab, dot):
            self.assertLess(pixels.colour_share(frame, UPDATED_RGB), UPDATED_SHARE)


class SeedDays(unittest.TestCase):
    def test_week_is_sunday_to_saturday(self):
        week = week_of(date(2026, 9, 24))  # a Thursday
        self.assertEqual(week[0], date(2026, 9, 20))
        self.assertEqual(week[-1], date(2026, 9, 26))

    def test_days_for_every_weekday(self):
        for offset in range(7):
            today = date(2026, 9, 20 + offset)  # Sunday … Saturday
            other, yesterday, empty = plan_days(today)
            week = week_of(today)
            self.assertIn(other, week)
            self.assertNotEqual(other, today)
            self.assertIn(empty, week)
            self.assertNotIn(empty, (today, other, yesterday))

    def test_calendar_names(self):
        self.assertEqual(day_cell_name(date(2026, 9, 24)), "Thursday, September 24, 2026")
        self.assertEqual(day_title(date(2026, 9, 24)), "Thursday, 24 September")


class MismatchDialogRead(unittest.TestCase):
    TITLE = (
        '<XCUIElementTypeStaticText name="Assigned to a different phone number" visible="true"/>'
    )
    REST = (
        '<XCUIElementTypeStaticText name="The jobs you are trying to access…" visible="true"/>'
        '<XCUIElementTypeButton name="Cancel" visible="true"/>'
        '<XCUIElementTypeButton name="Log out" visible="true"/>'
    )

    def _dialog(self, *sources: str) -> PhoneMismatchDialog:
        driver = mock.Mock()
        type(driver).page_source = mock.PropertyMock(side_effect=list(sources))
        return PhoneMismatchDialog(driver, "ios")

    def test_reads_add_up_while_the_dialog_builds(self):
        # run 3: the first read that held the dialog had its title only
        dialog = self._dialog(
            "<AppiumAUT/>",
            f"<AppiumAUT>{self.TITLE}</AppiumAUT>",
            f"<AppiumAUT>{self.TITLE}{self.REST}</AppiumAUT>",
        )
        seen = dialog.snapshot(timeout=5)
        self.assertEqual(seen["buttons"], ["Cancel", "Log out"])
        self.assertEqual(len(seen["texts"]), 2)

    def test_closed_after_a_partial_read_is_missed_not_passed(self):
        dialog = self._dialog(f"<AppiumAUT>{self.TITLE}</AppiumAUT>", "<AppiumAUT/>")
        with self.assertRaises(DialogMissed):
            dialog.snapshot(timeout=5)


if __name__ == "__main__":
    unittest.main()
