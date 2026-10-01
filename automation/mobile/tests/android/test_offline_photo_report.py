"""Photo report offline (module 09, Android stage step 5) — TC-PHR-008…010.

Source of every step and expectation: qa/mobile/09-photo-report/android/photo-report-test-cases.md
(recon A2 — qa/shared/recon-2026-10-01-android-offline.md; the owner's decisions 2026-10-01:
D-OFF-1…9 answered, test cases validated with no remarks). Data: fixtures/survey.py — one job per
test (``survey_job("short")``, the module's ``{{job.progress}}``), created and opened while the
device is still online, deleted after the test; photos from the simulator gallery
(``gallery_photos``). Network is toggled with the ``network`` fixture (fixtures/network.py; always
restored ON in ``finally``). The server copy is ``GET /job/{id}`` → ``photos`` (``api.jobPhotos``) /
the whole job (``api.job``).

The offline banner covers the first tile's delete icon (D-OFF-7, owner: a UI remark, not a bug) —
every test closes it (``OfflineBanner.close()``) before the first ``photo-report.delete`` tap.
TC-PHR-010's final server state is checked after submission, not during In progress (D-OFF-3, owner:
"перевір" — as BUG-PHR-001); DEV answers ``POST /job/{id}/submit`` with 500 although the submission
is recorded (Q-DLV-5), so the server record is checked regardless of the app's message. Android
only: the iOS simulator's network cannot be switched off (``network`` fixture skips there). Every
expected value goes through ``expected(...)``.
"""

import allure
import pytest

from pages.android.offline_page import ConnectionRestoredDialog, OfflineBanner
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.photo_report_page import PhotoMetadata, PhotoReportPage
from pages.survey_page import SurveyPage
from tests.shared.test_photo_report import server_photos
from tests.shared.test_submit_deliverables import (
    back_to_details,
    complete_survey,
    server_job,
    submitted,
)

SERVER = 30.0
LIST_REFRESHES = 3


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        report = PhotoReportPage(driver, platform)
        meta = PhotoMetadata(driver, platform)
        survey = SurveyPage(driver, platform)
        banner = OfflineBanner(driver, platform)
        restored = ConnectionRestoredDialog(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    """Refresh until the job is listed, then open it — the online half of the precondition
    (as tests/shared/test_photo_report.py's open_report, without the Photo report tap: the
    offline TCs open the deliverable themselves, as a step, once the network is off)."""
    locator = pages.jobs.locator("card", text=job.job_id)
    for _ in range(LIST_REFRESHES):
        pages.jobs.pull_to_refresh()
        if pages.jobs.driver.find_elements(*locator):
            break
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


def offline_add_edit_delete(pages, r, meta, expected) -> None:
    """The offline part of TC-PHR-008's preconditions, reused by TC-PHR-009: a photo added with a
    tag and edited, a second one added and deleted — all offline."""
    r.add_photo(1, "QA-AUTO offline keep", ("tag1",))
    r.open_photo(r.descriptions().index("QA-AUTO offline keep"))
    meta.fill_description("-edited")  # appends to the preloaded description (as TC-PHR-004)
    meta.tap("save")
    r.assert_open(SERVER)
    r.visible("photo", 10, text=expected("QA-AUTO offline keep-edited"))
    r.add_photo(1, "QA-AUTO offline throwaway")
    pages.banner.close()  # the banner covers the first tile's delete icon (D-OFF-7)
    r.delete_photo(r.descriptions().index("QA-AUTO offline throwaway"))
    r.wait_gone("photo", 10, text=expected("QA-AUTO offline throwaway"))


PHR008_CHKS = ("CHK-PHR-045", "CHK-PHR-049", "CHK-PHR-046")


@pytest.mark.android
@pytest.mark.smoke
@pytest.mark.tc("TC-PHR-008")
@pytest.mark.chk(*PHR008_CHKS)
@allure.tag(*PHR008_CHKS)
@allure.title(
    "TC-PHR-008 Offline: add a photo from the gallery with description and tag, edit the "
    "description, then delete a second photo at once — kept after a cold start, still offline"
)
def test_photo_report_offline_add_edit_delete_cold_start(
    survey_job, gallery_photos, ui_login, network, driver, pages, expected, evidence
):
    job, r, meta = survey_job("short"), pages.report, pages.meta
    open_job(pages, job, expected)
    network.off()
    pages.details.tap("deliverable", text=expected("Photo report"))
    pages.banner.expect_shown()
    r.assert_open(SERVER)
    offline_add_edit_delete(pages, r, meta, expected)
    evidence.checkpoint("offline-photo-report-kept-deleted")
    ui_login.relaunch()  # terminate + launch — cold start, still offline
    pages.jobs.assert_open(SERVER)
    open_job(pages, job, expected)
    pages.details.tap("deliverable", text=expected("Photo report"))
    r.assert_open(SERVER)
    r.visible("photo", 10, text=expected("QA-AUTO offline keep-edited"))
    evidence.checkpoint("offline-photo-report-after-cold-start")


PHR009_CHKS = ("CHK-PHR-047", "CHK-PHR-048")


@pytest.mark.android
@pytest.mark.smoke
@pytest.mark.tc("TC-PHR-009")
@pytest.mark.chk(*PHR009_CHKS)
@allure.tag(*PHR009_CHKS)
@allure.title(
    "TC-PHR-009 Network back: the offline photo (with its description and tag) is uploaded "
    "automatically; the photo deleted while unsynced never reaches the server"
)
def test_photo_report_offline_sync_on_network_back(
    survey_job, gallery_photos, ui_login, network, field_services_api, driver, pages, expected,
    evidence,
):  # fmt: skip
    job, r, meta = survey_job("short"), pages.report, pages.meta
    open_job(pages, job, expected)
    network.off()
    pages.details.tap("deliverable", text=expected("Photo report"))
    r.assert_open(SERVER)
    offline_add_edit_delete(pages, r, meta, expected)
    evidence.checkpoint("offline-photo-report-ready-for-sync")
    network.on()
    pages.banner.wait_gone("message", 5)
    photos = server_photos(
        field_services_api, job, driver,
        until=lambda p: [x.get("note") for x in p] == ["QA-AUTO offline keep-edited"],
    )  # fmt: skip
    with allure.step("expect the one synced photo, its tag, and no unsynced-deleted photo"):
        assert [p.get("note") for p in photos] == [expected("QA-AUTO offline keep-edited")], photos
        assert [t.get("name") for t in photos[0].get("tags") or []] == [expected("tag1")], photos[0]


PHR010_CHKS = ("CHK-PHR-050",)


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-PHR-010")
@pytest.mark.chk(*PHR010_CHKS)
@allure.tag(*PHR010_CHKS)
@allure.title(
    "TC-PHR-010 A synced photo deleted offline: network back → submit deliverables → the "
    "server's job has no such photo (D-OFF-3)"
)
def test_photo_report_synced_delete_offline_removed_after_submission(
    survey_job, ui_login, network, field_services_api, driver, pages, expected, evidence
):
    job, r = survey_job("short"), pages.report
    open_job(pages, job, expected)
    complete_survey(pages, expected, "QA-AUTO synced photo answer")
    pages.details.tap("deliverable", text=expected("Photo report"))
    r.assert_open(SERVER)
    r.add_photo(1, "QA-AUTO synced then deleted")
    server_photos(field_services_api, job, driver, until=lambda p: len(p) == 1)  # present, setup
    back_to_details(pages, job, expected, r)
    network.off()
    pages.details.tap("deliverable", text=expected("Photo report"))
    r.assert_open(SERVER)
    pages.banner.close()  # the banner covers the first tile's delete icon (D-OFF-7)
    r.delete_photo(r.descriptions().index("QA-AUTO synced then deleted"))
    r.wait_gone("photo", 10, text=expected("QA-AUTO synced then deleted"))
    r.tap("back")
    pages.details.expect_header(expected(job.title_line), SERVER)
    evidence.checkpoint("synced-photo-deleted-offline")
    network.on()
    pages.details.open_submit_dialog().submit()  # DEV 500s (Q-DLV-5); the server record decides
    gone = expected("QA-AUTO synced then deleted")
    # read until submitted AND the photo gone (or the wait ends): a slow server is not a failure
    body = server_job(
        field_services_api,
        job,
        driver,
        until=lambda b: submitted(b) and gone not in [p.get("note") for p in b.get("photos") or []],
    )
    with allure.step("expect the job submitted and the deleted photo gone from the server"):
        assert body.get("statusType") == expected("submitted"), body.get("statusType")
        photos = [p.get("note") for p in body.get("photos") or []]
        assert expected("QA-AUTO synced then deleted") not in photos, photos
