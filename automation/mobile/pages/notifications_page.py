"""Notifications — root only (module 11 extends it)."""

from pages.base_page import BasePage
from screens.notifications_map import NOTIFICATIONS


class NotificationsPage(BasePage):
    screen = NOTIFICATIONS
