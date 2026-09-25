"""Notes of an In progress job: the list, the ⋮ menu, Add / Edit note and the dialogs (module 10,
SRS §3.1.3.4.5–7).

Source: recon 10 (qa/shared/recon-dumps/ios-2026-09-24/recon10_*.xml). A note row is one Image whose
label joins the date, the text and 'Show menu'; the ⋮ button is not an element (TD-NOTE-001) — the
page taps the row's right end. The toasts are full-screen Others named by their message.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_HEADER = "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND "

NOTES = Screen(
    id="notes",
    anchor="header",
    elements={
        "header": El(ios=(_P, _HEADER + "name == 'Notes'")),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "empty-title": El(ios=(_P, _TEXT + "name == 'No notes have been added yet'")),
        "empty-text": El(ios=(_P, _TEXT + "name == 'Add note to the report to get started.'")),
        "add-note": El(
            ios=(_P, _BUTTON + "name == 'Add note'"),
            note="two in the empty state (centre and bottom), the bottom one always",
        ),
        "row": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND name ENDSWITH 'Show menu'"),
            note="a note: '<dd MMM yyyy HH:mm>\\n<text>\\nShow menu' — parsed by the page",
        ),
        "toast": El(
            ios=(
                _P,
                "name == 'Note added successfully' OR name == 'Note saved successfully' "
                "OR name == 'Note deleted successfully'",
            ),
            note="a toast for ~3 s after a save / delete",
        ),  # fmt: skip
    },
)

NOTE_MENU = Screen(
    id="note-menu",
    anchor="edit",
    elements={
        "edit": El(ios=(_P, _BUTTON + "name == 'Edit'")),
        "delete": El(
            ios=(_P, _BUTTON + "name == 'Delete' AND rect.width > 100"),
            note="the menu's item (the dialog's Delete is 75 wide)",
        ),  # fmt: skip
    },
)

NOTE_EDITOR = Screen(
    id="note-editor",
    anchor="field",
    elements={
        "add-title": El(ios=(_P, _HEADER + "name == 'Add note'")),
        "edit-title": El(ios=(_P, _HEADER + "name == 'Edit note'")),
        "field": El(
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="the only field; named by its placeholder 'Add note', the text is in value",
        ),
        "counter": El(ios=(_P, "name MATCHES '^[0-9]+/500$'"), note="'N/500'"),
        "save": El(ios=(_P, _BUTTON + "name == 'Save'")),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "delete-note": El(ios=(_P, _BUTTON + "name == 'Delete note'"), note="Edit note only"),
    },
)

NOTE_DELETE_DIALOG = Screen(
    id="note-delete-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Delete note'")),
        "message": El(
            ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want delete this note.'")
        ),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(ios=(_P, _BUTTON + "name == 'Delete' AND rect.width < 100")),
    },
)

NOTE_UNSAVED_DIALOG = Screen(
    id="note-unsaved-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Unsaved Changes'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "leave": El(ios=(_P, _BUTTON + "name == 'Leave'")),
    },
)
