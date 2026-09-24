"""Recon 5 (2026-09-24): module 04 Order details — what the app REALLY shows.

Not a test — discovery before the test cases of module 04 (owner's go 2026-09-24, Q-ORDD-5).
Passes, in this order (one Appium session, one process):

  files    — upload our own test files: a 2-page PDF and two JPGs (Q-ORDD-2, variant A)
  seed     — 3 jobs through the API: `full` (description, PF, 2 documents + 2 photos),
             `unviewed` (isViewed=false), `reschedule` (long description)
  details  — the details of `full`: every section, Check in position, PF phone tap, On map → Maps
  attach   — Attachments: tabs, selected tab, Documents / Photos, PDF viewer (pages, close),
             photo viewer (swipe, back), the tab after closing
  updated  — how long "Updated" lives on the details of `unviewed` (pixels + tree, fast loop)
  schedule — `reschedule`: Check in with a long description; PATCH /job/{id} scheduleDate, then a
             pull to refresh on the details
  checkin  — Check in on `full` with the location permission reset: what appears first (OS
             prompt, app dialogs) — cancelled, the job must stay New
  cleanup  — ALWAYS (finally): jobs (verified 404), then whether the file URLs outlive the job,
             then the files

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/recon_5.py <dumps-dir> <evidence-dir> [pass ...]

Server writes (owner's go 2026-09-24): 3 × POST /file/upload + 3 × DELETE /file/{id}; 3 × POST /job +
1 × PATCH /job/{id} + 3 × DELETE /job/{id}. No OTP unless the app is signed out. Screenshots stay in
<evidence-dir> (never committed); only XML trees go to <dumps-dir>.
"""

import json
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from appium import webdriver

from config.capabilities import get_capabilities
from config.settings import settings
from fixtures import test_data
from fixtures.app_state import _landing
from helpers import pixels
from helpers.app import AppControl
from helpers.field_services_api import FieldServicesApi
from pages.jobs_list_page import UPDATED_RGB
from pages.login_page import LoginPage
from pages.otp_page import OtpPage
from pages.welcome_page import WelcomePage

DUMPS, EVIDENCE = Path(sys.argv[1]), Path(sys.argv[2])
PASSES = sys.argv[3:] or ["files", "seed", "details", "attach", "updated", "schedule", "checkin"]
DUMPS.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
STATE_FILE = EVIDENCE / "state.json"
MEDIA = Path("fixtures/media")
SHORT_SURVEY = "2964b433-b734-4505-a8c5-6fb42c30fc33"
ADDRESS = "QA test site, 350 5th Ave, New York, NY 10118"
COORDS = {"latitude": "40.748440", "longitude": "-73.985664"}
RUN = datetime.now().strftime("%m%d-%H%M")
BUNDLE = settings.app_id("ios")
FINDINGS: list[dict] = []
DESCRIPTION = "Inspect and secure antenna mounts.\nReplace cable entry seals.\nTest signal transmission levels."
LONG_DESCRIPTION = "\n".join(f"QA-AUTO step {i}: check the item and write the result." for i in range(1, 19))
PF = {"name": "QA-AUTO PF Olive", "phone": "+1 202 555 0147", "email": "qa-auto+pf@example.com"}


def note(step: str, observed: object, ok: bool | None = None) -> None:
    FINDINGS.append({"step": step, "observed": observed, "ok": ok})
    mark = {True: "OK ", False: "NO ", None: "-- "}[ok]
    print(f"[{mark}] {step}: {observed}", flush=True)


def load_state() -> dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"jobs": {}, "files": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=1))


def rows_of(source: str, only_visible: bool = True) -> list[str]:
    rows = []
    for el in ET.fromstring(source).iter():
        a = el.attrib
        t = el.tag.replace("XCUIElementType", "")
        if t in ("Application", "Window", "Keyboard", "Key", "AppiumAUT"):
            continue
        if only_visible and a.get("visible") != "true":
            continue
        name = a.get("name")
        if t == "Other" and not name:
            continue
        rows.append(
            f"{t} name={name!r} value={a.get('value')!r} traits={a.get('traits')!r} "
            f"en={a.get('enabled')} @{a.get('x')},{a.get('y')} {a.get('width')}x{a.get('height')}"
        )
    return rows


def dump(driver, name: str, shot: bool = True) -> list[str]:
    source = driver.page_source
    (DUMPS / f"{name}.xml").write_text(source, encoding="utf-8")
    if shot:
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
        first = str(exc).splitlines()[0] if str(exc) else ""
        note(title, f"{type(exc).__name__}: {first}", False)
        traceback.print_exc(limit=3)


def iso(when: datetime) -> str:
    return when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")  # naive = device-local


def udid() -> str:
    out = subprocess.run(["xcrun", "simctl", "list", "devices", "booted"], capture_output=True,
                         text=True, check=True).stdout
    for line in out.splitlines():
        if "(Booted)" in line and "iPhone" in line:
            return line.split("(")[1].split(")")[0]
    raise RuntimeError("no booted iPhone simulator")


def main() -> None:
    tech = test_data.tech()
    state = load_state()
    api = FieldServicesApi()
    drv = None
    try:
        # ------------------------------------------------------------------ files
        def files_pass() -> None:
            for key, fname, mime in (
                ("pdf", "qa_auto_2_pages.pdf", "application/pdf"),
                ("photo1", "site_photo.jpg", "image/jpeg"),
                ("photo2", "site_photo_2.jpg", "image/jpeg"),
            ):
                data = (MEDIA / fname).read_bytes()
                resp = api._call("POST", "/file/upload",
                                 files={"file": (f"QA-AUTO-{RUN}-{fname}", data, mime)})
                body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                note(f"upload {fname}", f"HTTP {resp.status_code} keys={sorted(body)} "
                     f"mime={body.get('mimeType')} size={body.get('fileSize')}", resp.status_code in (200, 201))
                if resp.status_code in (200, 201):
                    state["files"][key] = {"id": body["id"], "url": body["location"], "name": fname}
                    save_state(state)
                    head = requests.head(body["location"], timeout=30)
                    note(f"uploaded {key} reachable", f"HEAD {head.status_code} "
                         f"{head.headers.get('content-type')}", head.status_code == 200)

        # ------------------------------------------------------------------ seed
        def seed_pass() -> None:
            user_id = api.technician_user_id(tech.email)
            f = state["files"]
            today = datetime.now().replace(second=0, microsecond=0)
            plans = {
                "full": dict(when=today.replace(hour=12, minute=0), description=DESCRIPTION,
                             projectFacilitator=PF,
                             attachments={
                                 "documents": [
                                     {"url": f["pdf"]["url"], "name": "QA-AUTO safety.pdf",
                                      "description": "2 pages"},
                                     {"url": f["pdf"]["url"], "name": "QA-AUTO power.pdf",
                                      "description": "same file, second entry"},
                                 ],
                                 "photos": [
                                     {"url": f["photo1"]["url"], "name": "QA-AUTO site 1.jpg",
                                      "description": "photo 1"},
                                     {"url": f["photo2"]["url"], "name": "QA-AUTO site 2.jpg",
                                      "description": "photo 2"},
                                 ]}),
                "unviewed": dict(when=today.replace(hour=13, minute=0), description=DESCRIPTION,
                                 isViewed=False),
                "reschedule": dict(when=today.replace(hour=10, minute=0),
                                   description=LONG_DESCRIPTION),
            }
            for kind, p in plans.items():
                when = p.pop("when")
                body = {"title": f"QA-AUTO recon5 {kind}", "jobId": f"QA-AUTO-R5-{RUN}-{kind.upper()}",
                        "userId": user_id, "surveyId": SHORT_SURVEY, "statusType": "new",
                        "startAt": iso(when), "scheduleDate": iso(when),
                        "location": {"address": ADDRESS, "coordinates": COORDS}, **p}
                resp = api._call("POST", "/job", json=body)
                ok = resp.status_code in (200, 201)
                note(f"POST /job {kind}", f"HTTP {resp.status_code} {'' if ok else resp.text[:300]}", ok)
                if ok:
                    job = resp.json()
                    state["jobs"][kind] = {"id": job["id"], "jobId": body["jobId"], "title": body["title"],
                                           "when": when.strftime("%Y-%m-%d %H:%M")}
                    save_state(state)
                    back = api._call("GET", f"/job/{job['id']}").json()
                    att = back.get("attachments") or {}
                    note(f"GET {kind}", {"pf": {k: bool(v) for k, v in (back.get("projectFacilitator") or {}).items()},
                                         "docs": len(att.get("documents") or []),
                                         "photos": len(att.get("photos") or []),
                                         "isViewed": back.get("isViewed")}, None)

        for name, fn in (("files", files_pass), ("seed", seed_pass)):
            if name in PASSES:
                step(name, fn)

        ui = [p for p in PASSES if p in ("details", "attach", "updated", "schedule", "checkin")]
        if not ui:
            return
        drv = webdriver.Remote(settings.appium_url, options=get_capabilities("ios"))
        app = AppControl(drv, "ios")
        size = drv.get_window_size()
        W, H = size["width"], size["height"]
        note("window", size, None)

        def el(pred: str):
            return drv.find_element("-ios predicate string", pred)

        def drag(x1, y1, x2, y2, duration=0.3) -> None:
            drv.execute_script("mobile: dragFromToForDuration", {
                "duration": duration, "fromX": x1, "fromY": y1, "toX": x2, "toY": y2})

        def pull_down() -> None:
            drag(W / 2, 300, W / 2, 720)
            time.sleep(3)  # recon only: let the refresh finish

        def signed_in_jobs() -> None:
            app.relaunch()
            landed = _landing(drv, "ios")
            note("landing", landed, None)
            if landed == "welcome":
                WelcomePage(drv, "ios").open_login()
                LoginPage(drv, "ios").request_code(tech.email)
                OtpPage(drv, "ios").enter_code(tech.otp)
                time.sleep(5)
                note("UI login", _landing(drv, "ios"), None)

        def open_job(kind: str) -> None:
            job = state["jobs"][kind]
            for attempt in range(3):
                pull_down()
                try:
                    card = el(f"name CONTAINS '{job['jobId']}'")
                    card.click()
                    break
                except Exception:
                    drag(W / 2, 700, W / 2, 300)
            time.sleep(2.5)

        # ------------------------------------------------------------------ details
        def details_pass() -> None:
            signed_in_jobs()
            open_job("full")
            rows = dump(drv, "recon5_details_full_top")
            btn = el("type == 'XCUIElementTypeButton' AND name == 'Check in'")
            note("Check in button rect / visible", (btn.rect, btn.is_displayed(), f"screen h={H}"), None)
            drag(W / 2, 650, W / 2, 200)
            time.sleep(1)
            dump(drv, "recon5_details_full_bottom")
            editable = [r for r in rows if r.startswith(("TextField", "TextView", "SecureTextField"))]
            note("editable elements on the details", editable, not editable)
            # PF phone → dialer?
            try:
                phone = el(f"name CONTAINS '{PF['phone'][-4:]}'")
                note("PF phone element", (phone.tag_name, phone.get_attribute("name"), phone.rect), None)
                phone.click()
                time.sleep(2.5)
                note("after PF phone tap: AUT state / phone app state",
                     (drv.query_app_state(BUNDLE), drv.query_app_state("com.apple.mobilephone")), None)
                dump(drv, "recon5_after_pf_phone")
                if drv.query_app_state(BUNDLE) != 4:
                    drv.activate_app(BUNDLE)
                    time.sleep(2)
            except Exception as exc:
                note("PF phone", f"{type(exc).__name__}: {str(exc)[:120]}", False)
            # On map → Maps
            drag(W / 2, 250, W / 2, 700)
            time.sleep(1)
            el("name == 'On map'").click()
            time.sleep(4)
            states = {b: drv.query_app_state(b) for b in (BUNDLE, "com.apple.Maps", "com.google.Maps")}
            note("after On map: app states (4 = foreground)", states, states.get("com.apple.Maps") == 4)
            (EVIDENCE / "recon5_maps.png").write_bytes(drv.get_screenshot_as_png())
            try:
                src = drv.page_source
                (DUMPS / "recon5_maps.xml").write_text(src, encoding="utf-8")
                hits = [r for r in rows_of(src) if "350 5th" in r or "QA test site" in r or "New York" in r]
                note("Maps tree mentions the address", hits[:5], bool(hits))
            except Exception as exc:
                note("Maps tree", f"{type(exc).__name__}", False)
            drv.activate_app(BUNDLE)
            time.sleep(2)
            note("back in the app after Maps", drv.query_app_state(BUNDLE), drv.query_app_state(BUNDLE) == 4)
            dump(drv, "recon5_details_after_maps", shot=False)

        # ------------------------------------------------------------------ attachments
        def attach_pass() -> None:
            signed_in_jobs()
            open_job("full")
            drag(W / 2, 650, W / 2, 200)
            time.sleep(1)
            el("name BEGINSWITH 'Attachments'").click()
            time.sleep(3)
            dump(drv, "recon5_attachments_documents")
            el("name == 'Photos'").click()
            time.sleep(3)
            dump(drv, "recon5_attachments_photos")
            el("name == 'Documents'").click()
            time.sleep(2)
            el("name CONTAINS 'QA-AUTO safety'").click()
            time.sleep(5)
            dump(drv, "recon5_pdf_viewer")
            png1 = drv.get_screenshot_as_png()
            drag(W / 2, 700, W / 2, 150, 0.2)
            drag(W / 2, 700, W / 2, 150, 0.2)
            time.sleep(1.5)
            png2 = drv.get_screenshot_as_png()
            (EVIDENCE / "recon5_pdf_viewer_scrolled.png").write_bytes(png2)
            note("PDF page 2 colour block (blue share) before / after scroll",
                 (round(pixels.colour_share(png1, (40, 90, 160)), 4),
                  round(pixels.colour_share(png2, (40, 90, 160)), 4)), None)
            unnamed = drv.find_elements("-ios predicate string",
                                        "type == 'XCUIElementTypeButton' AND (name == nil OR name == '') AND rect.y < 140")
            note("unnamed app-bar buttons in the PDF viewer", [b.rect for b in unnamed], None)
            if unnamed:
                max(unnamed, key=lambda b: b.rect["x"]).click()  # the right-most: close (X)
                time.sleep(2)
            dump(drv, "recon5_after_pdf_close")
            el("name == 'Photos'").click()
            time.sleep(2)
            imgs = [e for e in drv.find_elements("-ios predicate string", "type == 'XCUIElementTypeImage'")
                    if e.rect["y"] > 150]
            note("photo thumbnails (Image, y > 150)", [(e.get_attribute("name"), e.rect) for e in imgs], None)
            (imgs[0] if imgs else el("name CONTAINS 'site 1'")).click()
            time.sleep(3)
            dump(drv, "recon5_photo_viewer")
            drag(W * 0.85, H / 2, W * 0.15, H / 2, 0.2)
            time.sleep(1.5)
            (EVIDENCE / "recon5_photo_viewer_swiped.png").write_bytes(drv.get_screenshot_as_png())
            el("name == 'Back'").click()
            time.sleep(2)
            dump(drv, "recon5_attachments_after_photo")
            el("name == 'Back'").click()
            time.sleep(2)
            dump(drv, "recon5_details_after_attachments", shot=False)

        # ------------------------------------------------------------------ updated
        def updated_pass() -> None:
            signed_in_jobs()
            job = state["jobs"]["unviewed"]
            pull_down()
            card = el(f"name CONTAINS '{job['jobId']}'")
            note("unviewed card name starts with Updated", card.get_attribute("name").startswith("Updated"), None)
            t0 = time.monotonic()
            card.click()
            samples = []
            while time.monotonic() - t0 < 5:
                png = drv.get_screenshot_as_png()
                t_png = round(time.monotonic() - t0, 2)
                samples.append((t_png, round(pixels.colour_share(png, UPDATED_RGB), 4)))
                if len(samples) in (1, 3):
                    (EVIDENCE / f"recon5_updated_{len(samples)}.png").write_bytes(png)
            note("details of an unviewed job: (s after tap, banner fill)", samples, None)
            dump(drv, "recon5_details_unviewed")
            server = api._call("GET", f"/job/{job['id']}").json()
            note("server after opening", {"isViewed": server.get("isViewed")}, server.get("isViewed") is True)

        # ------------------------------------------------------------------ schedule
        def schedule_pass() -> None:
            signed_in_jobs()
            job = state["jobs"]["reschedule"]
            open_job("reschedule")
            dump(drv, "recon5_details_reschedule_before")
            btn = el("type == 'XCUIElementTypeButton' AND name == 'Check in'")
            note("long description: Check in rect / visible", (btn.rect, btn.is_displayed()), None)
            new = datetime.strptime(job["when"], "%Y-%m-%d %H:%M") + timedelta(days=1, hours=2)
            resp = api._call("PATCH", f"/job/{job['id']}", json={"scheduleDate": iso(new), "startAt": iso(new)})
            note("PATCH scheduleDate +1 d +2 h", f"HTTP {resp.status_code} {resp.text[:200]}",
                 resp.status_code == 200)
            back = api._call("GET", f"/job/{job['id']}").json()
            note("server after PATCH", {"scheduleDate": back.get("scheduleDate"), "status": back.get("statusType"),
                                        "title": back.get("title")}, None)
            drag(W / 2, 250, W / 2, 700)
            time.sleep(4)
            dump(drv, "recon5_details_reschedule_after")
            note("expected on screen", (f"{new.day} {new:%b %Y}", f"{new:%H:%M}"), None)

        # ------------------------------------------------------------------ check in
        def checkin_pass() -> None:
            dev = udid()
            app.terminate()
            for cmd in (["xcrun", "simctl", "privacy", dev, "reset", "location", BUNDLE],
                        ["xcrun", "simctl", "location", dev, "set",
                         f"{COORDS['latitude']},{COORDS['longitude']}"]):
                out = subprocess.run(cmd, capture_output=True, text=True)
                note(" ".join(cmd[2:5]), f"rc={out.returncode} {out.stderr.strip()[:120]}", out.returncode == 0)
            drv.update_settings({"defaultAlertAction": ""})
            try:
                signed_in_jobs()
                open_job("full")
                el("type == 'XCUIElementTypeButton' AND name == 'Check in'").click()
                t0 = time.monotonic()
                seen = []
                while time.monotonic() - t0 < 20:
                    try:
                        text = drv.execute_script("mobile: alert", {"action": "getText"})
                        buttons = drv.execute_script("mobile: alert", {"action": "getButtons"})
                        seen.append((round(time.monotonic() - t0, 1), "OS alert", text, buttons))
                        (EVIDENCE / "recon5_checkin_os_alert.png").write_bytes(drv.get_screenshot_as_png())
                        allow = next((b for b in buttons if "While Using" in b), buttons[-1])
                        drv.execute_script("mobile: alert", {"action": "accept", "buttonLabel": allow})
                        time.sleep(1)
                        continue
                    except Exception:
                        pass
                    src = drv.page_source
                    texts = [r for r in rows_of(src) if r.startswith(("StaticText", "Button"))
                             and any(k in r for k in ("ocation", "GPS", "site", "trusted", "Precise",
                                                      "manually", "Checking", "Got it", "Enable"))]
                    if texts:
                        seen.append((round(time.monotonic() - t0, 1), "app", texts))
                        if any("Got it" in r or "Cancel" in r for r in texts):
                            dump(drv, f"recon5_checkin_dialog_{len(seen)}")
                            break
                    time.sleep(0.7)
                note("after Check in (s, what)", seen, None)
                for label in ("Cancel", "Got it"):
                    try:
                        el(f"type == 'XCUIElementTypeButton' AND name == '{label}'").click()
                        note(f"tapped {label}", "", None)
                        break
                    except Exception:
                        pass
                time.sleep(2)
                dump(drv, "recon5_after_checkin_cancel")
                server = api._call("GET", f"/job/{state['jobs']['full']['id']}").json()
                note("job status after the cancelled flow", server.get("statusType"),
                     server.get("statusType") == "new")
            finally:
                drv.update_settings({"defaultAlertAction": "accept"})

        for name, fn in (("details", details_pass), ("attach", attach_pass), ("updated", updated_pass),
                         ("schedule", schedule_pass), ("checkin", checkin_pass)):
            if name in PASSES:
                step(name, fn)
    finally:
        # ------------------------------------------------------------------ cleanup
        print("\n==== cleanup", flush=True)
        for kind, job in list(state["jobs"].items()):
            try:
                api.delete_job({"id": job["id"], "jobId": job["jobId"]})
                note(f"deleted job {kind}", "404 after delete", True)
                del state["jobs"][kind]
            except Exception as exc:
                note(f"delete job {kind}", f"{type(exc).__name__}: {exc}", False)
            save_state(state)
        for key, f in list(state["files"].items()):
            try:
                alive = requests.head(f["url"], timeout=30).status_code
                resp = api._call("DELETE", f"/file/{f['id']}")
                after = requests.head(f["url"], timeout=30).status_code
                note(f"file {key}: HEAD after job delete / DELETE /file / HEAD after",
                     (alive, resp.status_code, resp.text[:100], after), resp.status_code == 200)
                if resp.status_code == 200:
                    del state["files"][key]
            except Exception as exc:
                note(f"delete file {key}", f"{type(exc).__name__}: {exc}", False)
            save_state(state)
        if drv is not None:
            drv.quit()
        (EVIDENCE / "findings.json").write_text(json.dumps(FINDINGS, indent=1, default=str))
        print(f"\nleft over: jobs={list(state['jobs'])} files={list(state['files'])}", flush=True)


if __name__ == "__main__":
    main()
