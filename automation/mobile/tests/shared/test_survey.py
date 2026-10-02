"""Survey (module 08) — TC-SRV-001…016.

Source of every step and expectation: qa/mobile/08-survey/survey-test-cases.md (recon 8; the owner's
decisions 2026-09-24: every D-SRV accepted, Q-SRV-1…6 closed). Logic expectations are rows of the
approved qa/mobile/08-survey/survey-logic-tables.md — the tests compare the questions the form
renders with a row, they do not re-implement the app's logic. Data: fixtures/survey.py — one job per
test, directly In progress with the survey under test, deleted after it. The server copy is ``GET
/job/{id}`` → ``surveyResponse`` (helpers/survey_response.py).

Fields have no names (TD-SRV-001): ``yes(n)`` is the n-th Yes button of the form (0-based, radio
options named "Yes" count too) — every index below is worked out from the survey's definition in
qa/mobile/08-survey/survey-definitions/. Every expected value goes through ``expected(...)``.
"""

import io
from datetime import UTC, datetime

import allure
import pytest
import requests
from PIL import Image

from fixtures.survey import SURVEYS
from helpers import survey_response as sr
from helpers import waits
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.survey_page import SurveyDeleteDialog, SurveyPage

SERVER = 30.0
LIST_REFRESHES = 3
READ_ONLY_WATCH = 3.0
MAX_SIDE = 1920  # the app's photo policy: longest side, JPEG 85 (recon 8: 4032×3024 → 1920×1440)
FIBER = "Fiber installation report long title section name for tests"
FIBER_Q = ("Was the job completed successfully?", "Date of work.",
           "Which tasks were performed on site?", "Overall job status.")  # fmt: skip


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        survey = SurveyPage(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    """Refresh until the new job is listed (DEV lists a job created a moment ago a little later —
    run 2: "No jobs" after the first refresh), then open it."""
    locator = pages.jobs.locator("card", text=job.job_id)
    for _ in range(LIST_REFRESHES):
        pages.jobs.pull_to_refresh()
        if pages.jobs.driver.find_elements(*locator):
            break
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


def open_survey(pages, job, expected) -> None:
    open_job(pages, job, expected)
    pages.details.tap("deliverable", text="Survey")
    pages.survey.assert_open(SERVER)


def reopen_survey(pages) -> None:
    """From the job's details (after Save or back): open the survey again."""
    pages.details.visible("deliverable", SERVER, text="Survey")
    pages.details.tap("deliverable", text="Survey")
    pages.survey.assert_open(SERVER)


def stored(api, job, driver, since: str | None = None) -> dict:
    """The job's saved survey once the queued upload has landed (and differs from ``since``)."""
    with allure.step("server: the job's saved survey"):

        def landed(_d):
            resp = api.job(job.id).get("surveyResponse") or {}
            fresh = resp.get("updatedAt") and resp.get("updatedAt") != since
            return resp if fresh and isinstance(resp.get("items"), list) else None

        resp = waits.wait_until(driver, landed, SERVER, "no saved survey on the server", poll=2)
        allure.attach(
            str(sr.answers(resp)), name="saved answers", attachment_type=allure.attachment_type.TEXT
        )
        return resp


def local_midnight(day: int, driver) -> str:
    """How the app stores a picked date: local midnight in UTC (accepted, Q-SRV-6) — midnight in
    the DEVICE's time zone, of the device's current month: the host's zone can differ (the Mac's
    own zone switched between +03:00 and +08:00 during a final Android run, and the emulator kept
    the one it booted with — TC-SRV-002 / -009 off by 5 h, run final-t1)."""
    now = datetime.fromisoformat(driver.get_device_time("YYYY-MM-DDTHH:mm:ssZ"))
    picked = datetime(now.year, now.month, day, tzinfo=now.tzinfo)
    return picked.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def section_title(api, kind: str, index: int = 0) -> str:
    """The title of the survey's ``index``-th section, from the template (the entries' names)."""
    template = api.survey(SURVEYS[kind])
    return [i["section"]["title"] for i in template["items"] if i.get("section")][index]


# --------------------------------------------------------------------------------------
# Field types, validation, save
# --------------------------------------------------------------------------------------

SAVE_CHKS = ("CHK-SRV-004", "CHK-SRV-015", "CHK-SRV-016", "CHK-SRV-017", "CHK-SRV-036",
             "CHK-SRV-037", "CHK-SRV-040")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-001")
@pytest.mark.chk(*SAVE_CHKS)
@allure.tag(*SAVE_CHKS)
@allure.title(
    "TC-SRV-001 Short Survey: Save stays disabled until every question is answered; Save stores "
    "the answers and returns to the job"
)
def test_short_survey_saved(
    survey_job, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, s = survey_job("short"), pages.survey
    open_survey(pages, job, expected)
    s.visible("survey-name", text=expected("Short Survey"))
    s.expect_titles([expected("Good?"), expected("Text?")])
    s.expect_disabled("save")
    s.tap_nth("yes", 0)
    s.expect_disabled("save")
    s.fill_text(0, "QA-AUTO short answer")
    s.expect_enabled("save")
    evidence.checkpoint("short-filled")
    s.save()
    pages.details.expect_header(expected(job.title_line), SERVER)
    resp = stored(field_services_api, job, driver)
    template = field_services_api.survey(SURVEYS["short"])
    with allure.step("expect the saved survey: the job, the template's questions, the answers"):
        assert resp.get("jobId") == expected(job.job_id), f"jobId {resp.get('jobId')!r}"
        ids = {q["question"]["id"] for q in template["items"] if q.get("question")}
        assert {a.id for a in sr.answers(resp)} == ids, f"question ids {sr.answers(resp)}"
        assert sr.answer(resp, "Good?").values == [True]
        assert sr.answer(resp, "Text?").values == [expected("QA-AUTO short answer")]
        assert resp.get("status") == expected("draft"), f"status {resp.get('status')!r}"


TYPES_CHKS = ("CHK-SRV-005", "CHK-SRV-006", "CHK-SRV-007", "CHK-SRV-019", "CHK-SRV-020",
              "CHK-SRV-037", "CHK-SRV-038", "CHK-SRV-057")  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-002")
@pytest.mark.chk(*TYPES_CHKS)
@allure.tag(*TYPES_CHKS)
@allure.title("TC-SRV-002 Mo3: every field type takes its answer, and the server stores each value")
def test_all_field_types(
    survey_job, gallery_photos, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, s = survey_job("mo3"), pages.survey
    open_survey(pages, job, expected)
    s.tap_nth("no", 0)
    s.tap_nth("yes", 0)
    s.expect_selected("yes", 0)
    s.expect_selected("no", 0, selected=False)
    s.tap_nth("option", 0, text="Completed")
    s.tap_nth("option", 0, text="Partially completed")
    s.expect_selected("option", 0, selected=False, text="Completed")
    s.expect_selected("option", 0, text="Partially completed")
    for task in ("Cable installation", "Testing"):
        s.tap_nth("checkbox", 0, text=task)
        s.expect_selected("checkbox", 0, text=task)
    s.tap_nth("checkbox", 0, text="ON!!!")
    s.visible("required-error", 5)  # the "Other" text is required at once (recon 8)
    s.fill_text(0, "QA-AUTO other task")
    s.wait_gone("required-error", 5)
    s.fill_text(1, "QA-AUTO notes")
    s.add_photo(0, 1, "QA-AUTO survey photo")
    s.set_date(15)
    s.set_time(9, 45)
    evidence.checkpoint("all-types-filled")
    s.save()
    resp = stored(field_services_api, job, driver)
    with allure.step("expect each value as the server stores it"):
        assert sr.answer(resp, "Was the job completed successfully?").values == [True]
        assert sr.answer(resp, "What is the current job result?").values == [
            expected("Partially completed")
        ]
        tasks = sr.answer(resp, "Which tasks were performed on site?").values
        assert tasks == [
            expected("Cable installation"),
            expected("Testing"),
            expected("QA-AUTO other task"),
        ], tasks
        assert sr.answer(resp, "Add technician notes").values == [expected("QA-AUTO notes")]
        photo = sr.answer(resp, "Upload a photo of the completed work")
        assert photo.notes == [expected("QA-AUTO survey photo")], photo.files
        assert sr.answer(resp, "Select the work completion date").values == [
            local_midnight(15, driver)
        ]
        assert sr.answer(resp, "Select the work completion time").values == [expected("09:45")]


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-003")
@pytest.mark.chk("CHK-SRV-008", "CHK-SRV-009")
@allure.tag("CHK-SRV-008", "CHK-SRV-009")
@allure.title("TC-SRV-003 A text answer takes 500 characters; the 501st is refused")
def test_text_limit(survey_job, ui_login, pages, expected):
    job, s = survey_job("short"), pages.survey
    text = ("QA-AUTO text limit " * 30)[:501]
    open_survey(pages, job, expected)
    s.fill_text(0, text)
    with allure.step("expect exactly the first 500 characters and 'No characters remaining'"):
        shown = s.text_value(0)
        assert len(shown) == 500 and shown == text[:500], f"{len(shown)} characters kept"
        assert s.names("counter") == [expected("No characters remaining")], s.names("counter")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-004")
@pytest.mark.chk("CHK-SRV-001", "CHK-SRV-002", "CHK-SRV-003", "CHK-SRV-004", "CHK-SRV-015")
@allure.tag("CHK-SRV-001", "CHK-SRV-002", "CHK-SRV-003", "CHK-SRV-004", "CHK-SRV-015")
@allure.title(
    "TC-SRV-004 Validation: no required marker; 'This field is required' after an emptied field, "
    "gone when filled"
)
def test_required_validation(survey_job, ui_login, pages, expected, evidence):
    job, s = survey_job("short"), pages.survey
    open_survey(pages, job, expected)
    s.expect_titles([expected("Good?"), expected("Text?")])
    with allure.step("expect no required marker in the question labels (D-SRV-1, accepted)"):
        marked = [lab for lab in s.labels() if "*" in lab or "equired" in lab]
        assert not marked, f"a marker: {marked}"
    s.fill_text(0, "abc")
    s.clear_text(0)
    s.visible("required-error", 5)
    evidence.checkpoint("required-error")
    s.fill_text(0, "QA-AUTO text")
    s.wait_gone("required-error", 5)
    s.expect_disabled("save")
    s.tap_nth("yes", 0)
    s.expect_enabled("save")


AUTOSAVE_CHKS = ("CHK-SRV-010", "CHK-SRV-011", "CHK-SRV-012", "CHK-SRV-013", "CHK-SRV-014",
                 "CHK-SRV-039")  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-005")
@pytest.mark.chk(*AUTOSAVE_CHKS)
@allure.tag(*AUTOSAVE_CHKS)
@allure.title(
    "TC-SRV-005 Auto-save: answers survive back, background and a restart; a new Save updates the "
    "stored survey"
)
def test_autosave(survey_job, ui_login, field_services_api, driver, pages, expected):
    job, s = survey_job("short"), pages.survey
    open_survey(pages, job, expected)
    s.tap_nth("yes", 0)
    s.fill_text(0, "QA-AUTO kept")

    def expect_kept(where: str) -> None:
        with allure.step(f"expect the answers kept ({where})"):
            s.expect_selected("yes", 0)
            assert s.text_value(0) == expected("QA-AUTO kept"), s.text_value(0)

    s.tap("back")
    reopen_survey(pages)
    expect_kept("after back")
    ui_login.background(5)
    s.assert_open(SERVER)
    expect_kept("after 5 s in the background")
    ui_login.relaunch()
    pages.jobs.assert_open(SERVER)
    open_survey(pages, job, expected)
    expect_kept("after a restart")
    s.save()
    first = stored(field_services_api, job, driver)
    reopen_survey(pages)
    s.tap_nth("no", 0)
    s.save()
    second = stored(field_services_api, job, driver, since=first["updatedAt"])
    with allure.step("expect the same saved survey, updated"):
        assert second["id"] == first["id"], "a second survey response was created"
        assert sr.answer(second, "Good?").values == [False]
        assert second["updatedAt"] > first["updatedAt"], (first["updatedAt"], second["updatedAt"])


# --------------------------------------------------------------------------------------
# Logic — rows of the approved logic tables
# --------------------------------------------------------------------------------------

MO5 = ("What issue type was identified on site?", "Q2 Describe the site access issue",
       "Q3 Select the missing or damaged equipment", "Q4 Select the follow-up visit date",
       "Q5 Enter customer-related notes")  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-006")
@pytest.mark.chk("CHK-SRV-041", "CHK-SRV-042")
@allure.tag("CHK-SRV-041", "CHK-SRV-042")
@allure.title(
    "TC-SRV-006 Mo5: each answer shows exactly the questions of its logic-table row, also after "
    "changing it"
)
def test_mo5_logic(survey_job, ui_login, pages, expected):
    job, s = survey_job("mo5"), pages.survey
    q1, q2, q3, q4, q5 = (expected(t) for t in MO5)
    open_survey(pages, job, expected)
    s.expect_titles([q1, q2, q3, q4, q5])  # MO5-0
    rows = (
        ("Access issue", [q1, q2, q3, q4, q5]),  # MO5-1
        ("Equipment issue", [q1, q3, q4, q5]),  # MO5-2
        ("Customer issue", [q1, q2, q3, q4, q5]),  # MO5-3
        ("No issue found", [q1, q4, q5]),  # MO5-4
        ("Access issue", [q1, q2, q3, q4, q5]),  # MO5-5: the hidden ones come back
    )
    for answer, visible in rows:
        s.tap_nth("option", 0, text=answer)
        s.expect_titles(visible)


T8 = ("S1Q3 Was the site ready?", "S2Q5 Which tasks were completed?", "S3Q6 What blocked the work?",
      "S3Q7 Describe the blocker", "S4Q9 Add final summary",
      "S4Q8 Upload evidence photo")  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-007")
@pytest.mark.chk("CHK-SRV-041", "CHK-SRV-042", "CHK-SRV-043")
@allure.tag("CHK-SRV-041", "CHK-SRV-042", "CHK-SRV-043")
@allure.title("TC-SRV-007 T8: 'No' hides the 'Site Ready' section; 'Yes' brings it back")
def test_t8_section_logic(survey_job, ui_login, pages, expected):
    job, s = survey_job("t8"), pages.survey
    titles = [expected(t) for t in T8]
    open_survey(pages, job, expected)
    s.tap_nth("no", 0)
    s.expect_titles([titles[0], *titles[2:]])  # T8-2
    assert s.count("section", text=expected("S2 Site Ready Path")) == 0, (
        "the S2 section is still drawn"
    )
    s.tap_nth("yes", 0)
    s.expect_titles(titles)  # T8-3
    assert s.count("section", text=expected("S2 Site Ready Path")) == 1, (
        "the S2 section did not come back"
    )


END = ("End Survey", "Q1 Enter the work order ID", "Q2 text Select the visit date",
       "Q3 photo Question",
       "Q4 Select the technician arrival time", "Q5 time Question", "Q6 date Question",
       "Q7 yes/no Question", "Q8 Radio Question", "Q9 test question", "Q10 photo question",
       "Q11 Checkbox Question", "Bad?", "Good?", "Problems?")  # fmt: skip
END_CHKS = ("CHK-SRV-041", "CHK-SRV-042", "CHK-SRV-044", "CHK-SRV-045")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-008")
@pytest.mark.chk(*END_CHKS)
@allure.tag(*END_CHKS)
@allure.title(
    "TC-SRV-008 End Survey: an 'end' answer hides everything after it, removes 'Repeat section', "
    "and the survey saves with only what is visible"
)
def test_end_survey(survey_job, ui_login, field_services_api, driver, pages, expected, evidence):
    job, s = survey_job("end"), pages.survey
    titles = [expected(t) for t in END]
    open_survey(pages, job, expected)
    s.tap_nth("no", 0)  # End Survey = No
    s.expect_titles(titles)  # END-2
    s.tap_nth("yes", 1)  # entry 1: Q1 Enter the work order ID = Yes → end
    s.expect_titles(titles[:2])  # END-3
    assert s.count("repeat") == 0, "'Repeat section' after the survey ended"
    s.tap_nth("yes", 0)  # End Survey = Yes → end
    s.expect_titles(titles[:1])  # END-1
    s.expect_enabled("save")
    evidence.checkpoint("end-survey-ended")
    s.save()
    resp = stored(field_services_api, job, driver)
    with allure.step("expect only the visible question saved"):
        saved = sr.answers(resp)
        assert [(a.title, a.values) for a in saved] == [(expected("End Survey"), [True])], saved
        assert sr.blocks(resp) == [], f"hidden sections saved: {sr.blocks(resp)}"


def fill_fiber_entry(s, n: int, toggle: str, toggle_index: int, day: int, task: str) -> None:
    """One entry of "Fiber installation report": the toggle, the date, a task and
    "Completed as planned"."""
    s.tap_nth(toggle, toggle_index)
    s.set_date(day)  # the first empty date field is this entry's
    s.tap_nth("checkbox", n, text=task)
    s.tap_nth("option", n, text="Completed as planned")


def fiber_start(s, entries: int = 1) -> None:
    """Q1 = No (FIB-2), the comments, entry 1 filled; ``entries`` − 1 more (empty) entries added."""
    s.tap_nth("no", 0)  # Are there any rooms…? = No → "Room Information" hidden
    s.fill_text(0, "QA-AUTO comments")
    fill_fiber_entry(s, 0, "yes", 1, 10, "Splicing")
    for _ in range(entries - 1):
        s.tap_nth("repeat", 0)  # the Fiber section's (the Room section is hidden)


FIBER_CHKS = (
    "CHK-SRV-037",
    "CHK-SRV-041",
    "CHK-SRV-044",
    "CHK-SRV-045",
    "CHK-SRV-048",
    "CHK-SRV-054",
)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-009")
@pytest.mark.chk(*FIBER_CHKS)
@allure.tag(*FIBER_CHKS)
@allure.title(
    "TC-SRV-009 Fiber Site Survey end to end: a hidden section, two entries of a repeatable "
    "section, an 'end' in the copy; editing adds no duplicate"
)
def test_fiber_end_to_end(
    survey_job, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, s = survey_job("fiber"), pages.survey
    fiber = [expected(t) for t in FIBER_Q]
    head = [
        expected("Are there any rooms to survey on this site?"),
        expected("Additional comments"),
    ]
    open_survey(pages, job, expected)
    fiber_start(s, entries=2)
    s.expect_titles(head + fiber * 3)  # FIB-2 with two Fiber entries and the copy
    assert s.entry_headers(FIBER) == [expected(FIBER), expected(f"{FIBER} 2"), f"{FIBER} (Copy)"]
    fill_fiber_entry(s, 1, "no", 2, 11, "Testing")
    s.tap_nth("yes", 3)  # (Copy): Was the job completed successfully? = Yes → end
    s.expect_titles(head + fiber * 2 + fiber[:1])  # FIB-3
    evidence.checkpoint("fiber-filled")
    s.save()
    resp = stored(field_services_api, job, driver)
    with allure.step(
        "expect one block per entry, the copy with its first answer only, no Room Information"
    ):
        assert sr.blocks(resp) == [
            expected(FIBER),
            expected(f"{FIBER} 2"),
            expected(f"{FIBER} (Copy)"),
        ]
        assert sr.answer(resp, "Are there any rooms to survey on this site?").values == [
            expected("No")
        ]
        assert sr.answer(resp, "Additional comments").values == [expected("QA-AUTO comments")]
        for block, toggle, day, task in (
            (FIBER, True, 10, "Splicing"),
            (f"{FIBER} 2", False, 11, "Testing"),
        ):
            assert sr.answer(resp, FIBER_Q[0], block).values == [toggle]
            assert sr.answer(resp, FIBER_Q[1], block).values == [local_midnight(day, driver)]
            assert sr.answer(resp, FIBER_Q[2], block).values == [expected(task)]
            assert sr.answer(resp, FIBER_Q[3], block).values == [expected("Completed as planned")]
        copy = [a for a in sr.answers(resp) if a.block == f"{FIBER} (Copy)"]
        assert [(a.title, a.values) for a in copy] == [(FIBER_Q[0], [True])], copy
    reopen_survey(pages)
    s.tap_nth("option", 0, text="Partially completed")  # entry 1
    s.save()
    edited = stored(field_services_api, job, driver, since=resp["updatedAt"])
    with allure.step("expect the edit under the same entry, no duplicate block"):
        assert sr.blocks(edited) == sr.blocks(resp), sr.blocks(edited)
        assert sr.answer(edited, FIBER_Q[3], FIBER).values == [expected("Partially completed")]


# --------------------------------------------------------------------------------------
# CR-2 repeatable sections
# --------------------------------------------------------------------------------------

ENTRY_CHKS = ("CHK-SRV-046", "CHK-SRV-047", "CHK-SRV-048", "CHK-SRV-055")
TOGGLES_PER_ENTRY = 5  # Repeatable Single: Q1, Q4, Q7, Bad?, Good?


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-010")
@pytest.mark.chk(*ENTRY_CHKS)
@allure.tag(*ENTRY_CHKS)
@allure.title(
    "TC-SRV-010 CR-2: the first entry is named after the section; 'Repeat section' adds numbered "
    "entries; each entry keeps its answers, also after a restart"
)
def test_repeat_entries(survey_job, ui_login, field_services_api, pages, expected, evidence):
    job, s = survey_job("rep1"), pages.survey
    title = section_title(field_services_api, "rep1")
    open_survey(pages, job, expected)
    assert s.entry_headers(title) == [expected(title)], s.entry_headers(title)
    assert s.count("delete-entry") == 0, "the first entry can be deleted"
    s.tap_nth("repeat", 0)
    s.tap_nth("repeat", 0)  # the button sits on the last entry
    three = [expected(title), expected(f"{title} 2"), expected(f"{title} 3")]
    assert s.entry_headers(title) == three, s.entry_headers(title)
    assert s.count("delete-entry") == 2, (
        f"{s.count('delete-entry')} delete buttons for 2 added entries"
    )
    s.tap_nth("yes", 0)  # entry 1: Q1 Enter the work order ID = Yes
    s.tap_nth("no", TOGGLES_PER_ENTRY)  # entry 2: the same question = No

    def expect_answers(where: str) -> None:
        with allure.step(f"expect each entry's own answer ({where})"):
            s.expect_selected("yes", 0)
            s.expect_selected("no", TOGGLES_PER_ENTRY)
            s.expect_selected("yes", 2 * TOGGLES_PER_ENTRY, selected=False)
            s.expect_selected("no", 2 * TOGGLES_PER_ENTRY, selected=False)

    expect_answers("now")
    evidence.checkpoint("three-entries")
    ui_login.relaunch()
    pages.jobs.assert_open(SERVER)
    open_survey(pages, job, expected)
    assert s.entry_headers(title) == three, s.entry_headers(title)
    expect_answers("after a restart")


DELETE_MESSAGE = "Are you sure you want to delete this section? All data will be lost."


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-011")
@pytest.mark.chk("CHK-SRV-049", "CHK-SRV-050")
@allure.tag("CHK-SRV-049", "CHK-SRV-050")
@allure.title(
    "TC-SRV-011 CR-2: deleting an entry — no dialog when empty; with data: Cancel keeps it, Delete "
    "removes it and the rest renumber; a deleted entry is not saved"
)
def test_delete_entries(
    survey_job, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, s = survey_job("fiber"), pages.survey
    open_survey(pages, job, expected)
    fiber_start(s, entries=3)
    s.tap_nth("yes", 2)  # entry 2: Yes
    s.tap_nth("no", 3)  # entry 3: No
    assert s.entry_headers(FIBER)[:3] == [
        expected(FIBER),
        expected(f"{FIBER} 2"),
        expected(f"{FIBER} 3"),
    ]
    dialog = SurveyDeleteDialog(driver, s.platform)
    s.tap_nth("delete-entry", 0)  # entry 2 (has data) → the dialog
    dialog.visible("title", 5)
    dialog.visible("message", text=expected(DELETE_MESSAGE))
    evidence.checkpoint("delete-dialog")
    dialog.tap("cancel")
    dialog.wait_gone("title", 5)
    assert len([h for h in s.entry_headers(FIBER) if "(Copy)" not in h]) == 3, (
        "Cancel removed the entry"
    )
    s.delete_entry(0, confirm=True)
    assert s.entry_headers(FIBER)[:2] == [expected(FIBER), expected(f"{FIBER} 2")], s.entry_headers(
        FIBER
    )
    s.expect_selected("no", 2)  # the old entry 3 (No) is entry 2 now
    s.tap_nth("repeat", 0)
    s.delete_entry(1, confirm=None)  # an empty entry: removed without a dialog
    s.delete_entry(0, confirm=True)
    assert s.entry_headers(FIBER) == [expected(FIBER), f"{FIBER} (Copy)"], s.entry_headers(FIBER)
    assert s.count("delete-entry") == 0, "the first entry can be deleted"
    s.tap_nth("yes", 2)  # (Copy) = Yes → end
    s.save()
    resp = stored(field_services_api, job, driver)
    with allure.step("expect exactly one 'Fiber installation report' entry saved"):
        assert sr.blocks(resp) == [expected(FIBER), expected(f"{FIBER} (Copy)")], sr.blocks(resp)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-012")
@pytest.mark.chk("CHK-SRV-051")
@allure.tag("CHK-SRV-051")
@allure.title("TC-SRV-012 CR-2: an incomplete entry keeps Save disabled")
def test_incomplete_entry_blocks_save(survey_job, ui_login, pages, expected, evidence):
    job, s = survey_job("fiber"), pages.survey
    open_survey(pages, job, expected)
    fiber_start(s, entries=2)
    s.tap_nth("yes", 3)  # (Copy) = Yes → end; entry 2 is still empty
    s.expect_disabled("save")
    evidence.checkpoint("entry-2-empty")
    fill_fiber_entry(s, 1, "no", 2, 11, "Testing")
    s.expect_enabled("save")


TWO_CHKS = ("CHK-SRV-041", "CHK-SRV-052")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-013")
@pytest.mark.chk(*TWO_CHKS)
@allure.tag(*TWO_CHKS)
@allure.title(
    "TC-SRV-013 Repeatable TWO: logic applies per entry; a rule leads into the next section; "
    "backward rules as approved; 'end' removes the rest"
)
def test_two_sections_logic(survey_job, ui_login, field_services_api, pages, expected, evidence):
    job, s = survey_job("two"), pages.survey
    s1 = section_title(field_services_api, "two", 0)
    open_survey(pages, job, expected)
    # "No" buttons — S1 entry 1: 0 Q1, 1 Q4, 2 Q7, 3 Bad?, 4 Good?;
    # S2 once it starts at Q4: 5 Q4, 6 Q7, 7 Bad?, 8 Good?, 9 Finish?
    s.tap_nth("no", 4)  # TWO-12: Good?  Redirect to S2 = No
    with allure.step("expect TWO-12: 'Problems?' gone, S2 starts at 'S2 Q4 …'"):
        shown = s.titles()
        assert (
            expected("Problems?") not in shown and "S2 Q1 Enter the work order ID" not in shown
        ), shown
        assert "S2 Q4 Select the technician arrival time" in shown, shown
    s.tap_nth("no", 9)  # TWO-14: S2 Finish? = No (backward — ignored)
    s.expect_titles(shown)
    s.tap_nth("no", 8)  # TWO-15: S2 Good? … Redirect to S1 Q1 = No (backward, owner: as the app)
    with allure.step("expect TWO-15: 'S2 Finish?' gone; the rest of the survey stays"):
        after = s.titles()
        assert "S2 Finish?" not in after and "Question 1" in after, after
        assert "S3 Q1 Enter the work order ID" in after, after
    s.tap_nth("no", 0)  # TWO-1: entry 1 Q1 = No
    with allure.step("expect 'Q2 text …' gone from entry 1"):
        assert s.titles().count("Q2 text Select the visit date") == 0, s.titles()
    s.tap_nth("repeat", 0)  # S1's
    with allure.step("expect TWO-8: entry 2 of S1 shows 'Q2 text …'"):
        assert s.entry_headers(s1) == [expected(s1), expected(f"{s1} 2")], s.entry_headers(s1)
        assert s.titles().count("Q2 text Select the visit date") == 1, s.titles()
    evidence.checkpoint("two-per-entry")
    s.tap_nth("no", 3)  # TWO-9: entry 1 Bad? = No → end
    with allure.step("expect TWO-9: S2, Question 1…7 and S3 gone; no 'Repeat section'"):
        ended = s.titles()
        rest = [t for t in ended if t.startswith(("S2 ", "S3 ", "Question "))]
        assert not rest, f"still shown after the end: {rest}"
        assert s.count("repeat") == 0, "'Repeat section' after the survey ended"


# --------------------------------------------------------------------------------------
# Photos, empty survey, read-only
# --------------------------------------------------------------------------------------

PHOTO_CHKS = (
    "CHK-SRV-019",
    "CHK-SRV-020",
    "CHK-SRV-021",
    "CHK-SRV-022",
    "CHK-SRV-038",
    "CHK-SRV-053",
)
PHOTOS = ("QA-AUTO overview 1", "QA-AUTO overview 2", "QA-AUTO close-up", "QA-AUTO room photo")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-014")
@pytest.mark.chk(*PHOTO_CHKS)
@allure.tag(*PHOTO_CHKS)
@allure.title(
    "TC-SRV-014 Photos: required, several per question, kept after leaving, compressed, and stored "
    "under their question / entry"
)
def test_photos(
    survey_job, gallery_photos, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, s = survey_job("photo"), pages.survey
    open_survey(pages, job, expected)
    s.fill_text(0, "QA-AUTO room")  # Per-room photos: Room name
    s.fill_text(1, "QA-AUTO comments")  # Additional comments
    s.expect_disabled("save")  # no photo yet — photos are required (owner, Q-SRV-1)
    for upload, cell, note in (
        (0, 0, PHOTOS[0]),
        (0, 1, PHOTOS[1]),
        (1, 1, PHOTOS[2]),
        (2, 1, PHOTOS[3]),
    ):
        s.add_photo(upload, cell, note)
    s.tap("back")
    reopen_survey(pages)
    with allure.step("expect the 4 thumbnails after leaving and returning"):
        for note in PHOTOS:
            assert s.count("thumbnail", text=expected(note)) == 1, f"no thumbnail {note!r}"
    evidence.checkpoint("photos-kept")
    s.save()
    resp = stored(field_services_api, job, driver)
    with allure.step("expect each photo under its question / entry"):
        assert sr.answer(resp, "Site overview photos").notes == [
            expected(PHOTOS[0]),
            expected(PHOTOS[1]),
        ]
        close_up = sr.answer(resp, "Equipment close-up (add a note if something looks off)")
        assert close_up.notes == [expected(PHOTOS[2])], close_up.files
        room = sr.answer(resp, "Room photos", block="Per-room photos")
        assert room.notes == [expected(PHOTOS[3])], room.files
    large = sr.answer(resp, "Site overview photos").files[0]
    with allure.step(f"expect the 4032×3024 photo stored with its longest side ≤ {MAX_SIDE} px"):
        body = requests.get(large["location"], timeout=SERVER)
        assert body.status_code == 200, f"stored photo: HTTP {body.status_code}"
        size = Image.open(io.BytesIO(body.content)).size
        assert max(size) == MAX_SIDE and size == (1920, 1440), f"stored {size}"


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-015")
@pytest.mark.chk("CHK-SRV-056")
@allure.tag("CHK-SRV-056")
@allure.title("TC-SRV-015 A survey with no questions opens and saves")
def test_empty_survey(survey_job, ui_login, field_services_api, driver, pages, expected):
    job, s = survey_job("empty"), pages.survey
    open_survey(pages, job, expected)
    s.expect_titles([])
    s.expect_enabled("save")
    s.save()
    pages.details.expect_header(expected(job.title_line), SERVER)
    resp = stored(field_services_api, job, driver)
    assert sr.answers(resp) == [], sr.answers(resp)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-SRV-016")
@pytest.mark.chk("CHK-SRV-033", "CHK-SRV-034", "CHK-SRV-035")
@allure.tag("CHK-SRV-033", "CHK-SRV-034", "CHK-SRV-035")
@allure.title(
    "TC-SRV-016 After the deliverables are submitted the survey cannot be opened or changed"
)
def test_submitted_survey_read_only(survey_job, ui_login, pages, expected, evidence):
    job = survey_job("short", status="submitted")
    open_job(pages, job, expected)
    pages.details.tap("deliverable", text=expected("Survey"))
    with allure.step(f"expect no survey screen for {READ_ONLY_WATCH:.0f}s (read-only)"):
        assert not pages.survey.is_visible("header", READ_ONLY_WATCH), "the survey opened"
    evidence.checkpoint("submitted-read-only")
    pages.details.expect_header(expected(job.title_line))
