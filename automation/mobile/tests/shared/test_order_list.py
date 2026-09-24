"""Order list (module 03) — TC-ORDL-001…015.

Source of every step and expectation: qa/mobile/03-order-list/order-list-test-cases.md (D-ORDL-1…12
decided by the owner; recon 4, 2026-09-24). Data: fixtures/jobs.py (9 seed jobs created through
the API out of date order, a late job for TC-ORDL-015, https job links) — all removed after use.

Red today on purpose (regression checks, owner 2026-09-24): TC-ORDL-014 (BUG-ORDL-002, the list
follows creation time) and TC-ORDL-015 (BUG-ORDL-001, the calendar does not follow a list refresh).
TC-ORDL-012 is two tests: the dialog itself, and Cancel / Log out — the latter is Blocked on the
iOS simulator (the dialog closes by itself there; iOS simulator testing specific, Q-ORDL-8).

Order of the functions = order of the run (plan, Step 12): signed-out first, no-data tests before
the seed, TC-ORDL-012 last (it signs out). Every expected value goes through ``expected(...)``.
"""

from datetime import datetime, timedelta

import allure
import pytest

from fixtures.jobs import week_of
from pages.job_details_page import JobDetailsPage
from pages.jobs_calendar_page import JobsCalendarPage, day_title
from pages.jobs_list_page import Card, JobsListPage
from pages.link_dialogs_page import LinkExpiredDialog, PhoneMismatchDialog, expect_no_link_dialog
from pages.notifications_page import NotificationsPage
from pages.profile_page import ProfilePage
from pages.registration_page import RegistrationPage
from pages.tabbar_page import TabBarPage
from pages.welcome_page import WelcomePage
from screens.jobs_list_map import EMPTY_MESSAGE
from screens.link_dialogs_map import MISMATCH_MESSAGE

LANDING = 30.0
SERVER = 20.0
STATUS = {"new": "New", "in_progress": "In progress", "submitted": "Submitted"}


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        calendar = JobsCalendarPage(driver, platform)
        tabbar = TabBarPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        notifications = NotificationsPage(driver, platform)
        profile = ProfilePage(driver, platform)
        welcome = WelcomePage(driver, platform)
        registration = RegistrationPage(driver, platform)
        link_expired = LinkExpiredDialog(driver, platform)
        mismatch = PhoneMismatchDialog(driver, platform)

    return Pages


def expected_card(job, expected, updated: bool = False) -> Card:
    return Card(
        updated=updated,
        date=expected(job.date_text),
        time=expected(job.time_text),
        status=expected(STATUS[job.status]),
        title=expected(job.title_line),
        address=expected(job.address),
    )


def card_date(card: Card):
    return datetime.strptime(card.date, "%d %b %Y").date()


# --------------------------------------------------------------------------------------
# Signed out
# --------------------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-011")
@pytest.mark.chk("CHK-ORDL-003", "CHK-ORDL-038")
@allure.tag("CHK-ORDL-003", "CHK-ORDL-038")
@allure.title(
    "TC-ORDL-011 Signed out, a job link does not open the Jobs list: an unknown key shows "
    "'Link expired', a valid key leads to registration"
)
def test_signed_out_job_links(logged_out_app, job_links, pages, expected, evidence):
    with logged_out_app.alerts_left_alone():
        logged_out_app.open_link(job_links.invalid)
        dialog = pages.link_expired
        dialog.expect_text("title", expected("Link expired"), SERVER)
        dialog.expect_text("message", expected("This link is no longer valid."))
        evidence.checkpoint("link-expired-signed-out")
        dialog.tap("ok")
    pages.welcome.assert_open()
    logged_out_app.open_link(job_links.other_phone)
    pages.registration.expect_text("title", expected("Registration"), SERVER)
    pages.jobs.wait_gone("root", 2)


# --------------------------------------------------------------------------------------
# Signed in, no test data yet
# --------------------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-001")
@pytest.mark.chk(
    "CHK-ORDL-009", "CHK-ORDL-011", "CHK-ORDL-012", "CHK-ORDL-026", "CHK-ORDL-027",
    "CHK-ORDL-028", "CHK-ORDL-029",
)  # fmt: skip
@allure.tag(
    "CHK-ORDL-009", "CHK-ORDL-011", "CHK-ORDL-012", "CHK-ORDL-026", "CHK-ORDL-027",
    "CHK-ORDL-028", "CHK-ORDL-029",
)  # fmt: skip
@allure.title(
    "TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation "
    "with Jobs active, and the 'No jobs' empty state"
)
def test_empty_jobs_list(no_active_jobs, ui_login, pages, expected, evidence):
    jobs = pages.jobs
    jobs.pull_to_refresh()
    jobs.expect_text("root", expected("Jobs list"))
    jobs.visible("view-toggle")
    for tab in ("jobs", "notifications", "profile"):
        pages.tabbar.visible(tab)
    pages.tabbar.expect_selected(expected("jobs"))
    jobs.expect_text("empty-state", expected("No jobs"), SERVER)
    jobs.expect_text("empty-message", expected(EMPTY_MESSAGE))
    jobs.expect_drawn("empty-image")  # the tree reports it not visible while drawn (TD-JOBS-002)
    jobs.expect_no_cards()
    evidence.checkpoint("jobs-list-empty")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-002")
@pytest.mark.chk("CHK-ORDL-013")
@allure.tag("CHK-ORDL-013")
@allure.title("TC-ORDL-002 The Jobs list stays reachable from the other bottom tabs")
def test_jobs_reachable_from_tabs(ui_login, pages, expected):
    for tab, page, title in (
        ("notifications", pages.notifications, "Notification list"),
        ("profile", pages.profile, "Profile"),
    ):
        pages.tabbar.open(tab)
        page.expect_text("root", expected(title), SERVER)
        pages.tabbar.open("jobs")
        pages.jobs.expect_text("root", expected("Jobs list"), SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-006")
@pytest.mark.chk(
    "CHK-ORDL-010", "CHK-ORDL-037", "CHK-ORDL-039", "CHK-ORDL-040", "CHK-ORDL-042", "CHK-ORDL-044"
)  # fmt: skip
@allure.tag(
    "CHK-ORDL-010", "CHK-ORDL-037", "CHK-ORDL-039", "CHK-ORDL-040", "CHK-ORDL-042", "CHK-ORDL-044"
)  # fmt: skip
@allure.title(
    "TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today "
    "selected and Jobs still active, and toggles back"
)
def test_calendar_toggle(ui_login, pages, expected, evidence):
    today = datetime.now().date()
    pages.jobs.to_calendar()
    calendar = pages.calendar
    calendar.expect_week(week_of(today))
    calendar.expect_text("selected-day-title", expected(day_title(today)))
    pages.tabbar.expect_selected(expected("jobs"))
    evidence.checkpoint("calendar-this-week")
    pages.jobs.to_list()
    pages.jobs.visible("root")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-009")
@pytest.mark.chk("CHK-ORDL-043", "CHK-ORDL-047", "CHK-ORDL-048")
@allure.tag("CHK-ORDL-043", "CHK-ORDL-047", "CHK-ORDL-048")
@allure.title("TC-ORDL-009 Swiping the week strip moves to the next and the previous week")
def test_week_swipe(ui_login, pages, expected):
    today = datetime.now().date()
    pages.jobs.to_calendar()
    calendar = pages.calendar
    calendar.swipe_week("left")
    calendar.expect_week(week_of(today + timedelta(days=7)))
    # the same weekday stays selected, one week later (D-ORDL-12)
    calendar.expect_text("selected-day-title", expected(day_title(today + timedelta(days=7))))
    calendar.swipe_week("right")
    calendar.expect_week(week_of(today))
    calendar.swipe_week("right")
    calendar.expect_week(week_of(today - timedelta(days=7)))


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-013")
@pytest.mark.chk("CHK-ORDL-002")
@allure.tag("CHK-ORDL-002")
@allure.title("TC-ORDL-013 A job link for the technician's own phone opens the Jobs list")
def test_own_phone_link_opens_jobs(ui_login, job_links, pages, expected):
    pages.tabbar.open("profile")
    pages.profile.assert_open(SERVER)
    with ui_login.alerts_left_alone():
        ui_login.open_link(job_links.own_phone)
        pages.jobs.expect_text("root", expected("Jobs list"), SERVER)
        expect_no_link_dialog(pages.jobs.driver)


# --------------------------------------------------------------------------------------
# Signed in, with the seed (9 jobs)
# --------------------------------------------------------------------------------------


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-003")
@pytest.mark.chk(
    "CHK-ORDL-015", "CHK-ORDL-016", "CHK-ORDL-017", "CHK-ORDL-018", "CHK-ORDL-019",
    "CHK-ORDL-024", "CHK-ORDL-036",
)  # fmt: skip
@allure.tag(
    "CHK-ORDL-015", "CHK-ORDL-016", "CHK-ORDL-017", "CHK-ORDL-018", "CHK-ORDL-019",
    "CHK-ORDL-024", "CHK-ORDL-036",
)  # fmt: skip
@allure.title(
    "TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, "
    "status, title and address, and opens its details"
)
def test_job_card_and_details(jobs_seed, ui_login, pages, expected, evidence):
    job = jobs_seed["new"]
    jobs = pages.jobs
    jobs.pull_to_refresh()
    with allure.step(f"expect the card of {job.job_id} with its fields"):
        assert jobs.card(job.job_id) == expected_card(job, expected)
    evidence.checkpoint("jobs-list-card")
    jobs.pull_to_refresh()
    with allure.step("expect exactly one card of the job after a refresh"):
        assert jobs.card_count(job.job_id) == 1
    jobs.scroll_to("card", text=job.job_id)
    jobs.tap("card", text=job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)
    pages.details.go_back()
    jobs.assert_open(SERVER)
    with allure.step("expect exactly one card of the job after coming back"):
        assert jobs.card_count(job.job_id) == 1


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-004")
@pytest.mark.chk("CHK-ORDL-015", "CHK-ORDL-020")
@allure.tag("CHK-ORDL-015", "CHK-ORDL-020")
@allure.title(
    "TC-ORDL-004 Each job status shows its own badge; completed, canceled and expired jobs "
    "are not listed"
)
def test_status_badges(jobs_seed, ui_login, pages, expected):
    jobs = pages.jobs
    jobs.pull_to_refresh()
    for kind in ("new", "inprog", "submitted"):
        job = jobs_seed[kind]
        jobs.expect_card_field(job.job_id, "status", expected(STATUS[job.status]))
    listed = {card.job_id for card in jobs.all_cards()}
    with allure.step("expect no card of the completed, canceled and expired jobs"):
        for kind in ("completed", "canceled", "expired"):
            assert jobs_seed[kind].job_id not in listed, f"{kind} job is listed"


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-014")
@pytest.mark.chk("CHK-ORDL-069")
@allure.tag("CHK-ORDL-069")
@allure.title("TC-ORDL-014 The Jobs list is ordered by scheduled date, earliest first")
def test_list_ordered_by_date(jobs_seed, ui_login, pages, expected):
    jobs = pages.jobs
    jobs.pull_to_refresh()
    run_prefix = jobs_seed["new"].job_id.rsplit("-", 1)[0]
    shown = [c for c in jobs.all_cards() if c.job_id.startswith(run_prefix)]
    # jobs on three different dates (on a Saturday the "other day" is yesterday: left out)
    trio = [jobs_seed[k] for k in ("yesterday", "new", "otherday")]
    trio = [j for i, j in enumerate(trio) if j.when.date() not in {t.when.date() for t in trio[:i]}]
    wanted = [expected(j.job_id) for j in sorted(trio, key=lambda j: j.when.date())]
    with allure.step(f"expect {wanted} top → bottom"):
        order = [c.job_id for c in shown if c.job_id in {j.job_id for j in trio}]
        assert order == wanted, f"list order {order}, expected by date {wanted}"
    with allure.step("expect the dates never to decrease from top to bottom"):
        dates = [card_date(c) for c in shown]
        assert dates == sorted(dates), f"dates top → bottom: {[c.date for c in shown]}"


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-015")
@pytest.mark.chk("CHK-ORDL-070")
@allure.tag("CHK-ORDL-070")
@allure.title(
    "TC-ORDL-015 Jobs that the refreshed list shows are shown in the calendar on their dates"
)
def test_calendar_follows_list_refresh(jobs_seed, ui_login, late_job, pages, expected):
    jobs = pages.jobs
    jobs.wait_loaded(SERVER)
    job = late_job()  # created now, after the Jobs screen has loaded
    jobs.pull_to_refresh()
    jobs.expect_card_field(job.job_id, "title", expected(job.title_line))
    jobs.to_calendar()
    calendar = pages.calendar
    # no pull-to-refresh in the calendar here — that is the point (BUG-ORDL-001)
    calendar.visible("card", SERVER, text=expected(job.job_id))
    calendar.select_day(jobs_seed.other_day)
    calendar.visible("card", SERVER, text=jobs_seed["otherday"].job_id)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-010")
@pytest.mark.chk("CHK-ORDL-057")
@allure.tag("CHK-ORDL-057")
@allure.title(
    "TC-ORDL-010 The weekly calendar shows New, In progress and Submitted jobs and hides "
    "Completed, Canceled and Expired ones"
)
def test_calendar_statuses(jobs_seed, ui_login, pages, expected):
    pages.jobs.to_calendar()
    calendar = pages.calendar
    calendar.pull_to_refresh()  # BUG-ORDL-001 must not hide what this TC checks
    for kind in ("new", "inprog", "submitted"):
        calendar.visible("card", SERVER, text=expected(jobs_seed[kind].job_id))
    shown = {card.job_id for card in calendar.all_cards()}
    with allure.step("expect no card of the completed, canceled and expired jobs"):
        for kind in ("completed", "canceled", "expired"):
            assert jobs_seed[kind].job_id not in shown, f"{kind} job is in the calendar"


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-007")
@pytest.mark.chk(
    "CHK-ORDL-049", "CHK-ORDL-050", "CHK-ORDL-051", "CHK-ORDL-052", "CHK-ORDL-053",
    "CHK-ORDL-054", "CHK-ORDL-055", "CHK-ORDL-060", "CHK-ORDL-061", "CHK-ORDL-062",
    "CHK-ORDL-063",
)  # fmt: skip
@allure.tag(
    "CHK-ORDL-049", "CHK-ORDL-050", "CHK-ORDL-051", "CHK-ORDL-052", "CHK-ORDL-053",
    "CHK-ORDL-054", "CHK-ORDL-055", "CHK-ORDL-060", "CHK-ORDL-061", "CHK-ORDL-062",
    "CHK-ORDL-063",
)  # fmt: skip
@allure.title(
    "TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs "
    "shows 'No jobs'"
)
def test_calendar_date_selection(jobs_seed, ui_login, pages, expected, evidence):
    new, other = jobs_seed["new"], jobs_seed["otherday"]
    pages.jobs.to_calendar()
    calendar = pages.calendar
    calendar.pull_to_refresh()  # BUG-ORDL-001
    with allure.step("expect the calendar card to carry the same fields as the list card"):
        assert calendar.card(new.job_id) == expected_card(new, expected)
    calendar.expect_no_card(other.job_id)
    calendar.select_day(jobs_seed.other_day)
    calendar.expect_text("selected-day-title", expected(day_title(jobs_seed.other_day)))
    calendar.visible("card", SERVER, text=other.job_id)
    calendar.expect_no_card(new.job_id)
    calendar.select_day(jobs_seed.empty_day)
    calendar.expect_text("empty-state", expected("No jobs"), SERVER)
    calendar.expect_text("empty-message", expected(EMPTY_MESSAGE))
    calendar.expect_no_cards()
    evidence.checkpoint("calendar-empty-day")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-008")
@pytest.mark.chk("CHK-ORDL-058", "CHK-ORDL-068")
@allure.tag("CHK-ORDL-058", "CHK-ORDL-068")
@allure.title(
    "TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar "
    "card opens its job"
)
def test_calendar_selection_kept_and_card_opens(jobs_seed, ui_login, pages, expected):
    other = jobs_seed["otherday"]
    title = expected(day_title(jobs_seed.other_day))
    pages.jobs.to_calendar()
    calendar = pages.calendar
    calendar.pull_to_refresh()  # BUG-ORDL-001
    calendar.select_day(jobs_seed.other_day)
    pages.jobs.to_list()
    pages.jobs.to_calendar()
    calendar.expect_text("selected-day-title", title)
    calendar.tap("card", SERVER, text=other.job_id)
    pages.details.expect_header(expected(other.title_line), SERVER)
    pages.details.go_back()
    calendar.expect_text("selected-day-title", title, SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-005")
@pytest.mark.chk("CHK-ORDL-022", "CHK-ORDL-056")
@allure.tag("CHK-ORDL-022", "CHK-ORDL-056")
@allure.title(
    "TC-ORDL-005 An unviewed job carries 'Updated' in the list and in the calendar until its "
    "details are opened"
)
def test_updated_label_until_viewed(jobs_seed, ui_login, field_services_api, pages, expected):
    job = jobs_seed["unviewed"]
    jobs = pages.jobs
    jobs.pull_to_refresh()
    jobs.expect_card_field(job.job_id, "title", expected(job.title_line))
    jobs.expect_card_field(job.job_id, "updated", True)
    jobs.to_calendar()
    calendar = pages.calendar
    calendar.pull_to_refresh()  # BUG-ORDL-001
    calendar.expect_card_field(job.job_id, "updated", True)
    calendar.tap("card", SERVER, text=job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)
    pages.details.go_back()
    jobs.to_list()
    jobs.pull_to_refresh()
    server = field_services_api.job(job.id)  # evidence: what the server says after the viewing
    allure.attach(
        f"isViewed={server.get('isViewed')} updatedAt={server.get('updatedAt')}",
        name="server state of the job after its details were opened",
        attachment_type=allure.attachment_type.TEXT,
    )
    jobs.expect_card_field(job.job_id, "updated", False)


# --------------------------------------------------------------------------------------
# Job link for another phone — last: Log out ends the session
# --------------------------------------------------------------------------------------

MISMATCH_CHKS = ("CHK-ORDL-004", "CHK-ORDL-005", "CHK-ORDL-006")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-012")
@pytest.mark.chk(*MISMATCH_CHKS)
@allure.tag(*MISMATCH_CHKS)
@allure.title("TC-ORDL-012 A job link for another phone number shows the mismatch dialog")
def test_mismatch_dialog_shown(ui_login, job_links, pages, platform, expected, evidence):
    with ui_login.alerts_left_alone():
        ui_login.open_link(job_links.other_phone)
        seen = pages.mismatch.snapshot(SERVER)
        evidence.checkpoint("mismatch-dialog")
        with allure.step("expect the dialog's title, text and both buttons"):
            assert expected("Assigned to a different phone number") in seen["texts"]
            assert expected(MISMATCH_MESSAGE) in seen["texts"]
            assert {expected("Cancel"), expected("Log out")} <= set(seen["buttons"])
        # A device keeps the dialog open: leave it the way a user would. On the iOS simulator it
        # closes by itself (Q-ORDL-8) — a tap there races that close (run 1: stale element).
        if platform != "ios":
            pages.mismatch.tap("cancel")
    pages.jobs.assert_open(SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDL-012")
@pytest.mark.chk("CHK-ORDL-007", "CHK-ORDL-008")
@allure.tag("CHK-ORDL-007", "CHK-ORDL-008")
@allure.title("TC-ORDL-012 Mismatch dialog: Cancel keeps the session, Log out ends it")
def test_mismatch_cancel_and_log_out(ui_login, job_links, pages, platform, expected):
    if platform == "ios":
        pytest.skip(
            "Blocked: iOS simulator testing specific — the mismatch dialog closes by itself "
            "~0.6 s after it appears (recon 4, 4 of 4); on a device it stays until a button is "
            "tapped (owner, 2026-09-24, Q-ORDL-8). Runs in full on Android."
        )
    with ui_login.alerts_left_alone():
        ui_login.open_link(job_links.other_phone)
        pages.mismatch.expect_text(
            "title", expected("Assigned to a different phone number"), SERVER
        )
        pages.mismatch.tap("cancel")
        pages.jobs.assert_open(SERVER)
        ui_login.open_link(job_links.other_phone)
        pages.mismatch.tap("log-out", SERVER)
    pages.welcome.assert_open(SERVER)
    ui_login.relaunch()
    pages.welcome.assert_open(LANDING)
