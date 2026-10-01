"""Offline — Submit deliverables (module 07) — TC-DLV-007…009 (Android stage, step 5).

Source of every step and expectation:
qa/mobile/07-submit-deliverables/android/submit-deliverables-offline-test-cases.md (owner
validated 2026-10-01; recon A2, qa/shared/recon-2026-10-01-android-offline.md). Network control:
fixtures/network.py (the ``network`` fixture — Adb.set_network under the hood, restores ON in
``finally``, ``.on()`` waits until DNS resolves again). The per-screen offline message
(``job-details.offline-message``) and the "Connection restored" dialog:
pages/android/offline_page.py over screens/job_details_map.py and screens/offline_banner_map.py.
DEV answers ``POST /job/{id}/submit`` with 500 although the submission is recorded (Q-DLV-5,
unchanged on Android) — TC-DLV-009 checks the server record, exactly as the existing TC-DLV-003
does, not the app's own success toast (that reaction stays ``Blocked`` on DEV, TC-DLV-004). One
job per test (``{{job.progress}}``), created directly In progress with the Short Survey while the
device is online, deleted after the test (fixtures/survey.py ``survey_job``, as the online file).
Every expected value goes through ``expected(...)``.
"""

import re

import allure
import pytest

from helpers import survey_response as sr
from pages.android.offline_page import ConnectionRestoredDialog, OfflineBanner
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.notes_page import NotesPage
from pages.photo_report_page import PhotoReportPage
from pages.submit_dialog_page import SubmitDialog
from pages.survey_page import SurveyPage
from tests.shared.test_submit_deliverables import (
    SERVER,
    back_to_details,
    complete_survey,
    open_deliverable,
    open_job,
    server_job,
    submitted,
)

COLD_START_WAIT = 30.0  # recon A2: cache + banner settle within ~10–15 s after a cold start
JOB_IDS = re.compile(r"QA-AUTO-[0-9A-Z-]+")  # the job ids the Connection restored dialog names


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        dialog = SubmitDialog(driver, platform)
        survey = SurveyPage(driver, platform)
        report = PhotoReportPage(driver, platform)
        notes = NotesPage(driver, platform)
        banner = OfflineBanner(driver, platform)
        restored = ConnectionRestoredDialog(driver, platform)

    return Pages


def tap_disabled(page: JobDetailsPage, alias: str) -> None:
    """Tap a control that is visible but accessibility-disabled. ``BasePage.tap`` waits on
    ``wait_clickable`` (visible AND enabled), which never resolves on a disabled button — and
    TC-DLV-007 needs exactly that: a tap on the disabled Submit deliverables sends nothing."""
    rect = page.rect(alias)
    page.tap_xy(rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2)


@pytest.mark.android
@pytest.mark.smoke
@pytest.mark.tc("TC-DLV-007")
@pytest.mark.chk("CHK-DLV-023", "CHK-DLV-024")
@allure.tag("CHK-DLV-023", "CHK-DLV-024")
@allure.title(
    "TC-DLV-007 Offline on an In progress job with complete deliverables: Submit deliverables "
    "is disabled with its offline message, and a tap sends nothing"
)
def test_offline_submit_disabled_with_message(
    survey_job, ui_login, network, field_services_api, pages, expected, evidence
):
    job = survey_job("short")
    open_job(pages, job, expected)
    complete_survey(pages, expected, "QA-AUTO offline-submit answer")
    pages.details.expect_enabled("submit-deliverables")  # precondition, online
    network.off()
    pages.details.expect_text(
        "offline-message", expected("Offline. Data will sync when the connection is restored.")
    )  # CHK-DLV-024
    pages.details.expect_disabled("submit-deliverables")  # CHK-DLV-023
    evidence.checkpoint("offline-submit-disabled")
    tap_disabled(pages.details, "submit-deliverables")  # disabled control — a no-op
    pages.dialog.wait_gone("title", 5)  # the confirmation dialog never appears
    body = field_services_api.job(job.id)
    with allure.step("expect nothing submitted on the server"):
        assert body.get("statusType") == expected("in_progress"), body.get("statusType")
        assert body.get("submissionDate") is None, body.get("submissionDate")


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-DLV-008")
@pytest.mark.chk("CHK-DLV-025")
@allure.tag("CHK-DLV-025")
@allure.title(
    "TC-DLV-008 Offline: deliverables added without network (survey answer, a note, a photo) "
    "stay on the device, also after a cold start"
)
def test_offline_deliverables_survive_cold_start(
    survey_job, gallery_photos, ui_login, app, network, pages, expected, evidence
):
    job = survey_job("short")
    open_job(pages, job, expected)  # precondition: details open, device online at creation
    network.off()
    complete_survey(pages, expected, "QA-AUTO offline survey")  # FR-SUR-12, fully offline
    open_deliverable(pages, expected, "Photo report", pages.report)
    pages.report.add_photo(1, "QA-AUTO offline photo")
    back_to_details(pages, job, expected, pages.report)
    open_deliverable(pages, expected, "Notes", pages.notes)
    pages.notes.add_note("QA-AUTO offline note")
    back_to_details(pages, job, expected, pages.notes)
    evidence.checkpoint("offline-deliverables-before-cold-start")
    app.relaunch()  # terminate + launch, still offline
    pages.banner.close()  # D-OFF-7: close the banner before tapping the covered top card
    pages.jobs.visible("card", COLD_START_WAIT, text=job.job_id)
    pages.jobs.tap("card", text=job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)  # job-details reopened, cache
    open_deliverable(pages, expected, "Survey", pages.survey)
    with allure.step("expect survey.text[1] = the offline answer, survived the cold start"):
        value = pages.survey.text_value(0)
        assert value == expected("QA-AUTO offline survey"), value  # CHK-DLV-025
    pages.survey.tap("back")  # nothing changed: no unsaved-changes dialog
    pages.details.expect_header(expected(job.title_line), SERVER)
    open_deliverable(pages, expected, "Photo report", pages.report)
    pages.report.visible("photo", text=expected("QA-AUTO offline photo"))  # survived
    back_to_details(pages, job, expected, pages.report)
    open_deliverable(pages, expected, "Notes", pages.notes)
    pages.notes.expect_texts([expected("QA-AUTO offline note")])  # survived
    evidence.checkpoint("offline-deliverables-after-cold-start")


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-DLV-009")
@pytest.mark.chk("CHK-DLV-026")
@allure.tag("CHK-DLV-026")
@allure.title(
    "TC-DLV-009 Network back: the 'Connection restored' dialog names the job; its Submit leads "
    "to the job, where the resubmission is recorded on the server"
)
def test_offline_connection_restored_dialog_leads_to_resubmit(
    survey_job, ui_login, network, field_services_api, driver, pages, expected, evidence
):
    job = survey_job("short")
    open_job(pages, job, expected)
    complete_survey(pages, expected, "QA-AUTO reconnect answer")  # precondition, as TC-DLV-007
    network.off()
    pages.details.expect_disabled("submit-deliverables")  # baseline, CHK-DLV-023
    # the dialog is drawn on the tab screens: over job details it would wait unseen until the
    # user is back on a tab (app_shell.dart; offline run 0307-r1) — so back to the Jobs list
    pages.details.tap("back")
    pages.jobs.assert_open(SERVER)
    network.on()  # waits until DNS resolves again
    pages.restored.wait_open()  # recon A2: ≈15 s after the network returns
    evidence.checkpoint("connection-restored-dialog")
    for fragment in (
        expected("unfinished job"),
        expected(job.job_id),
        expected("Submit your deliverables now"),
    ):
        pages.restored.expect_text("message", fragment)  # names the job (CHK-DLV-026)
    pages.restored.visible("cancel")
    pages.restored.visible("submit")
    # Submit does not submit by itself (app_shell.dart): it opens the one unfinished job, or the
    # Jobs list when the dialog names several — every In progress job in the app's details cache
    # counts, also ones deleted on the server since (offline run 0307-r2). The user resubmits
    # from there (FR-IP-06 "so he can resubmit it", D-OFF-2).
    message = pages.restored.label_of(pages.restored.find("message"))
    allure.attach(
        message, name="Connection restored — message", attachment_type=allure.attachment_type.TEXT
    )
    named = set(JOB_IDS.findall(message))
    pages.restored.tap("submit")
    if len(named) > 1:
        pages.jobs.assert_open(SERVER)
        pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)
    pages.details.open_submit_dialog().submit()  # DEV 500s (Q-DLV-5); the server record decides
    body = server_job(field_services_api, job, driver, until=submitted)
    resp = body.get("surveyResponse") or {}
    with allure.step("expect the submission recorded on the server (CHK-DLV-026, Q-DLV-5)"):
        assert body.get("statusType") == expected("submitted"), body.get("statusType")
        assert body.get("submissionDate"), body.get("submissionDate")
        assert sr.answer(resp, "Text?").values == [expected("QA-AUTO reconnect answer")]
