"""Offline self-test of the harness helpers — no device, no Appium, no network.

    cd automation/mobile && uv run python -m unittest discover -s unit_tests -v

unittest on purpose (as in automation/api/unit_tests): pytest would load conftest.py,
which wants a platform and a device.
"""

import base64
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from selenium.common.exceptions import TimeoutException

from config.settings import settings
from fixtures import test_data
from helpers import evidence, reporting
from helpers.app import AppControl
from helpers.field_services_api import ApiBlocked, FieldServicesApi, safe_body
from helpers.waits import wait_any


class FakeDriver:
    """Records calls; stands in for an Appium WebDriver."""

    def __init__(self, fail_recording: bool = False):
        self.calls: list[tuple] = []
        self.fail_recording = fail_recording

    def execute_script(self, script, args):
        self.calls.append(("execute_script", script, args))

    def start_recording_screen(self, **options):
        if self.fail_recording:
            raise RuntimeError("ffmpeg missing")
        self.calls.append(("start_recording_screen", options))

    def stop_recording_screen(self):
        self.calls.append(("stop_recording_screen",))
        return base64.b64encode(b"mp4-bytes").decode()

    def get_screenshot_as_png(self):
        return b"png"


class TestData(unittest.TestCase):
    def test_new_user_is_valid_for_the_registration_form(self):
        user = test_data.new_user()
        for name in (user.first_name, user.last_name):
            self.assertTrue(name.isalpha(), name)  # "Has invalid characters." otherwise
            self.assertTrue(2 <= len(name) <= 100, name)
        self.assertRegex(user.email, test_data.TEST_EMAIL_RE)
        self.assertRegex(user.phone_national, r"^20255501\d\d$")  # fictional NANP block
        self.assertEqual(user.phone, "+1" + user.phone_national)

    def test_generated_values_are_unique(self):
        emails = {test_data.new_user().email for _ in range(200)}  # same second, mostly
        self.assertEqual(len(emails), 200)

    def test_unregistered_values_are_test_owned_and_e164(self):
        self.assertRegex(test_data.unregistered_email(), test_data.TEST_EMAIL_RE)
        self.assertRegex(test_data.unregistered_phone(), r"^\+120255501\d\d$")

    def test_wrong_otp_never_equals_the_real_code(self):
        for real in ("0000", "1234", "1111"):
            wrong = test_data.wrong_otp(real)
            self.assertNotEqual(wrong, real)
            self.assertRegex(wrong, r"^\d{4}$")

    def test_tech_formats(self):
        with (
            mock.patch.object(settings, "app_user_email", "t@example.com"),
            mock.patch.object(settings, "app_user_phone", "+12025550188"),
            mock.patch.object(settings, "app_user_otp", "4321"),
        ):
            tech = test_data.tech()
        self.assertEqual(tech.phone_national, "2025550188")
        self.assertEqual(tech.phone_last4, "0188")

    def test_missing_tech_is_blocked(self):
        with (
            mock.patch.object(settings, "app_user_otp", ""),
            self.assertRaisesRegex(LookupError, r"^Blocked: .*APP_USER_OTP"),
        ):
            test_data.tech()


class Reporting(unittest.TestCase):
    def test_module_label_from_feature_code_and_folder(self):
        self.assertEqual(reporting.module_for(["CHK-AUTH-001"]), "02 · Authentication")
        self.assertEqual(reporting.module_for(("CHK-SRV-010",)), "08 · Survey")
        self.assertEqual(reporting.module_for(["CHK-ORDL-003"]), "03 · Order list")
        self.assertEqual(reporting.module_for([]), reporting.UNMAPPED_MODULE)
        self.assertEqual(reporting.module_for(["CHK-ZZZ-001"]), reporting.UNMAPPED_MODULE)

    def test_every_registered_mobile_module_has_a_label(self):
        self.assertEqual(len(reporting.module_labels()), 12)

    def test_run_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            reporting.write_allure_run_files(Path(tmp), "ios")
            props = (Path(tmp) / "environment.properties").read_text(encoding="utf-8")
            self.assertIn("Platform=iOS", props)
            self.assertIn("Harness.commit=", props)
            categories = json.loads((Path(tmp) / "categories.json").read_text(encoding="utf-8"))
            self.assertTrue(categories[0]["name"].startswith("Blocked"))

    def test_env_label_names_platform_device_and_build(self):
        label = reporting.env_label("ios")
        self.assertTrue(label.startswith("iOS · "), label)
        self.assertIn("build ", label)


class Api(unittest.TestCase):
    def _api(self) -> FieldServicesApi:
        with (
            mock.patch.object(settings, "api_base_url", "https://api.invalid/"),
            mock.patch.object(settings, "api_admin_email", "admin@example.com"),
            mock.patch.object(settings, "api_admin_password", "x" * 12),
        ):
            api = FieldServicesApi()
        api._signed_in = True  # no sign-in call in these tests
        return api

    @staticmethod
    def _resp(status: int, payload: dict | None = None):
        resp = mock.Mock(status_code=status, text=json.dumps(payload or {}))
        resp.json.return_value = payload or {}
        return resp

    def test_unconfigured_api_is_blocked(self):
        with (
            mock.patch.object(settings, "api_base_url", ""),
            self.assertRaisesRegex(ApiBlocked, r"^Blocked: API_BASE_URL"),
        ):
            FieldServicesApi()

    def test_refuses_to_delete_a_non_test_user_before_any_request(self):
        api = self._api()
        with mock.patch.object(api._http, "request") as request:
            for email in ("tech@concerttech.com", "qa-auto+x@gmail.com", "qa-auto@example.com"):
                with self.assertRaises(ValueError):
                    api.full_delete_test_user(email)
            request.assert_not_called()

    def test_deletes_only_the_exact_email_and_verifies(self):
        api = self._api()
        email = "qa-auto+20260923120000ab@example.com"
        found = {
            "data": [
                {"user": {"id": "u-1", "email": email}},
                {"user": {"id": "u-2", "email": "qa-auto+20260923120000ab@example.com.other"}},
            ]
        }
        responses = [self._resp(200, found), self._resp(200), self._resp(200, {"data": []})]
        with mock.patch.object(api._http, "request", side_effect=responses) as request:
            self.assertEqual(api.full_delete_test_user(email), ["u-1"])
        methods = [(c.args[0], c.args[1].split("invalid")[1]) for c in request.call_args_list]
        self.assertEqual(
            methods,
            [("GET", "/technician"), ("DELETE", "/user/full-delete/u-1"), ("GET", "/technician")],
        )

    def test_failed_delete_names_the_user_for_recovery(self):
        api = self._api()
        email = "qa-auto+20260923120000cd@example.com"
        found = {"data": [{"user": {"id": "u-9", "email": email}}]}
        responses = [self._resp(200, found), self._resp(500)]
        with (
            mock.patch.object(api._http, "request", side_effect=responses),
            self.assertRaisesRegex(ApiBlocked, "u-9"),
        ):
            api.full_delete_test_user(email)

    def test_nothing_registered_means_nothing_deleted(self):
        api = self._api()
        with mock.patch.object(api._http, "request", return_value=self._resp(200, {"data": []})):
            self.assertEqual(api.full_delete_test_user("qa-auto+1a@example.com"), [])

    def test_report_body_masks_personal_data_and_tokens(self):
        body = json.dumps({
            "user": {"id": "u-1", "email": "tech@example.com", "phone": "+12025550100",
                     "firstName": "Ann", "lastName": "Lee"},
            "access": {"token": "abc.def"}, "refreshToken": "r-1", "isViewed": True,
        })  # fmt: skip
        safe = safe_body(body)
        for secret in ("tech@example.com", "+12025550100", "Ann", "Lee", "abc.def", "r-1"):
            self.assertNotIn(secret, safe)
        self.assertIn('"id": "u-1"', safe)
        self.assertIn('"isViewed": true', safe)


class AppAndEvidence(unittest.TestCase):
    def test_clear_data_uses_the_platform_parameter(self):
        # Android: mobile: clearApp. iOS: a reinstall — clearApp there deletes the container's
        # metadata and iOS later resets the container (final runs 1–2, 2026-09-27).
        drv = FakeDriver()
        AppControl(drv, "android").clear_data()
        self.assertEqual(drv.calls, [("execute_script", "mobile: clearApp", {"appId": mock.ANY})])
        drv = FakeDriver()
        with (
            mock.patch.object(AppControl, "reinstall") as reinstall,
            mock.patch.object(AppControl, "_first_launch") as first_launch,
        ):
            AppControl(drv, "ios").clear_data()
        reinstall.assert_called_once_with()
        first_launch.assert_called_once_with()  # the notification prompt is answered once
        self.assertNotIn("mobile: clearApp", [c[1] for c in drv.calls if len(c) > 1])

    def test_recorder_that_cannot_start_does_not_fail_the_test(self):
        drv = FakeDriver(fail_recording=True)
        rec = evidence.ScreenRecorder(drv, "ios")
        rec.start()
        rec.stop(keep=True)
        self.assertEqual(drv.calls, [])

    def test_video_kept_only_when_asked(self):
        for keep in (True, False):
            drv = FakeDriver()
            rec = evidence.ScreenRecorder(drv, "ios")
            rec.start()
            with mock.patch.object(evidence.allure, "attach") as attach:
                rec.stop(keep=keep)
            self.assertIn(("stop_recording_screen",), drv.calls)  # always stopped
            self.assertEqual(attach.called, keep)
            if keep:
                self.assertEqual(attach.call_args.args[0], b"mp4-bytes")

    def test_ios_video_is_browser_playable(self):
        self.assertEqual(evidence.IOS_RECORDING["videoType"], "libx264")
        self.assertEqual(evidence.IOS_RECORDING["pixelFormat"], "yuv420p")

    def test_checkpoints_are_numbered_in_order(self):
        ev = evidence.Evidence(FakeDriver())
        with mock.patch.object(evidence.allure, "attach") as attach:
            ev.checkpoint("welcome")
            ev.checkpoint("otp-screen")
        names = [c.kwargs["name"] for c in attach.call_args_list]
        self.assertEqual(names, ["01 · welcome", "02 · otp-screen"])


class WaitAny(unittest.TestCase):
    def test_returns_the_first_true_probe(self):
        self.assertEqual(
            wait_any(object(), {"welcome": lambda: False, "jobs-list": lambda: True}, 1),
            "jobs-list",
        )

    def test_times_out_when_nothing_shows(self):
        with self.assertRaises(TimeoutException):
            wait_any(object(), {"welcome": lambda: False}, 0.3)


class PixelOracle(unittest.TestCase):
    """helpers/pixels.py — the oracle for elements the tree reports visible but does not draw."""

    @staticmethod
    def _png(draw_text: bool) -> bytes:
        import io

        from PIL import Image, ImageDraw

        image = Image.new("RGB", (300, 120), (247, 247, 249))  # the app's light background
        if draw_text:
            ImageDraw.Draw(image).text((20, 50), "Incorrect code.", fill=(200, 30, 30))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_blank_box_has_no_ink(self):
        from helpers import pixels

        box = {"x": 5, "y": 15, "width": 40, "height": 8}  # points, scale 3 → 120×24 px
        self.assertEqual(pixels.ink_ratio(self._png(False), box, 3), 0.0)

    def test_drawn_text_is_ink(self):
        from helpers import pixels

        box = {"x": 5, "y": 15, "width": 40, "height": 8}
        ratio = pixels.ink_ratio(self._png(True), box, 3)
        self.assertGreater(ratio, pixels.MIN_INK_RATIO)


class Markers(unittest.TestCase):
    def test_tc_and_chk_patterns_match_the_contract(self):
        import conftest  # noqa: PLC0415 — only for its compiled patterns

        self.assertRegex("TC-AUTH-005", conftest.TC_ID)
        self.assertIsNone(conftest.TC_ID.match("TC-auth-5"))
        self.assertRegex("CHK-AUTH-001", conftest.CHK_ID)
        self.assertIsNone(re.match(conftest.CHK_ID, "CHK-AUTH-1"))


if __name__ == "__main__":
    unittest.main()
