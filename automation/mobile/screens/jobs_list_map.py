"""Jobs list — the first screen of a signed-in technician (module 03-order-list).

Source: recon 3b and recon 4 (qa/shared/recon-dumps/ios-2026-09-24/recon4_list_*.xml).
A card is ONE element whose name is the whole card: ``date\\ntime\\nstatus\\n<jobId> - <title>\\n
address`` — a StaticText, or an Image when the "Updated" banner tops it — so a card is found by
its jobId without a type, and its fields are parsed by pages/jobs_list_page.py. The list ↔ calendar
toggle has no name (TD-JOBS-001): it is the only unnamed button in the app bar. The tab bar lives
in screens/tabbar_map.py.

Android: qa/shared/recon-dumps/android-2026-09-29/jobs_list.xml, jobs_list_empty.xml (recon A1)
— a card is one ``android.view.View`` (content-desc = the whole card, same format); the toggle
is an unnamed clickable ImageView top-right (TD-JOBS-001 holds); the empty-state picture is a
non-clickable unnamed ImageView, present in the tree only when the list is actually empty
(unlike iOS, where it exists but visible=false — Android difference, D-ORDL note).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR

EMPTY_MESSAGE = (
    "Your list of jobs is currently empty. New jobs from your Project Facilitator will appear here."
)

JOBS_LIST = Screen(
    id="jobs-list",
    anchor="root",
    elements={
        # The app-bar title "Jobs list" stays in calendar mode too.
        "root": El(
            android=(_A, "Jobs list"),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Jobs list'"),
        ),
        "view-toggle": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.ImageView")'
                ".clickable(true).instance(0)",
            ),
            ios=(
                _P,
                "type == 'XCUIElementTypeButton' AND (name == nil OR name == '') AND rect.y < 140",
            ),
            note="unnamed icon button in the app bar (y ≈ 66) — TD-JOBS-001. Android: the first "
            "clickable ImageView — the app bar comes before the tabs (recon A1); it has no "
            "content-desc at all, which no description selector matches (01+03 run 3)",
        ),
        "card": El(
            android=(_U, "new UiSelector().descriptionContains({text})"),
            ios=(
                _P,
                "name CONTAINS {text} AND (type == 'XCUIElementTypeStaticText' "
                "OR type == 'XCUIElementTypeImage')",
            ),
            note="parametrised by the jobId; a StaticText, or an Image with the 'Updated' banner "
            "on iOS — Android: one android.view.View, same content-desc format (recon A1)",
        ),  # fmt: skip
        "empty-state": El(
            android=(_A, "No jobs"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'No jobs'"),
        ),
        "empty-message": El(android=(_A, EMPTY_MESSAGE), ios=(_A, EMPTY_MESSAGE)),
        "empty-image": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.ImageView")'
                ".clickable(false).instance(0)",
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND (name == nil OR name == '')"),
            note="unlabelled picture above 'No jobs'; the tree reports it visible=false in list "
            "mode while it is drawn — decide by pixels (expect_drawn), TD-JOBS-002. Android: "
            "the node is only in the tree when the list is actually empty (jobs_list_empty.xml) "
            "— not present at all in the populated list (recon A1)",
        ),
    },
)
