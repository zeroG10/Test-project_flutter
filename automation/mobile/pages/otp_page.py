"""OTP verification — behaviour over screens/otp_map.py.

The code field is a hidden 1×1 input that already has focus (the four cells are drawn);
the app submits by itself after the 4th digit (D-5). ``Incorrect code.`` sits in the tree
while hidden — only its visibility means anything (recon 3b).
"""

import contextlib
import re

import allure
from selenium.common.exceptions import WebDriverException

from helpers import waits
from pages.base_page import BasePage, normalized
from screens.otp_map import OTP

_MM_SS = re.compile(r"(\d{1,2}):(\d{2})")
OTP_SCREEN_TIMEOUT = 20.0  # the code request goes to the (weak) DEV server


class OtpPage(BasePage):
    screen = OTP

    def enter_code(self, code: str) -> None:
        with allure.step(f"OTP: enter {len(code)} digits"):
            # The code locator is "the only input on the screen" — valid ONLY once this screen
            # is open. Typing earlier put the code into the Login field (prove-red run, TC-003).
            self.assert_open(OTP_SCREEN_TIMEOUT)
            field = self.find("code")
            with contextlib.suppress(WebDriverException):
                field.clear()  # after a wrong code the field may still hold the old digits
            try:
                field.send_keys(code)
            except WebDriverException:
                # The hidden field may refuse a direct type; it already holds the focus.
                with allure.step("code field refused direct input → typing into the focused field"):
                    waits.focused(self.driver).send_keys(code)

    def expect_error_shown(self, shown: bool = True, timeout: float | None = None) -> None:
        """``Incorrect code.`` really drawn (or not) — by pixels; the tree always says visible."""
        self.expect_drawn("error", drawn=shown, timeout=timeout)

    def expect_sent_to(self, destination: str) -> None:
        """The screen names where the code went (full email, or the phone's last digits)."""
        self.visible("destination", text=destination)

    def countdown_seconds(self) -> int:
        """Seconds left before a new code may be requested, read from the resend text."""
        text = normalized(self.text("resend"))
        match = _MM_SS.search(text)
        if match is None:
            raise AssertionError(f"no m:ss countdown in the resend text {text!r}")
        return int(match.group(1)) * 60 + int(match.group(2))
