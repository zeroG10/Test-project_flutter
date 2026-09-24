"""Offline checks of the module 08 helpers: question titles from the tree, the saved survey.

cd automation/mobile && uv run python -m unittest discover -s unit_tests -v
"""

import unittest
from pathlib import Path

from helpers import survey_response as sr
from pages.survey_page import titles_in

DUMPS = Path(__file__).resolve().parents[3] / "qa/shared/recon-dumps/ios-2026-09-24"


class SurveyTitles(unittest.TestCase):
    """The visible questions are parsed from the card labels (TD-SRV-001), in number order."""

    def titles(self, dump: str) -> list[str]:
        return titles_in((DUMPS / f"{dump}.xml").read_text(encoding="utf-8"))

    def test_every_question_of_the_form_by_number(self):
        # recon 8, End Survey with "End Survey" = No: all 15, although the radio question sits in
        # its own container and most cards are off screen
        got = self.titles("recon8_end_bottom")
        self.assertEqual(len(got), 15)
        self.assertEqual(got[:2], ["End Survey", "Q1 Enter the work order ID"])
        self.assertEqual(got[8], "Q8 Radio Question")

    def test_hidden_questions_are_not_listed(self):
        # recon 8, Mo5 after "No issue found": row MO5-4 of the logic tables
        self.assertEqual(
            self.titles("recon8_mo5_no_issue"),
            ["What issue type was identified on site?", "Q4 Select the follow-up visit date",
             "Q5 Enter customer-related notes"],
        )  # fmt: skip

    def test_a_loose_card_text_field_label_is_read_too(self):
        # recon 8, Short Survey: the card is one TextField,
        # labelled '1. \nGood?\n2. \nText?\nDescription'
        self.assertEqual(self.titles("recon8_short_empty"), ["Good?", "Text?"])


FIBER = "Fiber installation report long title section name for tests"
RESPONSE = {  # the shape of a saved survey (recon 8, Fiber Site Survey), trimmed
    "items": [
        {"sort": 0, "question": {"id": "q1", "title": "Are there any rooms?",
                                 "type": "singleSelect", "value": [{"id": "a", "data": "No"}]}},
        {"sort": 1, "section": {"id": "s1", "title": FIBER, "questions": [
            {"id": "t1", "title": "Was the job completed successfully?", "type": "toggle",
             "value": [{"id": "y", "data": True}]}]}},
        {"sort": 2, "section": {"id": "s2", "title": f"{FIBER} 2", "questions": [
            {"id": "t2", "title": "Was the job completed successfully?", "type": "toggle",
             "value": [{"id": "n", "data": False}]},
            {"id": "p2", "title": "Room photos", "type": "image", "value": [],
             "files": [{"id": "f", "note": "QA-AUTO room photo", "location": "https://x/y.jpg"}]}]}},
    ]
}  # fmt: skip


class SavedSurvey(unittest.TestCase):
    def test_blocks_are_one_per_entry_in_order(self):
        self.assertEqual(sr.blocks(RESPONSE), [FIBER, f"{FIBER} 2"])

    def test_an_answer_is_found_inside_its_entry(self):
        self.assertEqual(
            sr.answer(RESPONSE, "Was the job completed successfully?", FIBER).values, [True]
        )
        self.assertEqual(
            sr.answer(RESPONSE, "Was the job completed successfully?", f"{FIBER} 2").values, [False]
        )
        self.assertEqual(sr.answer(RESPONSE, "Are there any rooms?").block, None)

    def test_an_ambiguous_title_without_its_entry_fails(self):
        with self.assertRaises(AssertionError):
            sr.answer(RESPONSE, "Was the job completed successfully?")

    def test_photos_are_read_by_their_notes(self):
        self.assertEqual(sr.answer(RESPONSE, "Room photos").notes, ["QA-AUTO room photo"])
