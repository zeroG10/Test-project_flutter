"""Survey / Photo report / Notes as reached from an In progress job (module 06; modules 08–10
extend them).

Source: recon 7 (qa/shared/recon-dumps/ios-2026-09-24/recon7_*_screen.xml): each screen has a
Header named after it and a 'Back' button; the survey screen shows the survey's name as a
StaticText.

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/notes_empty.xml, notes.xml,
notes_toast.xml, photo_report_empty.xml, photo_report.xml, photo_report_toast.xml,
survey_short.xml, survey_short_filled.xml, survey_mo3_1.xml, survey_mo3_2.xml, survey_mo3_3.xml):
same shared Header + Back shape on every one — content-desc "Back" Button, content-desc
"Survey" / "Photo report" / "Notes" title View, both unique per screen.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_HEADER = "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND "
_A = AppiumBy.ACCESSIBILITY_ID

DELIVERABLE_SCREEN = Screen(
    id="deliverable-screen",
    anchor="back",
    elements={
        "title": El(
            ios=(_P, _HEADER + "name == {text}"),
            android=(_A, "{text}"),
            note="'Survey' / 'Photo report' / 'Notes'",
        ),
        "survey-name": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == {text}"),
            android=(_A, "{text}"),
            note="the survey's name under the Survey header (e.g. 'Short Survey')",
        ),
        "back": El(
            ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Back'"), android=(_A, "Back")
        ),
    },
)
