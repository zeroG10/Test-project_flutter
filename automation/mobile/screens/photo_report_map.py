"""The Photo report of an In progress job and its dialogs (module 09, SRS §3.1.3.4.3–4).

Source: recon 9 (qa/shared/recon-dumps/ios-2026-09-24/recon9_*.xml). A photo in the grid is an Image
named by its description and tags joined by line breaks (unnamed without them); its delete icon is
an unnamed 40-pt Button in the photo's top-right corner (TD-PHR-001) — the page pairs them by
position. The metadata page ("Add photo" / "Edit photo"), the gallery picker and the editor are in
screens/survey_photo_map.py (the same screens as the survey).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_TEXT = "type == 'XCUIElementTypeStaticText' AND "

PHOTO_REPORT = Screen(
    id="photo-report",
    anchor="header",
    elements={
        "header": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' "
                "AND name == 'Photo report'",
            ),
        ),  # fmt: skip
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "empty-title": El(ios=(_P, _TEXT + "name == 'No photos have been added yet'")),
        "empty-text": El(ios=(_P, _TEXT + "name == 'Add photos to the report to get started.'")),
        "add-photo": El(
            ios=(_P, _BUTTON + "name == 'Add photo'"),
            note="two in the empty state (centre and bottom), the bottom one always",
        ),
        "photo": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeImage' AND rect.width > 150 AND name BEGINSWITH {text}",
            ),
            note="a photo of the grid, named '<description>\\n<tag>…' — pass the description",
        ),
        "photos": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND rect.width > 150"),
            note="every photo of the grid (the page pairs each with its delete icon)",
        ),
        "delete": El(
            ios=(_P, _BUTTON + "(name == nil OR name == '') AND rect.width < 50"),
            note="a photo's delete icon — unnamed, top-right of the photo (TD-PHR-001)",
        ),
    },
)

PHOTO_ADD_SHEET = Screen(
    id="photo-add-sheet",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Add photo'")),
        "camera": El(ios=(_P, "name == 'Camera'")),
        "gallery": El(ios=(_P, "name == 'Gallery'"), note="an Image in the tree, tappable"),
    },
)

PHOTO_DELETE_DIALOG = Screen(
    id="photo-delete-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Delete photo'")),
        "message": El(
            ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want to delete this photo.'")
        ),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(ios=(_P, _BUTTON + "name == 'Delete'")),
    },
)

PHOTO_UNSAVED_DIALOG = Screen(
    id="photo-unsaved-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Unsaved Changes'")),
        "message": El(ios=(_P, _TEXT + "name BEGINSWITH 'You have unsaved changes.'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "leave": El(ios=(_P, _BUTTON + "name == 'Leave'")),
    },
)
