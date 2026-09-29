"""Jobs — weekly calendar mode of the same screen (module 03-order-list).

Source: recon 3b and recon 4 (qa/shared/recon-dumps/ios-2026-09-24/recon4_calendar_*.xml).
Day cells are texts named by the full date ('Thursday, September 24, 2026'); the selected day's
title under the strip is 'Thursday, 24 September'. No month / year, no arrows: weeks change by a
horizontal swipe on the strip (D-ORDL-6, -7). Cards: the same format as the list
(screens/jobs_list_map.py). The toggle back to the list is jobs-list.view-toggle.

Android: qa/shared/recon-dumps/android-2026-09-29/jobs_calendar.xml,
jobs_calendar_after_refresh.xml (recon A1) — same day-cell and selected-day-title formats;
today ('Tuesday, September 29, 2026') carries NO ', Today' suffix (checked, recon A1).
BUG-ORDL-001 reproduces on Android too (D-ORDL-A3): a list refresh does not reach the
calendar's own copy of the jobs.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen
from screens.jobs_list_map import EMPTY_MESSAGE

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_DAY_CELL = _TEXT + "name MATCHES '^[A-Za-z]+day, [A-Za-z]+ [0-9]+, [0-9]+$'"
_DAY_CELL_ANDROID = (
    'new UiSelector().descriptionMatches("^[A-Za-z]+day, [A-Za-z]+ [0-9]+, [0-9]+$")'
)

JOBS_CALENDAR = Screen(
    id="jobs-calendar",
    anchor="root",
    elements={
        "root": El(
            android=(_U, _DAY_CELL_ANDROID),
            ios=(_P, _DAY_CELL),
            note="any day cell — they exist only in calendar mode",
        ),
        "week": El(
            android=(_U, _DAY_CELL_ANDROID),
            ios=(_P, _DAY_CELL),
            note="a day cell; the strip is swiped across it",
        ),
        "day": El(
            android=(_A, "{text}"),
            ios=(_A, "{text}"),
            note="parametrised by the full date, e.g. 'Thursday, September 24, 2026'",
        ),
        "selected-day-title": El(
            android=(
                _U,
                'new UiSelector().descriptionMatches("^[A-Za-z]+day, [0-9]+ [A-Za-z]+$")',
            ),
            ios=(
                _P,
                "type == 'XCUIElementTypeStaticText' AND "
                "name MATCHES '^[A-Za-z]+day, [0-9]+ [A-Za-z]+$'",
            ),
            note="the title of the selected day, e.g. 'Thursday, 24 September'",
        ),
        "card": El(
            android=(_U, "new UiSelector().descriptionContains({text})"),
            ios=(
                _P,
                "name CONTAINS {text} AND (type == 'XCUIElementTypeStaticText' "
                "OR type == 'XCUIElementTypeImage')",
            ),
            note="parametrised by the jobId; same card as the list",
        ),  # fmt: skip
        "empty-state": El(
            android=(_A, "No jobs"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'No jobs'"),
        ),
        "empty-message": El(android=(_A, EMPTY_MESSAGE), ios=(_A, EMPTY_MESSAGE)),
    },
)
