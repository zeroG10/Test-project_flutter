"""Registration — behaviour over screens/registration_map.py.

Unnamed controls (testability defects, decision 2026-09-23 — nearest labelled anchor):
* the two channel radios — told apart by where they sit inside ``channel-options``
  (SMS left, Email right); the selected one has ``value == "1"``;
* the SMS consent switch — the only switch on the screen.
Validation messages are drawn inside their field's bounds as text without an id, so a
field's errors are the texts found inside that field (``BasePage.texts_within``).
"""

import allure
from selenium.common.exceptions import WebDriverException

from helpers import waits
from pages.base_page import BasePage, normalized
from screens.registration_map import REGISTRATION

FIELDS = ("first-name", "last-name", "phone", "email")
CHANNELS = ("sms", "email")


class RegistrationPage(BasePage):
    screen = REGISTRATION

    # --- form ---------------------------------------------------------------------------

    def fill(self, field: str, value: str) -> None:
        if field not in FIELDS:
            raise ValueError(f"unknown registration field {field!r}; one of {FIELDS}")
        self.type(field, value)

    def fill_form(self, first_name: str, last_name: str, phone_national: str, email: str) -> None:
        with allure.step("Registration: fill the form"):
            self.fill("first-name", first_name)
            self.fill("last-name", last_name)
            self.fill("phone", phone_national)
            self.fill("email", email)

    def phone_prefix(self) -> str:
        """The visible country code, spaces removed ("+ 1" → "+1").

        The button's name is "United States + 1\\n+ 1": the spoken label, then what is drawn.
        """
        name = self.visible("phone-prefix").get_attribute("name") or ""
        return name.splitlines()[-1].replace(" ", "")

    # --- notification channel -----------------------------------------------------------

    def _radios(self) -> dict[str, object]:
        """{"sms": element, "email": element} by position inside channel-options."""
        box = self.rect("channel-options")
        middle = box["x"] + box["width"] / 2
        radios: dict[str, object] = {}
        for element in self.driver.find_elements(*self.locator("channel-radios")):
            rect = element.rect
            centre_x = rect["x"] + rect["width"] / 2
            centre_y = rect["y"] + rect["height"] / 2
            if not box["y"] <= centre_y <= box["y"] + box["height"]:
                continue  # an unnamed button elsewhere on the screen
            radios["sms" if centre_x < middle else "email"] = element
        if set(radios) != set(CHANNELS):
            raise AssertionError(
                f"expected SMS and Email radios in channel-options, found {sorted(radios)}"
            )
        return radios

    def choose_channel(self, channel: str) -> None:
        """Tap a channel radio. SMS opens the SMS Terms screen first (D-9)."""
        if channel not in CHANNELS:
            raise ValueError(f"channel must be one of {CHANNELS}")
        with allure.step(f"Registration: choose the {channel.upper()} channel"):
            self._radios()[channel].click()

    def selected_channel(self) -> str | None:
        for channel, element in self._radios().items():
            if str(element.get_attribute("value") or "") == "1":
                return channel
        return None

    def expect_channel(self, channel: str | None) -> None:
        with allure.step(f"expect channel selected: {channel}"):
            actual = self.selected_channel()
            assert actual == channel, f"selected channel is {actual!r}, expected {channel!r}"

    # --- SMS consent ----------------------------------------------------------------------

    def sms_consent_checked(self) -> bool:
        return self.value("sms-consent") == "1"

    def set_sms_consent(self, checked: bool = True) -> None:
        with allure.step(f"Registration: SMS consent → {'on' if checked else 'off'}"):
            if self.sms_consent_checked() != checked:
                self.tap("sms-consent")

    # --- validation messages --------------------------------------------------------------

    def field_errors(self, field: str) -> list[str]:
        return self.texts_within(field)

    def expect_field_error(self, field: str, text: str, timeout: float | None = None) -> None:
        wanted = normalized(text)
        with allure.step(f"expect {field} error {text!r}"):
            waits.wait_until(
                self.driver,
                lambda _d: wanted in self._errors_or_empty(field),
                timeout,
                f"{field}: no error {text!r} (shown: {self._errors_or_empty(field)})",
            )

    def expect_some_field_error(self, field: str, timeout: float | None = None) -> str:
        """An error is shown under ``field`` whatever its wording; returns the wording."""
        with allure.step(f"expect {field} shows an error"):
            waits.wait_until(
                self.driver,
                lambda _d: bool(self._errors_or_empty(field)),
                timeout,
                f"{field}: no error shown",
            )
            shown = self._errors_or_empty(field)
            allure.attach(
                "\n".join(shown),
                name=f"{field} error wording",
                attachment_type=allure.attachment_type.TEXT,
            )
            return shown[0]

    def expect_no_field_error(self, field: str, timeout: float | None = None) -> None:
        with allure.step(f"expect no error under {field}"):
            waits.wait_until(
                self.driver,
                lambda _d: not self._errors_or_empty(field),
                timeout,
                f"{field}: still shows {self._errors_or_empty(field)}",
            )

    def _errors_or_empty(self, field: str) -> list[str]:
        try:
            return self.field_errors(field)
        except WebDriverException:
            return []
