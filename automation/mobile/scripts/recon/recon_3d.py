"""Recon 3d (2026-09-23): the OTP tree, three never-seen messages, first live harness shakedown.

Not a test — discovery. It drives the app through the step-5 pages and step-4b helpers and
records what the app REALLY shows, so the UNCONFIRMED map entries can be confirmed or fixed.

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/recon_3d.py <dumps-dir> <evidence-dir>

Server calls from the app: one OTP request for the test account, one unregistered-email
check, one registration attempt with the test technician's (registered) phone. No wrong OTP.
Afterwards one read-only API search confirms the registration attempt created nothing.
"""

import base64
import json
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

from appium import webdriver
from selenium.common.exceptions import TimeoutException

from config.capabilities import get_capabilities
from config.settings import settings
from fixtures import test_data
from fixtures.app_state import _landing
from helpers.app import AppControl
from helpers.evidence import IOS_RECORDING
from helpers.field_services_api import FieldServicesApi
from pages.login_page import LoginPage
from pages.otp_page import OtpPage
from pages.registration_page import RegistrationPage
from pages.welcome_page import WelcomePage

DUMPS, EVIDENCE = Path(sys.argv[1]), Path(sys.argv[2])
EVIDENCE.mkdir(parents=True, exist_ok=True)
FINDINGS: list[dict] = []


def note(step: str, observed: object, ok: bool | None = None) -> None:
    FINDINGS.append({"step": step, "observed": observed, "ok": ok})
    mark = {True: "OK ", False: "NO ", None: "-- "}[ok]
    print(f"[{mark}] {step}: {observed}", flush=True)


def visible_elements(driver) -> list[str]:
    rows = []
    for el in ET.fromstring(driver.page_source).iter():
        a = el.attrib
        t = el.tag.replace("XCUIElementType", "")
        if a.get("visible") != "true" or t in ("Application", "Window", "Keyboard", "Key"):
            continue
        name = a.get("name") or ""
        if t == "Other" and not name:
            continue
        rows.append(
            f"{t} name={name!r} value={a.get('value')!r} enabled={a.get('enabled')} "
            f"@{a.get('x')},{a.get('y')} {a.get('width')}x{a.get('height')}"
        )
    return rows


def dump(driver, name: str) -> list[str]:
    (DUMPS / f"{name}.xml").write_text(driver.page_source, encoding="utf-8")
    (EVIDENCE / f"{name}.png").write_bytes(driver.get_screenshot_as_png())
    rows = visible_elements(driver)
    print(f"---- {name}: {len(rows)} visible elements", flush=True)
    for row in rows:
        print("     " + row, flush=True)
    return rows


def step(title: str, fn) -> None:
    print(f"\n==== {title}", flush=True)
    try:
        fn()
    except Exception as exc:  # recon keeps going; the failure is itself a finding
        note(title, f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}", False)
        traceback.print_exc(limit=2)


def main() -> None:
    tech = test_data.tech()
    t0 = time.monotonic()
    drv = webdriver.Remote(settings.appium_url, options=get_capabilities("ios"))
    note("session created (build installed)", f"{time.monotonic() - t0:.1f}s", True)
    app = AppControl(drv, "ios")
    welcome, login, otp = WelcomePage(drv, "ios"), LoginPage(drv, "ios"), OtpPage(drv, "ios")
    reg = RegistrationPage(drv, "ios")
    recording = False
    try:
        try:
            drv.start_recording_screen(**IOS_RECORDING)
            recording = True
            note("screen recording started", "ffmpeg / MJPEG", True)
        except Exception as exc:
            note("screen recording started", f"{type(exc).__name__}: {exc}", False)

        def reset_to_welcome() -> None:
            t = time.monotonic()
            app.clear_data()
            app.launch()
            landed = _landing(drv, "ios")
            note(
                "clearApp → cold start lands on",
                f"{landed} in {time.monotonic() - t:.1f}s",
                landed == "welcome",
            )

        step("A. clearApp → Welcome", reset_to_welcome)

        def format_error() -> None:
            welcome.open_login()
            login.assert_open(15)
            login.type("identifier", "abc@")
            value = login.find("identifier").get_attribute("value")
            note("typed 'abc@' reads back as", repr(value), value == "abc@")
            try:
                login.expect_error("Format is incorrect.", timeout=5)
                note("'Format is incorrect.' while typing", "visible", True)
            except TimeoutException:
                note("'Format is incorrect.' while typing", "not visible within 5s", False)
                login.tap("title")
                try:
                    login.expect_error("Format is incorrect.", timeout=5)
                    note("'Format is incorrect.' after focus loss", "visible", True)
                except TimeoutException:
                    note("'Format is incorrect.' after focus loss", "not visible", False)
            enabled = login.find("continue").is_enabled()
            note("Continue with 'abc@'", "enabled" if enabled else "disabled", not enabled)
            dump(drv, "recon3d_login_format_error")

        step("B. Login: invalid format", format_error)

        def unregistered_email() -> None:
            email = test_data.unregistered_email()
            login.type("identifier", email)
            try:
                login.expect_no_error("Format is incorrect.", timeout=5)
                note("format error cleared after a valid email", "hidden", True)
            except TimeoutException:
                note("format error cleared after a valid email", "still visible", False)
            login.tap("continue")
            expected = "This email is not registered yet. Create an account to get started."
            try:
                login.expect_error(expected, timeout=15)
                note("unregistered email message", repr(expected), True)
            except TimeoutException:
                note("unregistered email message", "expected text not visible within 15s", False)
            rows = dump(drv, "recon3d_login_unregistered_email")
            value = login.find("identifier").get_attribute("value")
            note("identifier value preserved", repr(value), value == email)
            note("texts on screen", [r for r in rows if r.startswith("StaticText")], None)

        step("C. Login: unregistered email", unregistered_email)

        def otp_screen() -> None:
            login.type("identifier", tech.email)
            login.tap("continue")
            otp.assert_open(30)
            note("OTP screen opened", otp.text("title"), True)
            rows = dump(drv, "recon3d_otp")
            note("OTP visible elements", rows, None)
            for alias in ("instruction", "verify", "resend", "error", "code"):
                try:
                    shown = otp.is_visible(alias, 2)
                    present = bool(drv.find_elements(*otp.locator(alias)))
                    note(f"otp.{alias}", f"present={present} visible={shown}", present)
                except Exception as exc:
                    note(f"otp.{alias}", f"{type(exc).__name__}", False)
            try:
                otp.expect_sent_to(tech.email)
                note("otp.destination shows the email", "visible", True)
            except TimeoutException:
                note("otp.destination shows the email", "not found", False)

        step("D. OTP screen", otp_screen)

        def otp_partial_and_countdown() -> None:
            otp.enter_code("123")
            rows = dump(drv, "recon3d_otp_3digits")
            try:
                enabled = otp.find("verify", 3).is_enabled()
                note("Verify with 3 digits", "enabled" if enabled else "disabled", not enabled)
            except TimeoutException:
                note("Verify with 3 digits", "no element named 'Verify'", False)
            try:
                first = otp.countdown_seconds()
                time.sleep(2.5)  # recon only: the countdown must visibly move
                second = otp.countdown_seconds()
                note("countdown moves", f"{first}s → {second}s", second < first)
            except Exception as exc:
                note("countdown read", f"{type(exc).__name__}: {exc}", False)
            note("OTP texts after 3 digits", [r for r in rows if r.startswith("StaticText")], None)

        step("E. OTP: 3 digits, Verify, countdown", otp_partial_and_countdown)

        def back_from_otp() -> None:
            otp.go_back()
            landed = login.is_open(10)
            note("edge swipe back from OTP → Login", "Login" if landed else "not Login", landed)
            if not landed:
                dump(drv, "recon3d_after_back")

        step("F. Back from OTP (edge swipe)", back_from_otp)

        new = test_data.new_user()

        def duplicate_phone() -> None:
            reset_to_welcome()
            welcome.open_sign_up()
            reg.assert_open(15)
            reg.fill_form(new.first_name, new.last_name, tech.phone_national, new.email)
            for field, want in (("first-name", new.first_name), ("email", new.email)):
                got = reg.find(field).get_attribute("value")
                note(f"typed {field} reads back", repr(got), got == want)
            note("phone reads back", repr(reg.find("phone").get_attribute("value")), None)
            note("phone prefix", reg.phone_prefix(), reg.phone_prefix() == "+1")
            reg.choose_channel("email")
            note("selected channel", reg.selected_channel(), reg.selected_channel() == "email")
            reg.scroll_to("continue")
            reg.expect_enabled("continue", timeout=5)
            note("Continue with a valid form", "enabled", True)
            reg.tap("continue")
            expected = (
                "An account with this phone number already exists. Please log in to continue."
            )
            try:
                reg.visible("form-error", 15, text=expected)
                note("duplicate phone message", repr(expected), True)
            except TimeoutException:
                note("duplicate phone message", "expected text not visible within 15s", False)
            rows = dump(drv, "recon3d_registration_duplicate_phone")
            note("texts on screen", [r for r in rows if r.startswith("StaticText")], None)
            note("still on Registration", reg.is_open(2), reg.is_open(2))

        step("G. Registration: already registered phone", duplicate_phone)

        def nothing_created() -> None:
            api = FieldServicesApi()
            found = api.find_technicians_by_email(new.email)
            note("API: user created by the attempt", len(found), not found)
            if found:
                note("API: cleanup", api.full_delete_test_user(new.email), True)
            api.close()

        step("H. API read-back: nothing registered", nothing_created)
        step("I. Leave the app signed out on Welcome", reset_to_welcome)
    finally:
        if recording:
            try:
                video = base64.b64decode(drv.stop_recording_screen())
                (EVIDENCE / "recon3d.mp4").write_bytes(video)
                note("screen video saved", f"{len(video) / 1e6:.1f} MB", len(video) > 0)
            except Exception as exc:
                note("screen video saved", f"{type(exc).__name__}: {exc}", False)
        drv.quit()
        (EVIDENCE / "findings.json").write_text(json.dumps(FINDINGS, indent=1, ensure_ascii=False))


def capture_transient(driver, needle: str, name: str, seconds: float = 8.0) -> list[str]:
    """Poll the tree right after an action; save the first dump that holds ``needle``.

    Pass 1 showed a red banner on video for ~4 s that an exact-text StaticText search never
    matched — this records HOW the banner is exposed (type, name, label, value, bounds).
    """
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        source = driver.page_source
        if needle in source:
            (DUMPS / f"{name}.xml").write_text(source, encoding="utf-8")
            (EVIDENCE / f"{name}.png").write_bytes(driver.get_screenshot_as_png())
            hits = []
            for el in ET.fromstring(source).iter():
                a = el.attrib
                if any(needle in (a.get(k) or "") for k in ("name", "label", "value")):
                    hits.append(
                        f"{el.tag.replace('XCUIElementType', '')} name={a.get('name')!r} "
                        f"label={a.get('label')!r} visible={a.get('visible')} "
                        f"@{a.get('x')},{a.get('y')} {a.get('width')}x{a.get('height')}"
                    )
            return hits
    return []


def pass2() -> None:
    """Re-run what pass 1 could not observe: login format errors, the two banners."""
    tech = test_data.tech()
    drv = webdriver.Remote(settings.appium_url, options=get_capabilities("ios"))
    app = AppControl(drv, "ios")
    welcome, login, reg = (
        WelcomePage(drv, "ios"),
        LoginPage(drv, "ios"),
        RegistrationPage(drv, "ios"),
    )
    try:
        app.clear_data()
        app.launch()
        note("landing", _landing(drv, "ios"), None)

        def formats() -> None:
            welcome.open_login()
            login.assert_open(15)
            for value in ("12ab", "abc", "abc@x", "+1abc", "a b@c.com"):
                login.type("identifier", value)
                time.sleep(1.5)  # recon only: give an on-typing validator time to render
                texts = login.texts_within("identifier")
                enabled = login.find("continue").is_enabled()
                note(f"login {value!r}", f"texts in field={texts} continue_enabled={enabled}", None)
            dump(drv, "recon3d_login_formats")

        if "only-registration" not in sys.argv:
            step("B2. Login: more invalid formats (no server call)", formats)

        def unregistered_banner() -> None:
            login.type("identifier", test_data.unregistered_email())
            login.tap("continue")
            hits = capture_transient(drv, "not registered yet", "recon3d_login_unregistered_banner")
            note(
                "unregistered-email banner in the tree", hits or "never in page source", bool(hits)
            )

        if "only-registration" not in sys.argv:
            step("C2. Login: unregistered email banner", unregistered_banner)

        new = test_data.new_user()

        def duplicate_phone() -> None:
            app.clear_data()
            app.launch()
            note("landing before Registration", _landing(drv, "ios"), None)
            welcome.open_sign_up()
            reg.assert_open(15)
            reg.fill_form(new.first_name, new.last_name, tech.phone_national, new.email)
            for field, want in (
                ("first-name", new.first_name),
                ("last-name", new.last_name),
                ("email", new.email),
            ):
                got = reg.find(field).get_attribute("value")
                note(f"typed {field} reads back", repr(got), got == want)
            note("phone reads back", repr(reg.find("phone").get_attribute("value")), None)
            note("phone prefix", reg.phone_prefix(), reg.phone_prefix() == "+1")
            reg.choose_channel("email")
            note("selected channel", reg.selected_channel(), reg.selected_channel() == "email")
            note("SMS consent block after Email", reg.is_visible("sms-consent-label", 1), None)
            reg.scroll_to("continue")
            reg.expect_enabled("continue", timeout=5)
            note("Continue with a valid form", "enabled", True)
            dump(drv, "recon3d_registration_filled")
            reg.tap("continue")
            hits = capture_transient(drv, "already exists", "recon3d_registration_duplicate_phone")
            note("duplicate-phone message in the tree", hits or "never in page source", bool(hits))
            time.sleep(5)  # recon only: let a banner go, see where the form is left
            rows = dump(drv, "recon3d_registration_after_duplicate")
            note("still on Registration", reg.is_open(2), None)
            value = reg.find("phone").get_attribute("value")
            note("phone value preserved", repr(value), None)
            note("texts after", [r for r in rows if r.startswith("StaticText")], None)

        step("G2. Registration: already registered phone", duplicate_phone)

        def nothing_created() -> None:
            api = FieldServicesApi()
            found = api.find_technicians_by_email(new.email)
            note("API: user created by the attempt", len(found), not found)
            if found:
                note("API: cleanup", api.full_delete_test_user(new.email), True)
            api.close()

        step("H2. API read-back: nothing registered", nothing_created)
        app.clear_data()
        app.launch()
        note("left on", _landing(drv, "ios"), None)
    finally:
        drv.quit()
        (EVIDENCE / "findings_pass2.json").write_text(
            json.dumps(FINDINGS, indent=1, ensure_ascii=False)
        )


if __name__ == "__main__":
    pass2() if "pass2" in sys.argv[3:] else main()
