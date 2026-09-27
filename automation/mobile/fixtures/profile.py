"""The account data and its undo for module 12 Profile (pytest plugin, registered in conftest.py).

| Test-case precondition                                   | Fixture             |
|----------------------------------------------------------|---------------------|
| the main account's name as the server holds it           | ``account``         |
| the main account's name put back after the test          | ``name_restored``   |
| App theme Auto again after the test                      | ``theme_restored``  |
| a throwaway technician registered in the app, Jobs list  | ``throwaway_account`` |

Owner, 2026-09-27 (Q-PRF-1…3): the main account's name may be changed and is put back; an account
is deleted only when it is a throwaway one registered by the test; a log out signs the main account
out (the next test signs in again).
"""

import contextlib
from collections.abc import Iterator
from dataclasses import dataclass

import allure
import pytest
from selenium.common.exceptions import TimeoutException

from fixtures.test_data import NewUser


@dataclass(frozen=True)
class Account:
    user_id: str
    first_name: str
    last_name: str

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@pytest.fixture
def account(field_services_api, tech) -> Account:
    """The main test account's name, read from the server (``GET /user/{id}``)."""
    user_id = field_services_api.technician_user_id(tech.email)
    user = field_services_api.user(user_id) or {}
    return Account(user_id, str(user.get("firstName", "")), str(user.get("lastName", "")))


@pytest.fixture
def name_restored(account, field_services_api) -> Iterator[Account]:
    """If the test leaves the account with another name, it is put back through the API."""
    try:
        yield account
    finally:
        user = field_services_api.user(account.user_id) or {}
        if (user.get("firstName"), user.get("lastName")) != (account.first_name, account.last_name):
            field_services_api.restore_user_name(
                account.user_id, account.first_name, account.last_name
            )


@pytest.fixture
def theme_restored(app) -> Iterator[None]:
    """App theme back to Auto after the test, pass or fail (the app's preference)."""
    try:
        yield
    finally:
        app.reset_theme()


@contextlib.contextmanager
def _blocked_on_timeout(reason: str) -> Iterator[None]:
    try:
        yield
    except TimeoutException as exc:
        pytest.skip(f"Blocked: {reason} ({exc.msg or 'timeout'})")


@dataclass(frozen=True)
class Throwaway:
    user: NewUser
    user_id: str


@pytest.fixture
def throwaway_account(new_user, logged_out_app, driver, platform, tech, field_services_api):
    """``{{new_user}}`` registered in the app (Email channel, DEV code) → Jobs list; its user id
    is kept, and whatever is left of it is removed through the API after the test (the app
    deletes the technician; the user record may stay). ``new_user`` then clears the app."""
    from pages.jobs_list_page import JobsListPage
    from pages.otp_page import OtpPage
    from pages.registration_page import RegistrationPage
    from pages.welcome_page import WelcomePage

    user_ids: list[str] = []
    try:
        with (
            allure.step(f"precondition: register the throwaway technician {new_user.email}"),
            _blocked_on_timeout("the registration precondition failed; TC-AUTH-013 owns it"),
        ):
            WelcomePage(driver, platform).open_sign_up()
            reg = RegistrationPage(driver, platform)
            reg.fill_form(new_user.first_name, new_user.last_name, new_user.phone_national,
                          new_user.email)  # fmt: skip
            reg.choose_channel("email")
            reg.scroll_to("continue")
            reg.tap("continue")
            OtpPage(driver, platform).enter_code(tech.otp)
            JobsListPage(driver, platform).assert_open(30)
            found = field_services_api.find_technicians_by_email(new_user.email)
            user_ids += [str(t["user"]["id"]) for t in found if (t.get("user") or {}).get("id")]
        yield Throwaway(new_user, user_ids[0] if user_ids else "")
    finally:
        for user_id in user_ids:
            field_services_api.delete_test_user(user_id)
