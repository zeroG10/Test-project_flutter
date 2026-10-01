"""Survey offline (module 08, Android stage step 5) — TC-SRV-017…019.

Source of every step and expectation: qa/mobile/08-survey/android/survey-test-cases.md (recon A2 —
qa/shared/recon-2026-10-01-android-offline.md; the owner's decisions 2026-10-01: D-OFF-1…9 answered,
test cases validated with no remarks). Data: fixtures/survey.py — one job per test, directly In
progress, created and opened while the device is still online, deleted after the test. Network is
toggled with the ``network`` fixture (fixtures/network.py; always restored ON in ``finally``). The
server copy is ``GET /job/{id}`` → ``surveyResponse`` (helpers/survey_response.py), read after the
device is back online.

Android only: the iOS simulator's network cannot be switched off (``network`` fixture skips there).
Every expected value goes through ``expected(...)``.
"""

import allure
import pytest

from helpers import survey_response as sr
from pages.android.offline_page import ConnectionRestoredDialog, OfflineBanner
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.survey_page import SurveyPage
from tests.shared.test_survey import open_job, stored

SERVER = 30.0


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        survey = SurveyPage(driver, platform)
        banner = OfflineBanner(driver, platform)
        restored = ConnectionRestoredDialog(driver, platform)

    return Pages


SRV017_CHKS = ("CHK-SRV-024", "CHK-SRV-025")


@pytest.mark.android
@pytest.mark.smoke
@pytest.mark.tc("TC-SRV-017")
@pytest.mark.chk(*SRV017_CHKS)
@allure.tag(*SRV017_CHKS)
@allure.title(
    "TC-SRV-017 Offline: the survey is reachable and fully functional — answer, change the "
    "answer, and Save all work with no network"
)
def test_survey_offline_answer_change_save(
    survey_job, ui_login, network, driver, pages, expected, evidence
):
    job, s = survey_job("short"), pages.survey
    open_job(pages, job, expected)
    network.off()
    pages.details.tap("deliverable", text=expected("Survey"))
    pages.banner.expect_shown()
    s.assert_open(SERVER)
    s.tap_nth("yes", 0)
    s.fill_text(0, "QA-AUTO offline answer")
    s.expect_enabled("save")
    s.tap_nth("no", 0)  # change the answer, offline
    s.expect_selected("no", 0)
    s.expect_selected("yes", 0, selected=False)
    evidence.checkpoint("offline-answered")
    s.save()  # "Survey saved" — accepted with no network error
    pages.details.expect_header(expected(job.title_line), SERVER)


SRV018_CHKS = ("CHK-SRV-026", "CHK-SRV-023")


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-SRV-018")
@pytest.mark.chk(*SRV018_CHKS)
@allure.tag(*SRV018_CHKS)
@allure.title(
    "TC-SRV-018 Offline: a photo attached to a survey photo question is kept, also after a cold "
    "start while still offline"
)
def test_survey_offline_photo_kept_after_cold_start(
    survey_job, gallery_photos, ui_login, network, driver, pages, expected, evidence
):
    job, s = survey_job("photo"), pages.survey
    open_job(pages, job, expected)
    network.off()
    pages.details.tap("deliverable", text=expected("Survey"))
    s.assert_open(SERVER)
    s.add_photo(0, 0, "QA-AUTO offline photo")  # upload-photo[1] = Site overview, gallery cell 0
    s.visible("thumbnail", 15, text=expected("QA-AUTO offline photo"))
    evidence.checkpoint("offline-photo-added")
    ui_login.relaunch()  # terminate + launch — cold start, still offline
    pages.jobs.assert_open(SERVER)
    open_job(pages, job, expected)
    pages.details.tap("deliverable", text=expected("Survey"))
    s.assert_open(SERVER)
    s.visible("thumbnail", 15, text=expected("QA-AUTO offline photo"))
    evidence.checkpoint("offline-photo-after-cold-start")


SRV019_CHKS = ("CHK-SRV-027",)


@pytest.mark.android
@pytest.mark.smoke
@pytest.mark.tc("TC-SRV-019")
@pytest.mark.chk(*SRV019_CHKS)
@allure.tag(*SRV019_CHKS)
@allure.title(
    "TC-SRV-019 Network back: the survey answers and the attached photo from TC-SRV-018 are "
    "synced to the server within about 15 s"
)
def test_survey_offline_sync_on_network_back(
    survey_job, gallery_photos, ui_login, network, field_services_api, driver, pages, expected,
    evidence,
):  # fmt: skip
    job, s = survey_job("photo"), pages.survey
    open_job(pages, job, expected)
    network.off()
    pages.details.tap("deliverable", text=expected("Survey"))
    s.assert_open(SERVER)
    # Same fill sequence as the online TC-SRV-014, with the Site overview photo kept to the one
    # TC-SRV-018 names (the precondition does not ask for a second one there).
    s.fill_text(0, "QA-AUTO room")  # Per-room photos: Room name
    s.fill_text(1, "QA-AUTO comments")  # Additional comments
    s.add_photo(0, 0, "QA-AUTO offline photo")  # Site overview photos (as TC-SRV-018)
    s.add_photo(1, 1, "QA-AUTO offline close-up")  # Equipment close-up photo
    s.add_photo(2, 1, "QA-AUTO offline room photo")  # Per-room photos: Room photo
    evidence.checkpoint("offline-survey-filled")
    s.save()  # "Survey saved" — accepted offline, queued for sync
    network.on()
    pages.banner.wait_gone("message", 5)
    resp = stored(field_services_api, job, driver)
    with allure.step("expect every required answer and the synced photo on the server"):
        assert resp.get("jobId") == expected(job.job_id), f"jobId {resp.get('jobId')!r}"
        assert sr.answer(resp, "Room name").values == [expected("QA-AUTO room")]
        assert sr.answer(resp, "Additional comments").values == [expected("QA-AUTO comments")]
        overview = sr.answer(resp, "Site overview photos")
        assert overview.notes == [expected("QA-AUTO offline photo")], overview.files
        close_up = sr.answer(resp, "Equipment close-up (add a note if something looks off)")
        assert close_up.notes == [expected("QA-AUTO offline close-up")], close_up.files
        room = sr.answer(resp, "Room photos", block="Per-room photos")
        assert room.notes == [expected("QA-AUTO offline room photo")], room.files
