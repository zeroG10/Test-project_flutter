"""Jobs list — the first screen of a signed-in technician (module 03-order-list).

Source: recon 3b and recon 4 (qa/shared/recon-dumps/ios-2026-09-24/recon4_list_*.xml).
A card is ONE element whose name is the whole card: ``date\\ntime\\nstatus\\n<jobId> - <title>\\n
address`` — a StaticText, or an Image when the "Updated" banner tops it — so a card is found by
its jobId without a type, and its fields are parsed by pages/jobs_list_page.py. The list ↔ calendar
toggle has no name (TD-JOBS-001): it is the only unnamed button in the app bar. The tab bar lives
in screens/tabbar_map.py.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE

EMPTY_MESSAGE = (
    "Your list of jobs is currently empty. New jobs from your Project Facilitator will appear here."
)

JOBS_LIST = Screen(
    id="jobs-list",
    anchor="root",
    elements={
        # The app-bar title "Jobs list" stays in calendar mode too.
        "root": El(ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Jobs list'")),
        "view-toggle": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeButton' AND (name == nil OR name == '') AND rect.y < 140",
            ),
            note="unnamed icon button in the app bar (y ≈ 66) — TD-JOBS-001",
        ),
        "card": El(
            ios=(
                _P,
                "name CONTAINS {text} AND (type == 'XCUIElementTypeStaticText' "
                "OR type == 'XCUIElementTypeImage')",
            ),
            note="parametrised by the jobId; a StaticText, or an Image with the 'Updated' banner",
        ),  # fmt: skip
        "empty-state": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'No jobs'")),
        "empty-message": El(ios=(_A, EMPTY_MESSAGE)),
        "empty-image": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND (name == nil OR name == '')"),
            note="unlabelled picture above 'No jobs'; the tree reports it visible=false in list "
            "mode while it is drawn — decide by pixels (expect_drawn), TD-JOBS-002",
        ),
    },
)
