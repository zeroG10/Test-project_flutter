"""Profile (module 12) — TC-PRF-001…008.

Source of every step and expectation: qa/mobile/12-profile/profile-test-cases.md (recon 13; the
owner's decisions 2026-09-27). The main test account is read from the server; its name is changed
only in TC-PRF-003 and put back. An account is deleted only in TC-PRF-008, on a throwaway technician
registered by the test (fixtures/profile.py). A log out signs the main account out; the next test
signs in again (``ui_login``).

Accepted baseline (owner, D-PRF-1…6): the email is not editable; Back with changes asks "Unsaved
Changes"; the theme is a menu Auto / Light / Dark; Delete account sits on Edit profile and asks for
no typed word; Save is disabled for a bad name without a message. Every expected value goes through
``expected(...)``.
"""

import re
import time
from pathlib import Path

import allure
import pytest

from pages.edit_profile_page import DeleteDialog, EditProfilePage, UnsavedDialog
from pages.in_app_browser_page import InAppBrowserPage
from pages.jobs_list_page import JobsListPage
from pages.login_page import LoginPage
from pages.profile_page import LIGHT_ABOVE, LogoutDialog, ProfilePage
from pages.tabbar_page import TabBarPage
from pages.welcome_page import WelcomePage

SERVER = 30.0
BUILD_INFO = Path(__file__).resolve().parents[2] / "builds" / "ios" / "BUILD_INFO.txt"
UNREGISTERED_EMAIL = "This email is not registered yet. Create an account to get started."


@pytest.fixture
def pages(driver, platform):
    class Pages:
        tabs = TabBarPage(driver, platform)
        profile = ProfilePage(driver, platform)
        edit = EditProfilePage(driver, platform)
        unsaved = UnsavedDialog(driver, platform)
        delete = DeleteDialog(driver, platform)
        logout = LogoutDialog(driver, platform)
        browser = InAppBrowserPage(driver, platform)
        welcome = WelcomePage(driver, platform)
        login = LoginPage(driver, platform)
        jobs = JobsListPage(driver, platform)

    return Pages


def open_profile(pages) -> None:
    """The Profile tab (the tabs appear a moment after launch)."""
    pages.tabs.tap("profile", SERVER)
    pages.profile.assert_open(SERVER)


def open_edit(pages) -> None:
    pages.profile.tap("edit", 5)
    pages.edit.assert_open(10)


def build_version() -> str:
    """'1.1.1 (178)' from the build under test (builds/ios/BUILD_INFO.txt); Blocked without it."""
    if not BUILD_INFO.exists():
        pytest.skip("Blocked: builds/ios/BUILD_INFO.txt missing — the build's version is unknown")
    found = re.search(r"^version:\s*(.+)$", BUILD_INFO.read_text(encoding="utf-8"), re.M)
    if not found:
        pytest.skip("Blocked: no 'version:' line in builds/ios/BUILD_INFO.txt")
    return found.group(1).strip()


def server_name(api, account, until) -> dict:
    """The account's user record, read until ``until(user)`` holds or SERVER seconds pass."""
    end, user = time.monotonic() + SERVER, {}
    while time.monotonic() < end:
        user = api.user(account.user_id) or {}
        if until(user):
            break
        time.sleep(2)
    return user


def expect_card(pages, expected, name: str, tech) -> None:
    card = pages.profile.card(10)
    with allure.step("expect the card: name, phone, email of the account"):
        assert card.name == expected(name), card
        assert card.phone == expected(tech.phone), card
        assert card.email == expected(tech.email), card


CARD_CHKS = ("CHK-PRF-001", "CHK-PRF-002", "CHK-PRF-003", "CHK-PRF-004", "CHK-PRF-005",
             "CHK-PRF-006", "CHK-PRF-007", "CHK-PRF-008")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-001")
@pytest.mark.chk(*CARD_CHKS)
@allure.tag(*CARD_CHKS)
@allure.title(
    "TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the "
    "settings and the footer; the same after a restart"
)
def test_profile_card(ui_login, app, account, tech, pages, expected, evidence):
    p, version = pages.profile, build_version()
    for attempt in ("first open", "after a restart"):
        with allure.step(f"Profile — {attempt}"):
            if attempt == "after a restart":
                app.relaunch()
            open_profile(pages)
            pages.tabs.expect_selected(expected("profile"))
            expect_card(pages, expected, account.name, tech)
            p.expect_enabled("edit", timeout=5)
            p.visible("theme", 5)
            p.visible("privacy", 5)
            p.visible("logout", 5)
            p.expect_text("version", expected(f"v{version}"))
            evidence.checkpoint(f"profile-{attempt.replace(' ', '-')}")


EDIT_CHKS = ("CHK-PRF-009", "CHK-PRF-010", "CHK-PRF-011", "CHK-PRF-012", "CHK-PRF-013",
             "CHK-PRF-014", "CHK-PRF-016", "CHK-PRF-019", "CHK-PRF-020")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-002")
@pytest.mark.chk(*EDIT_CHKS)
@allure.tag(*EDIT_CHKS)
@allure.title(
    "TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, "
    "Leave saves nothing"
)
def test_edit_profile_rules(
    ui_login, name_restored, field_services_api, tech, pages, expected, evidence
):
    account, e = name_restored, pages.edit
    open_profile(pages)
    open_edit(pages)
    e.visible("back")
    e.expect_enabled("save", timeout=5)
    with allure.step("expect the fields pre-filled; phone and email disabled"):
        assert e.field("first-name") == expected(account.first_name), e.field("first-name")
        assert e.field("last-name") == expected(account.last_name), e.field("last-name")
        phone = re.sub(r"\D", "", e.field("phone"))
        assert phone.endswith(expected(tech.phone_national)), e.field("phone")
        assert e.field("email") == expected(tech.email), e.field("email")
        assert not e.is_enabled("phone"), "the phone field is enabled"
        assert not e.is_enabled("email"), "the email field is enabled"
    evidence.checkpoint("edit-profile")
    e.set_name("first-name", "")
    e.expect_disabled("save", timeout=5)
    e.set_name("first-name", "QA")
    e.expect_enabled("save", timeout=5)
    e.set_name("last-name", "")
    e.expect_disabled("save", timeout=5)
    e.tap("back")
    pages.unsaved.assert_open(5)
    pages.unsaved.expect_text("title", expected("Unsaved Changes"))
    pages.unsaved.tap("leave")
    pages.profile.assert_open(10)
    expect_card(pages, expected, account.name, tech)
    user = field_services_api.user(account.user_id) or {}
    with allure.step("expect the server's name unchanged"):
        assert (user.get("firstName"), user.get("lastName")) == (
            expected(account.first_name), expected(account.last_name)
        ), user  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-003")
@pytest.mark.chk("CHK-PRF-017", "CHK-PRF-018")
@allure.tag("CHK-PRF-017", "CHK-PRF-018")
@allure.title(
    "TC-PRF-003 A changed name is saved: Profile shows it at once, the server has it; the name is "
    "put back"
)
def test_edit_name_saved(
    ui_login, name_restored, field_services_api, tech, pages, expected, evidence
):
    account, e, api = name_restored, pages.edit, field_services_api
    new_first = "Qaedit" if account.first_name != "Qaedit" else "Qaagain"
    open_profile(pages)
    open_edit(pages)
    e.set_name("first-name", new_first)
    e.save()
    pages.profile.assert_open(10)
    expect_card(pages, expected, f"{new_first} {account.last_name}", tech)
    evidence.checkpoint("name-saved")
    user = server_name(api, account, until=lambda u: u.get("firstName") == new_first)
    with allure.step("expect the new first name on the server"):
        assert user.get("firstName") == expected(new_first), user
    open_edit(pages)
    e.set_name("first-name", account.first_name)
    e.save()
    pages.profile.assert_open(10)
    expect_card(pages, expected, account.name, tech)
    user = server_name(api, account, until=lambda u: u.get("firstName") == account.first_name)
    with allure.step("expect the old first name back on the server"):
        assert user.get("firstName") == expected(account.first_name), user


THEME_CHKS = ("CHK-PRF-021", "CHK-PRF-022", "CHK-PRF-023")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-004")
@pytest.mark.chk(*THEME_CHKS)
@allure.tag(*THEME_CHKS)
@allure.title(
    "TC-PRF-004 App theme: Dark turns the app dark at once and stays after a restart; Auto again"
)
def test_app_theme(ui_login, theme_restored, app, pages, expected, evidence):
    p = pages.profile
    open_profile(pages)
    with allure.step("precondition: App theme (Auto), light"):
        if p.theme() != "Auto" or p.brightness() < LIGHT_ABOVE:
            pytest.skip(f"Blocked: the app is not in Auto / light ({p.theme()!r})")
    p.set_theme("Dark")
    with allure.step("expect 'App theme (Dark)'"):
        assert p.theme() == expected("Dark"), p.theme()
    p.expect_dark()
    evidence.checkpoint("theme-dark")
    app.relaunch()
    open_profile(pages)
    with allure.step("expect 'App theme (Dark)' after a restart"):
        assert p.theme() == expected("Dark"), p.theme()
    p.expect_dark()
    evidence.checkpoint("theme-dark-restart")
    p.set_theme("Auto")
    with allure.step("expect 'App theme (Auto)'"):
        assert p.theme() == expected("Auto"), p.theme()
    p.expect_dark(False)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-005")
@pytest.mark.chk("CHK-PRF-024", "CHK-PRF-025")
@allure.tag("CHK-PRF-024", "CHK-PRF-025")
@allure.title("TC-PRF-005 Privacy Policy opens in the app's browser; Close returns to Profile")
def test_privacy_policy(ui_login, pages, expected, evidence):
    open_profile(pages)
    pages.profile.tap("privacy", 5)
    pages.browser.assert_open(SERVER)
    pages.browser.expect_host(expected("concerttech.com"), SERVER)
    evidence.checkpoint("privacy-policy")
    pages.browser.close()
    pages.profile.assert_open(10)


LOGOUT_CHKS = ("CHK-PRF-026", "CHK-PRF-027", "CHK-PRF-028", "CHK-PRF-029")


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-006")
@pytest.mark.chk(*LOGOUT_CHKS)
@allure.tag(*LOGOUT_CHKS)
@allure.title(
    "TC-PRF-006 Log out: the dialog; Cancel stays signed in; Log out goes to Welcome and a "
    "relaunch stays there"
)
def test_log_out(ui_login, app, pages, expected, evidence):
    d = pages.logout
    open_profile(pages)
    pages.profile.tap("logout", 5)
    d.assert_open(5)
    with allure.step("expect the dialog's texts"):
        assert d.text("title") == expected("Log out"), d.text("title")
        assert d.text("message").strip() == expected("Are you sure you want to log out?")
    d.visible("cancel")
    d.visible("confirm")
    evidence.checkpoint("logout-dialog")
    d.tap("cancel")
    d.wait_gone("title", 5)
    pages.profile.assert_open(5)
    pages.profile.log_out(confirm=True)
    pages.welcome.assert_open(SERVER)
    evidence.checkpoint("logged-out")
    app.relaunch()
    pages.welcome.assert_open(SERVER)
    with allure.step("expect no Jobs list after a relaunch (signed out)"):
        assert not pages.jobs.is_open(3), "the Jobs list opened after the log out"


DELETE_DIALOG_CHKS = ("CHK-PRF-031", "CHK-PRF-032", "CHK-PRF-033")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-007")
@pytest.mark.chk(*DELETE_DIALOG_CHKS)
@allure.tag(*DELETE_DIALOG_CHKS)
@allure.title("TC-PRF-007 The delete-account dialog as the app has it; Cancel changes nothing")
def test_delete_account_dialog(ui_login, field_services_api, tech, pages, expected, evidence):
    d, e = pages.delete, pages.edit
    open_profile(pages)
    open_edit(pages)
    e.tap("delete-account", 5)
    d.assert_open(5)
    with allure.step("expect the dialog's texts, Cancel and Delete, no text field (D-PRF-4)"):
        assert d.text("title") == expected("Delete account"), d.text("title")
        assert d.text("message").strip() == expected("Are you sure you want to delete account?")
        d.visible("cancel")
        d.visible("delete")
        assert not e.driver.find_elements(*e.locator("any-text-field")), "a text field is shown"
    evidence.checkpoint("delete-dialog")
    d.tap("cancel")
    d.wait_gone("title", 5)
    e.assert_open(5)
    with allure.step("expect the account still on the server"):
        assert field_services_api.find_technicians_by_email(tech.email), "the account is gone"
    e.tap("back")
    pages.profile.assert_open(10)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PRF-008")
@pytest.mark.chk("CHK-PRF-034", "CHK-PRF-035")
@allure.tag("CHK-PRF-034", "CHK-PRF-035")
@allure.title(
    "TC-PRF-008 A throwaway account deleted in the app: Welcome; the same email cannot sign in; "
    "gone on the server"
)
def test_delete_throwaway_account(throwaway_account, field_services_api, pages, expected, evidence):
    user = throwaway_account.user
    open_profile(pages)
    with allure.step("expect the throwaway account on the card"):
        assert pages.profile.card(10).email == expected(user.email), pages.profile.card()
    open_edit(pages)
    pages.edit.tap("delete-account", 5)
    pages.delete.assert_open(5)
    pages.delete.tap("delete")
    pages.welcome.assert_open(SERVER)
    evidence.checkpoint("account-deleted")
    end, found = time.monotonic() + SERVER, [True]
    while time.monotonic() < end:
        found = field_services_api.find_technicians_by_email(user.email)
        if not found:
            break
        time.sleep(2)
    with allure.step("expect no technician with the email on the server"):
        assert not found, found
    pages.welcome.open_login()
    pages.login.type("identifier", user.email)
    pages.login.tap("continue")
    pages.login.expect_error(expected(UNREGISTERED_EMAIL), SERVER)
    evidence.checkpoint("email-not-registered")
