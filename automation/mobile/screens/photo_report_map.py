"""The Photo report of an In progress job and its dialogs (module 09, SRS §3.1.3.4.3–4).

Source: recon 9 (qa/shared/recon-dumps/ios-2026-09-24/recon9_*.xml). A photo in the grid is an Image
named by its description and tags joined by line breaks (unnamed without them); its delete icon is
an unnamed 40-pt Button in the photo's top-right corner (TD-PHR-001) — the page pairs them by
position. The metadata page ("Add photo" / "Edit photo"), the gallery picker and the editor are in
screens/survey_photo_map.py (the same screens as the survey).

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/photo_report*.xml, 2026-09-29):
- a photo tile is an ImageView named '<description>\\n<tag>', clickable=false; its delete icon is a
  SIBLING unlabelled ImageView, clickable=true (TD-PHR-001 extends: distinguished from the tile by
  having no content-desc at all, not just by size); the "Add photo" buttons are ImageViews too
  (clickable=true, desc 'Add photo') so a bare className+clickable filter would also catch them —
  the delete-icon locator counts by position (``instance(n)``; "Add photo" comes last) —
  a node without content-desc matches no description selector on the device, not even ``""``.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, InAppBar, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_TEXT = "type == 'XCUIElementTypeStaticText' AND "

_AID = AppiumBy.ACCESSIBILITY_ID
_UI = AppiumBy.ANDROID_UIAUTOMATOR

PHOTO_REPORT = Screen(
    id="photo-report",
    anchor="header",
    elements={
        "header": El(
            android=InAppBar("Photo report"),
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' "
                "AND name == 'Photo report'",
            ),
        ),  # fmt: skip
        "back": El(android=(_AID, "Back"), ios=(_P, _BUTTON + "name == 'Back'")),
        "empty-title": El(
            android=(_AID, "No photos have been added yet"),
            ios=(_P, _TEXT + "name == 'No photos have been added yet'"),
        ),
        "empty-text": El(
            android=(_AID, "Add photos to the report to get started."),
            ios=(_P, _TEXT + "name == 'Add photos to the report to get started.'"),
        ),
        "add-photo": El(
            android=(_AID, "Add photo"),
            ios=(_P, _BUTTON + "name == 'Add photo'"),
            note="two in the empty state (centre and bottom), the bottom one always. Android: an "
            "ImageView (not a Button)",
        ),
        "photo": El(
            android=(
                _UI,
                'new UiSelector().className("android.widget.ImageView").clickable(false)'
                ".descriptionStartsWith({text})",
            ),
            ios=(
                _P,
                "type == 'XCUIElementTypeImage' AND rect.width > 150 AND name BEGINSWITH {text}",
            ),
            note="a photo of the grid, named '<description>\\n<tag>…' — pass the description. "
            "Android: clickable(false) excludes the delete icon and the 'Add photo' ImageViews "
            "(both clickable=true)",
        ),
        "photos": El(
            android=(
                _UI,
                'new UiSelector().className("android.widget.ImageView").clickable(false)',
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND rect.width > 150"),
            note="every photo of the grid (the page pairs each with its delete icon). Android: "
            "clickable(false) excludes 'Add photo' and the delete icons",
        ),
        "toast": El(
            android=(
                _UI,
                "new UiSelector().descriptionMatches("
                '"Photo added successfully|Changes saved successfully")',
            ),
            ios=(_P, "name == 'Photo added successfully' OR name == 'Changes saved successfully'"),
            note="a bottom toast for 3 s after a save — it lies over Add photo (module 09 run 1). "
            "Android: 'Photo added successfully' confirmed in photo_report_toast.xml; "
            "'Changes saved successfully' not reached but same Flutter text as iOS",
        ),
        "delete": El(
            android=(
                _UI,
                'new UiSelector().className("android.widget.ImageView").clickable(true)'
                ".instance({text})",
            ),
            ios=(_P, _BUTTON + "(name == nil OR name == '') AND rect.width < 50"),
            note="a photo's delete icon — unnamed, top-right of the photo (TD-PHR-001). Android: "
            "the n-th clickable ImageView — pass the tile's index as {text}; 'Add photo' comes "
            "after every tile (recon A1). No content-desc at all, which no description selector "
            "matches (01+03 run 3); the page reads the icons from the page source",
        ),
    },
)

PHOTO_ADD_SHEET = Screen(
    id="photo-add-sheet",
    anchor="title",
    elements={
        "title": El(android=(_AID, "Add photo"), ios=(_P, _TEXT + "name == 'Add photo'")),
        "camera": El(android=(_AID, "Camera"), ios=(_P, "name == 'Camera'")),
        "gallery": El(
            android=(_AID, "Gallery"),
            ios=(_P, "name == 'Gallery'"),
            note="an Image in the tree, tappable",
        ),
    },
)

PHOTO_DELETE_DIALOG = Screen(
    id="photo-delete-dialog",
    anchor="title",
    elements={
        "title": El(android=(_AID, "Delete photo"), ios=(_P, _TEXT + "name == 'Delete photo'")),
        "message": El(
            android=(
                _UI,
                "new UiSelector().descriptionStartsWith("
                '"Are you sure you want to delete this photo.")',
            ),
            ios=(_P, _TEXT + "name BEGINSWITH 'Are you sure you want to delete this photo.'"),
        ),
        "cancel": El(android=(_AID, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(android=(_AID, "Delete"), ios=(_P, _BUTTON + "name == 'Delete'")),
    },
)

PHOTO_UNSAVED_DIALOG = Screen(
    id="photo-unsaved-dialog",
    anchor="title",
    elements={
        "title": El(
            android=(_AID, "Unsaved Changes"), ios=(_P, _TEXT + "name == 'Unsaved Changes'")
        ),
        "message": El(
            android=(_UI, 'new UiSelector().descriptionStartsWith("You have unsaved changes.")'),
            ios=(_P, _TEXT + "name BEGINSWITH 'You have unsaved changes.'"),
        ),
        "cancel": El(android=(_AID, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "leave": El(android=(_AID, "Leave"), ios=(_P, _BUTTON + "name == 'Leave'")),
    },
)
