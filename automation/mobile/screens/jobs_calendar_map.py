"""Jobs — weekly calendar mode of the same screen (module 03-order-list).

Source: recon 3b and recon 4 (qa/shared/recon-dumps/ios-2026-09-24/recon4_calendar_*.xml).
Day cells are texts named by the full date ('Thursday, September 24, 2026'); the selected day's
title under the strip is 'Thursday, 24 September'. No month / year, no arrows: weeks change by a
horizontal swipe on the strip (D-ORDL-6, -7). Cards: the same format as the list
(screens/jobs_list_map.py). The toggle back to the list is jobs-list.view-toggle.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen
from screens.jobs_list_map import EMPTY_MESSAGE

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_DAY_CELL = _TEXT + "name MATCHES '^[A-Za-z]+day, [A-Za-z]+ [0-9]+, [0-9]+$'"

JOBS_CALENDAR = Screen(
    id="jobs-calendar",
    anchor="root",
    elements={
        "root": El(ios=(_P, _DAY_CELL), note="any day cell — they exist only in calendar mode"),
        "week": El(ios=(_P, _DAY_CELL), note="a day cell; the strip is swiped across it"),
        "day": El(
            ios=(_A, "{text}"),
            note="parametrised by the full date, e.g. 'Thursday, September 24, 2026'",
        ),
        "selected-day-title": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeStaticText' AND "
                "name MATCHES '^[A-Za-z]+day, [0-9]+ [A-Za-z]+$'",
            ),
            note="the title of the selected day, e.g. 'Thursday, 24 September'",
        ),
        "card": El(
            ios=(
                _P,
                "name CONTAINS {text} AND (type == 'XCUIElementTypeStaticText' "
                "OR type == 'XCUIElementTypeImage')",
            ),
            note="parametrised by the jobId; same card as the list",
        ),  # fmt: skip
        "empty-state": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'No jobs'")),
        "empty-message": El(ios=(_A, EMPTY_MESSAGE)),
    },
)
