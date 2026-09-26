"""Recon 12 (2026-09-26): module 11 Notifications — step by step (owner's go, 2026-09-26).

Built on ``recon_8.py``: the same attach-to-the-open-app ``do`` with the verbs below added; test
jobs for the technician (each one sends "New job assigned"); the technician's notifications read
from the server (admin, read-only).

    cd automation/mobile
    R="uv run python scripts/recon/recon_12.py"; export PYTHONPATH=.
    $R seed <state.json> <kind> [<kind> …]     (kind "long…" gets a long title)
    $R do <state.json> <dumps-dir> <action> [<action> …]
    $R notifs <state.json>
    $R patch <state.json> <kind> <field>=<value> [...]
    $R cleanup <state.json>

Added actions: ``tab:<1|2|3>`` (the bottom tab) · ``activate:<bundle id>`` (bring an app to the
front, e.g. com.apple.Preferences) · ``appstate:<bundle id>`` · ``patch:<kind>:<field>=<value>``
(in the same session). Everything of ``recon_8.py`` works too.
"""

import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import recon_8  # noqa: E402

LONG = "QA-AUTO recon12 a very long job title that keeps going to see how the row wraps it"


def _state(state: Path) -> dict:
    return json.loads(state.read_text()) if state.exists() else {"jobs": {}}


def seed(state: Path, kinds: list[str]) -> None:
    from fixtures import test_data
    from helpers.field_services_api import FieldServicesApi

    api, st = FieldServicesApi(), _state(state)
    st.setdefault("run", datetime.now().strftime("%m%d-%H%M"))
    st.setdefault("user", api.technician_user_id(test_data.tech().email))
    today = datetime.now().replace(second=0, microsecond=0)
    for kind in kinds:
        at = today.replace(hour=9 + len(st["jobs"]) % 12, minute=0).astimezone(UTC)
        iso = at.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        title = LONG if kind.startswith("long") else f"QA-AUTO recon12 {kind}"
        body = {"title": title, "jobId": f"QA-AUTO-R12-{st['run']}-{kind.upper()}",
                "userId": st["user"], "surveyId": recon_8.SURVEYS["short"], "statusType": "new",
                "startAt": iso, "scheduleDate": iso,
                "location": {"address": recon_8.ADDRESS,
                             "coordinates": recon_8.COORDS}}  # fmt: skip
        resp = api._call("POST", "/job", json=body)
        print(f"POST /job {kind}: {resp.status_code}", flush=True)
        st["jobs"][kind] = {"id": resp.json()["id"], "jobId": body["jobId"], "title": title}
        time.sleep(1.5)  # distinct createdAt, so the order is readable
    state.write_text(json.dumps(st, indent=1))


def notifs(state: Path) -> None:
    from helpers.field_services_api import FieldServicesApi

    st = _state(state)
    resp = FieldServicesApi()._call("GET", "/notification", params={
        "page": 1, "pageSize": 100, "userId": st["user"]})  # fmt: skip
    items = resp.json().get("data") or []
    print(f"GET /notification?userId=<technician>: HTTP {resp.status_code}, {len(items)} item(s)")
    for n in items:
        job = n.get("job") or {}
        print(f"  {n.get('createdAt')} | {n.get('status'):7} | {n.get('title')!r} | "
              f"{n.get('body')!r} | job {job.get('jobId')} {job.get('statusType')} | "
              f"id {n.get('id')}")  # fmt: skip


def patch(state: Path, kind: str, pairs: list[str]) -> None:
    from helpers.field_services_api import FieldServicesApi

    job = _state(state)["jobs"][kind]
    changes = dict(p.split("=", 1) for p in pairs)
    FieldServicesApi().update_job(job["id"], job["jobId"], changes)
    print(f"PATCH /job {kind}: {changes} ok", flush=True)


def extra(drv, verb: str, arg: str, jobs: dict) -> bool:
    if verb == "tab":
        tabs = drv.find_elements(recon_8.P, f"name ENDSWITH 'Tab {arg} of 3'")
        print(f"    tab: {[t.get_attribute('name') for t in tabs]}")
        tabs[0].click()
        time.sleep(2)
    elif verb == "activate":
        drv.activate_app(arg)
        time.sleep(2)
    elif verb == "appstate":
        print(f"    {arg}: state {drv.query_app_state(arg)} (4 = foreground)")
    elif verb == "patch":
        from helpers.field_services_api import FieldServicesApi

        kind, _, pair = arg.partition(":")
        field, _, value = pair.partition("=")
        FieldServicesApi().update_job(jobs[kind]["id"], jobs[kind]["jobId"], {field: value})
        print(f"    PATCH /job {kind}: {field}={value}", flush=True)
    else:
        return False
    return True


if __name__ == "__main__":
    cmd, state_path = sys.argv[1], Path(sys.argv[2])
    if cmd == "seed":
        seed(state_path, sys.argv[3:])
    elif cmd == "notifs":
        notifs(state_path)
    elif cmd == "patch":
        patch(state_path, sys.argv[3], sys.argv[4:])
    elif cmd == "cleanup":
        recon_8.cleanup(state_path)
    elif cmd == "do":
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        recon_8.do(state_path, out, sys.argv[4:], extra=extra)
