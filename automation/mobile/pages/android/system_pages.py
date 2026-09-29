"""Android-only screens (recon A1): Google Maps, the dialer, system dialogs.

Behaviour over screens/android/*_map.py. None of these exists on iOS (the in-app browser shows
the map, the simulator has no Phone app, system alerts are answered by ``autoAcceptAlerts``).
"""

import allure

from helpers import waits
from pages.base_page import BasePage
from screens.android.dialer_map import DIALER, DIALER_PACKAGE
from screens.android.location_manual_map import LOCATION_MANUAL
from screens.android.maps_app_map import MAPS_APP, MAPS_PACKAGE
from screens.android.system_dialogs_map import (
    ANR_DIALOG,
    LOCATION_ACCURACY,
    NOTIFICATION_PERMISSION,
)


class MapsAppPage(BasePage):
    screen = MAPS_APP

    def expect_place(self, place: str, timeout: float) -> None:
        """Google Maps is in front and its search holds ``place`` (a part of the job address)."""
        with allure.step(f"expect Google Maps to show {place!r}"):
            waits.wait_until(
                self.driver,
                lambda d: d.query_app_state(MAPS_PACKAGE) == 4,
                timeout,
                "Google Maps did not open",
            )
            if self.is_visible("skip", 3):  # the first-run offer of a fresh emulator
                self.tap("skip")
            waits.wait_until(
                self.driver,
                lambda _d: place in self.label_of(self.find("search", 2)),
                timeout,
                f"Google Maps does not show {place!r}",
            )


class DialerPage(BasePage):
    screen = DIALER

    def number(self, timeout: float = 15) -> str:
        """The dialed number, once the dialer is in front — nothing is ever called."""
        waits.wait_until(
            self.driver,
            lambda d: d.query_app_state(DIALER_PACKAGE) == 4,
            timeout,
            "the dialer did not open",
        )
        return self.field_value(self.visible("number", timeout))


class NotificationPermissionDialog(BasePage):
    screen = NOTIFICATION_PERMISSION

    def answer_if_shown(self, allow: bool = True, timeout: float = 3) -> bool:
        """Answer the system notification prompt if it is up; whether it was."""
        if not self.is_visible("allow", timeout):
            return False
        with allure.step(f"system prompt: notifications → {'Allow' if allow else 'Deny'}"):
            self.tap("allow" if allow else "deny")
        return True


class LocationAccuracyDialog(BasePage):
    screen = LOCATION_ACCURACY


class LocationManualDialog(BasePage):
    screen = LOCATION_MANUAL


class AnrDialog(BasePage):
    screen = ANR_DIALOG
