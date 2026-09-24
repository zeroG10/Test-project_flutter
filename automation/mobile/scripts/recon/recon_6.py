"""Recon 6 / 6b (2026-09-24): module 05 Check-in / Check-out — what the app REALLY does.

Not a test — discovery before the test cases of module 05 (owner's go 2026-09-24, Q-CHIO-1).
One Appium session, one process; every check-in / check-out happens through the UI on OUR jobs:

  seed     — 5 jobs through the API: new_gps, new_far, new_manual (New), in_progress, submitted
  gps      — location AT the job site, first check-in: system prompt → Allow While Using App → what
             the app does with the simulator's fix (mocked → "Location could not be trusted"?)
  far      — location ~5.5 km away → "You are not at the job site"? (only if the fix is accepted)
  manual   — NO location → after the app's 15 s timeout "Enter location manually" → confirmation
             screen: X, then Cancel (job stays New), then Confirm → record on the server
  statuses — in_progress job: which actions the details offer
  checkout — submitted job, no location → manual → "Confirm check out": Cancel, then Confirm →
             status and record on the server
  cleanup  — ALWAYS: jobs deleted (404 verified); the simulator's location back at the job site

6b: RECON6_KINDS=new_manual,submitted RECON6_STALE_WAIT=75 … manual checkout — recon 6 showed the
last simulated fix still delivered right after `location clear` (the app keeps fixes ≤ 60 s old).

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/recon_6.py <dumps-dir> <evidence-dir> [pass ...]

Server writes: 5 × POST /job, the app's own check-in / check-out on those jobs, 5 × DELETE /job.
"""

import json
import os
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
PASSES = sys.argv[3:] or ["seed", "gps", "far", "manual", "statuses", "checkout"]
KINDS = os.environ.get("RECON6_KINDS", "new_gps,new_far,new_manual,in_progress,submitted").split(",")
STALE_WAIT = int(os.environ.get("RECON6_STALE_WAIT", "0"))  # 6b: seconds after `location clear`
DUMPS.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
STATE_FILE = EVIDENCE / "state.json"
SHORT_SURVEY = "2964b433-b734-4505-a8c5-6fb42c30fc33"
ADDRESS = "QA test site, 350 5th Ave, New York, NY 10118"
LAT, LNG = 40.748440, -73.985664
FAR = (LAT + 0.05, LNG)  # ~5.5 km north
RUN = datetime.now().strftime("%m%d-%H%M")
BUNDLE = settings.app_id("ios")
FINDINGS: list[dict] = []
KEYS = ("ocation", "GPS", "site", "trusted", "Precise", "manually", "Checking", "Got it", "Enable",
        "Allow", "Confirm", "Check in", "Check out", "Cancel", "signal")  # fmt: skip


def note(step: str, observed: object, ok: bool | None = None) -> None:
    FINDINGS.append({"step": step, "observed": observed, "ok": ok})
    print(f"[{ {True: 'OK ', False: 'NO ', None: '-- '}[ok]}] {step}: {observed}", flush=True)


def load_state() -> dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"jobs": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=1))


def rows_of(source: str) -> list[str]:
    rows = []
    for el in ET.fromstring(source).iter():
        a, t = el.attrib, el.tag.replace("XCUIElementType", "")
        if t in ("Application", "Window", "Keyboard", "Key", "AppiumAUT") or a.get("visible") != "true":
            continue
        if t == "Other" and not a.get("name"):
            continue
        rows.append(f"{t} name={a.get('name')!r} value={a.get('value')!r} traits={a.get('traits')!r} "
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
    except Exception as exc:  # recon keeps going; the failure is itself a finding
        note(title, f"{type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}", False)
        traceback.print_exc(limit=3)


def udid() -> str:
    out = subprocess.run(["xcrun", "simctl", "list", "devices", "booted"], capture_output=True,
                         text=True, check=True).stdout  # fmt: skip
    for line in out.splitlines():
        if "(Booted)" in line and "iPhone" in line:
            return line.split("(")[1].split(")")[0]
    raise RuntimeError("no booted iPhone simulator")


def set_location(dev: str, where: tuple[float, float] | None) -> None:
    cmd = ["xcrun", "simctl", "location", dev] + (["clear"] if where is None else ["set", f"{where[0]},{where[1]}"])
    out = subprocess.run(cmd, capture_output=True, text=True)
    note(f"simctl location {'clear' if where is None else where}", f"rc={out.returncode}", out.returncode == 0)
    if where is None and STALE_WAIT and not set_location.waited:
        note("waiting for the last simulated fix to go stale", f"{STALE_WAIT}s", None)
        time.sleep(STALE_WAIT)
        set_location.waited = True


set_location.waited = False


def main() -> None:
    tech = test_data.tech()
    state = load_state()
    api = FieldServicesApi()
    dev = udid()
    drv = None
    try:
        def seed_pass() -> None:
            user_id = api.technician_user_id(tech.email)
            today = datetime.now().replace(second=0, microsecond=0)
            for kind, status, hour in (("new_gps", "new", 9), ("new_far", "new", 10), ("new_manual", "new", 11),
                                       ("in_progress", "in_progress", 12), ("submitted", "submitted", 13)):  # fmt: skip
                if kind not in KINDS:
                    continue
                when = today.replace(hour=hour, minute=0)
                iso = when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
                body = {"title": f"QA-AUTO recon6 {kind}", "jobId": f"QA-AUTO-R6-{RUN}-{kind.upper()}",
                        "userId": user_id, "surveyId": SHORT_SURVEY, "statusType": status,
                        "startAt": iso, "scheduleDate": iso, "description": "Recon 6 (module 05).",
                        "location": {"address": ADDRESS,
                                     "coordinates": {"latitude": str(LAT), "longitude": str(LNG)}}}  # fmt: skip
                resp = api._call("POST", "/job", json=body)
                ok = resp.status_code in (200, 201)
                note(f"POST /job {kind} ({status})", f"HTTP {resp.status_code}", ok)
                if ok:
                    state["jobs"][kind] = {"id": resp.json()["id"], "jobId": body["jobId"], "title": body["title"]}
                    save_state(state)

        if "seed" in PASSES:
            step("seed", seed_pass)
        drv = webdriver.Remote(settings.appium_url, options=get_capabilities("ios"))
        app = AppControl(drv, "ios")
        W, H = drv.get_window_size()["width"], drv.get_window_size()["height"]
        drv.update_settings({"defaultAlertAction": ""})  # the recon answers every alert itself

        def el(pred: str):
            return drv.find_element("-ios predicate string", pred)

        def has(pred: str) -> bool:
            return bool(drv.find_elements("-ios predicate string", pred))

        def signed_in() -> None:
            app.relaunch()
            landed = _landing(drv, "ios")
            if landed == "welcome":
                WelcomePage(drv, "ios").open_login()
                LoginPage(drv, "ios").request_code(tech.email)
                OtpPage(drv, "ios").enter_code(tech.otp)
                time.sleep(5)
            note("landing", _landing(drv, "ios"), None)

        def open_job(kind: str) -> None:
            job = state["jobs"][kind]
            for _ in range(3):
                drv.execute_script("mobile: dragFromToForDuration", {"duration": 0.3, "fromX": W / 2,
                                   "fromY": 300, "toX": W / 2, "toY": 720})  # fmt: skip
                time.sleep(3)
                if has(f"name CONTAINS '{job['jobId']}'"):
                    el(f"name CONTAINS '{job['jobId']}'").click()
                    time.sleep(2.5)
                    return
            raise RuntimeError(f"card {job['jobId']} not found")

        def server(kind: str) -> dict:
            j = api._call("GET", f"/job/{state['jobs'][kind]['id']}").json()
            return {k: j.get(k) for k in ("statusType", "statusInfo", "checkInDate", "checkInTimezone",
                                          "userLocation", "checkOutDate", "checkOutTimezone", "checkOutLocation")}  # fmt: skip

        def watch(label: str, seconds: float) -> list:
            """What appears after an action: system alert (with respectSystemAlerts) and app texts."""
            t0, seen, last = time.monotonic(), [], None
            while time.monotonic() - t0 < seconds:
                drv.update_settings({"respectSystemAlerts": True})
                src = drv.page_source
                drv.update_settings({"respectSystemAlerts": False})
                if "to use your location" in src:
                    seen.append((round(time.monotonic() - t0, 1), "OS prompt"))
                    dump(drv, f"recon6_{label}_os_prompt")
                    return seen
                app_src = drv.page_source
                texts = [r.split(" value=")[0] for r in rows_of(app_src) if any(k in r for k in KEYS)
                         and not r.startswith("StaticText name='Location'")]  # fmt: skip
                if texts != last:
                    seen.append((round(time.monotonic() - t0, 1), texts))
                    last = texts
                if any(k in app_src for k in ("Enter location manually", "Confirm check", "not at the job site",
                                              "could not be trusted", "Precise location", "Weak GPS",
                                              "Location disabled", "Location access required")):  # fmt: skip
                    dump(drv, f"recon6_{label}_after")
                    return seen
                time.sleep(0.8)
            dump(drv, f"recon6_{label}_timeout")
            return seen

        def answer_prompt(button: str) -> None:
            drv.update_settings({"respectSystemAlerts": True})
            try:
                el(f"type == 'XCUIElementTypeButton' AND name == '{button}'").click()
            finally:
                drv.update_settings({"respectSystemAlerts": False})
            time.sleep(1)

        def tap(label: str) -> None:
            el(f"type == 'XCUIElementTypeButton' AND name == '{label}'").click()
            time.sleep(1.5)

        # ------------------------------------------------------------------ gps
        def gps_pass() -> None:
            set_location(dev, (LAT, LNG))
            signed_in()
            open_job("new_gps")
            tap("Check in")
            seen = watch("gps_start", 20)
            note("gps: after Check in", seen, None)
            if seen and seen[-1][1] == "OS prompt":
                answer_prompt("Allow While Using App")
                seen = watch("gps_allowed", 25)
                note("gps: after Allow While Using App", seen, None)
            src = drv.page_source
            if "Confirm check in" in src:
                note("gps: simulator fix ACCEPTED — confirmation screen reached", True, True)
                tap("Confirm")
                time.sleep(4)
                dump(drv, "recon6_gps_after_confirm")
                note("gps: server after Confirm", server("new_gps"), None)
            else:
                for label in ("Got it", "Cancel", "OK"):
                    if has(f"type == 'XCUIElementTypeButton' AND name == '{label}'"):
                        tap(label)
                        note(f"gps: dismissed with {label}", "", None)
                        break
                note("gps: server status", server("new_gps")["statusType"], None)

        # ------------------------------------------------------------------ far
        def far_pass() -> None:
            set_location(dev, FAR)
            signed_in()
            open_job("new_far")
            tap("Check in")
            seen = watch("far", 25)
            note("far: after Check in (5.5 km away)", seen, None)
            for label in ("Got it", "Cancel", "OK"):
                if has(f"type == 'XCUIElementTypeButton' AND name == '{label}'"):
                    tap(label)
                    note(f"far: dismissed with {label}", "", None)
                    break
            note("far: server status", server("new_far")["statusType"], None)

        # ------------------------------------------------------------------ manual
        def through_prompt(label: str, seconds: float) -> list:
            seen = watch(label, seconds)
            if seen and seen[-1][1] == "OS prompt":
                answer_prompt("Allow While Using App")
                seen += watch(f"{label}_allowed", seconds)
            return seen

        def manual_to_confirm(label: str) -> bool:
            tap("Check in")
            t0 = time.monotonic()
            seen = through_prompt(f"{label}_start", 35)
            note(f"{label}: after Check in with no location ({time.monotonic() - t0:.0f}s)", seen, None)
            if not has("name == 'Enter location manually'"):
                return False
            fields = drv.find_elements("-ios predicate string", "type == 'XCUIElementTypeTextField'")
            note(f"{label}: manual field value (prefilled?)", [f.get_attribute("value") for f in fields], None)
            tap("Confirm")
            time.sleep(2)
            ok = has("name == 'Confirm check in'")
            dump(drv, f"recon6_{label}_confirm_screen")
            return ok

        def manual_pass() -> None:
            set_location(dev, None)
            signed_in()
            open_job("new_manual")
            if manual_to_confirm("manual1"):
                unnamed = drv.find_elements("-ios predicate string",
                                            "type == 'XCUIElementTypeButton' AND (name == nil OR name == '') AND rect.y < 140")
                note("manual: unnamed app-bar buttons on the confirmation screen", [b.rect for b in unnamed], None)
                if unnamed:
                    min(unnamed, key=lambda b: b.rect["x"]).click()  # X is on the left (leading)
                    time.sleep(2)
                note("manual: after X — server status", server("new_manual")["statusType"], None)
                dump(drv, "recon6_manual_after_x")
            if manual_to_confirm("manual2"):
                tap("Cancel")
                note("manual: after Cancel — server status", server("new_manual")["statusType"], None)
            if manual_to_confirm("manual3"):
                t_tap = datetime.now(UTC)
                tap("Confirm")
                time.sleep(4)
                dump(drv, "recon6_manual_after_confirm")
                note("manual: tap time (UTC)", t_tap.isoformat(), None)
                note("manual: server after Confirm", server("new_manual"), None)

        # ------------------------------------------------------------------ statuses
        def statuses_pass() -> None:
            signed_in()
            open_job("in_progress")
            rows = dump(drv, "recon6_details_in_progress")
            note("in_progress: buttons", [r for r in rows if r.startswith("Button")], None)

        # ------------------------------------------------------------------ checkout
        def checkout_pass() -> None:
            set_location(dev, None)
            signed_in()
            open_job("submitted")
            rows = dump(drv, "recon6_details_submitted")
            note("submitted: buttons", [r for r in rows if r.startswith("Button")], None)
            for attempt, final in (("co1", "Cancel"), ("co2", "Confirm")):
                tap("Check out")
                seen = through_prompt(f"{attempt}_start", 35)
                note(f"{attempt}: after Check out", seen, None)
                if has("name == 'Enter location manually'"):
                    tap("Confirm")
                    time.sleep(2)
                dump(drv, f"recon6_{attempt}_confirm_screen")
                if not has("name == 'Confirm check out'"):
                    note(f"{attempt}: no check-out confirmation screen", "", False)
                    return
                t_tap = datetime.now(UTC)
                tap(final)
                time.sleep(4)
                dump(drv, f"recon6_{attempt}_after_{final.lower()}")
                note(f"{attempt}: {final} at {t_tap.isoformat()} — server", server("submitted"), None)

        for name, fn in (("gps", gps_pass), ("far", far_pass), ("manual", manual_pass),
                         ("statuses", statuses_pass), ("checkout", checkout_pass)):  # fmt: skip
            if name in PASSES:
                step(name, fn)
    finally:
        print("\n==== cleanup", flush=True)
        for kind, job in list(state["jobs"].items()):
            try:
                api.delete_job({"id": job["id"], "jobId": job["jobId"]})
                note(f"deleted job {kind}", "404 after delete", True)
                del state["jobs"][kind]
            except Exception as exc:
                note(f"delete job {kind}", f"{type(exc).__name__}: {exc}", False)
            save_state(state)
        set_location(dev, (LAT, LNG))
        if drv is not None:
            drv.update_settings({"defaultAlertAction": "accept", "respectSystemAlerts": False})
            drv.quit()
        (EVIDENCE / "findings.json").write_text(json.dumps(FINDINGS, indent=1, default=str))
        print(f"\nleft over: jobs={list(state['jobs'])}", flush=True)


if __name__ == "__main__":
    main()
