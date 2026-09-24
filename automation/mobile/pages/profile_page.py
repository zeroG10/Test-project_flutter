"""Profile — root only (module 12 extends it)."""

from pages.base_page import BasePage
from screens.profile_map import PROFILE


class ProfilePage(BasePage):
    screen = PROFILE
