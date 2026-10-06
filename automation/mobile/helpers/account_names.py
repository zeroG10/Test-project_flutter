"""The test accounts' names — the project's hook for the privacy check of the shared reports.

``automation/tools/mobile_redact_screens.py`` hides every test account's email, phone and name
on the shared copy of the reports. Email and phone come from ``.env``; a project may also put the
names there (``APP_USER_NAME`` …) or, as here, read them from the product's API so a renamed
account is still hidden. Runs in this harness's environment, in a child process; the names go
back to the caller and are never printed.
"""

from __future__ import annotations

from config.settings import settings
from helpers.field_services_api import FieldServicesApi


def account_names() -> list[str]:
    """First and last name of every test account the runs sign in with (``settings.accounts()``)."""
    api = FieldServicesApi()
    try:
        names: list[str] = []
        for email, _ in settings.accounts():
            found = api.find_technicians_by_email(email) if email else []
            user = (found[0].get("user") or {}) if found else {}
            names += [user.get("firstName", ""), user.get("lastName", "")]
        return [n for n in names if n]
    finally:
        api.close()
