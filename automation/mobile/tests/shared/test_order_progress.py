"""Order progress (module 06) — TC-ORDP-001…006.

Source of every step and expectation: qa/mobile/06-order-progress/order-progress-test-cases.md
(recon 7; D-ORDP-1…5 accepted and Q-ORDP-1…3 closed by the owner 2026-09-24). Data:
fixtures/progress.py — 2 jobs through the API, removed after the module; `progress` is checked in
through the UI by the first test that needs it (its timer then counts from that check-in —
Q-ORDP-4).

Nothing is filled, uploaded or submitted here: the submission flow is module 07. TC-ORDP-006 is
Blocked on iOS: the simulator has no Phone app (as TC-ORDD-004). Every expected value goes through
``expected(...)``.
"""

from datetime import UTC, datetime

import allure
import pytest

from helpers import waits
from pages.attachments_page import AttachmentsPage
from pages.deliverable_screen_page import DeliverableScreenPage
from pages.in_app_browser_page import InAppBrowserPage
from pages.job_details_page import TIMER_TOLERANCE, JobDetailsPage
from pages.jobs_list_page import JobsListPage

SERVER = 20.0
MAPS_PAGE = 40.0  # maps.apple.com loads slowly on the simulator (recon 5: blank at 4 s)
BACKGROUND = 10  # seconds in the background (TC-ORDP-002)
CLOCK_SKEW = 5.0  # timer vs the server's checkInDate: device and server clocks, the check-in call
READ_ONLY_WATCH = 3.0  # seconds a tap on a read-only row is watched for a screen that must not open
ROWS = ("Survey", "Photo report", "Notes")


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        deliverable = DeliverableScreenPage(driver, platform)
        attachments = AttachmentsPage(driver, platform)
        browser = InAppBrowserPage(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    pages.jobs.pull_to_refresh()
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


IN_PROGRESS_CHKS = (
    "CHK-ORDP-001", "CHK-ORDP-002", "CHK-ORDP-004", "CHK-ORDP-005", "CHK-ORDP-010",
    "CHK-ORDP-011", "CHK-ORDP-012", "CHK-ORDP-014", "CHK-ORDP-015", "CHK-ORDP-017",
    "CHK-ORDP-018",
)  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-ORDP-001")
@pytest.mark.chk(*IN_PROGRESS_CHKS)
@allure.tag(*IN_PROGRESS_CHKS)
@allure.title(
    "TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, "
    "deliverables, info and 'Submit deliverables'"
)
def test_in_progress_screen(in_progress_job, ui_login, progress_seed, pages, expected, evidence):
    job, d, pf = in_progress_job, pages.details, progress_seed.pf
    open_job(pages, job, expected)
    d.expect_field("status", expected("In progress"))
    d.expect_timer_running(gap=3.0)
    for row in ROWS:
        d.expect_deliverable_row(expected(row))
    evidence.checkpoint("in-progress-top")
    d.expect_description(expected(job.description))
    d.expect_field("address", expected(job.address))
    d.expect_enabled("on-map")
    d.expect_field("date", expected(job.date_text))
    d.expect_field("time", expected(job.time_text))
    d.expect_field("pf-name", expected(pf["name"]))
    d.scroll_to("pf-phone", text=expected(pf["phone"]))
    phone = d.visible("pf-phone", text=expected(pf["phone"]))
    assert phone.is_enabled(), "the PF phone is not tappable"
    d.expect_enabled("submit-deliverables")
    evidence.checkpoint("in-progress-bottom")
    d.open_attachments()
    pages.attachments.assert_open(SERVER)
    pages.attachments.tap("back")
    d.expect_header(expected(job.title_line), SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDP-002")
@pytest.mark.chk("CHK-ORDP-003")
@allure.tag("CHK-ORDP-003")
@allure.title("TC-ORDP-002 The timer keeps counting while the app is in the background")
def test_timer_after_background(in_progress_job, ui_login, field_services_api, pages, expected):
    job, d = in_progress_job, pages.details
    open_job(pages, job, expected)
    before, start = d.timer_seconds(), datetime.now(UTC)
    ui_login.background(BACKGROUND)
    d.expect_header(expected(job.title_line), SERVER)
    after, now = d.timer_seconds(), datetime.now(UTC)
    elapsed = (now - start).total_seconds()
    with allure.step(f"expect the timer {before}s + {elapsed:.1f}s (±{TIMER_TOLERANCE:.0f}s)"):
        assert abs((after - before) - elapsed) <= TIMER_TOLERANCE, (
            f"timer {before}s → {after}s in {elapsed:.1f}s ({BACKGROUND}s in the background)"
        )
    stamp = field_services_api.job(job.id).get("checkInDate")
    with allure.step(f"expect the timer = the time since checkInDate {stamp} (±{CLOCK_SKEW:.0f}s)"):
        assert stamp, "no checkInDate stored for the checked-in job"
        since = (now - datetime.fromisoformat(stamp.replace("Z", "+00:00"))).total_seconds()
        assert abs(after - since) <= CLOCK_SKEW, (
            f"timer {after}s, {since:.1f}s since the check-in on the server"
        )


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDP-003")
@pytest.mark.chk("CHK-ORDP-006", "CHK-ORDP-007", "CHK-ORDP-008")
@allure.tag("CHK-ORDP-006", "CHK-ORDP-007", "CHK-ORDP-008")
@allure.title("TC-ORDP-003 Survey, Photo report and Notes open their screens and come back")
def test_deliverables_open_their_screens(
    in_progress_job, ui_login, progress_seed, pages, expected, evidence
):
    job, d, screen = in_progress_job, pages.details, pages.deliverable
    open_job(pages, job, expected)
    for row in ROWS:
        d.scroll_to("deliverable", text=expected(row))
        d.tap("deliverable", text=expected(row))
        screen.expect_open(expected(row), SERVER)
        if row == "Survey":
            screen.visible("survey-name", text=expected(progress_seed.survey_name))
        evidence.checkpoint(f"deliverable-{row.lower().replace(' ', '-')}")
        screen.tap("back")
        d.expect_header(expected(job.title_line), SERVER)
    d.expect_field("status", expected("In progress"))


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDP-004")
@pytest.mark.chk("CHK-ORDP-013")
@allure.tag("CHK-ORDP-013")
@allure.title("TC-ORDP-004 'On map' on the In progress screen opens the job's location")
def test_on_map_in_progress(in_progress_job, ui_login, pages, expected, evidence):
    job = in_progress_job
    open_job(pages, job, expected)
    pages.details.scroll_to("on-map")
    pages.details.tap("on-map")
    pages.browser.expect_host(expected("maps.apple.com"), SERVER)
    street = job.address.split(", ")[1]  # "QA test site, 350 5th Ave, …" → "350 5th Ave"
    pages.browser.visible("place", MAPS_PAGE, text=expected(street))
    evidence.checkpoint("on-map-in-progress")
    pages.browser.close()
    pages.details.expect_header(expected(job.title_line), SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDP-005")
@pytest.mark.chk("CHK-ORDP-042")
@allure.tag("CHK-ORDP-042")
@allure.title(
    "TC-ORDP-005 The primary action follows the status after leaving and reopening; a Submitted "
    "job's deliverables are read-only"
)
def test_primary_action_follows_status(
    in_progress_job, ui_login, progress_seed, pages, expected, evidence
):
    job, done, d = in_progress_job, progress_seed["done"], pages.details
    open_job(pages, job, expected)
    d.tap("back")  # not the edge swipe: Flutter ignores it while the details still slide in (run 2)
    pages.jobs.assert_open(SERVER)
    pages.jobs.open_card(job.job_id)
    d.expect_header(expected(job.title_line), SERVER)
    d.expect_enabled("submit-deliverables", timeout=SERVER)
    assert not d.is_visible("check-out", 0), "'Check out' on an In progress job"
    d.tap("back")
    pages.jobs.assert_open(SERVER)
    pages.jobs.open_card(done.job_id)
    d.expect_header(expected(done.title_line), SERVER)
    d.expect_enabled("check-out", timeout=SERVER)
    assert not d.is_visible("submit-deliverables", 0), "'Submit deliverables' on a Submitted job"
    d.tap("deliverable", text=expected("Survey"))
    with allure.step(f"expect no Survey screen for {READ_ONLY_WATCH:.0f}s (read-only)"):
        opened = pages.deliverable.is_visible("title", READ_ONLY_WATCH, text=expected("Survey"))
        assert not opened, "the Survey screen opened from a Submitted job"
    evidence.checkpoint("submitted-read-only")
    d.expect_header(expected(done.title_line))


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDP-006")
@pytest.mark.chk("CHK-ORDP-016")
@allure.tag("CHK-ORDP-016")
@allure.title("TC-ORDP-006 The PF phone on the In progress screen opens the dialer")
def test_pf_phone_in_progress(progress_seed, request, driver, platform, pages, expected):
    if platform == "ios":
        pytest.skip(
            "Blocked: iOS simulator limitation — there is no Phone app, the tap cannot open a "
            "dialer (owner, 2026-09-24, as Q-ORDD-3). Runs in full on the Android emulator."
        )
    job, phone = request.getfixturevalue("in_progress_job"), progress_seed.pf["phone"]
    open_job(pages, job, expected)
    pages.details.scroll_to("pf-phone", text=phone)
    pages.details.tap("pf-phone", text=phone)
    digits = "".join(ch for ch in expected(phone) if ch.isdigit())
    with allure.step(f"expect the dialer with {digits}"):
        waits.wait_until(driver, lambda d: "dialer" in (d.current_package or ""), SERVER,
                         "the dialer did not open")  # fmt: skip
        shown = "".join(ch for ch in driver.page_source if ch.isdigit())
        assert digits in shown, f"dialer does not show {digits}"
    driver.back()
