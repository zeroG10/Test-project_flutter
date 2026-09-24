"""Recon 7 (2026-09-24): module 06 Order progress — the In progress screen (owner's go, Q-ORDP-3).

Nothing is filled, uploaded or submitted:

  progress — a job created In progress (description, PF): timer twice, timer after 10 s in the
             background, the rows Survey / Photo report / Notes → each screen and back, the
             lower part (info, the primary action)
  done     — a job created Submitted: the rows (read-only?), the primary action
  cleanup  — ALWAYS: jobs deleted (404)

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/recon_7.py <dumps-dir> <evidence-dir>
"""

import re
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
COORDS = {"latitude": "40.748440", "longitude": "-73.985664"}
RUN = datetime.now().strftime("%m%d-%H%M")
PF = {"name": "QA-AUTO PF Olive", "phone": "+1 202 555 0147", "email": "qa-auto+pf@example.com"}
TIMER = re.compile(r"^(\d)\n(\d)\n:\n(\d)\n(\d)\n:\n(\d)\n(\d)$")


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
        rows.append(f"{t} name={a.get('name')!r} traits={a.get('traits')!r} en={a.get('enabled')} "
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


def main() -> None:
    tech = test_data.tech()
    api = FieldServicesApi()
    jobs: dict[str, dict] = {}
    drv = None
    try:
        user_id = api.technician_user_id(tech.email)
        today = datetime.now().replace(second=0, microsecond=0)
        for kind, status, hour in (("progress", "in_progress", 9), ("done", "submitted", 10)):
            when = today.replace(hour=hour, minute=0)
            iso = when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            body = {"title": f"QA-AUTO recon7 {kind}", "jobId": f"QA-AUTO-R7-{RUN}-{kind.upper()}",
                    "userId": user_id, "surveyId": SHORT_SURVEY, "statusType": status, "startAt": iso,
                    "scheduleDate": iso, "description": "Recon 7 (module 06).\nSecond line of the scope.",
                    "projectFacilitator": PF, "location": {"address": ADDRESS, "coordinates": COORDS}}  # fmt: skip
            resp = api._call("POST", "/job", json=body)
            note(f"POST /job {kind}", resp.status_code, resp.status_code in (200, 201))
            jobs[kind] = {"id": resp.json()["id"], "jobId": body["jobId"]}

        drv = webdriver.Remote(settings.appium_url, options=get_capabilities("ios"))
        app = AppControl(drv, "ios")
        W = drv.get_window_size()["width"]

        def el(pred: str):
            return drv.find_element("-ios predicate string", pred)

        def has(pred: str) -> bool:
            return bool(drv.find_elements("-ios predicate string", pred))

        def timer() -> str | None:
            for e in drv.find_elements("-ios predicate string", "type == 'XCUIElementTypeStaticText' AND name CONTAINS ':'"):
                m = TIMER.match(e.get_attribute("name") or "")
                if m:
                    d = m.groups()
                    return f"{d[0]}{d[1]}:{d[2]}{d[3]}:{d[4]}{d[5]}"
            return None

        def open_job(kind: str) -> None:
            for _ in range(3):
                drv.execute_script("mobile: dragFromToForDuration", {"duration": 0.3, "fromX": W / 2, "fromY": 300,
                                                                     "toX": W / 2, "toY": 720})  # fmt: skip
                time.sleep(3)
                if has(f"name CONTAINS '{jobs[kind]['jobId']} - '"):
                    el(f"name CONTAINS '{jobs[kind]['jobId']} - '").click()
                    time.sleep(3)
                    return
            raise RuntimeError(f"card {kind} not found")

        app.relaunch()
        if _landing(drv, "ios") == "welcome":
            WelcomePage(drv, "ios").open_login()
            LoginPage(drv, "ios").request_code(tech.email)
            OtpPage(drv, "ios").enter_code(tech.otp)
            time.sleep(5)

        def progress_pass() -> None:
            open_job("progress")
            dump(drv, "recon7_progress_top")
            t1 = timer()
            time.sleep(4)
            t2 = timer()
            note("timer twice, 4 s apart", (t1, t2), None)
            drv.background_app(10)
            time.sleep(1)
            note("timer after 10 s in the background", timer(), None)
            for row in ("Survey", "Photo report", "Notes"):
                el(f"type == 'XCUIElementTypeOther' AND name == '{row}'").click()
                time.sleep(4)
                dump(drv, f"recon7_{row.lower().replace(' ', '_')}_screen")
                if has("type == 'XCUIElementTypeButton' AND name == 'Back'"):
                    el("type == 'XCUIElementTypeButton' AND name == 'Back'").click()
                else:
                    app_back = drv.find_elements("-ios predicate string",
                                                 "type == 'XCUIElementTypeButton' AND rect.y < 140")
                    note(f"{row}: no 'Back' — app-bar buttons", [(b.get_attribute('name'), b.rect) for b in app_back], None)
                    if app_back:
                        min(app_back, key=lambda b: b.rect["x"]).click()
                time.sleep(3)
                note(f"back from {row}: timer visible again", timer(), None)
            drv.execute_script("mobile: dragFromToForDuration", {"duration": 0.3, "fromX": W / 2, "fromY": 650,
                                                                 "toX": W / 2, "toY": 200})  # fmt: skip
            time.sleep(1.5)
            dump(drv, "recon7_progress_bottom")
            if has("type == 'XCUIElementTypeButton' AND name == 'Submit deliverables'"):
                b = el("type == 'XCUIElementTypeButton' AND name == 'Submit deliverables'")
                note("Submit deliverables: enabled / rect", (b.is_enabled(), b.rect), None)
            el("type == 'XCUIElementTypeButton' AND name == 'Back'").click()
            time.sleep(2)

        def done_pass() -> None:
            open_job("done")
            rows = dump(drv, "recon7_done_top")
            note("done: timer shown?", timer(), None)
            el("type == 'XCUIElementTypeOther' AND name == 'Survey'").click()
            time.sleep(3)
            note("done: after tapping Survey (read-only?)", [r for r in dump(drv, "recon7_done_after_survey_tap")
                                                            if "Header" in r][:3], None)  # fmt: skip
            note("done: buttons", [r for r in rows if r.startswith("Button")], None)

        step("progress", progress_pass)
        step("done", done_pass)
    finally:
        print("\n==== cleanup", flush=True)
        for kind, job in jobs.items():
            try:
                api.delete_job(job)
                note(f"deleted job {kind}", "404", True)
            except Exception as exc:
                note(f"delete job {kind}", f"{type(exc).__name__}: {exc}", False)
        if drv is not None:
            drv.quit()


if __name__ == "__main__":
    main()
