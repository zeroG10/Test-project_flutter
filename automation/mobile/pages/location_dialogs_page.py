"""The location prompts of a check-in start — behaviour over screens/location_dialogs_map.py.

The system permission alert is in the page source only while ``respectSystemAlerts`` is on, and
auto-accept (``defaultAlertAction``) must be off or WDA answers it first (recon 5 / 5b).
``system_alerts()`` switches both for the steps inside it and restores them afterwards.
"""

import contextlib
from collections.abc import Iterator

from pages.base_page import BasePage
from screens.location_dialogs_map import LOCATION_DISABLED, LOCATION_PROMPT


@contextlib.contextmanager
def system_alerts(driver, platform: str) -> Iterator[None]:
    """Let the test see and answer system alerts itself (iOS)."""
    if platform != "ios":
        yield
        return
    driver.update_settings({"defaultAlertAction": "", "respectSystemAlerts": True})
    try:
        yield
    finally:
        with contextlib.suppress(Exception):
            driver.update_settings({"defaultAlertAction": "accept", "respectSystemAlerts": False})


class LocationPromptPage(BasePage):
    screen = LOCATION_PROMPT


class LocationDisabledDialog(BasePage):
    screen = LOCATION_DISABLED
