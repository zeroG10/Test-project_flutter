"""Submit deliverables (module 07) — TC-DLV-001…006.

Source of every step and expectation:
qa/mobile/07-submit-deliverables/submit-deliverables-test-cases.md (recon 11; the owner's decisions
2026-09-26). Data: fixtures/survey.py — one job per test, directly In progress with the Short
Survey, deleted after it.

DEV answers ``POST /job/{id}/submit`` with 500 although the submission is recorded (COPS; the owner,
Q-DLV-5: expected for now). The app then shows "Server error. Try again later." and keeps the job In
progress until it is opened again. So the tests check the server and the reopened job, never that
error; TC-DLV-004 — the app's reaction to a successful answer — reports ``Blocked`` while the 500
stands. The "all deleted" case is a remark, not a test (D-DLV-7). Every expected value goes
through ``expected(...)``.
"""

import contextlib
from datetime import datetime, timedelta

import allure
import pytest
from selenium.common.exceptions import TimeoutException

from helpers import survey_response as sr
from helpers import waits
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.notes_page import NotesPage
from pages.photo_report_page import TOAST, PhotoMetadata, PhotoReportPage
from pages.submit_dialog_page import SubmitDialog
from pages.survey_page import SurveyPage

SERVER = 30.0
LIST_REFRESHES = 3
READ_ONLY_WATCH = 3.0
RETRY_SETTLE = 0.3  # the failed submission's Retry lives ~4 s: act on it at once (recon 11)
CLOCK = timedelta(seconds=30)  # the server's submissionDate vs the tap (device and server clocks)
# The environment probe of TC-DLV-004 (Q-DLV-5) — not an oracle, so not through expected()
DEV_SUBMIT_ERROR = "Server error. Try again later."


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        dialog = SubmitDialog(driver, platform)
        survey = SurveyPage(driver, platform)
        report = PhotoReportPage(driver, platform)
        meta = PhotoMetadata(driver, platform)
        notes = NotesPage(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    """Refresh until DEV lists the new job, then open it."""
    locator = pages.jobs.locator("card", text=job.job_id)
    for _ in range(LIST_REFRESHES):
        pages.jobs.pull_to_refresh()
        if pages.jobs.driver.find_elements(*locator):
            break
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


def complete_survey(pages, expected, text: str) -> None:
    """The Short Survey: Yes, ``text``, Save → back on the details."""
    pages.details.tap("deliverable", text=expected("Survey"))
    pages.survey.assert_open(SERVER)
    pages.survey.tap_nth("yes", 0)
    pages.survey.fill_text(0, text)
    pages.survey.save()


def open_deliverable(pages, expected, name: str, page) -> None:
    pages.details.tap("deliverable", text=expected(name))
    page.assert_open(SERVER)


def back_to_details(pages, job, expected, page) -> None:
    """The deliverable screen's Back — once its toast (full-screen, ~3 s) is gone."""
    page.wait_gone("toast", TOAST)
    page.tap("back")
    pages.details.expect_header(expected(job.title_line), SERVER)


def server_job(api, job, driver, until) -> dict:
    """``GET /job/{id}``, read until ``until(job)`` holds or SERVER seconds pass — the last read is
    returned either way and the test asserts on it."""
    last: list[dict] = []

    def ready(_d) -> bool:
        last.append(api.job(job.id))
        return bool(until(last[-1]))

    with allure.step("server: the job"), contextlib.suppress(TimeoutException):
        waits.wait_until(driver, ready, SERVER, poll=2)
    return last[-1]


def submitted(body: dict) -> bool:
    return body.get("statusType") == "submitted"


def expect_locked(pages, expected, name: str, page) -> None:
    """Tapping the deliverable row opens nothing (read-only after submission)."""
    pages.details.tap("deliverable", text=expected(name))
    with allure.step(f"expect no {name} screen for {READ_ONLY_WATCH:.0f}s (locked)"):
        assert not page.is_visible("header", READ_ONLY_WATCH), f"{name} opened after submission"


DIALOG_CHKS = ("CHK-DLV-001", "CHK-DLV-002", "CHK-DLV-004", "CHK-DLV-005", "CHK-DLV-006",
               "CHK-DLV-007", "CHK-DLV-008", "CHK-DLV-009", "CHK-ORDP-019", "CHK-ORDP-020",
               "CHK-ORDP-021", "CHK-ORDP-022")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-DLV-001")
@pytest.mark.chk(*DIALOG_CHKS)
@allure.tag(*DIALOG_CHKS)
@allure.title(
    "TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, "
    "deliverables stay editable"
)
def test_dialog_and_cancel(survey_job, ui_login, field_services_api, pages, expected, evidence):
    job, d, dialog = survey_job("short"), pages.details, pages.dialog
    open_job(pages, job, expected)
    d.open_submit_dialog()
    with allure.step("expect the dialog's title and warning"):
        assert dialog.text("title") == expected("Submit deliverables"), dialog.text("title")
        assert dialog.text("message") == expected(
            "You won't be able to edit it after submission."
        ), dialog.text("message")
    dialog.visible("cancel")
    dialog.visible("submit")
    dialog.expect_modal(job.title_line)
    evidence.checkpoint("submit-dialog")
    dialog.tap("cancel")
    dialog.wait_gone("title", 5)
    d.expect_header(expected(job.title_line), 5)
    d.visible("status", 5, text=expected("In progress"))
    d.visible("submit-deliverables", 5)
    open_deliverable(pages, expected, "Notes", pages.notes)
    pages.notes.add_note("QA-AUTO after cancel")
    pages.notes.expect_texts([expected("QA-AUTO after cancel")])
    body = field_services_api.job(job.id)
    with allure.step("expect nothing submitted on the server"):
        assert body.get("statusType") == expected("in_progress"), body.get("statusType")
        assert body.get("submissionDate") is None, body.get("submissionDate")


INCOMPLETE_CHKS = ("CHK-DLV-010", "CHK-DLV-011", "CHK-DLV-012")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-DLV-002")
@pytest.mark.chk(*INCOMPLETE_CHKS)
@allure.tag(*INCOMPLETE_CHKS)
@allure.title(
    "TC-DLV-002 With the survey not completed, Submit is refused with 'Complete the survey before "
    "job submission.'; nothing is submitted"
)
def test_incomplete_survey_refused(
    survey_job, ui_login, field_services_api, pages, expected, evidence
):
    job, d = survey_job("short"), pages.details
    open_job(pages, job, expected)
    seen = d.open_submit_dialog().submit()
    evidence.checkpoint("survey-incomplete")
    with allure.step("expect the survey message"):
        assert expected("Complete the survey before job submission.") in seen.messages, (
            seen.summary()
        )
    d.visible("submit-deliverables", 10)
    with allure.step("expect the job still In progress in the app — no Check out"):
        assert not d.is_visible("check-out", 1), "Check out shown"
    body = field_services_api.job(job.id)
    with allure.step("expect nothing submitted on the server — no survey response either"):
        assert body.get("statusType") == expected("in_progress"), body.get("statusType")
        assert body.get("submissionDate") is None, body.get("submissionDate")
        assert not body.get("surveyResponse"), body.get("surveyResponse")


SUBMIT_CHKS = ("CHK-DLV-014", "CHK-DLV-015", "CHK-DLV-016", "CHK-DLV-017", "CHK-DLV-018",
               "CHK-DLV-019", "CHK-DLV-021", "CHK-DLV-022", "CHK-DLV-030", "CHK-DLV-031",
               "CHK-DLV-032", "CHK-DLV-033", "CHK-ORDP-023", "CHK-ORDP-024", "CHK-ORDP-025",
               "CHK-ORDP-041")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-DLV-003")
@pytest.mark.chk(*SUBMIT_CHKS)
@allure.tag(*SUBMIT_CHKS)
@allure.title(
    "TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server "
    "records the job, the time and every deliverable; the job opened again is Submitted with "
    "Check out and locked, also after an app restart"
)
def test_submission_recorded_and_locked(
    survey_job, gallery_photos, ui_login, app, tech_user_id, field_services_api, driver, pages,
    expected, evidence,
):  # fmt: skip
    job, d = survey_job("short"), pages.details
    open_job(pages, job, expected)
    with allure.step("expect no Check out before the submission"):
        assert not d.is_visible("check-out", 1), "Check out before the submission"
    complete_survey(pages, expected, "QA-AUTO submit answer")
    open_deliverable(pages, expected, "Photo report", pages.report)
    pages.report.add_photo(1, "QA-AUTO submit photo")
    back_to_details(pages, job, expected, pages.report)
    open_deliverable(pages, expected, "Notes", pages.notes)
    pages.notes.add_note("QA-AUTO submit note")
    back_to_details(pages, job, expected, pages.notes)
    seen = d.open_submit_dialog().submit()
    with allure.step("expect 'Submitting deliverables', disabled, while it ran"):
        assert seen.submitting_disabled, seen.summary()
        assert not seen.submitting_enabled, seen.summary()
    body = server_job(field_services_api, job, driver, until=submitted)
    resp = body.get("surveyResponse") or {}
    with allure.step("expect the submission recorded on the server"):
        assert body.get("statusType") == expected("submitted"), body.get("statusType")
        at = datetime.fromisoformat(str(body.get("submissionDate")).replace("Z", "+00:00"))
        assert seen.tapped_at - CLOCK <= at <= seen.tapped_at + CLOCK, (
            f"submissionDate {at}, tapped at {seen.tapped_at}"
        )
        assert (body.get("user") or {}).get("id") == tech_user_id, body.get("user")
        assert sr.answer(resp, "Good?").values == [True], sr.answers(resp)
        assert sr.answer(resp, "Text?").values == [expected("QA-AUTO submit answer")]
        photos = [p.get("note") for p in body.get("photos") or []]
        assert photos == [expected("QA-AUTO submit photo")], photos
        notes = [n.get("text") for n in body.get("notes") or []]
        assert notes == [expected("QA-AUTO submit note")], notes
    d.pull_to_refresh()
    d.visible("status", SERVER, text=expected("Submitted"))
    d.expect_enabled("check-out", timeout=10)
    with allure.step("expect no Submit deliverables on a submitted job"):
        assert not d.is_visible("submit-deliverables", 1), "Submit deliverables still shown"
    evidence.checkpoint("submitted")
    expect_locked(pages, expected, "Survey", pages.survey)
    expect_locked(pages, expected, "Photo report", pages.report)
    expect_locked(pages, expected, "Notes", pages.notes)
    app.relaunch()
    open_job(pages, job, expected)
    d.visible("status", SERVER, text=expected("Submitted"))
    d.visible("check-out", 10)
    expect_locked(pages, expected, "Survey", pages.survey)


SUCCESS_CHKS = ("CHK-DLV-013", "CHK-DLV-020", "CHK-ORDP-026", "CHK-ORDP-027", "CHK-ORDP-028")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-DLV-004")
@pytest.mark.chk(*SUCCESS_CHKS)
@allure.tag(*SUCCESS_CHKS)
@allure.title(
    "TC-DLV-004 The app's reaction to a successful submission: 'Deliverables sent to review "
    "successfully', 'Successful', then Check out, locked at once"
)
def test_success_reaction(survey_job, ui_login, field_services_api, pages, expected, evidence):
    job, d = survey_job("short"), pages.details
    open_job(pages, job, expected)
    complete_survey(pages, expected, "QA-AUTO success answer")
    seen = d.open_submit_dialog().submit()
    evidence.checkpoint("after-submit")
    success = expected("Deliverables sent to review successfully")
    if success not in seen.messages and DEV_SUBMIT_ERROR in seen.messages:
        body = field_services_api.job(job.id)
        if submitted(body) and body.get("submissionDate"):
            pytest.skip(
                "Blocked: DEV answers POST /job/{id}/submit with 500 although the submission is "
                "recorded (COPS; owner, Q-DLV-5, 2026-09-26) — the app shows 'Server error. Try "
                "again later.', so its reaction to a successful submission cannot be observed"
            )
    with allure.step("expect the success message and 'Successful'"):
        assert success in seen.messages, seen.summary()
        assert seen.successful, seen.summary()
    d.visible("check-out", 10)
    with allure.step("expect no Submit deliverables after the success"):
        assert not d.is_visible("submit-deliverables", 1), "Submit deliverables still shown"
    expect_locked(pages, expected, "Survey", pages.survey)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-DLV-005")
@pytest.mark.chk("CHK-DLV-032")
@allure.tag("CHK-DLV-032")
@allure.title(
    "TC-DLV-005 After edits and deletions, the server holds after submission exactly the photos "
    "and notes left on the phone"
)
def test_server_matches_phone_after_submission(
    survey_job, gallery_photos, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, r, n = survey_job("short"), pages.report, pages.notes
    open_job(pages, job, expected)
    complete_survey(pages, expected, "QA-AUTO edits answer")
    open_deliverable(pages, expected, "Photo report", r)
    r.add_photo(1, "QA-AUTO photo A")
    r.add_photo(0, "QA-AUTO photo B")
    r.expect_photo_count(2)
    r.open_photo(r.descriptions().index("QA-AUTO photo A"))
    pages.meta.fill_description(" edited")
    pages.meta.tap("save")
    r.assert_open(SERVER)
    r.wait_gone("toast", TOAST)
    r.delete_photo(r.descriptions().index("QA-AUTO photo B"))
    r.expect_photo_count(1)
    with allure.step("expect the one photo left on the phone"):
        assert r.descriptions() == [expected("QA-AUTO photo A edited")], r.descriptions()
    back_to_details(pages, job, expected, r)
    open_deliverable(pages, expected, "Notes", n)
    n.add_note("QA-AUTO note A")
    n.add_note("QA-AUTO note B")
    editor = n.edit(n.texts().index("QA-AUTO note A"))
    editor.type_text(" edited")
    editor.tap("save")
    n.assert_open(SERVER)
    n.wait_toast_gone()
    n.delete_from_menu(n.texts().index("QA-AUTO note B"), confirm=True)
    n.expect_texts([expected("QA-AUTO note A edited")])
    evidence.checkpoint("phone-before-submit")
    back_to_details(pages, job, expected, n)
    pages.details.open_submit_dialog().submit()
    body = server_job(field_services_api, job, driver, until=submitted)
    with allure.step("expect the server to hold exactly the photo and the note left"):
        assert body.get("statusType") == expected("submitted"), body.get("statusType")
        photos = [p.get("note") for p in body.get("photos") or []]
        assert photos == [expected("QA-AUTO photo A edited")], photos
        notes = [x.get("text") for x in body.get("notes") or []]
        assert notes == [expected("QA-AUTO note A edited")], notes


FAILURE_CHKS = ("CHK-DLV-027", "CHK-DLV-028", "CHK-DLV-029", "CHK-ORDP-038", "CHK-ORDP-039")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-DLV-006")
@pytest.mark.chk(*FAILURE_CHKS)
@allure.tag(*FAILURE_CHKS)
@allure.title(
    "TC-DLV-006 A failed submission: 'Job is not found.' with Retry; the job is not submitted; "
    "Retry sends it again and nothing is lost"
)
def test_failed_submission_and_retry(
    survey_job, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, d, api = survey_job("short"), pages.details, field_services_api
    open_job(pages, job, expected)
    complete_survey(pages, expected, "QA-AUTO retry answer")
    with allure.step("server: the job set Canceled (the failure, Q-DLV-2)"):
        api.update_job(job.id, job.job_id, {"statusType": "canceled"})
    seen = d.open_submit_dialog().submit(settle=RETRY_SETTLE)
    assert seen.retry, f"no Retry after the failed submission: {seen.summary()}"
    failed = api.job(job.id)  # read and restore at once — the Retry lives ~4 s
    with allure.step("server: the job set back In progress"):
        api.update_job(job.id, job.job_id, {"statusType": "in_progress"})
    again = d.retry_submission()
    with allure.step("expect the error with Retry, the job not submitted"):
        assert expected("Job is not found.") in seen.messages, seen.summary()
        assert not seen.check_out, f"Check out after a failure: {seen.summary()}"
        assert failed.get("statusType") == expected("canceled"), failed.get("statusType")
        assert failed.get("submissionDate") is None, failed.get("submissionDate")
    with allure.step("expect Retry to send the deliverables again"):
        assert again.submitting_disabled, again.summary()
    evidence.checkpoint("after-retry")
    body = server_job(api, job, driver, until=submitted)
    resp = body.get("surveyResponse") or {}
    with allure.step("expect the retried submission on the server, the survey kept"):
        assert body.get("statusType") == expected("submitted"), body.get("statusType")
        assert sr.answer(resp, "Text?").values == [expected("QA-AUTO retry answer")]
