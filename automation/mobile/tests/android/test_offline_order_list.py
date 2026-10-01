"""Offline — Order list (module 03) — TC-ORDL-016…019 (Android stage, step 5).

Source of every step and expectation:
qa/mobile/03-order-list/android/order-list-offline-test-cases.md (owner validated 2026-10-01;
recon A2, qa/shared/recon-2026-10-01-android-offline.md). Network control: fixtures/network.py
(the ``network`` fixture — Adb.set_network under the hood, restores ON in ``finally``, ``.on()``
waits until DNS resolves again). The app-wide offline banner: pages/android/offline_page.py over
screens/offline_banner_map.py — D-OFF-7 (the banner covers the top content strip) does not apply
here: no step in this file taps inside that strip, so ``offline-banner.close`` is never needed.
One job per test (``{{job.new}}``, status ``new``, today), created through ``POST /job`` while the
device is online and deleted after the test — as the online file's ``jobs_seed``, one job at a
time. TC-ORDL-018 additionally creates ``{{job.offline_created}}`` mid-test, through the API,
while the device stays offline. Every expected value goes through ``expected(...)``.
"""

from datetime import date

import allure
import pytest

from fixtures.jobs import _create, _run_stamp
from pages.android.offline_page import OfflineBanner
from pages.jobs_calendar_page import JobsCalendarPage
from pages.jobs_list_page import JobsListPage

COLD_START_WAIT = 30.0  # recon A2 row 6: the cache appears 10–15 s after a cold start offline
RECONNECT_WAIT = 30.0  # the app refreshes the list on reconnect, no manual pull (CHK-ORDL-035)


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        calendar = JobsCalendarPage(driver, platform)
        banner = OfflineBanner(driver, platform)

    return Pages


@pytest.fixture
def job_new(field_services_api, tech_user_id):
    """``{{job.new}}`` (TC-ORDL-016, -017, -019) — one job, status ``new``, today, created
    through the API while the device is online; deleted after the test (as the online file's
    ``jobs_seed``, one job at a time — convention of the offline test-case file)."""
    job = _create(
        field_services_api, tech_user_id, _run_stamp(), "new", date.today(), 9, "new", None
    )
    try:
        yield job
    finally:
        field_services_api.delete_job({"id": job.id, "jobId": job.job_id})


@pytest.fixture
def job_offline_creator(field_services_api, tech_user_id):
    """``{{job.offline_created}}`` (TC-ORDL-018) — created mid-test through ``POST /job`` while
    the device stays offline; deleted after the test. A callable, as ``late_job`` (fixtures/jobs.py)
    is for the online file: the job does not exist until the test creates it."""
    made: list = []

    def make():
        job = _create(
            field_services_api, tech_user_id, _run_stamp(), "offline", date.today(), 9, "new", None
        )
        made.append(job)
        return job

    try:
        yield make
    finally:
        for job in made:
            field_services_api.delete_job({"id": job.id, "jobId": job.job_id})


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-ORDL-016")
@pytest.mark.chk("CHK-ORDL-031", "CHK-ORDL-064", "CHK-ORDL-033")
@allure.tag("CHK-ORDL-031", "CHK-ORDL-064", "CHK-ORDL-033")
@allure.title(
    "TC-ORDL-016 Offline: the cached list and the cached calendar are shown with the offline "
    "banner, including after a cold start"
)
def test_offline_cached_list_and_calendar_with_banner(
    job_new, ui_login, app, network, pages, expected, evidence
):
    jobs, calendar, banner = pages.jobs, pages.calendar, pages.banner
    with allure.step("precondition: prime the list cache, then (separately) the calendar cache"):
        jobs.pull_to_refresh()
        jobs.visible("card", text=job_new.job_id)
        jobs.to_calendar()
        calendar.pull_to_refresh()  # BUG-ORDL-001: a list refresh does not reach the calendar
        calendar.visible("card", text=job_new.job_id)
        jobs.to_list()
    network.off()
    jobs.pull_to_refresh()
    jobs.visible("card", text=job_new.job_id)  # cached card still shown, no crash (CHK-ORDL-031)
    banner.expect_text("message", expected("No internet connection."))  # settled text, CHK-ORDL-033
    jobs.to_calendar()
    calendar.visible("card", text=job_new.job_id)  # cached calendar card shown (CHK-ORDL-064)
    banner.expect_shown()
    evidence.checkpoint("offline-list-and-calendar")
    app.relaunch()  # terminate + launch, still offline
    jobs.visible("card", COLD_START_WAIT, text=job_new.job_id)  # cache shown after a cold start
    banner.expect_shown()


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-ORDL-017")
@pytest.mark.chk("CHK-ORDL-034")
@allure.tag("CHK-ORDL-034")
@allure.title(
    "TC-ORDL-017 Offline: pulling the list and tapping 'Try again' keep the cached list, no crash"
)
def test_offline_pull_and_try_again_keep_cached_list(job_new, ui_login, network, pages, evidence):
    jobs, banner = pages.jobs, pages.banner
    jobs.pull_to_refresh()  # precondition: cache primed while online
    jobs.visible("card", text=job_new.job_id)
    network.off()
    jobs.pull_to_refresh()  # retry attempt 1, offline
    jobs.visible("card", text=job_new.job_id)  # same cached list, no crash
    banner.visible("try-again")
    evidence.checkpoint("offline-try-again")
    banner.tap("try-again")
    jobs.visible("card", text=job_new.job_id)  # list unchanged, no crash
    banner.expect_shown()  # banner persists (network still off)
    jobs.pull_to_refresh()  # retry attempt 2
    jobs.visible("card", text=job_new.job_id)  # still stable after repeated retries (CHK-ORDL-034)


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-ORDL-018")
@pytest.mark.chk("CHK-ORDL-035")
@allure.tag("CHK-ORDL-035")
@allure.title(
    "TC-ORDL-018 Network back: a job created through the API while offline appears in the list "
    "by itself, without a manual pull"
)
def test_offline_created_job_appears_on_reconnect(
    ui_login, network, job_offline_creator, pages, evidence
):
    jobs, banner = pages.jobs, pages.banner
    jobs.pull_to_refresh()  # precondition: list already refreshed online
    network.off()
    banner.expect_shown()
    job = job_offline_creator()  # POST /job while the device stays offline
    jobs.wait_gone("card", text=job.job_id)  # not shown yet — nothing to sync
    network.on()  # waits until DNS resolves again
    jobs.visible("card", RECONNECT_WAIT, text=job.job_id)  # auto-refresh on reconnect, no pull
    evidence.checkpoint("offline-created-job-synced")
    banner.wait_gone("message")  # banner gone now that the network is back


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-ORDL-019")
@pytest.mark.chk("CHK-ORDL-032", "CHK-ORDL-065")
@allure.tag("CHK-ORDL-032", "CHK-ORDL-065")
@allure.title(
    "TC-ORDL-019 Offline with no jobs for the technician: list and calendar show 'No jobs' with "
    "the offline banner"
)
def test_offline_no_jobs_shows_empty_state_and_banner(
    no_active_jobs, ui_login, network, pages, expected, evidence
):
    jobs, calendar, banner = pages.jobs, pages.calendar, pages.banner
    jobs.pull_to_refresh()  # precondition: no cached job data (matches the "no cache" scenario)
    network.off()
    jobs.expect_text("empty-state", expected("No jobs"))
    banner.expect_shown()  # CHK-ORDL-032
    evidence.checkpoint("offline-empty-list")
    jobs.to_calendar()
    calendar.expect_text("empty-state", expected("No jobs"))
    banner.expect_shown()  # CHK-ORDL-065
