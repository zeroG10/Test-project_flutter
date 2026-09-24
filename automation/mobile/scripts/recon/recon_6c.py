"""Recon 6c (2026-09-24): module 05 with the app's "allow mock location" switch ON (owner, Q-CHIO-5).

The app rejects every simulator fix as mocked (recon 6 / 6b). With the debug switch
``flutter.mock_location_override_enabled`` (the app's own preference — code and build unchanged)
the rest of the flow can be seen:

  site     — at the job site: confirmation screen → X (job New) → Cancel (job New) → Confirm →
             status + the check-in record on the server
  far      — ~5.5 km away: "You are not at the job site"? → Got it / Cancel (job New)
  double   — at the site: two quick taps on Confirm → status + record (one event?)
  checkout — Submitted job at the site: "Confirm check out" → Cancel (status kept) → Confirm →
             status + the check-out record
  cleanup  — ALWAYS: jobs deleted (404), the switch OFF again, location back at the site

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/recon_6c.py <dumps-dir> <evidence-dir>

Server writes: 4 × POST /job, the app's check-ins / check-out on them, 4 × DELETE /job.
"""

import json
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

from appium import webdriver

from config.capabilities import get_capabilities
from config.settings import settings
from fixtures import test_data
from fixtures.app_state import _landing
from helpers.app import AppControl
from helpers.field_services_api import FieldServicesApi
from pages.login_page import LoginPage
from pages.otp_page import OtpPage
from pages.welcome_page import WelcomePage

DUMPS, EVIDENCE = Path(sys.argv[1]), Path(sys.argv[2])
DUMPS.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
SHORT_SURVEY = "2964b433-b734-4505-a8c5-6fb42c30fc33"
ADDRESS = "QA test site, 350 5th Ave, New York, NY 10118"
LAT, LNG = 40.748440, -73.985664
FAR = (LAT + 0.05, LNG)
RUN = datetime.now().strftime("%m%d-%H%M")
BUNDLE = settings.app_id("ios")
SWITCH = "flutter.mock_location_override_enabled"


def note(step: str, observed: object, ok: bool | None = None) -> None:
    print(f"[{ {True: 'OK ', False: 'NO ', None: '-- '}[ok]}] {step}: {observed}", flush=True)


def rows_of(source: str) -> list[str]:
    rows = []
    for el in ET.fromstring(source).iter():
        a, t = el.attrib, el.tag.replace("XCUIElementType", "")
        if t in ("Application", "Window", "Keyboard", "Key", "AppiumAUT") or a.get("visible") != "true":
            continue
        if t == "Other" and not a.get("name"):
            continue
        rows.append(f"{t} name={a.get('name')!r} traits={a.get('traits')!r} "
                    f"@{a.get('x')},{a.get('y')} {a.get('width')}x{a.get('height')}")  # fmt: skip
    return rows


def dump(driver, name: str) -> list[str]:
    source = driver.page_source
    (DUMPS / f"{name}.xml").write_text(source, encoding="utf-8")
    (EVIDENCE / f"{name}.png").write_bytes(driver.get_screenshot_as_png())
    rows = rows_of(source)
    print(f"---- {name}: {len(rows)} visible elements", flush=True)
    for row in rows:
        print("     " + row, flush=True)
    return rows


def step(title: str, fn) -> None:
    print(f"\n==== {title}", flush=True)
    try:
        fn()
    except Exception as exc:
        note(title, f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}", False)
        traceback.print_exc(limit=3)


def sh(*cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(list(cmd), capture_output=True, text=True, timeout=60)


def udid() -> str:
    for line in sh("xcrun", "simctl", "list", "devices", "booted").stdout.splitlines():
        if "(Booted)" in line and "iPhone" in line:
            return line.split("(")[1].split(")")[0]
    raise RuntimeError("no booted iPhone simulator")


def main() -> None:
    tech = test_data.tech()
    api = FieldServicesApi()
    dev = udid()
    jobs: dict[str, dict] = {}
    drv = None

    def location(where) -> None:
        sh("xcrun", "simctl", "location", dev, "set", f"{where[0]},{where[1]}")
        note("simctl location", where, None)

    def prefs_plist() -> str:
        data = sh("xcrun", "simctl", "get_app_container", dev, BUNDLE, "data").stdout.strip()
        return f"{data}/Library/Preferences/{BUNDLE}"

    def switch(on: bool) -> None:
        plist = prefs_plist()
        sh("xcrun", "simctl", "spawn", dev, "defaults", "write", plist, SWITCH, "-bool", "YES" if on else "NO")
        read = sh("xcrun", "simctl", "spawn", dev, "defaults", "read", plist, SWITCH).stdout.strip()
        note(f"mock-location switch {'ON' if on else 'OFF'}", f"read back: {read!r}", read == ("1" if on else "0"))

    def server(kind: str) -> dict:
        j = api._call("GET", f"/job/{jobs[kind]['id']}").json()
        return {k: j.get(k) for k in ("statusType", "statusInfo", "checkInDate", "checkInTimezone", "userLocation",
                                      "checkOutDate", "checkOutTimezone", "checkOutLocation")}  # fmt: skip

    try:
        user_id = api.technician_user_id(tech.email)
        today = datetime.now().replace(second=0, microsecond=0)
        for kind, status, hour in (("site", "new", 9), ("far", "new", 10), ("double", "new", 11),
                                   ("submitted", "submitted", 12)):  # fmt: skip
            when = today.replace(hour=hour, minute=0)
            iso = when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            body = {"title": f"QA-AUTO recon6c {kind}", "jobId": f"QA-AUTO-R6C-{RUN}-{kind.upper()}",
                    "userId": user_id, "surveyId": SHORT_SURVEY, "statusType": status, "startAt": iso,
                    "scheduleDate": iso, "description": "Recon 6c (module 05).",
                    "location": {"address": ADDRESS, "coordinates": {"latitude": str(LAT), "longitude": str(LNG)}}}  # fmt: skip
            resp = api._call("POST", "/job", json=body)
            note(f"POST /job {kind}", resp.status_code, resp.status_code in (200, 201))
            jobs[kind] = {"id": resp.json()["id"], "jobId": body["jobId"]}

        drv = webdriver.Remote(settings.appium_url, options=get_capabilities("ios"))
        app = AppControl(drv, "ios")
        W = drv.get_window_size()["width"]
        drv.update_settings({"defaultAlertAction": ""})
        app.terminate()
        switch(True)
        location((LAT, LNG))

        def el(pred: str):
            return drv.find_element("-ios predicate string", pred)

        def has(pred: str) -> bool:
            return bool(drv.find_elements("-ios predicate string", pred))

        def button(label: str) -> None:
            el(f"type == 'XCUIElementTypeButton' AND name == '{label}'").click()
            time.sleep(1.5)

        def signed_in() -> None:
            app.launch()
            if _landing(drv, "ios") == "welcome":
                WelcomePage(drv, "ios").open_login()
                LoginPage(drv, "ios").request_code(tech.email)
                OtpPage(drv, "ios").enter_code(tech.otp)
                time.sleep(5)
            note("landing", _landing(drv, "ios"), None)

        def open_job(kind: str) -> None:
            for _ in range(3):
                drv.execute_script("mobile: dragFromToForDuration", {"duration": 0.3, "fromX": W / 2, "fromY": 300,
                                                                     "toX": W / 2, "toY": 720})  # fmt: skip
                time.sleep(3)
                if has(f"name CONTAINS '{jobs[kind]['jobId']}'"):
                    el(f"name CONTAINS '{jobs[kind]['jobId']}'").click()
                    time.sleep(2.5)
                    return
            raise RuntimeError(f"card {kind} not found")

        def start(action: str, label: str, seconds: float = 30) -> str:
            """Tap Check in / Check out; answer the system prompt; return what the app showed."""
            button(action)
            t0 = time.monotonic()
            while time.monotonic() - t0 < seconds:
                drv.update_settings({"respectSystemAlerts": True})
                src = drv.page_source
                if "to use your location" in src:
                    el("type == 'XCUIElementTypeButton' AND name == 'Allow While Using App'").click()
                    drv.update_settings({"respectSystemAlerts": False})
                    note(f"{label}: system prompt answered", round(time.monotonic() - t0, 1), None)
                    time.sleep(1)
                    continue
                drv.update_settings({"respectSystemAlerts": False})
                src = drv.page_source
                for marker in ("Confirm check in", "Confirm check out", "not at the job site", "could not be trusted",
                               "Precise location", "Weak GPS", "Enter location manually", "Location disabled"):  # fmt: skip
                    if marker in src:
                        note(f"{label}: shown after {time.monotonic() - t0:.1f}s", marker, None)
                        dump(drv, f"recon6c_{label}")
                        return marker
                time.sleep(0.7)
            dump(drv, f"recon6c_{label}_timeout")
            return "timeout"

        signed_in()

        def site_pass() -> None:
            open_job("site")
            if start("Check in", "site_1") != "Confirm check in":
                return
            unnamed = drv.find_elements("-ios predicate string",
                                        "type == 'XCUIElementTypeButton' AND (name == nil OR name == '') AND rect.y < 140")
            note("site: unnamed app-bar buttons (X?)", [b.rect for b in unnamed], len(unnamed) == 1)
            unnamed[0].click()
            time.sleep(2)
            note("site: after X — status", server("site")["statusType"], server("site")["statusType"] == "new")
            if start("Check in", "site_2") == "Confirm check in":
                button("Cancel")
                note("site: after Cancel — status", server("site")["statusType"], server("site")["statusType"] == "new")
            if start("Check in", "site_3") == "Confirm check in":
                t_tap = datetime.now(UTC)
                button("Confirm")
                time.sleep(5)
                dump(drv, "recon6c_site_after_confirm")
                note("site: Confirm tapped at (UTC)", t_tap.isoformat(), None)
                note("site: server after Confirm", server("site"), None)

        def far_pass() -> None:
            location(FAR)
            app.terminate()
            signed_in()
            open_job("far")
            shown = start("Check in", "far_1")
            if shown == "not at the job site":
                button("Got it")
                note("far: after Got it — status", server("far")["statusType"], server("far")["statusType"] == "new")
                dump(drv, "recon6c_far_after_got_it")
                if start("Check in", "far_2") == "not at the job site":
                    button("Cancel")
                    note("far: after Cancel — status", server("far")["statusType"], None)
                    dump(drv, "recon6c_far_after_cancel")
            location((LAT, LNG))

        def double_pass() -> None:
            app.terminate()
            signed_in()
            open_job("double")
            if start("Check in", "double") != "Confirm check in":
                return
            rect = el("type == 'XCUIElementTypeButton' AND name == 'Confirm'").rect
            x, y = rect["x"] + rect["width"] // 2, rect["y"] + rect["height"] // 2
            drv.execute_script("mobile: doubleTap", {"x": x, "y": y})
            time.sleep(5)
            dump(drv, "recon6c_double_after")
            note("double: server after a double tap on Confirm", server("double"), None)

        def checkout_pass() -> None:
            app.terminate()
            signed_in()
            open_job("submitted")
            if start("Check out", "co_1") != "Confirm check out":
                return
            button("Cancel")
            note("checkout: after Cancel — status", server("submitted")["statusType"],
                 server("submitted")["statusType"] == "submitted")
            if start("Check out", "co_2") == "Confirm check out":
                t_tap = datetime.now(UTC)
                button("Confirm")
                time.sleep(5)
                dump(drv, "recon6c_co_after_confirm")
                note("checkout: Confirm tapped at (UTC)", t_tap.isoformat(), None)
                note("checkout: server after Confirm", server("submitted"), None)

        for name, fn in (("site", site_pass), ("far", far_pass), ("double", double_pass), ("checkout", checkout_pass)):
            step(name, fn)
    finally:
        print("\n==== cleanup", flush=True)
        for kind, job in jobs.items():
            try:
                api.delete_job(job)
                note(f"deleted job {kind}", "404", True)
            except Exception as exc:
                note(f"delete job {kind}", f"{type(exc).__name__}: {exc}", False)
        try:
            if drv is not None:
                AppControl(drv, "ios").terminate()
            switch(False)
        except Exception as exc:
            note("switch OFF", f"{type(exc).__name__}: {exc}", False)
        sh("xcrun", "simctl", "location", dev, "set", f"{LAT},{LNG}")
        if drv is not None:
            drv.update_settings({"defaultAlertAction": "accept", "respectSystemAlerts": False})
            drv.quit()


if __name__ == "__main__":
    main()
