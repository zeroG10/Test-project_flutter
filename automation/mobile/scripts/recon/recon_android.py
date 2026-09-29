"""Recon A1 (2026-09-29): every screen on the Android emulator — Android stage step 2 (owner's go).

Built like ``recon_8.py`` (iOS): every ``do`` attaches to the app that is already open (no relaunch,
no reinstall), runs a few actions and dumps the UiAutomator2 tree. Test data follows the harness
recipe (``fixtures/details.py``): our own files, then ``QA-AUTO-*`` jobs; cleanup deletes the files
first, then the jobs.

    cd automation/mobile
    R="uv run python scripts/recon/recon_android.py"; export PYTHONPATH=.
    $R seed    <state.json>
    $R do      <state.json> <dumps-dir> <action> [<action> …]
    $R server  <state.json> <kind>
    $R cleanup <state.json>

A target ``<q>`` is a UiAutomator query: ``Sign up`` (content-desc, else text, exact) · ``~part``
(contains) · ``cls:EditText`` (class) · ``id:<resource-id>``; ``<q>#<n>`` picks the n-th match.

Actions: ``login`` (Welcome → Login → email → OTP; the account never printed) · ``open:<kind>`` ·
``tap:<q>`` · ``tapxy:<x>,<y>`` · ``long:<q>`` · ``type:<q>:<text>`` · ``keys:<text>`` ·
``clearfocused`` · ``hidekb`` · ``swipe:up|down|left|right`` · ``pull`` · ``scrollto:<q>`` ·
``back`` (system Back) · ``appback`` (the app's Back button) · ``wait:<q>:<s>`` (prints the
seconds it took — DEV timings, plan §6) · ``gone:<q>:<s>`` · ``sleep:<s>`` · ``dump:<name>`` ·
``rows`` · ``shot:<name>`` · ``launch`` · ``terminate`` · ``bg:<s>`` · ``adb:<shell command>`` ·
``geo:<lat>,<lon>`` · ``perm:grant|revoke:<android.permission.X>`` · ``activity``.
Screenshots go to the scratchpad (``RECON_SHOTS``), never into the repo; the XML dumps are
redacted with ``redact_dumps.py`` before a commit.
"""

import json
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import recon_8  # noqa: E402  (survey ids, the test address)

PKG = "com.concerttechnologies.app.dev"
UDID = os.environ.get("ANDROID_UDID", "emulator-5554")
SHOTS = Path(os.environ.get("RECON_SHOTS", "/tmp/recon-android-shots"))
UIA = "-android uiautomator"
KINDS = {  # kind: (hour, status, survey, extra) — one job per screen family
    "full": (12, "new", "short", "pf+attachments"),
    "checkin": (11, "new", "short", ""),
    "prog": (9, "in_progress", "short", ""),
    "mo3": (8, "in_progress", "mo3", ""),
    "photo": (7, "in_progress", "photo", ""),
}


def adb(*args: str) -> str:
    out = subprocess.run(["adb", "-s", UDID, *args], capture_output=True, text=True, timeout=60)
    return (out.stdout + out.stderr).strip()


def _sel(q: str) -> list[str]:
    """UiSelector expressions for a query, tried in order."""
    q, _, _ = q.partition("#") if "#" in q and q.rsplit("#", 1)[1].isdigit() else (q, "", "")
    esc = q.replace("\\", "\\\\").replace('"', '\\"')
    if q.startswith("cls:"):
        return [f'new UiSelector().className("android.widget.{q[4:]}")']
    if q.startswith("id:"):
        return [f'new UiSelector().resourceId("{esc[3:]}")']
    if q.startswith("~"):
        return [f'new UiSelector().descriptionContains("{esc[1:]}")',
                f'new UiSelector().textContains("{esc[1:]}")']  # fmt: skip
    return [f'new UiSelector().description("{esc}")', f'new UiSelector().text("{esc}")']


def _index(q: str) -> int:
    head, _, tail = q.rpartition("#")
    return int(tail) if head and tail.isdigit() else 0


def rows_of(source: str) -> list[str]:
    rows = []
    for el in ET.fromstring(source).iter():
        a = el.attrib
        text, desc, rid = a.get("text") or "", a.get("content-desc") or "", a.get("resource-id") or ""
        flags = [f for f in ("clickable", "checkable", "checked", "scrollable", "focused", "password",
                             "selected", "long-clickable") if a.get(f) == "true"]  # fmt: skip
        if a.get("enabled") == "false":
            flags.append("DISABLED")
        if not (text or desc or rid or {"clickable", "scrollable", "checkable"} & set(flags)):
            continue
        if rid.startswith("android:id/") and not (text or desc):
            continue
        cls = (a.get("class") or el.tag).split(".")[-1]
        parts = [cls]
        if desc:
            parts.append("desc=" + repr(desc.replace("\n", "|")[:90]))
        if text:
            parts.append("text=" + repr(text.replace("\n", "|")[:60]))
        if a.get("hint"):
            parts.append("hint=" + repr(a.get("hint")[:40]))
        if rid:
            parts.append("id=" + rid)
        pkg = a.get("package") or ""
        if pkg and pkg != PKG:
            parts.append(f"pkg={pkg}")
        parts.append(" ".join(flags) + " " + (a.get("bounds") or ""))
        rows.append(" ".join(parts))
    return rows


# --- test data (the harness recipe) ----------------------------------------------------------


def seed(state: Path) -> None:
    from fixtures import details
    from fixtures.jobs import ADDRESS, COORDINATES
    from fixtures import test_data
    from helpers.field_services_api import FieldServicesApi

    api = FieldServicesApi()
    run = datetime.now().strftime("%m%d-%H%M")
    user = api.technician_user_id(test_data.tech().email)
    swept = api.sweep_test_jobs(user)
    print(f"swept leftovers: {swept}", flush=True)
    st = {"run": run, "user": user, "files": {}, "jobs": {}}
    try:
        for key, name, mime in details.FILES:
            st["files"][key] = api.upload_file(details.MEDIA / name, f"QA-AUTO-{run}-{name}", mime)
            print(f"uploaded {key}", flush=True)
        today = date.today()
        for kind, (hour, status, survey, extra) in KINDS.items():
            job_id, title = f"QA-AUTO-RA-{run}-{kind.upper()}", f"QA-AUTO recon-a {kind}"
            kw = {}
            if extra:
                kw = {"project_facilitator": details.PF,
                      "attachments": details._attachments(st["files"])}  # fmt: skip
            t0 = time.time()
            created = api.create_job(
                user_id=user, job_id=job_id, title=title,
                when=datetime(today.year, today.month, today.day, hour, 0), status=status,
                survey_id=recon_8.SURVEYS[survey], address=ADDRESS, coordinates=COORDINATES,
                description=details.DESCRIPTION, **kw,
            )  # fmt: skip
            print(f"POST /job {kind}: {time.time() - t0:.1f}s", flush=True)
            st["jobs"][kind] = {"id": str(created["id"]), "jobId": job_id, "title": title}
    finally:
        state.write_text(json.dumps(st, indent=1))


def cleanup(state: Path) -> None:
    from helpers.field_services_api import FieldServicesApi

    api, st = FieldServicesApi(), json.loads(state.read_text())
    for key, f in st.get("files", {}).items():  # files BEFORE the jobs (recon 5b)
        try:
            api.delete_file(f)
            print(f"deleted file {key}", flush=True)
        except Exception as exc:  # report and carry on — everything gets its attempt
            print(f"delete file {key}: {type(exc).__name__}: {exc}", flush=True)
    for kind, job in st.get("jobs", {}).items():
        try:
            api.delete_job(job)
            print(f"deleted job {kind}", flush=True)
        except Exception as exc:
            print(f"delete job {kind}: {type(exc).__name__}: {exc}", flush=True)
    left = [j for j in api.jobs_of_user(st["user"]) if str(j.get("jobId", "")).startswith("QA-AUTO")]
    print(f"QA-AUTO jobs left on the technician: {len(left)}")


def server(state: Path, kind: str) -> None:
    from helpers.field_services_api import FieldServicesApi

    job = json.loads(state.read_text())["jobs"][kind]
    body = FieldServicesApi().job(job["id"])
    keep = ("statusType", "updatedAt", "checkInDate", "checkOutDate", "surveyResponse")
    print(json.dumps({k: body.get(k) for k in keep}, indent=1, ensure_ascii=False)[:8000])


# --- the session -----------------------------------------------------------------------------


def do(state: Path, dumps: Path, actions: list[str]) -> None:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    from config.settings import settings

    jobs = json.loads(state.read_text())["jobs"] if state.exists() else {}
    o = UiAutomator2Options()
    o.device_name, o.platform_version = settings.android_device_name, settings.android_platform_version
    o.udid, o.no_reset, o.auto_launch = UDID, True, False
    o.set_capability("appium:newCommandTimeout", 3600)
    # A busy emulator (first Chrome run, Play services) needs longer than the default 30 s.
    o.set_capability("appium:uiautomator2ServerLaunchTimeout", 90000)
    # ONE long-lived session for the whole recon: a new session starts with an EMPTY Flutter tree
    # on a static screen (Flutter sends semantics again only on the next change — recon A1).
    sid_file = state.with_suffix(".session")
    drv = None
    if sid_file.exists():
        sid = sid_file.read_text().strip()

        class Attached(webdriver.Remote):
            def start_session(self, capabilities, browser_profile=None):  # reuse, never create
                self.session_id, self.caps = sid, {}

        try:
            drv = Attached(settings.appium_url, options=o)
            drv.current_package  # alive?
            print(f"    attached to session {sid[:8]}", flush=True)
        except Exception:
            drv = None
    if drv is None:
        drv = webdriver.Remote(settings.appium_url, options=o)
        sid_file.write_text(drv.session_id)
        print(f"    new session {drv.session_id[:8]}", flush=True)
    # Flutter redraws (spinners, the job timer) keep UiAutomator from ever seeing "idle".
    drv.update_settings({"waitForIdleTimeout": 100})
    size = drv.get_window_size()
    w, h = size["width"], size["height"]
    SHOTS.mkdir(parents=True, exist_ok=True)

    def find_all(q: str):
        for sel in _sel(q):
            found = drv.find_elements(UIA, sel)
            if found:
                return found
        return []

    def one(q: str):
        found = find_all(q)
        n = _index(q)
        if len(found) <= n:
            raise LookupError(f"no match #{n} for {q!r} ({len(found)} found)")
        print(f"    {len(found)} match(es) for {q!r}", flush=True)
        return found[n]

    def drag(x1: int, y1: int, x2: int, y2: int) -> None:
        drv.execute_script("mobile: dragGesture", {
            "startX": x1, "startY": y1, "endX": x2, "endY": y2, "speed": 2500})  # fmt: skip
        time.sleep(1.2)

    def wait_for(q: str, timeout: float, present: bool = True) -> float:
        t0 = time.time()
        while time.time() - t0 < timeout:
            if bool(find_all(q)) == present:
                return time.time() - t0
            time.sleep(0.3)
        raise TimeoutError(f"{q!r} {'did not appear' if present else 'still shown'} in {timeout}s")

    try:
        for action in actions:
            verb, _, arg = action.partition(":")
            print(f"\n>>> {action if verb not in ('type', 'keys') else verb + ':…'}", flush=True)
            try:
                if verb == "login":
                    t0 = time.time()
                    if find_all("Login"):  # from Welcome; already on Login otherwise
                        one("Login").click()
                    wait_for("cls:EditText", 20)
                    one("cls:EditText").click()
                    time.sleep(0.8)
                    drv.switch_to.active_element.send_keys(settings.app_user_email)
                    time.sleep(0.8)
                    one("Continue").click()
                    print(f"    code screen after {wait_for('~verification', 60):.1f}s", flush=True)
                    time.sleep(1)
                    drv.switch_to.active_element.send_keys(settings.app_user_otp)
                    print(f"    login done in {time.time() - t0:.1f}s total", flush=True)
                elif verb == "open":
                    job_id = jobs[arg]["jobId"]
                    drag(w // 2, int(h * 0.3), w // 2, int(h * 0.75))  # pull to refresh
                    time.sleep(2)
                    for _ in range(12):
                        if find_all("~" + job_id):
                            break
                        drag(w // 2, int(h * 0.75), w // 2, int(h * 0.4))
                    one("~" + job_id).click()
                    time.sleep(2)
                elif verb == "tap":
                    one(arg).click()
                    time.sleep(1.5)
                elif verb == "long":
                    el = one(arg)
                    drv.execute_script("mobile: longClickGesture", {"elementId": el.id, "duration": 1200})
                    time.sleep(1.5)
                elif verb == "tapxy":
                    x, _, y = arg.partition(",")
                    drv.execute_script("mobile: clickGesture", {"x": int(x), "y": int(y)})
                    time.sleep(1.5)
                elif verb == "type":
                    q, _, text = arg.rpartition(":")
                    one(q).click()
                    time.sleep(0.8)  # the field re-renders on focus: type into the focused one
                    drv.switch_to.active_element.send_keys(text)
                    time.sleep(1)
                elif verb == "keys":
                    drv.switch_to.active_element.send_keys(arg)
                    time.sleep(1)
                elif verb == "imetype":  # key-by-key through an IME: for merged Flutter fields
                    try:
                        drv.execute_script("mobile: type", {"text": arg})
                    except Exception as exc:
                        print(f"    mobile: type failed ({type(exc).__name__}) — adb input text")
                        adb("shell", "input", "text", arg.replace(" ", "%s"))
                    time.sleep(1)
                elif verb == "clearfocused":
                    drv.switch_to.active_element.clear()
                    time.sleep(1)
                elif verb == "hidekb":
                    print(f"    keyboard shown: {drv.is_keyboard_shown()}")
                    if drv.is_keyboard_shown():
                        drv.hide_keyboard()
                        time.sleep(1)
                elif verb == "swipe":
                    moves = {"up": (w // 2, int(h * 0.7), w // 2, int(h * 0.3)),
                             "down": (w // 2, int(h * 0.3), w // 2, int(h * 0.7)),
                             "left": (int(w * 0.85), h // 2, int(w * 0.15), h // 2),
                             "right": (int(w * 0.15), h // 2, int(w * 0.85), h // 2)}  # fmt: skip
                    drag(*moves[arg])
                elif verb == "pull":
                    drag(w // 2, int(h * 0.3), w // 2, int(h * 0.75))
                    time.sleep(2)
                elif verb == "scrollto":
                    for _ in range(12):
                        if find_all(arg):
                            break
                        drag(w // 2, int(h * 0.72), w // 2, int(h * 0.4))
                    print(f"    found: {bool(find_all(arg))}")
                elif verb == "back":
                    drv.back()
                    time.sleep(2)
                elif verb == "appback":
                    one("Back").click()
                    time.sleep(2)
                elif verb == "wait":
                    q, _, s = arg.rpartition(":")
                    print(f"    appeared after {wait_for(q, float(s)):.1f}s", flush=True)
                elif verb == "gone":
                    q, _, s = arg.rpartition(":")
                    print(f"    gone after {wait_for(q, float(s), present=False):.1f}s", flush=True)
                elif verb == "sleep":
                    time.sleep(float(arg))
                elif verb == "dump":
                    src = drv.page_source
                    (dumps / f"{arg}.xml").write_text(src, encoding="utf-8")
                    rows = rows_of(src)
                    print(f"---- {arg}: {len(rows)} rows")
                    print("\n".join("     " + r for r in rows), flush=True)
                elif verb == "rows":
                    print("\n".join("     " + r for r in rows_of(drv.page_source)), flush=True)
                elif verb == "shot":
                    (SHOTS / f"{arg}.png").write_bytes(drv.get_screenshot_as_png())
                    print(f"    {SHOTS / (arg + '.png')}")
                elif verb == "launch":
                    t0 = time.time()
                    drv.activate_app(PKG)
                    print(f"    activate_app {time.time() - t0:.1f}s")
                    time.sleep(3)
                elif verb == "terminate":
                    drv.terminate_app(PKG)
                    time.sleep(1)
                elif verb == "bg":
                    drv.background_app(float(arg))
                    time.sleep(1)
                elif verb == "adb":
                    print("    " + adb("shell", arg)[:2000])
                elif verb == "geo":
                    lat, _, lon = arg.partition(",")
                    print("    " + adb("emu", "geo", "fix", lon, lat))
                    time.sleep(1)
                elif verb == "mockgeo":  # Appium Settings as a MOCK provider (isMock=true)
                    lat, _, lon = arg.partition(",")
                    drv.set_location(float(lat), float(lon), 10)
                    time.sleep(1)
                elif verb == "perm":
                    how, _, perm = arg.partition(":")
                    print("    " + (adb("shell", "pm", how, PKG, perm) or "ok"))
                elif verb == "end":
                    pass  # quits the session in finally
                elif verb == "activity":
                    print(f"    {drv.current_package} / {drv.current_activity}")
                else:
                    print(f"    unknown action {verb!r}")
            except Exception as exc:  # recon: note and carry on with the next action
                msg = str(exc).splitlines()[0] if str(exc) else ""
                print(f"    FAILED {type(exc).__name__}: {msg[:300]}", flush=True)
    finally:
        if "end" in actions:  # the session stays for the next ``do`` otherwise
            drv.quit()
            sid_file.unlink(missing_ok=True)


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
