"""Attachments and the file viewers (module 04-order-details, SRS §3.1.3.2).

Source: recon 5b (qa/shared/recon-dumps/ios-2026-09-24/recon5_attachments_documents.xml,
recon5_attachments_photos.xml, recon5_pdf_viewer.xml, recon5_after_pdf_close.xml).
Tabs are named '<Tab>\\nTab N of 2'; the selected one is an Other with traits 'Selected', the
other one a StaticText. Documents are Buttons named by the file name. Photo thumbnails are NOT
in the tree (TD-ORDD-002) — pixels (pages/attachments_page.py). The PDF viewer's close (X) is
the only unnamed Button in its app bar (TD-ORDD-001). The photo viewer was not seen yet
(Q-ORDD-6): its back button is expected to be 'Back', as every Flutter app bar here.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_HEADER = "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND "

ATTACHMENTS = Screen(
    id="attachments",
    anchor="title",
    elements={
        "title": El(ios=(_P, _HEADER + "name == 'Attachments'")),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "tab": El(
            ios=(_P, "name BEGINSWITH {text} AND name CONTAINS 'Tab '"),
            note="'Documents' / 'Photos' — the tab's name starts with its label",
        ),
        "tabs": El(
            ios=(_P, "name CONTAINS 'Tab ' AND rect.y < 200"),
            note="every tab of the top tab bar (y 118 in recon 5b) — not the app's bottom tab bar",
        ),
        "selected-tab": El(
            ios=(_P, "traits CONTAINS 'Selected' AND name CONTAINS 'Tab '"),
            note="the tab whose traits contain 'Selected' (recon 5b)",
        ),
        "document": El(
            ios=(_P, _BUTTON + "name == {text}"),
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
            note="the document's name, as the viewer's app-bar title",
        ),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "close": El(
            ios=(_P, _BUTTON + "(name == nil OR name == '') AND rect.y < 140"),
            note="TD-ORDD-001: the X icon has no label; once the PDF loads the download icon is a "
            "second unnamed button to its left — the page taps the right-most one",
        ),
        "any-editable": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeTextField' OR type == 'XCUIElementTypeTextView' "
                "OR type == 'XCUIElementTypeSecureTextField'",
            ),
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
            note="the viewer's back arrow (D-ORDD-7) — to confirm when photos load (Q-ORDD-6)",
        ),
    },
)
