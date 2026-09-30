"""Notes of an In progress job: the list, the ⋮ menu, Add / Edit note and the dialogs (module 10,
SRS §3.1.3.4.5–7).

Source: recon 10 (qa/shared/recon-dumps/ios-2026-09-24/recon10_*.xml). A note row is one Image whose
label joins the date, the text and 'Show menu'; the ⋮ button is not an element (TD-NOTE-001) — the
page taps the row's right end. The toasts are full-screen Others named by their message.

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/note*.xml, 2026-09-29):
- a note row's content-desc joins only the date and the text ('29 Sep 2026 12:27\\nQA recon note
  A1') — no 'Show menu' suffix like iOS (TD-NOTE-001 extends), so a row is matched by its leading
  date pattern instead, not an ENDSWITH; the ⋮ menu is still opened the same way, by a tap at the
  row's right end (no own element either);
- the field of Add / Edit note is the screen's only EditText, named only by its hint ('Add note') —
  TD-A1, UiSelector cannot match hint.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, InAppBar, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_HEADER = "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND "

_AID = AppiumBy.ACCESSIBILITY_ID
_UI = AppiumBy.ANDROID_UIAUTOMATOR

NOTES = Screen(
    id="notes",
    anchor="header",
    elements={
        "header": El(android=InAppBar("Notes"), ios=(_P, _HEADER + "name == 'Notes'")),
        "back": El(android=(_AID, "Back"), ios=(_P, _BUTTON + "name == 'Back'")),
        "empty-title": El(
            android=(_AID, "No notes have been added yet"),
            ios=(_P, _TEXT + "name == 'No notes have been added yet'"),
        ),
        "empty-text": El(
            android=(_AID, "Add note to the report to get started."),
            ios=(_P, _TEXT + "name == 'Add note to the report to get started.'"),
        ),
        "add-note": El(
            android=(_AID, "Add note"),
            ios=(_P, _BUTTON + "name == 'Add note'"),
            note="two in the empty state (centre and bottom), the bottom one always",
        ),
        "row": El(
            android=(
                _UI,
                # no {n} quantifiers: string.Formatter would misread them as {text}-style fields
                r'new UiSelector().className("android.widget.ImageView")'
                r'.descriptionMatches("\d\d? \w\w\w \d\d\d\d \d\d:\d\d\n.*")',
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND name ENDSWITH 'Show menu'"),
            note="a note: '<dd MMM yyyy HH:mm>\\n<text>\\nShow menu' — parsed by the page. "
            "Android: no 'Show menu' suffix (TD-NOTE-001 extends) — matched by the leading date "
            "pattern instead ('29 Sep 2026 12:27\\n…', notes.xml)",
        ),
        "toast": El(
            android=(
                _UI,
                'new UiSelector().descriptionMatches("Note (added|saved|deleted) successfully")',
            ),
            ios=(
                _P,
                "name == 'Note added successfully' OR name == 'Note saved successfully' "
                "OR name == 'Note deleted successfully'",
            ),
            note="a toast for ~3 s after a save / delete. Android: 'Note added successfully' "
            "confirmed in notes_toast.xml; the saved/deleted variants not reached but same "
            "Flutter text as iOS",
        ),  # fmt: skip
    },
)

NOTE_MENU = Screen(
    id="note-menu",
    anchor="edit",
    elements={
        "edit": El(android=(_AID, "Edit"), ios=(_P, _BUTTON + "name == 'Edit'")),
        "delete": El(
            android=(_AID, "Delete"),
            ios=(_P, _BUTTON + "name == 'Delete' AND rect.width > 100"),
            note="the menu's item (the dialog's Delete is 75 wide). Android: exact match, scoped "
            "to this screen's own dump (note_menu.xml) — no width filter needed there",
        ),  # fmt: skip
    },
)

NOTE_EDITOR = Screen(
    id="note-editor",
    anchor="field",
    elements={
        "add-title": El(android=(_AID, "Add note"), ios=(_P, _HEADER + "name == 'Add note'")),
        "edit-title": El(android=(_AID, "Edit note"), ios=(_P, _HEADER + "name == 'Edit note'")),
        "field": El(
            android=(_UI, 'new UiSelector().className("android.widget.EditText").instance(0)'),
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="the only field; named by its placeholder 'Add note', the text is in value. "
            "Android: hint 'Add note' (note_editor_empty.xml) — TD-A1, UiSelector cannot match "
            "hint, so instance(0) of the screen's only EditText",
        ),
        "counter": El(
            android=(_UI, 'new UiSelector().descriptionMatches("^[0-9]+/500$")'),
            ios=(_P, "name MATCHES '^[0-9]+/500$'"),
            note="'N/500'. Android: a View (note_editor_empty.xml: '0/500')",
        ),
        "save": El(android=(_AID, "Save"), ios=(_P, _BUTTON + "name == 'Save'")),
        "back": El(android=(_AID, "Back"), ios=(_P, _BUTTON + "name == 'Back'")),
        "delete-note": El(
            android=(_AID, "Delete note"),
            ios=(_P, _BUTTON + "name == 'Delete note'"),
            note="Edit note only. Android: an ImageView, not a Button",
        ),
    },
)

NOTE_DELETE_DIALOG = Screen(
    id="note-delete-dialog",
    anchor="title",
    elements={
        "title": El(android=(_AID, "Delete note"), ios=(_P, _TEXT + "name == 'Delete note'")),
        "message": El(
            android=(
                _UI,
                'new UiSelector().descriptionStartsWith("Are you sure you want delete this note.")',
            ),
            ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want delete this note.'"),
        ),
        "cancel": El(android=(_AID, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(
            android=(_AID, "Delete"),
            ios=(_P, _BUTTON + "name == 'Delete' AND rect.width < 100"),
            note="Android: exact match, scoped to this screen's own dump (note_delete_dialog.xml)",
        ),
    },
)

NOTE_UNSAVED_DIALOG = Screen(
    id="note-unsaved-dialog",
    anchor="title",
    elements={
        "title": El(
            android=(_AID, "Unsaved Changes"), ios=(_P, _TEXT + "name == 'Unsaved Changes'")
        ),
        "cancel": El(android=(_AID, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "leave": El(android=(_AID, "Leave"), ios=(_P, _BUTTON + "name == 'Leave'")),
    },
)
