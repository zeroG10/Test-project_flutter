"""The "Submit deliverables" confirmation dialog of an In progress job (module 07, SRS §3.1.3.4.1).

Source: recon 11 (qa/shared/recon-dumps/ios-2026-09-24/recon11_dialog.xml). The title and the
message are StaticTexts, Cancel and Submit are Buttons; a full-window Other named 'Dismiss' lies
under the dialog (the modal barrier) and the job's details leave the tree while it is open. The
checkmark icon is not in the tree (D-DLV-6).

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/submit_dialog.xml): same shape —
title and message are content-desc Views, Cancel/Submit are Buttons, and the same full-window
"Dismiss" barrier (clickable, dismissable) lies under the dialog.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_A = AppiumBy.ACCESSIBILITY_ID

SUBMIT_DIALOG = Screen(
    id="submit-dialog",
    anchor="title",
    elements={
        "title": El(
            ios=(_P, _TEXT + "name == 'Submit deliverables'"),
            android=(_A, "Submit deliverables"),
            note="a StaticText — the details' action of the same name is a Button. Android: a "
            "content-desc View, same text as the details' action Button — no clash within this "
            "dialog's own dump (recon A1)",
        ),
        "message": El(
            ios=(_P, _TEXT + "name BEGINSWITH 'You won'"),
            android=(_A, "You won't be able to edit it after submission."),
            note="Android: full text matched exactly (content-desc), recon A1",
        ),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'"), android=(_A, "Cancel")),
        "submit": El(ios=(_P, _BUTTON + "name == 'Submit'"), android=(_A, "Submit")),
        "layer": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Dismiss'"),
            android=(_A, "Dismiss"),
            note="the modal barrier: the whole window (0,0 402x874 in recon 11). Android: same "
            "content-desc 'Dismiss', full window, clickable+dismissable (recon A1)",
        ),
    },
)
