"""Attachments and the file viewers (module 04-order-details, SRS §3.1.3.2).

Source: recon 5b (qa/shared/recon-dumps/ios-2026-09-24/recon5_attachments_documents.xml,
recon5_attachments_photos.xml, recon5_pdf_viewer.xml, recon5_after_pdf_close.xml).
Tabs are named '<Tab>\\nTab N of 2'; the selected one is an Other with traits 'Selected', the
other one a StaticText. Documents are Buttons named by the file name. Photo thumbnails are NOT
in the tree (TD-ORDD-002) — pixels (pages/attachments_page.py). The PDF viewer's close (X) is
the only unnamed Button in its app bar (TD-ORDD-001). The photo viewer was not seen yet
(Q-ORDD-6): its back button is expected to be 'Back', as every Flutter app bar here.

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/attachments_documents.xml,
attachments_photos.xml, pdf_viewer.xml, photo_viewer.xml): same texts and shapes. One difference
worth a report, not a map change: Android's Photos tab DOES show two unlabelled, clickable
ImageView thumbnails in the tree (unlike iOS, TD-ORDD-002) — attachments_page.py still taps them
by pixel coordinates (grid_cells); an element-based tap would work on Android but is untouched here.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_HEADER = "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND "
_U = AppiumBy.ANDROID_UIAUTOMATOR
_A = AppiumBy.ACCESSIBILITY_ID

ATTACHMENTS = Screen(
    id="attachments",
    anchor="title",
    elements={
        "title": El(ios=(_P, _HEADER + "name == 'Attachments'"), android=(_A, "Attachments")),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'"), android=(_A, "Back")),
        "tab": El(
            ios=(_P, "name BEGINSWITH {text} AND name CONTAINS 'Tab '"),
            android=(_U, "new UiSelector().descriptionStartsWith({text})"),
            note="'Documents' / 'Photos' — the tab's name starts with its label. Android: same "
            "'<Label>\\nTab N of 2' content-desc (recon A1)",
        ),
        "tabs": El(
            ios=(_P, "name CONTAINS 'Tab ' AND rect.y < 200"),
            android=(_U, 'new UiSelector().descriptionContains("Tab ")'),
            note="every tab of the top tab bar (y 118 in recon 5b) — not the app's bottom tab bar. "
            "Android: same, the only content-desc containing 'Tab ' outside the bottom tab bar "
            "(which reads 'Tab N of 3', recon A1)",
        ),
        "selected-tab": El(
            ios=(_P, "traits CONTAINS 'Selected' AND name CONTAINS 'Tab '"),
            android=(_U, 'new UiSelector().descriptionContains("Tab ").selected(true)'),
            note="the tab whose traits contain 'Selected' (recon 5b). Android: the tab whose "
            "``selected`` attribute is true (recon A1: attachments_documents.xml / "
            "attachments_photos.xml)",
        ),
        "document": El(
            ios=(_P, _BUTTON + "name == {text}"),
            android=(_A, "{text}"),
            note="a document row, named by the document's name (with its extension)",
        ),
    },
)

PDF_VIEWER = Screen(
    id="pdf-viewer",
    anchor="close",
    elements={
        "title": El(
            ios=(_P, _HEADER + "name == {text}"),
            android=(_A, "{text}"),
            note="the document's name, as the viewer's app-bar title",
        ),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'"), android=(_A, "Back")),
        "close": El(
            ios=(_P, _BUTTON + "(name == nil OR name == '') AND rect.y < 140"),
            android=(
                _U,
                'new UiSelector().className("android.widget.Button").clickable(true)',
            ),
            note="TD-ORDD-001: the X icon has no label; once the PDF loads the download icon is a "
            "second unnamed button to its left — the page taps the right-most one. Android: every "
            "clickable Button — 'Back' (left) and the two unlabelled ones; the right-most is X "
            "(recon A1). They have no content-desc at all, which no description selector "
            "matches (01+03 run 3)",
        ),
        "any-editable": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeTextField' OR type == 'XCUIElementTypeTextView' "
                "OR type == 'XCUIElementTypeSecureTextField'",
            ),
            android=(_U, 'new UiSelector().className("android.widget.EditText")'),
            note="read-only viewer: must match nothing (CHK-ORDD-066)",
        ),
    },
)

PHOTO_VIEWER = Screen(
    id="photo-viewer",
    anchor="back",
    elements={
        "back": El(
            ios=(_P, _BUTTON + "name == 'Back'"),
            android=(_A, "Back"),
            note="the viewer's back arrow (D-ORDD-7) — to confirm when photos load (Q-ORDD-6). "
            "Android: reached in recon A1 (photo_viewer.xml); the viewer also shows a '1 of 2' "
            "counter (content-desc) with no alias yet — not added (no test references it)",
        ),
    },
)
