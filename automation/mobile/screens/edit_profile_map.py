"""Edit profile and its dialogs (module 12-profile, SRS §3.1.5). Source: recon 13
(qa/shared/recon-dumps/ios-2026-09-24/recon13_edit*.xml, recon13_unsaved.xml, recon13_delete.xml).

First and last name are TextFields named by their label, the text in ``value``. Phone and email are
disabled Others (``enabled=false``; D-PRF-1: the email is not editable). Save is disabled while a
name is empty or shorter than 2 letters (D-PRF-5). Delete account lives here (D-PRF-4); its dialog
has no text field.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "

EDIT_PROFILE = Screen(
    id="edit-profile",
    anchor="title",
    elements={
        "title": El(ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Edit profile'")),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "save": El(ios=(_P, _BUTTON + "name == 'Save'")),
        "first-name": El(ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'First name'")),
        "last-name": El(ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'Last name'")),
        "phone": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Phone number'"),
            note="disabled; value '(202) 555-0450'-style",
        ),
        "email": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Email'"), note="disabled"
        ),
        "delete-account": El(ios=(_P, _BUTTON + "name == 'Delete account'")),
        "any-text-field": El(
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="counted in the delete dialog: none must be there (D-PRF-4)",
        ),
    },
)

UNSAVED_DIALOG = Screen(
    id="unsaved-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Unsaved Changes'")),
        "message": El(ios=(_P, _TEXT + "name BEGINSWITH 'You have unsaved changes.'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "leave": El(ios=(_P, _BUTTON + "name == 'Leave'")),
    },
)

DELETE_DIALOG = Screen(
    id="delete-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Delete account'")),
        "message": El(
            ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want to delete account?'")
        ),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(ios=(_P, _BUTTON + "name == 'Delete'")),
    },
)
