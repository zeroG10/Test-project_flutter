"""The location prompts of a check-in start — behaviour over screens/location_dialogs_map.py.

The system permission alert is in the page source only while ``respectSystemAlerts`` is on — and
while it is on and the alert is up, the app's own elements are out of reach (run 1: 'Checking in'
not found under the alert). ``system_alerts()`` switches it on only for the steps that read or
answer the alert. Auto-accept (``defaultAlertAction``) must be off for the whole flow, or WDA
answers the alert — and may press an app dialog's button — first: wrap the flow in
``AppControl.alerts_left_alone()`` (recon 4, 5 / 5b).
"""

import contextlib
from collections.abc import Iterator

from pages.base_page import BasePage
from screens.location_dialogs_map import (
    LOCATION_DISABLED,
    LOCATION_PROMPT,
    MOCK_LOCATION,
    NOT_AT_SITE,
)


@contextlib.contextmanager
def system_alerts(driver, platform: str) -> Iterator[None]:
    """Let the test see a system alert in the page source (iOS) — for the steps inside only."""
    if platform != "ios":
        yield
        return
    driver.update_settings({"respectSystemAlerts": True})
    try:
        yield
    finally:
        with contextlib.suppress(Exception):
            driver.update_settings({"respectSystemAlerts": False})


class LocationPromptPage(BasePage):
    screen = LOCATION_PROMPT


class LocationDisabledDialog(BasePage):
    screen = LOCATION_DISABLED


class NotAtSiteDialog(BasePage):
    screen = NOT_AT_SITE


class MockLocationDialog(BasePage):
    screen = MOCK_LOCATION
