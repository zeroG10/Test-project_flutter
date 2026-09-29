"""Edit profile and its dialogs (module 12-profile, SRS §3.1.5). Source: recon 13
(qa/shared/recon-dumps/ios-2026-09-24/recon13_edit*.xml, recon13_unsaved.xml, recon13_delete.xml).

First and last name are TextFields named by their label, the text in ``value``. Phone and email are
disabled Others (``enabled=false``; D-PRF-1: the email is not editable). Save is disabled while a
name is empty or shorter than 2 letters (D-PRF-5). Delete account lives here (D-PRF-4); its dialog
has no text field.

Android: qa/shared/recon-dumps/android-2026-09-29/edit_profile.xml, delete_dialog.xml,
profile_unsaved_dialog.xml (recon A1) — Save is an unlabelled ImageView (top-right); first/last
name are EditTexts (label only in ``hint``, TD-A1); phone/email are disabled, unlabelled
``android.view.View`` rows with a ``hint`` too — not EditTexts, so found by
``enabled(false)`` + position, same idea as the EditText pattern.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_A = AppiumBy.ACCESSIBILITY_ID
_P = AppiumBy.IOS_PREDICATE
_U = AppiumBy.ANDROID_UIAUTOMATOR
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "

EDIT_PROFILE = Screen(
    id="edit-profile",
    anchor="title",
    elements={
        "title": El(
            android=(_A, "Edit profile"),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Edit profile'"),
        ),
        "back": El(android=(_A, "Back"), ios=(_P, _BUTTON + "name == 'Back'")),
        "save": El(
            android=(_A, "Save"),
            ios=(_P, _BUTTON + "name == 'Save'"),
            note="Android: an ImageView, not a Button (recon A1)",
        ),
        "first-name": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.EditText").instance(0)',
            ),
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'First name'"),
            note="Android: EditText instance(0), hint 'First name' — TD-A1",
        ),
        "last-name": El(
            android=(
                _U,
                'new UiSelector().className("android.widget.EditText").instance(1)',
            ),
            ios=(_P, "type == 'XCUIElementTypeTextField' AND name == 'Last name'"),
            note="Android: EditText instance(1), hint 'Last name' — TD-A1",
        ),
        "phone": El(
            android=(
                _U,
                'new UiSelector().className("android.view.View").enabled(false).instance(0)',
            ),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Phone number'"),
            note="disabled; value '(202) 555-0450'-style. Android: disabled android.view.View "
            "instance(0) among disabled Views, hint 'Phone number' (not an EditText — "
            "UiSelector cannot match the hint either way) — TD-A1, recon A1",
        ),
        "email": El(
            android=(
                _U,
                'new UiSelector().className("android.view.View").enabled(false).instance(1)',
            ),
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Email'"),
            note="disabled. Android: disabled android.view.View instance(1), hint 'Email' — "
            "TD-A1, recon A1",
        ),
        "delete-account": El(
            android=(_A, "Delete account"), ios=(_P, _BUTTON + "name == 'Delete account'")
        ),
        "any-text-field": El(
            android=(_U, 'new UiSelector().className("android.widget.EditText")'),
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="counted in the delete dialog: none must be there (D-PRF-4). Android: any "
            "EditText anywhere (delete_dialog.xml has none, recon A1)",
        ),
    },
)

UNSAVED_DIALOG = Screen(
    id="unsaved-dialog",
    anchor="title",
    elements={
        "title": El(android=(_A, "Unsaved Changes"), ios=(_P, _TEXT + "name == 'Unsaved Changes'")),
        "message": El(
            android=(
                _U,
                'new UiSelector().descriptionStartsWith("You have unsaved changes.")',
            ),
            ios=(_P, _TEXT + "name BEGINSWITH 'You have unsaved changes.'"),
        ),
        "cancel": El(android=(_A, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "leave": El(android=(_A, "Leave"), ios=(_P, _BUTTON + "name == 'Leave'")),
    },
)

DELETE_DIALOG = Screen(
    id="delete-dialog",
    anchor="title",
    elements={
        "title": El(android=(_A, "Delete account"), ios=(_P, _TEXT + "name == 'Delete account'")),
        "message": El(
            android=(
                _U,
                'new UiSelector().descriptionStartsWith("Are you sure you want to delete account?")',  # noqa: E501
            ),
            ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want to delete account?'"),
        ),
        "cancel": El(android=(_A, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(android=(_A, "Delete"), ios=(_P, _BUTTON + "name == 'Delete'")),
    },
)
