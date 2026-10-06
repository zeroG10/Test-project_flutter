"""This project's test-data ids: the platform's letter in the run stamp keeps an iOS and an
Android run that seed in the same second apart (PARALLEL-RUNS.md). Project-specific
(fixtures/jobs.py)."""

import re
import unittest
from unittest import mock

from config.settings import settings
from fixtures import jobs


class RunStamp(unittest.TestCase):
    def test_the_platforms_letter_keeps_two_runs_apart_at_the_same_length(self) -> None:
        with mock.patch.object(settings, "run_tag", "I"):
            ios = jobs._run_stamp()
        with mock.patch.object(settings, "run_tag", "A"):
            android = jobs._run_stamp()
        with mock.patch.object(settings, "run_tag", "-"):
            plain = jobs._run_stamp()
        self.assertRegex(ios, r"^\d{4}I\d{6}$")
        self.assertRegex(android, r"^\d{4}A\d{6}$")
        self.assertRegex(plain, r"^\d{4}-\d{6}$")  # the id shape the final runs used
        self.assertEqual(len(ios), len(plain))
        # the offline dialog's reader of job ids (tests/android/test_offline_submit_deliverables.py)
        self.assertTrue(re.fullmatch(r"QA-AUTO-[0-9A-Z-]+", f"QA-AUTO-{ios}-NEW"))


if __name__ == "__main__":
    unittest.main()
