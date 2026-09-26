"""The "Submit deliverables" confirmation dialog of an In progress job (module 07, SRS §3.1.3.4.1).

Source: recon 11 (qa/shared/recon-dumps/ios-2026-09-24/recon11_dialog.xml). The title and the
message are StaticTexts, Cancel and Submit are Buttons; a full-window Other named 'Dismiss' lies
under the dialog (the modal barrier) and the job's details leave the tree while it is open. The
checkmark icon is not in the tree (D-DLV-6).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "

SUBMIT_DIALOG = Screen(
    id="submit-dialog",
    anchor="title",
    elements={
        "title": El(
            ios=(_P, _TEXT + "name == 'Submit deliverables'"),
            note="a StaticText — the details' action of the same name is a Button",
        ),
        "message": El(ios=(_P, _TEXT + "name BEGINSWITH 'You won'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "submit": El(ios=(_P, _BUTTON + "name == 'Submit'")),
        "layer": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == 'Dismiss'"),
            note="the modal barrier: the whole window (0,0 402x874 in recon 11)",
        ),
    },
)
