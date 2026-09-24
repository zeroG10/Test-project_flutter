"""Recon 4 (2026-09-24): modules 01 Splash and 03 Order list — what the app REALLY shows.

Not a test — discovery before the screen maps and tests of the two modules (owner's go 2026-09-24).
Passes, in this order (one Appium session, one process):

  splash   — cold start without a session: timing of the first frames, brand colour, logo centre,
             tree during the splash, taps / edge swipe during the splash
  login    — UI login as the test technician (one OTP) and the session hand-over after a relaunch
  seed     — 8 jobs through the API (6 statuses today, one on another day, one unviewed)
  list     — cards, statuses, order, "Updated", refresh, details, tab state
  calendar — toggle, week days, selected day, other day, empty day, list ↔ calendar, week swipe
  tabs     — Notifications / Profile roots
  links    — invalid key, link for another phone (mismatch dialog), link for the own phone, log out,
             signed-out links
  revoked  — a freshly registered user deleted on the server, then a cold start
  cleanup  — ALWAYS (finally): every job and user this run created, by the ids kept in state.json

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/recon_4.py <dumps-dir> <evidence-dir> [pass ...]

Server writes (owner's go 2026-09-24): 8 × POST /job + 8 × DELETE /job/{id}; 2 × POST
/job/assign/{phone} (a reserved 555-01xx number and the test account's — not real — phone); one
self-registered user + DELETE /user/full-delete/{id}. Two OTP requests (test account, new user).
Screenshots and video stay in <evidence-dir> (customer UI — never committed); only XML trees go to
<dumps-dir>.
"""

import io
import json
import subprocess
import sys
import time
import traceback
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

from appium import webdriver
from PIL import Image

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
PASSES = sys.argv[3:] or [
    "splash", "login", "seed", "list", "calendar", "tabs", "links", "revoked",
]
DUMPS.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
STATE_FILE = EVIDENCE / "state.json"
FINDINGS: list[dict] = []
BRAND = (120, 42, 42)  # #782A2A — Figma `Spalsh` fill, app theme primary
SHORT_SURVEY = "2964b433-b734-4505-a8c5-6fb42c30fc33"
ADDRESS = "QA test site, 350 5th Ave, New York, NY 10118"
COORDS = {"latitude": "40.748440", "longitude": "-73.985664"}
RUN = datetime.now().strftime("%m%d-%H%M")
BUNDLE = settings.app_id("ios")


# --------------------------------------------------------------------------- recording helpers

def note(step: str, observed: object, ok: bool | None = None) -> None:
    FINDINGS.append({"step": step, "observed": observed, "ok": ok})
    mark = {True: "OK ", False: "NO ", None: "-- "}[ok]
    print(f"[{mark}] {step}: {observed}", flush=True)


def load_state() -> dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"jobs": {}, "users": []}


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
            f"{t} name={name!r} value={a.get('value')!r} sel={a.get('selected')} "
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


# --------------------------------------------------------------------------- pixel helpers

def frame_stats(png: bytes) -> dict:
    """Brand-colour share of the screen and the centre of the light blob (the logo)."""
    image = Image.open(io.BytesIO(png)).convert("RGB")
    w, h = image.size
    small = image.resize((w // 6, h // 6), Image.NEAREST)
    sw, sh = small.size
    pts_per_px = 402 / sw  # iPhone 17: 402 pt wide
    brand = light = 0
    xs, ys = [], []
    top, bottom = int(60 / pts_per_px), int((874 - 30) / pts_per_px)  # skip status bar + home bar
    for y in range(sh):
        for x in range(sw):
            r, g, b = small.getpixel((x, y))
            if abs(r - BRAND[0]) + abs(g - BRAND[1]) + abs(b - BRAND[2]) <= 45:
                brand += 1
            elif top <= y <= bottom and r + g + b > 600:
                light += 1
                xs.append(x)
                ys.append(y)
    stats = {"brand_share": round(brand / (sw * sh), 3), "light_px": light}
    if xs:
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        stats.update(
            logo_box_pt=[round(min(xs) * pts_per_px), round(min(ys) * pts_per_px),
                         round((max(xs) - min(xs)) * pts_per_px), round((max(ys) - min(ys)) * pts_per_px)],
            logo_dx_pct=round((cx - sw / 2) / sw * 100, 1),
            logo_dy_pct=round((cy - sh / 2) / sh * 100, 1),
        )
    colours = small.getcolors(maxcolors=sw * sh)
    stats["dominant"] = max(colours)[1]
    return stats


def interactive_count(source: str) -> int:
    kinds = {"StaticText", "Button", "TextField", "SecureTextField", "Link", "Switch", "Cell"}
    return sum(
        1
        for el in ET.fromstring(source).iter()
        if el.tag.replace("XCUIElementType", "") in kinds and el.attrib.get("visible") == "true"
    )


# --------------------------------------------------------------------------- API helpers (recon only)

def jobs_of_user(api: FieldServicesApi, user_id: str) -> list[dict]:
    out, page = [], 1
    while True:
        resp = api._call("GET", "/job", params={"userId": user_id, "page": page, "pageSize": 50})
        if resp.status_code != 200:
            raise RuntimeError(f"GET /job HTTP {resp.status_code}: {resp.text[:200]}")
        body = resp.json()
        data = body.get("data") if isinstance(body, dict) else body
        data = data or []
        out += data
        if len(data) < 50:
            return out
        page += 1


def create_job(api: FieldServicesApi, user_id: str, kind: str, when: datetime, status: str,
               viewed: bool | None = None) -> dict:
    iso = when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")  # naive = device-local
    body = {
        "title": f"QA-AUTO recon4 {kind}",
        "jobId": f"QA-AUTO-R4-{RUN}-{kind.upper()}",
        "userId": user_id,
        "surveyId": SHORT_SURVEY,
        "statusType": status,
        "startAt": iso,
        "scheduleDate": iso,
        "description": "Recon 4 (modules 01 + 03). Created by a QA script, deleted by it.",
        "location": {"address": ADDRESS, "coordinates": COORDS},
    }
    if viewed is not None:
        body["isViewed"] = viewed
    resp = api._call("POST", "/job", json=body)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"POST /job ({kind}) HTTP {resp.status_code}: {resp.text[:300]}")
    job = resp.json()
    return {"id": job["id"], "jobId": body["jobId"], "title": body["title"], "status": status,
            "when_local": when.strftime("%Y-%m-%d %H:%M"), "kind": kind,
            "server_status": job.get("statusType"), "server_isViewed": job.get("isViewed")}


def assign_link(api: FieldServicesApi, phone: str) -> dict:
    tried = []
    for form in (phone, phone.lstrip("+")):
        path = f"/job/assign/{urllib.parse.quote(form, safe='')}"
        resp = api._call("POST", path)
        tried.append(f"{form} → HTTP {resp.status_code} {resp.text[:200]}")
        if resp.status_code in (200, 201):
            message = (resp.json() or {}).get("message", "")
            return {"url": message, "key": message.rstrip("/").split("/")[-1], "tried": tried}
    return {"url": None, "key": None, "tried": tried}


# --------------------------------------------------------------------------- the run

def main() -> None:
    tech = test_data.tech()
    state = load_state()
    t0 = time.monotonic()
    drv = webdriver.Remote(settings.appium_url, options=get_capabilities("ios"))
    note("session created (build installed)", f"{time.monotonic() - t0:.1f}s", True)
    app = AppControl(drv, "ios")
    welcome, login, otp = WelcomePage(drv, "ios"), LoginPage(drv, "ios"), OtpPage(drv, "ios")
    api = FieldServicesApi()
    info = drv.execute_script("mobile: deviceInfo")
    note("device time zone", info.get("timeZone"), None)
    note("host time zone", str(datetime.now().astimezone().tzinfo), None)
    recording = False
    try:
        try:
            drv.start_recording_screen(**IOS_RECORDING)
            recording = True
        except Exception as exc:
            note("screen recording", f"{type(exc).__name__}: {exc}", False)

        def open_link(url: str) -> None:
            drv.execute_script("mobile: deepLink", {"url": url, "bundleId": BUNDLE})

        def jobs_page_open() -> bool:
            return "Jobs list" in drv.page_source

        def toggle():
            return drv.find_element(
                "-ios predicate string",
                "type == 'XCUIElementTypeButton' AND name == nil AND rect.y < 140",
            )

        def cards() -> list[tuple[str, int]]:
            # a card is a StaticText; with the "Updated" banner it is an Image (recon 4)
            out = []
            for el in ET.fromstring(drv.page_source).iter():
                name = el.attrib.get("name") or ""
                kind = el.tag.replace("XCUIElementType", "")
                if kind in ("StaticText", "Image") and "QA-AUTO-R4" in name:
                    out.append((name, int(el.attrib.get("y", 0))))
            return out

        def pull_down() -> None:
            size = drv.get_window_size()
            drv.execute_script("mobile: dragFromToForDuration", {
                "duration": 0.3, "fromX": size["width"] / 2, "fromY": 300,
                "toX": size["width"] / 2, "toY": 720})
            time.sleep(3)  # recon only: let the refresh finish

        def short(names: list) -> list[str]:
            return [" | ".join(n.split("\n")[:4]) for n, _ in names]

        def day_cell(day: datetime) -> str:
            return f"{day.strftime('%A')}, {day.strftime('%B')} {day.day}, {day.year}"

        # ------------------------------------------------------------------ splash
        def splash_pass() -> None:
            for label, idle in (("default", None), ("waitForIdleTimeout=0", 0)):
                app.clear_data()
                if idle is not None:
                    drv.update_settings({"waitForIdleTimeout": idle})
                t = time.monotonic()
                app.launch()
                t_launch = time.monotonic() - t
                frames = []
                sources = []
                while time.monotonic() - t < 9:
                    png = drv.get_screenshot_as_png()
                    frames.append((round(time.monotonic() - t, 2), frame_stats(png), png))
                    if len(sources) < 2:
                        src = drv.page_source
                        sources.append((round(time.monotonic() - t, 2), interactive_count(src), src))
                    if frames[-1][1]["brand_share"] < 0.2 and "Sign up" in drv.page_source:
                        break
                note(f"[{label}] activate_app returned after", f"{t_launch:.2f}s", None)
                for i, (ts, stats, png) in enumerate(frames):
                    note(f"[{label}] frame {i} at {ts}s", stats, None)
                    (EVIDENCE / f"splash_{label}_{i:02d}_{ts}s.png").write_bytes(png)
                for ts, count, src in sources:
                    note(f"[{label}] tree at {ts}s: visible text/button/field count", count, None)
                    (DUMPS / f"splash_{label.replace('=', '')}_tree_{ts}s.xml").write_text(src)
                splash_frames = [f for f in frames if f[1]["brand_share"] >= 0.9]
                note(f"[{label}] frames with ≥90 % brand colour", len(splash_frames), bool(splash_frames))
            drv.update_settings({"waitForIdleTimeout": 10})
            # interaction during the splash
            app.clear_data()
            t = time.monotonic()
            app.launch()
            size = drv.get_window_size()
            drv.execute_script("mobile: tap", {"x": size["width"] / 2, "y": size["height"] / 2})
            t_tap = time.monotonic() - t
            drv.execute_script("mobile: dragFromToForDuration", {
                "duration": 0.1, "fromX": 2, "fromY": size["height"] / 2,
                "toX": size["width"] * 0.6, "toY": size["height"] / 2})
            t_swipe = time.monotonic() - t
            png = drv.get_screenshot_as_png()
            stats = frame_stats(png)
            (EVIDENCE / "splash_after_tap_swipe.png").write_bytes(png)
            note("tap / edge swipe done at", f"{t_tap:.2f}s / {t_swipe:.2f}s; frame after: {stats}",
                 stats["brand_share"] >= 0.9)
            landed = _landing(drv, "ios")
            note("after tap + swipe the app lands on", landed, landed == "welcome")
            dump(drv, "recon4_welcome_after_splash")

        if "splash" in PASSES:
            step("SPLASH: cold start without a session", splash_pass)

        # ------------------------------------------------------------------ login
        def login_pass() -> None:
            landed = _landing(drv, "ios")
            if landed != "welcome":
                app.clear_data()
                app.launch()
                landed = _landing(drv, "ios")
            welcome.open_login()
            login.request_code(tech.email)
            otp.enter_code(tech.otp)
            landed = _landing(drv, "ios")
            note("UI login lands on", landed, landed == "jobs-list")
            # hand-over with a session: poll from the launch on
            app.terminate()
            t = time.monotonic()
            app.launch()
            seen = []
            while time.monotonic() - t < 12:
                src = drv.page_source
                now = round(time.monotonic() - t, 2)
                if "Sign up" in src:
                    seen.append((now, "welcome"))
                if "Jobs list" in src:
                    seen.append((now, "jobs-list"))
                    break
                seen.append((now, "other"))
            note("relaunch with a session: screens seen (s, screen)", seen,
                 not any(s == "welcome" for _, s in seen))

        if any(p in PASSES for p in ("login", "list", "calendar", "calendar2", "tabs", "links", "links2", "links3", "links3-tail", "links5", "links6", "sort")):
            step("LOGIN: UI login + relaunch hand-over", login_pass)

        # ------------------------------------------------------------------ seed
        def seed_pass() -> None:
            techs = api.find_technicians_by_email(tech.email)
            user_id = str(techs[0]["user"]["id"])
            state["tech_user_id"] = user_id
            before = jobs_of_user(api, user_id)
            by_status = {}
            for j in before:
                by_status[j.get("statusType")] = by_status.get(j.get("statusType"), 0) + 1
            note("technician jobs before the seed (by status)", by_status, None)
            leftovers = [j for j in before if str(j.get("jobId", "")).startswith("QA-AUTO")]
            note("leftover QA-AUTO jobs", [j.get("jobId") for j in leftovers], not leftovers)
            today = datetime.now().replace(second=0, microsecond=0)
            base = today.replace(hour=0, minute=0)
            weekday_sun0 = (today.weekday() + 1) % 7  # Sunday = 0
            other = base + timedelta(days=1 if weekday_sun0 < 6 else -1)
            plan = [
                ("new", base.replace(hour=9), "new", None),
                ("inprog", base.replace(hour=10), "in_progress", None),
                ("submitted", base.replace(hour=11), "submitted", None),
                ("completed", base.replace(hour=12), "completed", None),
                ("canceled", base.replace(hour=13), "canceled", None),
                ("expired", base.replace(hour=14), "expired", None),
                ("unviewed", base.replace(hour=15), "new", False),
                ("otherday", other.replace(hour=12), "new", None),
            ]
            for kind, when, status, viewed in plan:
                job = create_job(api, user_id, kind, when, status, viewed)
                state["jobs"][kind] = job
                save_state(state)
                note(f"created {kind}", job, job["server_status"] == status)
            state["other_day"] = other.strftime("%Y-%m-%d")
            save_state(state)

        if "seed" in PASSES:
            step("SEED: 8 jobs through the API", seed_pass)

        # ------------------------------------------------------------------ sort (D-ORDL-10)
        def sort_pass() -> None:
            techs = api.find_technicians_by_email(tech.email)
            user_id = str(techs[0]["user"]["id"])
            state["tech_user_id"] = user_id
            active = [j for j in jobs_of_user(api, user_id)
                      if j.get("statusType") not in ("completed", "canceled", "expired")]
            note("active jobs of the technician before the probe", [j.get("jobId") for j in active], not active)
            base = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
            # created on purpose NOT in date order: tomorrow, yesterday, today
            for kind, when in (("sort-tomorrow", base + timedelta(days=1)),
                               ("sort-yesterday", base - timedelta(days=1)),
                               ("sort-today", base)):
                job = create_job(api, user_id, kind, when, "new")
                state["jobs"][kind] = job
                save_state(state)
                note(f"created {kind} (creation order)", {"jobId": job["jobId"], "date": job["when_local"]}, True)
                time.sleep(1.5)  # distinct creation timestamps
            pull_down()
            order = [n.split("\n")[3].split(" - ")[0] if len(n.split("\n")) > 3 else n for n, _ in sorted(cards(), key=lambda c: c[1])]
            dates = [" ".join(n.split("\n")[:2]) for n, _ in sorted(cards(), key=lambda c: c[1])]
            note("list order top → bottom", list(zip(order, dates)), None)
            dump(drv, "recon4f_sort_probe", shot=True)
            by = {"date descending": ["SORT-TOMORROW", "SORT-TODAY", "SORT-YESTERDAY"],
                  "date ascending": ["SORT-YESTERDAY", "SORT-TODAY", "SORT-TOMORROW"],
                  "created newest first": ["SORT-TODAY", "SORT-YESTERDAY", "SORT-TOMORROW"],
                  "created oldest first": ["SORT-TOMORROW", "SORT-YESTERDAY", "SORT-TODAY"]}
            seen = [o.rsplit("-", 1)[-1] for o in order]
            seen = ["SORT-" + s for s in seen]
            match = [name for name, want in by.items() if seen == want]
            note("the order matches", match or "none of the four hypotheses", bool(match))

        if "sort" in PASSES:
            step("SORT: 3 jobs created out of date order", sort_pass)

        # ------------------------------------------------------------------ list
        def list_pass() -> None:
            if not jobs_page_open():
                note("list pass", "not on the Jobs list", False)
                return
            size = drv.get_window_size()
            drv.execute_script("mobile: dragFromToForDuration", {
                "duration": 0.3, "fromX": size["width"] / 2, "fromY": 260,
                "toX": size["width"] / 2, "toY": 700})
            time.sleep(3)  # recon only: let the refresh finish
            dump(drv, "recon4_list_top")
            seen: dict[str, int] = {}
            order: list[str] = []
            for _ in range(6):
                for name, _y in cards():
                    job_id = next((ln for ln in name.split("\n") if "QA-AUTO-R4" in ln), name)
                    if job_id not in seen:
                        order.append(job_id)
                    seen[job_id] = seen.get(job_id, 0) + 1
                drv.execute_script("mobile: dragFromToForDuration", {
                    "duration": 0.4, "fromX": 30, "fromY": 650, "toX": 30, "toY": 330})
                time.sleep(0.8)
            note("QA-AUTO-R4 cards in list order (top → bottom)", order, None)
            for kind, job in state["jobs"].items():
                shown = any(job["jobId"] in o for o in order)
                note(f"list shows {kind} ({job['status']})", shown, None)
            dump(drv, "recon4_list_bottom")
            full = [n for n, _ in cards()]
            note("card texts at the bottom", full, None)
            # back to top
            for _ in range(6):
                drv.execute_script("mobile: dragFromToForDuration", {
                    "duration": 0.4, "fromX": 30, "fromY": 330, "toX": 30, "toY": 650})
            time.sleep(1)
            texts = {n.split("\n")[3] if len(n.split("\n")) > 3 else n: n for n, _ in cards()}
            note("card texts at the top (raw)", list(texts.values()), None)
            src = drv.page_source
            for el in ET.fromstring(src).iter():
                name = el.attrib.get("name") or ""
                if "Tab 1 of 3" in name or "Tab 2 of 3" in name or "Tab 3 of 3" in name:
                    note(f"tab {name!r}", dict(el.attrib), None)
            tg = toggle()
            note("view toggle", {k: tg.get_attribute(k) for k in ("name", "label", "rect")}, True)
            # open the new job
            new = state["jobs"]["new"]
            el = drv.find_element("-ios predicate string", f"name CONTAINS '{new['jobId']}'")
            el.click()
            time.sleep(2)
            rows = dump(drv, "recon4_details_from_list")
            note("details header", [r for r in rows if new["jobId"] in r], None)
            drv.find_element("accessibility id", "Back").click()
            time.sleep(1.5)
            note("after back: cards with the new jobId", sum(new["jobId"] in n for n, _ in cards()), None)

        if "list" in PASSES:
            step("LIST: cards, statuses, order, refresh, details", list_pass)

        # ------------------------------------------------------------------ calendar
        def calendar_pass() -> None:
            toggle().click()
            time.sleep(2)
            rows = dump(drv, "recon4_calendar_today")
            days = [r for r in rows if r.startswith("StaticText") and ", 20" in r]
            note("week day cells", days, len(days) >= 7)
            note("calendar cards today", [n for n, _ in cards()], None)
            other = datetime.strptime(state["other_day"], "%Y-%m-%d")
            cell = f"{other.strftime('%A')}, {other.strftime('%B')} {other.day}, {other.year}"
            drv.find_element("accessibility id", cell).click()
            time.sleep(1.5)
            dump(drv, "recon4_calendar_other_day")
            note("cards on the other day", [n for n, _ in cards()], None)
            # an empty day in the same week (neither today nor other)
            today = datetime.now()
            sunday = today - timedelta(days=(today.weekday() + 1) % 7)
            empty = next(
                sunday + timedelta(days=i) for i in range(7)
                if (sunday + timedelta(days=i)).date() not in (today.date(), other.date())
            )
            ecell = f"{empty.strftime('%A')}, {empty.strftime('%B')} {empty.day}, {empty.year}"
            drv.find_element("accessibility id", ecell).click()
            time.sleep(1.5)
            dump(drv, "recon4_calendar_empty_day")
            # back to the other day, list and back
            drv.find_element("accessibility id", cell).click()
            time.sleep(1)
            toggle().click()
            time.sleep(1.5)
            toggle().click()
            time.sleep(1.5)
            rows = dump(drv, "recon4_calendar_after_list_roundtrip")
            note("day title after list ↔ calendar", [r for r in rows if "September" in r and ", 20" not in r], None)
            # unviewed "Updated" in the calendar (today) — look, do not open
            drv.find_element("accessibility id", f"{today.strftime('%A')}, {today.strftime('%B')} {today.day}, {today.year}").click()
            time.sleep(1.5)
            note("today's calendar cards (Updated?)", [n for n, _ in cards()], None)
            # week swipe: drag on the day strip
            strip_y = 176
            size = drv.get_window_size()
            drv.execute_script("mobile: dragFromToForDuration", {
                "duration": 0.3, "fromX": size["width"] * 0.85, "fromY": strip_y,
                "toX": size["width"] * 0.15, "toY": strip_y})
            time.sleep(2)
            rows = dump(drv, "recon4_calendar_next_week")
            note("after swipe left: days + title", [r for r in rows if "September" in r or "October" in r], None)
            for direction in ("right", "right"):
                drv.execute_script("mobile: dragFromToForDuration", {
                    "duration": 0.3, "fromX": size["width"] * 0.15, "fromY": strip_y,
                    "toX": size["width"] * 0.85, "toY": strip_y})
                time.sleep(2)
            rows = dump(drv, "recon4_calendar_prev_week")
            note("after two swipes right: days + title", [r for r in rows if "September" in r or "October" in r], None)
            toggle().click()
            time.sleep(1)

        if "calendar" in PASSES:
            step("CALENDAR", calendar_pass)

        # ------------------------------------------------------------------ tabs
        def tabs_pass() -> None:
            for tab, name in (("Tab 2 of 3", "recon4_notifications"), ("Tab 3 of 3", "recon4_profile")):
                drv.find_element("-ios predicate string", f"name ENDSWITH '{tab}'").click()
                time.sleep(2)
                dump(drv, name)
                drv.find_element("-ios predicate string", "name ENDSWITH 'Tab 1 of 3'").click()
                time.sleep(1.5)
                note(f"back to Jobs after {tab}", jobs_page_open(), jobs_page_open())

        # ------------------------------------------------------------------ calendar 2 (stale data?)
        def calendar2_pass() -> None:
            today = datetime.now()
            other = datetime.strptime(state["other_day"], "%Y-%m-%d")
            if not jobs_page_open():
                note("calendar2", "not on the Jobs list", False)
                return
            toggle().click()
            time.sleep(2)
            dump(drv, "recon4b_calendar_before_any_refresh", shot=False)
            note("A. calendar today, loaded before the seed", short(cards()), None)
            toggle().click()
            time.sleep(1)
            pull_down()
            note("B. list after pull-to-refresh", short(cards()), None)
            toggle().click()
            time.sleep(2)
            note("C. calendar today after the LIST refresh", short(cards()), None)
            dump(drv, "recon4b_calendar_after_list_refresh", shot=False)
            pull_down()
            rows = dump(drv, "recon4b_calendar_after_calendar_refresh")
            note("D. calendar today after a CALENDAR pull-to-refresh", short(cards()), None)
            drv.find_element("accessibility id", day_cell(other)).click()
            time.sleep(1.5)
            note("E. calendar other day", short(cards()), None)
            drv.find_element("accessibility id", day_cell(today)).click()
            time.sleep(1.5)
            # relaunch: a fresh load
            toggle().click()
            app.relaunch()
            _landing(drv, "ios")
            toggle().click()
            time.sleep(2.5)
            dump(drv, "recon4b_calendar_after_relaunch")
            note("F. calendar today after a relaunch", short(cards()), None)
            # unviewed from the calendar: open, back, list refresh → "Updated" gone?
            unv = state["jobs"]["unviewed"]["jobId"]
            hit = [n for n, _ in cards() if unv in n]
            note("G. unviewed card in the calendar", short([(h, 0) for h in hit]), bool(hit))
            if hit:
                drv.find_element("-ios predicate string", f"name CONTAINS '{unv}'").click()
                time.sleep(2)
                dump(drv, "recon4b_details_unviewed", shot=False)
                drv.find_element("accessibility id", "Back").click()
                time.sleep(1.5)
                note("H. calendar after back from details", short(cards()), None)
                toggle().click()
                time.sleep(1)
                pull_down()
                note("I. list after refresh (Updated gone?)", short(cards()), None)
                toggle().click()
                time.sleep(1.5)
            # week swipe from a fresh calendar: which day gets selected, and back
            size = drv.get_window_size()
            for direction, fx, tx in (("left", 0.85, 0.15), ("right", 0.15, 0.85)):
                drv.execute_script("mobile: dragFromToForDuration", {
                    "duration": 0.3, "fromX": size["width"] * fx, "fromY": 176,
                    "toX": size["width"] * tx, "toY": 176})
                time.sleep(2.5)
                rows = rows_of(drv.page_source)
                title = [r for r in rows if r.startswith("StaticText") and ", 20" not in r and "," in r][:1]
                note(f"J. swipe {direction}: day title + cards", {"title": title, "cards": short(cards())}, None)
            toggle().click()
            time.sleep(1)

        if "calendar2" in PASSES:
            step("CALENDAR 2: stale data after the list refresh?", calendar2_pass)

        if "tabs" in PASSES:
            step("TABS: Notifications / Profile", tabs_pass)

        # ------------------------------------------------------------------ links
        def links_pass() -> None:
            # 1. invalid key while signed in
            open_link(f"ctflutter://jobs/QA-AUTO-INVALID-{RUN}")
            time.sleep(4)
            dump(drv, "recon4_link_invalid_signed_in")
            for label in ("OK", "Ok"):
                found = drv.find_elements("accessibility id", label)
                if found:
                    found[0].click()
                    break
            time.sleep(1)
            # 2. link for another (reserved) phone
            other_phone = f"+1{test_data.new_user().phone_national}"
            link = assign_link(api, other_phone)
            state["links"] = state.get("links", {})
            state["links"]["other"] = {"phone": other_phone, **link}
            save_state(state)
            note("POST /job/assign/{reserved phone}", link, bool(link["key"]))
            if link["key"]:
                open_link(link["url"])
                time.sleep(5)
                app_state = drv.query_app_state(BUNDLE)
                active = drv.execute_script("mobile: activeAppInfo")
                note("https link → foreground app", {"app_state": app_state, "active": active.get("bundleId")}, None)
                dump(drv, "recon4_link_other_phone_https")
                if active.get("bundleId") != BUNDLE:
                    drv.activate_app(BUNDLE)
                    time.sleep(2)
                if "different phone" not in drv.page_source:
                    open_link(f"ctflutter://jobs/{link['key']}")
                    time.sleep(5)
                rows = dump(drv, "recon4_link_other_phone_dialog")
                note("mismatch dialog texts", [r for r in rows if r.startswith(("StaticText", "Button"))], None)
                cancel = drv.find_elements("accessibility id", "Cancel")
                if cancel:
                    cancel[0].click()
                    time.sleep(1.5)
                    note("after Cancel: Jobs list, signed in", jobs_page_open(), jobs_page_open())
            # 3. link for the test account's own phone
            own = assign_link(api, tech.phone)
            state["links"]["own"] = {"phone": "APP_USER_PHONE", **own}
            save_state(state)
            note("POST /job/assign/{own phone}", {k: v for k, v in own.items() if k != "tried"} | {"tried": [t.replace(tech.phone, "<tech phone>") for t in own["tried"]]}, bool(own["key"]))
            if own["key"]:
                before = {j["id"] for j in jobs_of_user(api, state["tech_user_id"])}
                open_link(f"ctflutter://jobs/{own['key']}")
                time.sleep(6)
                dump(drv, "recon4_link_own_phone")
                after = jobs_of_user(api, state["tech_user_id"])
                added = [j.get("jobId") for j in after if j["id"] not in before]
                note("jobs added to the technician by synchronize", added, None)
                note("technician job count before / after", f"{len(before)} / {len(after)}", None)
                state["synced_job_ids"] = [j["id"] for j in after if j["id"] not in before]
                save_state(state)
            # 4. mismatch → Log out
            if link["key"]:
                open_link(f"ctflutter://jobs/{link['key']}")
                time.sleep(5)
                out = drv.find_elements("accessibility id", "Log out")
                if out:
                    out[0].click()
                    time.sleep(3)
                    dump(drv, "recon4_after_log_out")
                    app.relaunch()
                    note("after Log out + relaunch lands on", _landing(drv, "ios"), None)
            # 5. signed out: invalid key, then the other phone's key
            if _landing(drv, "ios") != "welcome":
                app.clear_data()
                app.launch()
                _landing(drv, "ios")
            open_link(f"ctflutter://jobs/QA-AUTO-INVALID-{RUN}-2")
            time.sleep(4)
            dump(drv, "recon4_link_invalid_signed_out")
            for label in ("OK", "Ok"):
                found = drv.find_elements("accessibility id", label)
                if found:
                    found[0].click()
                    break
            time.sleep(1)
            note("signed out, after the invalid link", _landing(drv, "ios"), None)
            if link["key"]:
                open_link(f"ctflutter://jobs/{link['key']}")
                time.sleep(5)
                dump(drv, "recon4_link_other_phone_signed_out")

        if "links" in PASSES:
            step("LINKS", links_pass)

        # ------------------------------------------------------------------ links 2 (diagnosis)
        def links2_pass() -> None:
            other = (state.get("links") or {}).get("other") or {}
            probes = [("custom scheme, invalid key", f"ctflutter://jobs/QA-AUTO-INVALID-{RUN}-3")]
            if other.get("key"):
                probes += [("https redirect, other phone", other["url"]),
                           ("custom scheme, other phone", f"ctflutter://jobs/{other['key']}")]
            for label, url in probes:
                try:
                    drv.get_log("syslog")  # drain
                except Exception as exc:
                    note("syslog", f"{type(exc).__name__}: {exc}", False)
                subprocess.run(["xcrun", "simctl", "openurl", "booted", url], check=False,
                               capture_output=True, timeout=30)
                t = time.monotonic()
                found = None
                while time.monotonic() - t < 25 and not found:
                    src = drv.page_source
                    found = next((m for m in ("Link expired", "different phone", "no longer valid")
                                  if m in src), None)
                    if not found:
                        time.sleep(0.5)
                waited = round(time.monotonic() - t, 1)
                active = drv.execute_script("mobile: activeAppInfo").get("bundleId")
                lines = []
                try:
                    for entry in drv.get_log("syslog"):
                        msg = entry.get("message", "")
                        if any(k in msg for k in ("DeepLink", "ctflutter", "redirect", "app_links",
                                                  "openURL", "continueUserActivity", "flutter:")):
                            lines.append(msg[-220:])
                except Exception as exc:
                    lines.append(f"syslog unavailable: {type(exc).__name__}")
                note(f"{label}: dialog", {"found": found, "after_s": waited, "foreground": active}, bool(found))
                note(f"{label}: syslog lines", lines[-15:], None)
                dump(drv, "recon4b_link_" + label.split(",")[0].replace(" ", "_") + "_" + label.split(", ")[1].replace(" ", "_"))
                for button in ("OK", "Cancel"):
                    hit = drv.find_elements("accessibility id", button)
                    if hit:
                        hit[0].click()
                        time.sleep(1)
                        break
                if active != BUNDLE:
                    drv.activate_app(BUNDLE)
                    time.sleep(2)

        if "links2" in PASSES:
            step("LINKS 2: do links reach the app at all?", links2_pass)

        # ------------------------------------------------------------------ links 3 (https only)
        def links3_pass() -> None:
            base = "https://copsfieldservices.dev.concerttech.com/redirect/"
            other = state["links"]["other"]["url"]
            own = state["links"]["own"]["url"]
            invalid = f"{base}QA-AUTO-INVALID-{RUN}"

            def probe(label: str, url: str, markers: tuple[str, ...], wait: float = 20) -> str | None:
                subprocess.run(["xcrun", "simctl", "openurl", "booted", url], check=False,
                               capture_output=True, timeout=30)
                t = time.monotonic()
                found = None
                while time.monotonic() - t < wait and not found:
                    src = drv.page_source
                    found = next((m for m in markers if m in src), None)
                    if not found:
                        time.sleep(0.5)
                active = drv.execute_script("mobile: activeAppInfo").get("bundleId")
                rows = dump(drv, "recon4c_" + label)
                note(f"{label}", {"found": found, "after_s": round(time.monotonic() - t, 1),
                                  "foreground": active,
                                  "texts": [r.split(" value=")[0] for r in rows
                                            if r.startswith(("StaticText", "Button"))][:8]}, None)
                if active != BUNDLE:
                    drv.activate_app(BUNDLE)
                    time.sleep(2)
                return found

            markers = ("Link expired", "no longer valid", "different phone")
            if "links3-tail" in PASSES:
                pass
            elif probe("signed_in_invalid_key", invalid, markers):
                for b in ("OK", "Ok"):
                    hit = drv.find_elements("accessibility id", b)
                    if hit:
                        hit[0].click()
                        time.sleep(1)
                        break
            if "links3-tail" not in PASSES:
                before = {j["id"] for j in jobs_of_user(api, state["tech_user_id"])}
                probe("signed_in_own_phone", own, markers + ("Something",), wait=10)
                after = jobs_of_user(api, state["tech_user_id"])
                note("own-phone link: jobs added by synchronize", [j.get("jobId") for j in after if j["id"] not in before], None)
            if probe("signed_in_other_phone", other, ("different phone",)):
                tries = {
                    "accessibility id": drv.find_elements("accessibility id", "Log out"),
                    "predicate": drv.find_elements("-ios predicate string", "label == 'Log out'"),
                    "class chain": drv.find_elements("-ios class chain", "**/XCUIElementTypeButton[`label == 'Log out'`]"),
                }
                note("Log out found by", {k: len(v) for k, v in tries.items()}, any(tries.values()))
                try:
                    active_info = drv.execute_script("mobile: activeAppInfo")
                    note("active app for queries", active_info, None)
                except Exception as exc:
                    note("activeAppInfo", type(exc).__name__, False)
                drv.activate_app(BUNDLE)  # make our app the query target again
                time.sleep(1)
                again = drv.find_elements("accessibility id", "Log out")
                note("after activate_app: Log out found", len(again), bool(again))
                if again:
                    again[0].click()
                else:
                    node = next(el for el in ET.fromstring(drv.page_source).iter()
                                if el.attrib.get("name") == "Log out" and el.tag.endswith("Button"))
                    x = int(node.attrib["x"]) + int(node.attrib["width"]) / 2
                    y = int(node.attrib["y"]) + int(node.attrib["height"]) / 2
                    note("tap Log out by its bounds", (x, y), None)
                    drv.execute_script("mobile: tap", {"x": x, "y": y})
                time.sleep(3)
                note("after Log out lands on", _landing(drv, "ios"), None)
                dump(drv, "recon4c_after_log_out")
                app.relaunch()
                note("after Log out + relaunch", _landing(drv, "ios"), None)
            if _landing(drv, "ios") != "welcome":
                app.clear_data()
                app.launch()
                _landing(drv, "ios")
            if probe("signed_out_invalid_key", invalid + "-2", markers):
                for b in ("OK", "Ok"):
                    hit = drv.find_elements("accessibility id", b)
                    if hit:
                        hit[0].click()
                        time.sleep(1)
                        break
            note("signed out, after the invalid link", _landing(drv, "ios"), None)
            probe("signed_out_other_phone", other, ("Log in", "Registration", "different phone") + markers, wait=12)
            probe("signed_out_own_phone", own, ("Log in", "Registration") + markers, wait=12)

        if "links3" in PASSES or "links3-tail" in PASSES:
            step("LINKS 3: https links, signed in and out", links3_pass)

        # ------------------------------------------------------------------ links 5 (process + Log out by tap)
        def links5_pass() -> None:
            other = state["links"]["other"]["url"]
            pid_before = drv.execute_script("mobile: activeAppInfo").get("pid")
            subprocess.run(["xcrun", "simctl", "openurl", "booted", other], check=False,
                           capture_output=True, timeout=30)
            t = time.monotonic()
            seen = []
            while time.monotonic() - t < 15:
                src = drv.page_source
                shot = frame_stats(drv.get_screenshot_as_png())
                state_now = ("dialog" if "different phone" in src else
                             "jobs" if "Jobs list" in src else "other")
                seen.append((round(time.monotonic() - t, 1), state_now, shot["brand_share"]))
                if state_now == "dialog":
                    break
                time.sleep(0.3)
            pid_after = drv.execute_script("mobile: activeAppInfo").get("pid")
            note("pid before / after the https link", f"{pid_before} / {pid_after}", None)
            note("timeline (s, screen, brand share)", seen, None)
            found = drv.find_elements("accessibility id", "Log out")
            note("Log out by accessibility id", len(found), bool(found))
            node = next((el for el in ET.fromstring(drv.page_source).iter()
                         if el.attrib.get("name") == "Log out" and el.tag.endswith("Button")), None)
            if node is None:
                note("Log out in the tree", "gone", False)
                return
            x = int(node.attrib["x"]) + int(node.attrib["width"]) / 2
            y = int(node.attrib["y"]) + int(node.attrib["height"]) / 2
            drv.execute_script("mobile: tap", {"x": x, "y": y})
            time.sleep(4)
            rows = dump(drv, "recon4d_after_log_out_tap")
            note("after the Log out tap", [r.split(" value=")[0] for r in rows][:6], None)
            note("lands on", _landing(drv, "ios"), None)
            app.relaunch()
            note("after relaunch", _landing(drv, "ios"), None)

        if "links5" in PASSES:
            step("LINKS 5: process after the link, Log out by tap", links5_pass)

        # ------------------------------------------------------------------ links 6 (autoAcceptAlerts off)
        def links6_pass() -> None:
            other = state["links"]["other"]["url"]
            invalid = f"https://copsfieldservices.dev.concerttech.com/redirect/QA-AUTO-INVALID-{RUN}-6"
            note("settings before", {k: v for k, v in drv.get_settings().items() if "lert" in k}, None)
            drv.update_settings({"defaultAlertAction": ""})
            try:
                drv.update_settings({"acceptAlertButtonSelector": "", "dismissAlertButtonSelector": ""})
            except Exception:
                pass
            note("settings during", {k: v for k, v in drv.get_settings().items() if "lert" in k}, None)

            def watch(label: str, url: str, marker: str) -> bool:
                subprocess.run(["xcrun", "simctl", "openurl", "booted", url], check=False,
                               capture_output=True, timeout=30)
                t = time.monotonic()
                timeline = []
                while time.monotonic() - t < 10:
                    shown = marker in drv.page_source
                    if not timeline or timeline[-1][1] != shown:
                        timeline.append((round(time.monotonic() - t, 1), shown))
                    time.sleep(0.5)
                note(f"{label}: dialog shown over 10 s (s, shown)", timeline, timeline[-1][1])
                return timeline[-1][1]

            if watch("signed in, invalid key", invalid, "Link expired"):
                drv.find_element("accessibility id", "OK").click()
                time.sleep(1)
                note("after OK", _landing(drv, "ios"), None)
            if watch("signed in, other phone → Cancel", other, "different phone"):
                drv.find_element("accessibility id", "Cancel").click()
                time.sleep(1.5)
                note("after Cancel", _landing(drv, "ios"), None)
            if watch("signed in, other phone → Log out", other, "different phone"):
                drv.find_element("accessibility id", "Log out").click()
                time.sleep(3)
                note("after Log out", _landing(drv, "ios"), None)
                dump(drv, "recon4e_after_log_out")
                app.relaunch()
                note("after Log out + relaunch", _landing(drv, "ios"), None)
            if _landing(drv, "ios") != "welcome":
                app.clear_data()
                app.launch()
                _landing(drv, "ios")
            if watch("signed out, invalid key", invalid + "-b", "Link expired"):
                dump(drv, "recon4e_signed_out_invalid_key")
                drv.find_element("accessibility id", "OK").click()
                time.sleep(1)
            note("signed out, after the invalid link", _landing(drv, "ios"), None)
            subprocess.run(["xcrun", "simctl", "openurl", "booted", other], check=False,
                           capture_output=True, timeout=30)
            time.sleep(8)
            rows = dump(drv, "recon4e_signed_out_other_phone")
            note("signed out, other phone link → screen", [r.split(" value=")[0] for r in rows][:6], None)
            drv.update_settings({"defaultAlertAction": "accept"})

        if "links6" in PASSES:
            step("LINKS 6: link dialogs with autoAcceptAlerts off", links6_pass)

        # ------------------------------------------------------------------ revoked 2 (longer watch)
        def revoked2_pass() -> None:
            new = test_data.new_user()
            state["users"].append(new.email)
            save_state(state)
            app.clear_data()
            app.launch()
            _landing(drv, "ios")
            welcome.open_sign_up()
            reg = RegistrationPage(drv, "ios")
            reg.assert_open(15)
            reg.fill_form(new.first_name, new.last_name, new.phone_national, new.email)
            reg.choose_channel("email")
            reg.scroll_to("continue")
            reg.tap("continue")
            otp.enter_code(tech.otp)
            note("new user registered, lands on", _landing(drv, "ios"), None)
            app.terminate()
            note("API: new user deleted", api.full_delete_test_user(new.email), None)
            t = time.monotonic()
            app.launch()
            timeline = []
            while time.monotonic() - t < 60:
                src = drv.page_source
                screen = ("welcome" if "Sign up" in src else
                          "jobs-list:empty" if "No jobs" in src else
                          "jobs-list" if "Jobs list" in src else "other")
                texts = [r.split(" value=")[0] for r in rows_of(src) if r.startswith(("StaticText", "Other name='"))][:6]
                if not timeline or timeline[-1][1] != screen or timeline[-1][2] != texts:
                    timeline.append((round(time.monotonic() - t, 1), screen, texts))
                if screen == "welcome":
                    break
                time.sleep(2)
            note("deleted account: timeline over 60 s (s, screen, texts)", timeline, timeline[-1][1] == "welcome")
            dump(drv, "recon4b_revoked_after_60s")
            if "Jobs list" in drv.page_source:
                pull_down()
                dump(drv, "recon4b_revoked_after_pull")
                drv.find_element("-ios predicate string", "name ENDSWITH 'Tab 3 of 3'").click()
                time.sleep(3)
                dump(drv, "recon4b_revoked_profile")
            app.relaunch()
            time.sleep(12)
            note("next launch after 12 s", _landing(drv, "ios"), None)
            dump(drv, "recon4b_revoked_next_launch")

        if "revoked2" in PASSES:
            step("REVOKED 2: deleted account, 60 s watch", revoked2_pass)

        # ------------------------------------------------------------------ revoked session
        def revoked_pass() -> None:
            new = test_data.new_user()
            state["users"].append(new.email)
            save_state(state)
            app.clear_data()
            app.launch()
            _landing(drv, "ios")
            welcome.open_sign_up()
            reg = RegistrationPage(drv, "ios")
            reg.assert_open(15)
            reg.fill_form(new.first_name, new.last_name, new.phone_national, new.email)
            reg.choose_channel("email")
            reg.scroll_to("continue")
            reg.tap("continue")
            otp.enter_code(tech.otp)
            landed = _landing(drv, "ios")
            note("new user registered, lands on", landed, landed == "jobs-list")
            app.terminate()
            deleted = api.full_delete_test_user(new.email)
            note("API: new user deleted", deleted, bool(deleted))
            t = time.monotonic()
            app.launch()
            seen = []
            while time.monotonic() - t < 20:
                src = drv.page_source
                now = round(time.monotonic() - t, 2)
                screen = "welcome" if "Sign up" in src else "jobs-list" if "Jobs list" in src else "other"
                if not seen or seen[-1][1] != screen:
                    seen.append((now, screen))
                    if screen == "jobs-list":
                        dump(drv, "recon4_revoked_jobs_list_glimpse")
                if screen == "welcome":
                    break
            note("deleted account, cold start: screen changes (s, screen)", seen, seen[-1][1] == "welcome")
            app.relaunch()
            note("next launch lands on", _landing(drv, "ios"), None)

        if "revoked" in PASSES:
            step("REVOKED: deleted account → cold start", revoked_pass)

    finally:
        # ------------------------------------------------------------------ cleanup (always)
        print("\n==== CLEANUP", flush=True)
        for kind, job in list(state["jobs"].items()):
            resp = api._call("DELETE", f"/job/{job['id']}")
            gone = api._call("GET", f"/job/{job['id']}").status_code == 404
            note(f"deleted job {kind}", f"HTTP {resp.status_code}, GET afterwards 404: {gone}", gone)
            if gone:
                del state["jobs"][kind]
                save_state(state)
        for email in list(state["users"]):
            try:
                note(f"user {email} deleted (idempotent)", api.full_delete_test_user(email), True)
                state["users"].remove(email)
                save_state(state)
            except Exception as exc:
                note(f"user {email} cleanup", f"{type(exc).__name__}: {exc}", False)
        if state.get("synced_job_ids"):
            note("jobs attached by synchronize — NOT deleted (not ours), report to owner",
                 state["synced_job_ids"], None)
        try:
            app.clear_data()
            app.launch()
            note("left on", _landing(drv, "ios"), None)
        except Exception as exc:
            note("final reset", f"{type(exc).__name__}: {exc}", False)
        if recording:
            try:
                import base64
                (EVIDENCE / "recon4.mp4").write_bytes(base64.b64decode(drv.stop_recording_screen()))
            except Exception as exc:
                note("video", f"{type(exc).__name__}: {exc}", False)
        drv.quit()
        api.close()
        (EVIDENCE / "findings.json").write_text(json.dumps(FINDINGS, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
