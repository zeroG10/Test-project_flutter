"""Recon 8 (2026-09-24): module 08 Survey — step-by-step exploration (owner's go, Q-SRV-4).

Unlike recons 5–7 (one script, one pass) the survey form is explored in small steps: every ``do``
attaches to the app that is already open (no relaunch, no reinstall), runs a few actions and dumps
the tree. Jobs are created directly In progress (the timer is not under test), one per survey.

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/recon_8.py seed    <state.json>
    PYTHONPATH=. uv run python scripts/recon/recon_8.py do      <state.json> <dumps-dir> <action> [<action> …]
    PYTHONPATH=. uv run python scripts/recon/recon_8.py server  <state.json> <kind>
    PYTHONPATH=. uv run python scripts/recon/recon_8.py cleanup <state.json>

Actions: ``open:<kind>`` (Jobs list → the job's details) · ``tap:<predicate>`` · ``tapi:<n>:<predicate>`` ·
``type:<predicate>:<text>`` · ``clear:<predicate>`` · ``swipe:up|down`` · ``scrollto:<predicate>`` · ``back`` ·
``sleep:<s>`` · ``dump:<name>`` · ``rows`` · ``shot:<path.png>`` · ``alert:accept|dismiss|show`` · ``launch`` ·
``terminate`` · ``bg:<s>``. The state file holds job ids only (scratchpad, never committed).
"""

import json
import sys
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

SURVEYS = {  # kind: survey id (qa/mobile/08-survey/survey-definitions/)
    "short": "2964b433-b734-4505-a8c5-6fb42c30fc33",
    "mo3": "accc4039-cc3d-455f-b617-f89026760768",
    "mo5": "2db0c23c-1f90-4ed9-bb13-fe18c13f9421",
    "t8": "3fa5b8f2-7813-4055-97dd-a1a303d284c5",
    "end": "5478a9d2-8786-491d-bc09-bcc3a66d71e5",
    "fiber": "cd20d2a6-a9e8-4269-991b-3a544655425e",
    "rep1": "4c694562-dae5-494c-a8f9-c7e99b016d0f",
    "two": "4044453f-6660-43c7-9c58-9499c63c2b45",
    "photo": "b4e9b124-0048-4be0-9e22-4db8f446af41",
    "empty": "553411d6-9a98-4e97-bd58-1b2b0a6d6e2c",
}
ADDRESS = "QA test site, 350 5th Ave, New York, NY 10118"
COORDS = {"latitude": "40.748440", "longitude": "-73.985664"}
P = "-ios predicate string"


def rows_of(source: str) -> list[str]:
    rows = []
    for el in ET.fromstring(source).iter():
        a, t = el.attrib, el.tag.replace("XCUIElementType", "")
        if t in ("Application", "Window", "Keyboard", "Key", "AppiumAUT") or a.get("visible") != "true":
            continue
        if t == "Other" and not a.get("name"):
            continue
        name = (a.get("name") or "").replace("\n", "|")[:70]
        value = f" value={a.get('value')[:40]!r}" if a.get("value") else ""
        rows.append(f"{t} {name!r}{value} tr={a.get('traits')!r} en={a.get('enabled')} "
                    f"@{a.get('x')},{a.get('y')} {a.get('width')}x{a.get('height')}")  # fmt: skip
    return rows


def seed(state: Path) -> None:
    from fixtures import test_data
    from helpers.field_services_api import FieldServicesApi

    api, run = FieldServicesApi(), datetime.now().strftime("%m%d-%H%M")
    user_id = api.technician_user_id(test_data.tech().email)
    today = datetime.now().replace(second=0, microsecond=0)
    jobs = {}
    for hour, (kind, survey_id) in enumerate(SURVEYS.items(), start=7):
        iso = today.replace(hour=hour, minute=0).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        body = {"title": f"QA-AUTO recon8 {kind}", "jobId": f"QA-AUTO-R8-{run}-{kind.upper()}",
                "userId": user_id, "surveyId": survey_id, "statusType": "in_progress", "startAt": iso,
                "scheduleDate": iso, "location": {"address": ADDRESS, "coordinates": COORDS}}  # fmt: skip
        resp = api._call("POST", "/job", json=body)
        print(f"POST /job {kind}: {resp.status_code}", flush=True)
        jobs[kind] = {"id": resp.json()["id"], "jobId": body["jobId"], "title": body["title"]}
    state.write_text(json.dumps({"run": run, "jobs": jobs}, indent=1))


def cleanup(state: Path) -> None:
    from helpers.field_services_api import FieldServicesApi

    api = FieldServicesApi()
    for kind, job in json.loads(state.read_text())["jobs"].items():
        try:
            api.delete_job(job)
            print(f"deleted {kind}: 404", flush=True)
        except Exception as exc:  # report and carry on — every job gets its attempt
            print(f"delete {kind}: {type(exc).__name__}: {exc}", flush=True)


def server(state: Path, kind: str) -> None:
    from helpers.field_services_api import FieldServicesApi

    job = json.loads(state.read_text())["jobs"][kind]
    body = FieldServicesApi().job(job["id"])
    print(json.dumps({k: body.get(k) for k in ("statusType", "updatedAt", "surveyResponse")}, indent=1,
                     ensure_ascii=False)[:12000])  # fmt: skip


def do(state: Path, dumps: Path, actions: list[str]) -> None:
    from appium import webdriver
    from appium.options.ios import XCUITestOptions

    from config.settings import settings
    from pages.jobs_list_page import JobsListPage

    jobs = json.loads(state.read_text())["jobs"]
    o = XCUITestOptions()
    o.device_name, o.platform_version = settings.ios_device_name, settings.ios_platform_version
    o.bundle_id, o.no_reset, o.auto_accept_alerts = settings.ios_bundle_id, True, False
    o.set_capability("appium:forceAppLaunch", False)
    o.set_capability("appium:shouldTerminateApp", False)
    drv = webdriver.Remote(settings.appium_url, options=o)
    size = drv.get_window_size()

    def visible(pred: str):
        return [e for e in drv.find_elements(P, pred) if e.is_displayed()]

    def drag(from_y: int, to_y: int) -> None:
        drv.execute_script("mobile: dragFromToForDuration", {
            "duration": 0.3, "fromX": size["width"] // 2, "fromY": from_y,
            "toX": size["width"] // 2, "toY": to_y})  # fmt: skip
        time.sleep(1.2)

    try:
        for action in actions:
            verb, _, arg = action.partition(":")
            print(f"\n>>> {action}", flush=True)
            try:
                if verb == "open":
                    jl = JobsListPage(drv, "ios")
                    jl.pull_to_refresh()
                    time.sleep(2)
                    jl.open_card(jobs[arg]["jobId"])
                    time.sleep(2)
                elif verb == "tap":
                    found = visible(arg)
                    print(f"    {len(found)} visible match(es)")
                    found[0].click()
                    time.sleep(1.5)
                elif verb == "tapi":
                    index, _, pred = arg.partition(":")
                    found = visible(pred)
                    print(f"    {len(found)} visible match(es)")
                    found[int(index)].click()
                    time.sleep(1.5)
                elif verb == "type":
                    pred, _, text = arg.rpartition(":")
                    el = visible(pred)[0]
                    el.click()
                    el.send_keys(text)
                    time.sleep(1)
                elif verb == "clear":
                    visible(arg)[0].clear()
                    time.sleep(1)
                elif verb == "swipe":
                    h = size["height"]
                    drag(int(h * 0.7), int(h * 0.3)) if arg == "up" else drag(int(h * 0.3), int(h * 0.7))
                elif verb == "scrollto":
                    for _ in range(10):
                        if visible(arg):
                            break
                        drag(int(size["height"] * 0.7), int(size["height"] * 0.35))
                    print(f"    visible: {bool(visible(arg))}")
                elif verb == "back":
                    visible("type == 'XCUIElementTypeButton' AND name == 'Back'")[0].click()
                    time.sleep(2)
                elif verb == "sleep":
                    time.sleep(float(arg))
                elif verb == "dump":
                    src = drv.page_source
                    (dumps / f"{arg}.xml").write_text(src, encoding="utf-8")
                    rows = rows_of(src)
                    print(f"---- {arg}: {len(rows)} visible")
                    print("\n".join("     " + r for r in rows), flush=True)
                elif verb == "rows":
                    print("\n".join("     " + r for r in rows_of(drv.page_source)), flush=True)
                elif verb == "shot":  # a full path: screenshots stay out of the repo
                    Path(arg).write_bytes(drv.get_screenshot_as_png())
                elif verb == "alert":
                    if arg == "show":
                        print("    ", drv.execute_script("mobile: alert", {"action": "getButtons"}))
                    else:
                        drv.execute_script("mobile: alert", {"action": arg})
                    time.sleep(1.5)
                elif verb == "launch":
                    drv.activate_app(o.bundle_id)
                    time.sleep(4)
                elif verb == "terminate":
                    drv.terminate_app(o.bundle_id)
                    time.sleep(1)
                elif verb == "bg":
                    drv.background_app(float(arg))
                    time.sleep(1)
                else:
                    print(f"    unknown action {verb!r}")
            except Exception as exc:  # recon: note and carry on with the next action
                print(f"    FAILED {type(exc).__name__}: {str(exc).splitlines()[0] if str(exc) else ''}")
    finally:
        drv.quit()


if __name__ == "__main__":
    cmd, state_path = sys.argv[1], Path(sys.argv[2])
    if cmd == "seed":
        seed(state_path)
    elif cmd == "cleanup":
        cleanup(state_path)
    elif cmd == "server":
        server(state_path, sys.argv[3])
    elif cmd == "do":
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        do(state_path, out, sys.argv[4:])
