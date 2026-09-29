"""Notifications (module 11) — TC-NOTIF-001…006.

Source of every step and expectation: qa/mobile/11-notifications/notifications-test-cases.md
(recon 12; the owner's decisions 2026-09-27). Data: fixtures/notifications.py — the test's own
jobs send the notifications and take them away when they are deleted. The server copy is
``GET /notification`` for the technician (admin, read-only).

Accepted baseline (owner, D-NOTIF-1…5): a row shows no title; a cancelled job's row opens nothing
and shows nothing; "Job cancelled" arrives read; "Go to Settings" opens the Settings app; long names
wrap. Every expected value goes through ``expected(...)``.
"""

import time
from datetime import datetime

import allure
import pytest

from fixtures.notifications import server_notifications
from pages.job_details_page import JobDetailsPage
from pages.notifications_page import NotificationsPage
from pages.tabbar_page import TabBarPage

SERVER = 30.0
STAY = 3.0  # seconds the list must stay after a tap that opens nothing
SCROLLS = 6
LONG_TITLE = "QA-AUTO notif a very long job name that keeps going to see how the row wraps it"


@pytest.fixture
def pages(driver, platform):
    class Pages:
        tabs = TabBarPage(driver, platform)
        notes = NotificationsPage(driver, platform)
        details = JobDetailsPage(driver, platform)

    return Pages


def open_tab(pages) -> None:
    """The Notifications tab (the tabs appear a moment after launch), then a refresh."""
    pages.tabs.tap("notifications", SERVER)
    pages.notes.assert_open(SERVER)
    pages.notes.refresh()


def today() -> str:
    now = datetime.now()
    return f"{now.month}/{now.day}/{now.year}"


TAB_CHKS = ("CHK-NOTIF-001", "CHK-NOTIF-002", "CHK-NOTIF-003", "CHK-NOTIF-026", "CHK-NOTIF-027")


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-NOTIF-001")
@pytest.mark.chk(*TAB_CHKS)
@allure.tag(*TAB_CHKS)
@allure.title(
    "TC-NOTIF-001 The Notifications tab: 'Notification list', the tab selected, the empty state"
)
def test_tab_and_empty_state(no_notifications, ui_login, pages, expected, evidence):
    n = pages.notes
    open_tab(pages)
    with allure.step("expect the title 'Notification list'"):
        assert n.label_of(n.find("root")) == expected("Notification list")
    pages.tabs.expect_selected(expected("notifications"))
    n.expect_text("empty-title", expected("No notifications yet"))
    n.expect_text("empty-text", expected("You'll see updates about your jobs here."))
    evidence.checkpoint("notifications-empty")


ROWS_CHKS = ("CHK-NOTIF-011", "CHK-NOTIF-012", "CHK-NOTIF-013", "CHK-NOTIF-015", "CHK-NOTIF-016")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTIF-002")
@pytest.mark.chk(*ROWS_CHKS)
@allure.tag(*ROWS_CHKS)
@allure.title(
    "TC-NOTIF-002 Rows from job changes: the server's description, the chevron only for a job that "
    "can be opened, newest first, the tab's count; 'Job cancelled' arrives read"
)
def test_rows_from_job_changes(
    notif_job, ui_login, field_services_api, tech_user_id, driver, pages, expected, evidence
):
    api, n = field_services_api, pages.notes
    a, b = notif_job(), notif_job()
    time.sleep(1.2)
    with allure.step(f"server: {a.job_id} renamed (Job updated), {b.job_id} cancelled"):
        api.update_job(a.id, a.job_id, {"title": f"{a.title} updated"})
        time.sleep(1.2)
        api.update_job(b.id, b.job_id, {"statusType": "canceled"})
    stored = server_notifications(api, tech_user_id, driver, [a, b], 4)
    with allure.step("expect 4 notifications on the server: 2 assigned, updated, cancelled"):
        assert [x.get("title") for x in stored] == [
            "Job cancelled", "Job updated", "New job assigned", "New job assigned"
        ], [x.get("title") for x in stored]  # fmt: skip
    open_tab(pages)
    rows = [r for r in n.rows() if a.job_id in r.description or b.job_id in r.description]
    evidence.checkpoint("notification-rows")
    with allure.step("expect the rows: the server's bodies, newest first"):
        assert [r.description for r in rows] == [expected(x.get("body")) for x in stored], [
            r.description for r in rows
        ]
    with allure.step("expect each row dated today with a time"):
        assert all(r.date == expected(today()) for r in rows), [(r.date, r.time) for r in rows]
    with allure.step("expect a chevron on the rows of the job that can be opened only"):
        opens = {r.description: r.chevron for r in rows}
        assert [opens[r.description] for r in rows] == [False, True, False, True], opens
    with allure.step("expect the tab's count 3 — 'Job cancelled' arrives read"):
        count = pages.tabs.notifications_count()
        assert str(count) == expected("3"), count


READ_CHKS = ("CHK-NOTIF-019", "CHK-NOTIF-020", "CHK-NOTIF-022", "CHK-NOTIF-023", "CHK-NOTIF-024",
             "CHK-NOTIF-025")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-NOTIF-003")
@pytest.mark.chk(*READ_CHKS)
@allure.tag(*READ_CHKS)
@allure.title(
    "TC-NOTIF-003 Opening an unread notification: the job's details; back on the list the row is "
    "read, the count goes down, the server marks it viewed"
)
def test_open_marks_read(
    notif_job, ui_login, field_services_api, tech_user_id, driver, pages, expected, evidence
):
    api, n, d = field_services_api, pages.notes, pages.details
    c = notif_job()
    server_notifications(api, tech_user_id, driver, [c], 1)
    open_tab(pages)
    n.expect_unread(expected(c.job_id))
    with allure.step("expect the tab's count 1"):
        count = pages.tabs.notifications_count()
        assert str(count) == expected("1"), count
    evidence.checkpoint("unread")
    n.tap_row(expected(c.job_id))
    d.expect_header(expected(c.title_line), SERVER)
    d.tap("back")
    n.assert_open(SERVER)
    pages.tabs.visible("notifications", 5)
    n.expect_unread(expected(c.job_id), unread=False)
    evidence.checkpoint("read")
    with allure.step("expect no count on the tab"):
        count = pages.tabs.notifications_count()
        assert str(count) == expected("0"), count
    stored = server_notifications(api, tech_user_id, driver, [c], 1)
    with allure.step("expect the notification viewed on the server"):
        assert [x.get("status") for x in stored] == [expected("viewed")], stored


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTIF-004")
@pytest.mark.chk("CHK-NOTIF-021")
@allure.tag("CHK-NOTIF-021")
@allure.title(
    "TC-NOTIF-004 A notification of a job that can no longer be opened: no chevron, the tap stays "
    "on the list and shows nothing, the row turns read"
)
def test_cancelled_job_row(
    notif_job, ui_login, field_services_api, tech_user_id, driver, pages, expected, evidence
):
    api, n, d = field_services_api, pages.notes, pages.details
    job = notif_job()
    time.sleep(1.2)
    with allure.step(f"server: {job.job_id} cancelled"):
        api.update_job(job.id, job.job_id, {"statusType": "canceled"})
    server_notifications(api, tech_user_id, driver, [job], 2)
    open_tab(pages)
    assigned = expected(f"{job.job_id} was assigned")
    row = n.row(assigned)
    with allure.step("expect the assigned row unread, without a chevron"):
        assert not row.chevron, row
    n.expect_unread(assigned)
    n.tap_row(assigned)
    with allure.step(f"expect the list to stay for {STAY:.0f}s — no job details"):
        assert not d.is_visible("header", STAY, text=job.title_line), "the job's details opened"
        n.visible("root")
    evidence.checkpoint("cancelled-tapped")
    n.expect_unread(assigned, unread=False)
    stored = server_notifications(api, tech_user_id, driver, [job], 2)
    with allure.step("expect the assigned notification viewed on the server"):
        assert {x.get("title"): x.get("status") for x in stored}.get("New job assigned") == (
            expected("viewed")
        ), stored


PUSH_CHKS = ("CHK-NOTIF-005", "CHK-NOTIF-006", "CHK-NOTIF-007", "CHK-NOTIF-008", "CHK-NOTIF-009",
             "CHK-NOTIF-028")  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTIF-005")
@pytest.mark.chk(*PUSH_CHKS)
@allure.tag(*PUSH_CHKS)
@allure.title(
    "TC-NOTIF-005 Push not allowed: the banner with its texts, together with the empty state; "
    "Go to Settings opens Settings; allowed again: no banner"
)
def test_push_banner(no_notifications, ui_login, push_restored, app, pages, expected, evidence):
    n, settings_app = pages.notes, push_restored
    settings_app.set_app_notifications(False, app.app_id)
    open_tab(pages)
    with allure.step("expect the banner's texts"):
        assert n.banner_lines() == [
            expected("Turn on push notifications"),
            expected("Turn on push notifications to get alerts for job updates."),
            expected("Go to Settings"),
        ], n.banner_lines()
    title = n.visible("empty-title", 5).rect
    banner = n.visible("banner").rect
    with allure.step("expect the empty state below the banner, not overlapping it"):
        assert banner["y"] + banner["height"] <= title["y"], (banner, title)
    evidence.checkpoint("push-banner")
    n.tap_go_to_settings()
    with allure.step("expect the Settings app in front"):
        end = time.monotonic() + 10
        while not settings_app.is_foreground() and time.monotonic() < end:
            time.sleep(0.5)
        assert settings_app.is_foreground(), "Settings did not open"
    settings_app.set_app_notifications(True, app.app_id)
    open_tab(pages)
    with allure.step("expect no banner with push allowed"):
        assert not n.is_visible("banner", 3), "the banner is still shown"


LIST_CHKS = ("CHK-NOTIF-004", "CHK-NOTIF-014", "CHK-NOTIF-031")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTIF-006")
@pytest.mark.chk(*LIST_CHKS)
@allure.tag(*LIST_CHKS)
@allure.title(
    "TC-NOTIF-006 A long list scrolls; a long job name wraps inside the screen; rows do not overlap"
)
def test_long_list(
    notif_job, ui_login, field_services_api, tech_user_id, driver, pages, expected, evidence
):
    n = pages.notes
    jobs = [notif_job() for _ in range(9)]
    jobs.append(notif_job(LONG_TITLE))
    server_notifications(field_services_api, tech_user_id, driver, jobs, len(jobs))
    open_tab(pages)
    width = driver.get_window_size()["width"]
    rows = n.rows()
    evidence.checkpoint("long-list")
    with allure.step("expect the long job name first, whole, in its row"):
        assert expected(LONG_TITLE) in rows[0].description, rows[0].description
    with allure.step("expect every row inside the screen width and no two rows overlapping"):
        assert all(r.x >= 0 and r.x + r.width <= width for r in rows), rows
        assert all(r.y + r.height <= s.y + 1 for r, s in zip(rows, rows[1:], strict=False)), rows
        assert rows[0].height > rows[1].height, (rows[0], rows[1])
    oldest = expected(jobs[0].job_id)
    bottom = pages.tabs.visible("notifications").rect["y"]  # the list ends above the tab bar

    def shown() -> bool:
        return any(oldest in r.description and r.y + r.height <= bottom for r in n.rows())

    with allure.step("expect the oldest job's row below the screen, then shown after scrolling"):
        assert not shown(), "the oldest row is already on screen — nothing to scroll"
        for _ in range(SCROLLS):
            n.scroll_down()
            if shown():
                break
        assert shown(), n.descriptions()
