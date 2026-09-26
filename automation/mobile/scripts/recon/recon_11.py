"""Recon 11 (2026-09-26): module 07 Submit deliverables — step by step (owner's go, Q-DLV-4).

Built on ``recon_8.py``: the same attach-to-the-open-app ``do`` with the verbs below added; six
jobs with the Short Survey created directly In progress; the job's submission fields read from the
server.

    cd automation/mobile
    R="uv run python scripts/recon/recon_11.py"; export PYTHONPATH=.
    $R seed <state.json>
    $R do <state.json> <dumps-dir> <action> [<action> …]
    $R server <state.json> <kind>
    $R submission <state.json> <kind>
    $R status <state.json> <kind> <statusType>
    $R cleanup <state.json>

Added actions: ``deliv:<Survey|Photo report|Notes>`` · ``survey:<text>`` (Short Survey: Yes + the
text, Save) · ``addphoto:<cell>:<description>`` · ``editphoto:<n>:<append>`` · ``delphoto:<n>`` ·
``addnote:<text>`` · ``editnote:<n>:<append>`` · ``delnote:<n>`` · ``setstatus:<kind>:<status>``
(PATCH in the same session) · ``watch:<s>`` (poll the tree, print each change of the buttons and
messages) · ``tapwatch:<s>:<predicate>`` (tap, then watch at once — the "Submitting" state lasts
~1 s). Everything of ``recon_8.py`` works too.
"""

import json
import sys
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import recon_8  # noqa: E402

KINDS = ("cancel", "incomplete", "full", "photos", "none", "fail")
KEYWORDS = ("Submit", "Successful", "Check out", "Deliverables", "Complete the survey", "Retry",
            "Cannot", "rror", "Offline", "Survey was updated", "internet", "Check in")  # fmt: skip


def seed(state: Path) -> None:
    from fixtures import test_data
    from helpers.field_services_api import FieldServicesApi

    api, run = FieldServicesApi(), datetime.now().strftime("%m%d-%H%M")
    user_id = api.technician_user_id(test_data.tech().email)
    today = datetime.now().replace(second=0, microsecond=0)
    jobs = {}
    for hour, kind in enumerate(KINDS, start=7):
        at = today.replace(hour=hour, minute=0).astimezone(UTC)
        iso = at.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        body = {"title": f"QA-AUTO recon11 {kind}", "jobId": f"QA-AUTO-R11-{run}-{kind.upper()}",
                "userId": user_id, "surveyId": recon_8.SURVEYS["short"],
                "statusType": "in_progress",
                "startAt": iso, "scheduleDate": iso,
                "location": {"address": recon_8.ADDRESS,
                             "coordinates": recon_8.COORDS}}  # fmt: skip
        resp = api._call("POST", "/job", json=body)
        print(f"POST /job {kind}: {resp.status_code}", flush=True)
        jobs[kind] = {"id": resp.json()["id"], "jobId": body["jobId"], "title": body["title"]}
    state.write_text(json.dumps({"run": run, "user": user_id, "jobs": jobs}, indent=1))


def server(state: Path, kind: str) -> None:
    from helpers import survey_response as sr
    from helpers.field_services_api import FieldServicesApi

    st = json.loads(state.read_text())
    body = FieldServicesApi().job(st["jobs"][kind]["id"])
    resp = body.get("surveyResponse") or {}
    fields = ("statusType", "isSubmission", "checkInDate", "submissionDate", "submissionTimezone",
              "checkOutDate", "updatedAt")  # fmt: skip
    out = {k: body.get(k) for k in fields}
    out["user is the technician"] = (body.get("user") or {}).get("id") == st["user"]
    out["photos"] = [{"id": p.get("id"), "note": p.get("note"), "tags": p.get("tags")}
                     for p in body.get("photos") or []]  # fmt: skip
    out["notes"] = [n.get("text") for n in body.get("notes") or []]
    answers = [(a.title, a.values) for a in sr.answers(resp)] if resp else None
    out["surveyResponse"] = {"status": resp.get("status"),
                             "submittedDate": resp.get("submittedDate"), "answers": answers}
    out["userLocation"] = body.get("userLocation")
    print(json.dumps(out, indent=1, ensure_ascii=False, default=str), flush=True)


def submission(state: Path, kind: str) -> None:
    from helpers.field_services_api import FieldServicesApi

    job = json.loads(state.read_text())["jobs"][kind]
    resp = FieldServicesApi()._call("GET", f"/job/{job['id']}/submission")
    print(f"GET /job/<id>/submission: HTTP {resp.status_code}")
    if resp.ok:
        body = resp.json()
        print(json.dumps({k: body.get(k) for k in ("statusType", "isSubmission", "submissionDate",
                                                   "photos", "notes")}, indent=1,
                         ensure_ascii=False, default=str)[:4000])  # fmt: skip
        print("keys:", sorted(body))


def status(state: Path, kind: str, status_type: str) -> None:
    from helpers.field_services_api import FieldServicesApi

    job = json.loads(state.read_text())["jobs"][kind]
    FieldServicesApi().update_job(job["id"], job["jobId"], {"statusType": status_type})
    print(f"PATCH /job {kind}: statusType={status_type} ok", flush=True)


def snapshot(source: str) -> tuple[str, ...]:
    """The visible buttons (with enabled) and every message that matters for the submission."""
    seen = []
    for el in ET.fromstring(source).iter():
        a, t = el.attrib, el.tag.replace("XCUIElementType", "")
        name = (a.get("name") or "").replace("\n", "|")
        if a.get("visible") != "true" or not name:
            continue
        if t == "Button" or any(k in name for k in KEYWORDS):
            row = f"{t} {name[:70]!r} en={a.get('enabled')}"
            if row not in seen:
                seen.append(row)
    return tuple(seen)


def watch(drv, seconds: float) -> None:
    start, last = time.monotonic(), None
    while time.monotonic() - start < seconds:
        snap = snapshot(drv.page_source)
        if snap != last:
            print(f"  t={time.monotonic() - start:5.2f}s " + " · ".join(snap), flush=True)
            last = snap


def extra(drv, verb: str, arg: str, jobs: dict) -> bool:
    from pages.job_details_page import JobDetailsPage
    from pages.notes_page import NotesPage
    from pages.photo_report_page import PhotoMetadata, PhotoReportPage
    from pages.survey_page import SurveyPage

    if verb == "deliv":
        JobDetailsPage(drv, "ios").tap("deliverable", text=arg)
        time.sleep(2)
    elif verb == "survey":
        s = SurveyPage(drv, "ios")
        s.tap_nth("yes", 0)
        s.fill_text(0, arg)
        s.save()
    elif verb == "addphoto":
        cell, _, desc = arg.partition(":")
        PhotoReportPage(drv, "ios").add_photo(int(cell), desc)
    elif verb == "editphoto":
        n, _, append = arg.partition(":")
        r = PhotoReportPage(drv, "ios")
        r.open_photo(int(n))
        meta = PhotoMetadata(drv, "ios")
        meta.fill_description(append)
        meta.tap("save")
        r.assert_open(20)
    elif verb == "delphoto":
        PhotoReportPage(drv, "ios").delete_photo(int(arg))
    elif verb == "addnote":
        NotesPage(drv, "ios").add_note(arg)
    elif verb == "editnote":
        n, _, append = arg.partition(":")
        notes = NotesPage(drv, "ios")
        editor = notes.edit(int(n))
        editor.type_text(append)
        editor.tap("save")
        notes.assert_open(20)
        notes.wait_toast_gone()
    elif verb == "delnote":
        NotesPage(drv, "ios").delete_from_menu(int(arg), True)
    elif verb == "setstatus":  # in the same session: fast enough for the 4 s Retry snackbar
        from helpers.field_services_api import FieldServicesApi

        kind, _, status_type = arg.partition(":")
        FieldServicesApi().update_job(jobs[kind]["id"], jobs[kind]["jobId"],
                                      {"statusType": status_type})  # fmt: skip
        print(f"    PATCH /job {kind}: statusType={status_type}", flush=True)
    elif verb == "watch":
        watch(drv, float(arg))
    elif verb == "tapwatch":
        seconds, _, pred = arg.partition(":")
        [e for e in drv.find_elements(recon_8.P, pred) if e.is_displayed()][0].click()
        watch(drv, float(seconds))
    else:
        return False
    return True


if __name__ == "__main__":
    cmd, state_path = sys.argv[1], Path(sys.argv[2])
    if cmd == "seed":
        seed(state_path)
    elif cmd == "cleanup":
        recon_8.cleanup(state_path)
    elif cmd == "server":
        server(state_path, sys.argv[3])
    elif cmd == "submission":
        submission(state_path, sys.argv[3])
    elif cmd == "status":
        status(state_path, sys.argv[3], sys.argv[4])
    elif cmd == "do":
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        recon_8.do(state_path, out, sys.argv[4:], extra=extra)
