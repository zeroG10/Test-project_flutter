"""Edit profile — behaviour over screens/edit_profile_map.py (module 12, recon 13)."""

import allure

from helpers import waits
from pages.base_page import BasePage
from screens.edit_profile_map import DELETE_DIALOG, EDIT_PROFILE, UNSAVED_DIALOG

SAVE_WAIT = 20.0


class UnsavedDialog(BasePage):
    screen = UNSAVED_DIALOG


class DeleteDialog(BasePage):
    screen = DELETE_DIALOG


class EditProfilePage(BasePage):
    screen = EDIT_PROFILE

    def field(self, alias: str) -> str:
        """The text of a name field (``value``) or of a disabled field."""
        return str(self.visible(alias, 5).get_attribute("value") or "")

    def is_enabled(self, alias: str) -> bool:
        return self.visible(alias, 5).get_attribute("enabled") == "true"

    def set_name(self, alias: str, text: str) -> None:
        """Clear the field, then type ``text`` into the focused field (the field re-renders on
        focus — recon 8 / 13)."""
        with allure.step(f"edit-profile.{alias} ← {text!r}"):
            self.clear(alias, 5)
            if text:
                self.tap(alias)
                waits.focused(self.driver).send_keys(text)

    def save(self) -> None:
        with allure.step("tap edit-profile.save → back on Profile"):
            self.tap("save", 5)
            self.wait_gone("title", SAVE_WAIT)
