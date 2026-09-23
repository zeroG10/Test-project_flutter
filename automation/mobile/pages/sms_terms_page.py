"""SMS Messaging Terms & Conditions — behaviour over screens/sms_terms_map.py."""

import allure

from pages.base_page import BasePage
from screens.sms_terms_map import SMS_TERMS


class SmsTermsPage(BasePage):
    screen = SMS_TERMS

    def accept(self) -> None:
        """Scroll to the end (the button shows only there) and accept."""
        with allure.step("SMS Terms: accept"):
            self.scroll_to("accept")
            self.tap("accept")
