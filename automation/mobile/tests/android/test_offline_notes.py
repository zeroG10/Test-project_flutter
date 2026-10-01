"""Notes offline (module 10, Android stage step 5) — TC-NOTE-008…010.

Source of every step and expectation: qa/mobile/10-notes/android/notes-test-cases.md (recon A2 —
qa/shared/recon-2026-10-01-android-offline.md; the owner's decisions 2026-10-01: D-OFF-1…9 answered,
test cases validated with no remarks). Data: fixtures/survey.py — one job per test
(``survey_job("short")``, the module's ``{{job.progress}}``), created and opened while the device is
still online, deleted after the test. Network is toggled with the ``network`` fixture
(fixtures/network.py; always restored ON in ``finally``). The server copy is ``GET /job/{id}`` →
``notes`` (``api.jobNotes``) / the whole job (``api.job``).

The offline banner covers the first row's ⋮ (D-OFF-7, owner: a UI remark, not a bug) — every test
closes it (``OfflineBanner.close()``) before the first ``notes.menu`` tap. TC-NOTE-010's final
server state is checked after submission, not during In progress (D-OFF-3, owner: "перевір" — as
BUG-PHR-001); DEV answers ``POST /job/{id}/submit`` with 500 although the submission is recorded
(Q-DLV-5), so the server record is checked regardless of the app's message. Android only: the iOS
simulator's network cannot be switched off (``network`` fixture skips there). Every expected value
goes through ``expected(...)``.
"""

import allure
import pytest

from pages.android.offline_page import ConnectionRestoredDialog, OfflineBanner
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.notes_page import NotesPage
from pages.survey_page import SurveyPage
from tests.shared.test_notes import server_notes
from tests.shared.test_submit_deliverables import complete_survey, server_job, submitted

SERVER = 30.0
LIST_REFRESHES = 3


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        notes = NotesPage(driver, platform)
        survey = SurveyPage(driver, platform)
        banner = OfflineBanner(driver, platform)
        restored = ConnectionRestoredDialog(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    """Refresh until the job is listed, then open it — the online half of the precondition
    (as tests/shared/test_notes.py's open_notes, without the Notes tap: the offline TCs open
    the deliverable themselves, as a step, once the network is off)."""
    locator = pages.jobs.locator("card", text=job.job_id)
    for _ in range(LIST_REFRESHES):
        pages.jobs.pull_to_refresh()
        if pages.jobs.driver.find_elements(*locator):
            break
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


def offline_create_edit_delete(n, banner, expected) -> None:
    """The offline part of TC-NOTE-008's preconditions, reused by TC-NOTE-009: a note created and
    edited, a second one created and deleted — all offline."""
    editor = n.start_add()
    editor.type_text("QA-AUTO offline keep")
    editor.tap("save")
    n.assert_open(SERVER)
    n.visible("toast", 5)
    n.expect_text("toast", expected("Note added successfully"))
    editor = n.edit(n.texts().index("QA-AUTO offline keep"))
    editor.type_text(" edited")
    editor.tap("save")
    n.assert_open(SERVER)
    n.visible("toast", 5)
    n.expect_text("toast", expected("Note saved successfully"))
    n.add_note("QA-AUTO offline throwaway")
    banner.close()  # the banner covers the first row's ⋮ (D-OFF-7)
    n.delete_from_menu(n.texts().index("QA-AUTO offline throwaway"), confirm=True)
    n.visible("toast", 5)
    n.expect_text("toast", expected("Note deleted successfully"))


NOTE008_CHKS = ("CHK-NOTE-043", "CHK-NOTE-046", "CHK-NOTE-044")


@pytest.mark.android
@pytest.mark.smoke
@pytest.mark.tc("TC-NOTE-008")
@pytest.mark.chk(*NOTE008_CHKS)
@allure.tag(*NOTE008_CHKS)
@allure.title(
    "TC-NOTE-008 Offline: create a note, edit it, then delete a second note at once — kept "
    "after a cold start, still offline"
)
def test_notes_offline_create_edit_delete_cold_start(
    survey_job, ui_login, network, driver, pages, expected, evidence
):
    job, n = survey_job("short"), pages.notes
    open_job(pages, job, expected)
    network.off()
    pages.details.tap("deliverable", text=expected("Notes"))
    pages.banner.expect_shown()
    n.assert_open(SERVER)
    offline_create_edit_delete(n, pages.banner, expected)
    n.expect_texts([expected("QA-AUTO offline keep edited")])  # the throwaway note gone
    evidence.checkpoint("offline-notes-kept-deleted")
    ui_login.relaunch()  # terminate + launch — cold start, still offline
    pages.jobs.assert_open(SERVER)
    open_job(pages, job, expected)
    pages.details.tap("deliverable", text=expected("Notes"))
    n.assert_open(SERVER)
    n.expect_texts([expected("QA-AUTO offline keep edited")])
    evidence.checkpoint("offline-notes-after-cold-start")


NOTE009_CHKS = ("CHK-NOTE-045",)


@pytest.mark.android
@pytest.mark.smoke
@pytest.mark.tc("TC-NOTE-009")
@pytest.mark.chk(*NOTE009_CHKS)
@allure.tag(*NOTE009_CHKS)
@allure.title(
    "TC-NOTE-009 Network back: notes created and edited offline are synced to the server; the "
    "note deleted while unsynced never reaches it"
)
def test_notes_offline_sync_on_network_back(
    survey_job, ui_login, network, field_services_api, driver, pages, expected, evidence
):
    job, n = survey_job("short"), pages.notes
    open_job(pages, job, expected)
    network.off()
    pages.details.tap("deliverable", text=expected("Notes"))
    n.assert_open(SERVER)
    offline_create_edit_delete(n, pages.banner, expected)
    evidence.checkpoint("offline-notes-ready-for-sync")
    network.on()
    pages.banner.wait_gone("message", 5)
    notes = server_notes(
        field_services_api, job, driver, until=lambda t: t == ["QA-AUTO offline keep edited"]
    )
    with allure.step("expect exactly the synced note, no unsynced-deleted note"):
        assert notes == [expected("QA-AUTO offline keep edited")], notes


NOTE010_CHKS = ("CHK-NOTE-047",)


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-NOTE-010")
@pytest.mark.chk(*NOTE010_CHKS)
@allure.tag(*NOTE010_CHKS)
@allure.title(
    "TC-NOTE-010 A synced note deleted offline: network back → submit deliverables → the "
    "server has no such note (D-OFF-3)"
)
def test_notes_synced_delete_offline_removed_after_submission(
    survey_job, ui_login, network, field_services_api, driver, pages, expected, evidence
):
    job, n = survey_job("short"), pages.notes
    open_job(pages, job, expected)
    complete_survey(pages, expected, "QA-AUTO synced note answer")
    pages.details.tap("deliverable", text=expected("Notes"))
    n.assert_open(SERVER)
    n.add_note("QA-AUTO synced then deleted")
    server_notes(
        field_services_api, job, driver, until=lambda t: t == ["QA-AUTO synced then deleted"]
    )  # present, setup
    n.tap("back")
    pages.details.expect_header(expected(job.title_line), SERVER)
    network.off()
    pages.details.tap("deliverable", text=expected("Notes"))
    n.assert_open(SERVER)
    pages.banner.close()  # the banner covers the first row's ⋮ (D-OFF-7)
    n.delete_from_menu(n.texts().index("QA-AUTO synced then deleted"), confirm=True)
    n.expect_texts([])  # removed locally; the deletion is not sent while offline
    n.tap("back")
    pages.details.expect_header(expected(job.title_line), SERVER)
    evidence.checkpoint("synced-note-deleted-offline")
    network.on()
    pages.details.open_submit_dialog().submit()  # DEV 500s (Q-DLV-5); the server record decides
    body = server_job(field_services_api, job, driver, until=submitted)
    with allure.step("expect the job submitted and the deleted note gone from the server"):
        assert body.get("statusType") == expected("submitted"), body.get("statusType")
        notes = [x.get("text") for x in body.get("notes") or []]
        assert expected("QA-AUTO synced then deleted") not in notes, notes
