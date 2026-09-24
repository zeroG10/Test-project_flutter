"""Adding a photo to a survey question: the system photo picker, the app's editor and "Add photo".

Source: recon 8 (recon8_photo_picker.xml, recon8_photo_editor.xml, recon8_photo_metadata.xml).
- The picker is the system one (PHPicker): its photo cells are NOT in the tree — a cell is chosen by
  its position in the 3-column grid below ``photos_sectioned_layout`` (the newest photo first). iOS
  only; Android has its own picker (Android stage).
- The editor's two app-bar buttons have no names (TD-PHOTO-001): back on the left, done (✓) on the
  right.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "

PHOTO_PICKER = Screen(
    id="photo-picker",
    anchor="root",
    elements={
        "root": El(ios=(_P, "type == 'XCUIElementTypeNavigationBar' AND name == 'Photos'")),
        "grid": El(
            ios=(_P, "name == 'photos_sectioned_layout'"),
            note="the photo grid; a cell = its position (3 columns, square cells), newest first",
        ),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
    },
)

PHOTO_EDITOR = Screen(
    id="photo-editor",
    anchor="crop",
    elements={
        "crop": El(ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Crop'")),
        "done": El(
            ios=(_P, _BUTTON + "(name == nil OR name == '') AND rect.x > 330 AND rect.y < 140"),
            note="✓ — the right-most unnamed app-bar button (TD-PHOTO-001); undo / redo (x 258, "
            "306, unnamed, disabled) join the tree at times (module 08 run 2)",
        ),
    },
)

PHOTO_METADATA = Screen(
    id="photo-metadata",
    anchor="title",
    elements={
        "title": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' "
                "AND name == 'Add photo'",
            )
        ),  # fmt: skip
        "description": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeTextField' AND "
                "(name == 'Photo description' OR name == '')",
            )
        ),  # fmt: skip
        "save": El(ios=(_P, _BUTTON + "name == 'Save'")),
    },
)
