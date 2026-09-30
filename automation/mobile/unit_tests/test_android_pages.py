"""Offline check of the page objects' Android readers on the recon A1 trees (step 3).

The trees are the app on the emulator (qa/shared/recon-dumps/android-2026-09-29/); every reader
that parses a page source on Android is run on the tree of its screen and must return what the
recon saw. Device behaviour (gestures, timing) is proven by the module runs (step 4).

    cd automation/mobile && uv run python -m unittest unit_tests.test_android_pages -v
"""

import unittest
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from pages.base_page import page_nodes
from pages.jobs_calendar_page import _DAY_CELL
from pages.jobs_list_page import cards_in_tree, cards_on_screen
from pages.link_dialogs_page import _visible_texts
from pages.notes_page import rows_in as note_rows
from pages.notifications_page import rows_in as notification_rows
from pages.photo_report_page import PhotoReportPage
from pages.registration_page import RegistrationPage
from pages.submit_dialog_page import Submission, observe, snackbars
from pages.tabbar_page import TabBarPage

DUMPS = Path(__file__).resolve().parents[3] / "qa/shared/recon-dumps/android-2026-09-29"


def tree(name: str) -> str:
    return (DUMPS / f"{name}.xml").read_text(encoding="utf-8")


class FakeDriver(SimpleNamespace):
    capabilities = {"platformName": "Android"}


class AndroidReaders(unittest.TestCase):
    def test_job_cards(self):
        shown = cards_on_screen(tree("jobs_list"), "android")
        self.assertEqual([c.status for c, _ in shown], ["In progress"] * 3 + ["New"] * 2)
        self.assertTrue(shown[0][0].job_id.endswith("-PHOTO"))
        self.assertEqual(shown[0][0].date, "29 Sep 2026")
        self.assertEqual(len(cards_in_tree(tree("jobs_calendar_after_refresh"), "android")), 5)
        # BUG-ORDL-001 as recon A1 saw it: the calendar held no card before its own refresh
        self.assertEqual(cards_in_tree(tree("jobs_calendar"), "android"), [])

    def test_week_strip(self):
        days = sorted(
            (n.x, n.label.split(",")[0])
            for n in page_nodes(tree("jobs_calendar"), "android")
            if n.visible and _DAY_CELL.match(n.label)
        )
        self.assertEqual([d for _, d in days][:3], ["Sunday", "Monday", "Tuesday"])
        self.assertEqual(len(days), 7)

    def test_tabs(self):
        page = TabBarPage(FakeDriver(page_source=tree("notifications")), "android")
        self.assertEqual(page.selected(), "notifications")
        self.assertEqual(page.notifications_count(), 5)

    def test_phone_mismatch_dialog(self):
        texts, buttons = _visible_texts(tree("phone_mismatch"), "android")
        self.assertEqual(texts[0], "Assigned to a different phone number")
        self.assertEqual(buttons, ["Cancel", "Log out"])

    def test_notes(self):
        rows = note_rows(tree("notes"), "android")
        self.assertEqual([r.text for r in rows], ["QA recon note A1"])
        self.assertEqual(note_rows(tree("notes_empty"), "android"), [])

    def test_notifications(self):
        rows = notification_rows(tree("notifications"), "android")
        self.assertEqual(len(rows), 5)
        closed = [r for r in rows if "CHECKIN" in r.description]
        self.assertEqual([(r.kind, r.chevron) for r in closed], [("Image", False)])
        self.assertTrue(all(r.kind == "Other" and r.chevron for r in rows if r not in closed))

    def test_submission_states(self):
        seen = Submission(tapped_at=datetime.now(UTC))
        for name in ("submitting", "submit_result"):
            observe(tree(name), seen, "android")
        self.assertTrue(seen.submitting_disabled)
        self.assertFalse(seen.submitting_enabled)
        self.assertTrue(seen.retry)
        self.assertEqual(seen.messages, ["Server error. Try again later."])
        self.assertEqual(snackbars(tree("survey_saved_toast"), "android"), ["Survey saved"])
        self.assertEqual(snackbars(tree("job_details_in_progress"), "android"), [])

    def test_photo_grid(self):
        page = PhotoReportPage(FakeDriver(page_source=tree("photo_report")), "android")
        photos = page.photos()
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0]["name"], "QA recon photo A1\nUndamaged")
        self.assertIsNotNone(photos[0]["delete"])
        self.assertEqual(page.descriptions(), ["QA recon photo A1"])

    def test_field_message_reader_skips_controls(self):
        # the phone field holds the country-code Button inside its bounds; only plain text counts
        page = RegistrationPage(FakeDriver(), "android")
        texts = [
            page._text_and_bounds(n)[0]
            for n in ET.fromstring(tree("registration")).iter()
            if page._text_and_bounds(n)[1] is not None
        ]
        self.assertNotIn("United States + 1\n+ 1", texts)
        self.assertNotIn("Log in", texts)
        self.assertIn("Registration", texts)

    def test_null_attribute_is_empty(self):
        # UiAutomator2 answers the string 'null' for a missing attribute of a native view
        class El:
            def get_attribute(self, name):
                return {"text": "Allow [DEV] CT Mobile to access this device’s location?"}.get(
                    name, "null"
                )

        page = RegistrationPage(FakeDriver(), "android")
        self.assertEqual(
            page.label_of(El()), "Allow [DEV] CT Mobile to access this device’s location?"
        )
        self.assertEqual(page.placeholder_of(El()), "")


if __name__ == "__main__":
    unittest.main()
