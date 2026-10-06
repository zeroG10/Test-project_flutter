"""Parallel runs (PARALLEL-RUNS.md): what each platform's run uses, and when two may go side by
side. Offline — fresh ``Settings`` objects, no .env, no device, no API."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from config.settings import Settings
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


class Launcher(unittest.TestCase):
    """scripts/qa.py on a made-up project: modules from qa/mobile/<NN>/, tests by platform."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        mobile = root / "automation" / "mobile"
        for folder in ("01-sign-in", "02-item-list", "03-item-details"):
            (root / "qa" / "mobile" / folder).mkdir(parents=True)
        for rel in ("tests/shared/test_sign_in.py", "tests/shared/test_item_list.py",
                    "tests/android/test_offline_sign_in.py", "tests/ios/__init__.py"):  # fmt: skip
            (mobile / rel).parent.mkdir(parents=True, exist_ok=True)
            (mobile / rel).write_text("")
        patches = (
            mock.patch.object(qa, "MOBILE", mobile),
            mock.patch.object(qa, "SHARED", mobile / "tests" / "shared"),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_a_module_by_number_name_or_part(self) -> None:
        self.assertEqual(qa.resolve_module("01"), "sign_in")
        self.assertEqual(qa.resolve_module("sign"), "sign_in")
        self.assertEqual(qa.resolve_module("item-list"), "item_list")
        with self.assertRaises(SystemExit):
            qa.resolve_module("item")  # item_list, item_details

    def test_a_platform_gets_its_own_tests_too(self) -> None:
        self.assertEqual(qa.targets("ios", "all"), ["tests/shared"])  # tests/ios holds no test file
        self.assertEqual(qa.targets("android", "all"), ["tests/shared", "tests/android"])
        self.assertEqual(qa.targets("ios", "sign"), ["tests/shared/test_sign_in.py"])
        self.assertEqual(
            qa.targets("android", "01"),
            ["tests/shared/test_sign_in.py", "tests/android/test_offline_sign_in.py"],
        )
        node = "tests/shared/test_sign_in.py::test_x"
        self.assertEqual(qa.targets("ios", node), [node])
        with self.assertRaises(SystemExit):
            qa.targets("ios", "03")  # a module without a test file


if __name__ == "__main__":
    unittest.main()
