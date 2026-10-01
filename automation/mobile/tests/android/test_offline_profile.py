"""Profile — Android offline (step 5): TC-PRF-009.

Source: qa/mobile/12-profile/android/profile-test-cases.md (owner-validated 2026-10-01;
Resolved D-OFF-6 — no answer, «не знаю»: the test proves the session is cleared (FR-PROF-07);
whether local notes / photos / drafts must go stays an open question, not verified here).

Every expected text goes through ``expected(...)`` (--prove-red breaks it).
"""

import allure
import pytest

from pages.jobs_list_page import JobsListPage
from pages.profile_page import LogoutDialog, ProfilePage
from pages.tabbar_page import TabBarPage
from pages.welcome_page import WelcomePage
from tests.shared.test_profile import open_profile

SERVER = 30.0


@pytest.fixture
def pages(driver, platform):
    class Pages:
        tabs = TabBarPage(driver, platform)
        profile = ProfilePage(driver, platform)
        logout = LogoutDialog(driver, platform)
        welcome = WelcomePage(driver, platform)
        jobs = JobsListPage(driver, platform)

    return Pages


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-PRF-009")
@pytest.mark.chk("CHK-PRF-030")
@allure.tag("CHK-PRF-030")
@allure.title(
    "TC-PRF-009 Log out offline: the dialog clears the session (Welcome); a cold start while "
    "still offline stays on Welcome — the session is actually cleared, not just hidden"
)
def test_log_out_offline_clears_session(ui_login, app, network, pages, expected, evidence):
    open_profile(pages)
    network.off()  # open device.network off

    d = pages.logout
    pages.profile.tap("logout", 5)  # click profile.logout
    d.assert_open(5)
    with allure.step("expect the logout dialog's texts, same as online"):
        assert d.text("title") == expected("Log out"), d.text("title")
        assert d.text("message").strip() == expected("Are you sure you want to log out?")
        d.visible("cancel")
        d.visible("confirm")
    evidence.checkpoint("logout-dialog-offline")

    d.tap("confirm")  # click logout-dialog.confirm
    pages.welcome.assert_open(SERVER)  # expect-visible welcome.root — signed out while offline
    evidence.checkpoint("signed-out-offline")

    app.relaunch()  # open app: terminate, then cold start (still offline)
    pages.welcome.assert_open(SERVER)  # expect-visible welcome.root — stays signed out
    pages.jobs.wait_gone("root", 2)  # expect-hidden jobs-list.root — no cached Jobs list
