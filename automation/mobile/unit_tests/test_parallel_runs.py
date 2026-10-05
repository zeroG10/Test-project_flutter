"""Parallel runs (PARALLEL-RUNS.md): what each platform's run uses, and when two may go side by
side. Offline — fresh ``Settings`` objects, no .env, no device, no API."""

import re
import unittest
from unittest import mock

from config.settings import Settings, settings
from fixtures import jobs
from scripts import qa


def make(**values) -> Settings:
    return Settings(_env_file=None, **values)


SHARED = {
    "app_user_email": "one@example.com",
    "app_user_phone": "+12025550101",
    "app_user_otp": "0000",
}


class AccountPerPlatform(unittest.TestCase):
    def test_one_account_means_one_run_at_a_time(self) -> None:
        s = make(**SHARED)
        self.assertEqual(s.account("ios"), s.account("android"))
        ok, why = s.can_run_in_parallel()
        self.assertFalse(ok)
        self.assertIn("ONE test account", why)

    def test_a_second_account_alone_is_not_enough(self) -> None:
        s = make(**SHARED, ios_user_email="two@example.com", ios_user_phone="+12025550102")
        ok, why = s.can_run_in_parallel()
        self.assertFalse(ok)
        self.assertIn("ONE Appium server", why)

    def test_own_account_and_own_server_run_side_by_side(self) -> None:
        s = make(**SHARED, ios_user_email="two@example.com", ios_user_phone="+12025550102",
                 ios_appium_port=4723, android_appium_port=4724)  # fmt: skip
        self.assertEqual(s.can_run_in_parallel(), (True, ""))
        self.assertEqual(
            s.account("ios"), ("two@example.com", "+12025550102", "0000")
        )  # the OTP is shared
        self.assertEqual(s.account("android")[0], "one@example.com")
        self.assertNotEqual(s.account_key("ios"), s.account_key("android"))
        self.assertNotIn("two@", s.account_key("ios"))  # a fingerprint, never the address
        self.assertEqual(len(s.accounts()), 2)  # what a shared report must hide

    def test_apply_platform_makes_the_process_that_platforms_run(self) -> None:
        s = make(**SHARED, ios_user_email="two@example.com", ios_user_phone="+12025550102",
                 ios_appium_port=4723, android_appium_port=4724)  # fmt: skip
        s.apply_platform("android")
        self.assertEqual(
            (s.app_user_email, s.appium_url, s.run_tag),
            ("one@example.com", "http://127.0.0.1:4724", "A"),
        )
        s.apply_platform("ios")
        self.assertEqual(
            (s.app_user_email, s.appium_url, s.run_tag),
            ("two@example.com", "http://127.0.0.1:4723", "I"),
        )

    def test_no_account_blocks_parallel(self) -> None:
        self.assertEqual(make().can_run_in_parallel()[0], False)


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


class Launcher(unittest.TestCase):
    def test_a_module_by_number_name_or_part(self) -> None:
        self.assertEqual(qa.resolve_module("02"), "authentication")
        self.assertEqual(qa.resolve_module("auth"), "authentication")
        self.assertEqual(qa.resolve_module("order-list"), "order_list")
        with self.assertRaises(SystemExit):
            qa.resolve_module("order")  # order_list, order_details, order_progress

    def test_android_gets_its_own_tests_too(self) -> None:
        self.assertEqual(qa.targets("ios", "all"), ["tests/shared"])
        self.assertEqual(qa.targets("android", "all"), ["tests/shared", "tests/android"])
        self.assertEqual(qa.targets("ios", "auth"), ["tests/shared/test_authentication.py"])
        self.assertEqual(
            qa.targets("android", "auth"),
            ["tests/shared/test_authentication.py", "tests/android/test_offline_authentication.py"],
        )
        node = "tests/shared/test_splash.py::test_x"
        self.assertEqual(qa.targets("ios", node), [node])


if __name__ == "__main__":
    unittest.main()
