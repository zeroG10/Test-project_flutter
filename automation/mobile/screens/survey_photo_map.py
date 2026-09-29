"""Adding a photo to a survey question: the system photo picker, the app's editor and "Add photo".

Source: recon 8 (recon8_photo_picker.xml, recon8_photo_editor.xml, recon8_photo_metadata.xml).
- The picker is the system one (PHPicker): its photo cells are NOT in the tree — a cell is chosen by
  its position in the 3-column grid below ``photos_sectioned_layout`` (the newest photo first). iOS
  only; Android has its own picker (Android stage).
- The editor's two app-bar buttons have no names (TD-PHOTO-001): back on the left, done (✓) on the
  right.

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/photo_*.xml, 2026-09-29):
- the picker is the Android system Photo Picker (``com.google.android.photopicker``), structurally
  unrelated to PHPicker: cells are NOT clickable themselves — each is an unlabelled clickable View
  with a non-clickable sibling View named ``"Photo taken on <date>"`` on top (newest first);
  there is no ``photos_sectioned_layout``-like grid container id. ``SurveyPage.add_photo()`` needs
  Android-specific cell selection (locate by ``descriptionStartsWith("Photo taken on")``, tap that
  label's own bounds — it overlaps its clickable parent) instead of grid-percentage math;
- the editor's Back is LABELLED on Android (unlike iOS); done (✓) is still unlabelled, the 2nd
  enabled clickable Button in document order (undo/redo sit disabled between them) — TD-PHOTO-001
  extends: position-based, not by class alone (Back is also a Button);
- ``PHOTO_METADATA.description`` is the screen's only EditText, named by ``hint`` ('Photo
  description') only while empty — TD-A1, UiSelector cannot match hint, so it is
  ``className(...).instance(0)`` per screens/README.md.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "

_AID = AppiumBy.ACCESSIBILITY_ID
_UI = AppiumBy.ANDROID_UIAUTOMATOR

PHOTO_PICKER = Screen(
    id="photo-picker",
    anchor="root",
    elements={
        "root": El(
            android=(
                _UI,
                'new UiSelector().packageName("com.google.android.photopicker")'
                '.className("android.widget.TextView").text("Photos")',
            ),
            ios=(_P, "type == 'XCUIElementTypeNavigationBar' AND name == 'Photos'"),
            note="Android: the 'Photos' tab of the system Photo Picker — no navigation-bar title "
            "like iOS",
        ),
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
        "crop": El(
            android=(_AID, "Crop"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Crop'"),
        ),
        "markup": El(
            android=(_AID, "Markup"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Markup'"),
        ),
        "done": El(
            android=(
                _UI,
                'new UiSelector().className("android.widget.Button").clickable(true).instance(1)',
            ),
            ios=(_P, _BUTTON + "(name == nil OR name == '') AND rect.x > 330 AND rect.y < 140"),
            note="✓ — the right-most unnamed app-bar button (TD-PHOTO-001); undo / redo (x 258, "
            "306, unnamed, disabled) join the tree at times (module 08 run 2). Android: position-"
            "based — the 2nd clickable Button in document order (photo_editor.xml): Back is "
            "clickable+labelled (instance 0), undo/redo are disabled (clickable=false, excluded), "
            "done is instance 1",
        ),
    },
)

PHOTO_METADATA = Screen(
    id="photo-metadata",
    anchor="title",
    elements={
        "title": El(
            android=(_AID, "Add photo"),
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' "
                "AND name == 'Add photo'",
            ),
        ),  # fmt: skip
        "description": El(
            android=(_UI, 'new UiSelector().className("android.widget.EditText").instance(0)'),
            ios=(_P, "type == 'XCUIElementTypeTextField'"),
            note="the only text field of the page; named 'Photo description' while empty, unnamed "
            "once it holds text (Edit photo — module 09 run 1). Android: hint 'Photo description' "
            "(photo_metadata.xml) — TD-A1, UiSelector cannot match hint, so instance(0) of the "
            "screen's only EditText",
        ),
        "save": El(android=(_AID, "Save"), ios=(_P, _BUTTON + "name == 'Save'")),
        "edit-title": El(
            android=(_AID, "Edit photo"),
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' "
                "AND name == 'Edit photo'",
            ),
            note="the same page opened on a saved photo (Photo report, recon 9)",
        ),  # fmt: skip
        "back": El(android=(_AID, "Back"), ios=(_P, _BUTTON + "name == 'Back'")),
        "label": El(
            android=(_AID, "Description"),
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == 'Description'"),
            note="the field's label — a tap here dismisses the keyboard without touching a field",
        ),
        "counter": El(
            android=(_UI, 'new UiSelector().descriptionMatches("^[0-9]+ / 500$")'),
            ios=(_P, "name MATCHES '^[0-9]+ / 500$'"),
            note="'N / 500' — a StaticText, or an Other while it updates. Android: a View "
            "(photo_metadata.xml: '0 / 500', photo_metadata_filled.xml: '17 / 500')",
        ),
        "tag": El(
            android=(_AID, "{text}"),
            ios=(_P, _BUTTON + "name == {text}"),
            note="a tag chip from the Admin Panel (selected: value 1, trait Selected). Android: a "
            "Button named by the tag, 'selected' reflects state (photo_metadata_edit.xml)",
        ),
    },
)

# Android system UI (com.google.android.photopicker) has no equivalent to the iOS grid container
# id or a labelled Cancel — dismissed via hardware back / swipe, not reached in recon A1.
ANDROID_WITHOUT: dict[str, str] = {
    "photo-picker.grid": "Android's system Photo Picker has no grid-container id; a cell is chosen "
    "by locating its 'Photo taken on <date>' label directly (descriptionStartsWith), not by "
    "grid-position math — SurveyPage.add_photo() needs Android-specific cell selection",
    "photo-picker.cancel": "no labelled Cancel found in recon A1 (photo_picker.xml) — the system "
    "picker is dismissed by the hardware back gesture, not a button",
}
