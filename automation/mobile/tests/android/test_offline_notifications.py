"""Notifications — Android offline (step 5): TC-NOTIF-007.

Source: qa/mobile/11-notifications/android/notifications-test-cases.md (owner-validated
2026-10-01; Resolved D-OFF-4 — no cache, the offline message + Try again is the accepted
behaviour). Android only: CHK-NOTIF-029 and CHK-NOTIF-030 (identical checklist text) are
merged into this one TC, the same way the manual checklist does.

Every expected text goes through ``expected(...)`` (--prove-red breaks it).
"""

import allure
import pytest

from fixtures.notifications import server_notifications
from pages.notifications_page import NotificationsPage
from pages.tabbar_page import TabBarPage
from tests.shared.test_notifications import open_tab

OFFLINE_TITLE = "No internet connection"
TRY_AGAIN = "Try again"


@pytest.fixture
def pages(driver, platform):
    class Pages:
        tabs = TabBarPage(driver, platform)
        notes = NotificationsPage(driver, platform)

    return Pages


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-NOTIF-007")
@pytest.mark.chk("CHK-NOTIF-029", "CHK-NOTIF-030")
@allure.tag("CHK-NOTIF-029", "CHK-NOTIF-030")
@allure.title(
    "TC-NOTIF-007 Offline: no cached rows, only the offline message and 'Try again'; back "
    "online, 'Try again' shows the list"
)
def test_notifications_offline_no_cache(
    notif_job, ui_login, field_services_api, tech_user_id, driver, network, pages, expected,
    evidence,
):  # fmt: skip
    job = notif_job()
    server_notifications(field_services_api, tech_user_id, driver, [job], 1)
    open_tab(pages)  # click tabbar.notifications, then refresh
    pages.notes.row(job.job_id)  # the row shown online — at least 1 row
    evidence.checkpoint("notifications-online")

    network.off()  # open device.network off
    open_tab(pages)  # click tabbar.notifications, then refresh — the screen reloads offline
    with allure.step("expect no notification row (no cache, D-OFF-4)"):
        assert not pages.notes.rows(), pages.notes.rows()  # expect-hidden notifications.row
    # expect-visible notifications.offline-title / .offline-text / .try-again
    pages.notes.expect_text("offline-title", expected(OFFLINE_TITLE), 10)
    pages.notes.visible("offline-text", 5)
    pages.notes.expect_text("try-again", expected(TRY_AGAIN), 5)
    evidence.checkpoint("notifications-offline")

    network.on()  # open device.network on
    pages.notes.tap("try-again")  # click notifications.try-again — retry requested
    pages.notes.row(job.job_id)  # expect-visible notifications.row — the list reappears
