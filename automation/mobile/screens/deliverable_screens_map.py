"""Survey / Photo report / Notes as reached from an In progress job (module 06; modules 08–10
extend them).

Source: recon 7 (qa/shared/recon-dumps/ios-2026-09-24/recon7_*_screen.xml): each screen has a
Header named after it and a 'Back' button; the survey screen shows the survey's name as a
StaticText.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_HEADER = "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND "

DELIVERABLE_SCREEN = Screen(
    id="deliverable-screen",
    anchor="back",
    elements={
        "title": El(
            ios=(_P, _HEADER + "name == {text}"),
            note="'Survey' / 'Photo report' / 'Notes'",
        ),
        "survey-name": El(
            ios=(_P, "type == 'XCUIElementTypeStaticText' AND name == {text}"),
            note="the survey's name under the Survey header (e.g. 'Short Survey')",
        ),
        "back": El(ios=(_P, "type == 'XCUIElementTypeButton' AND name == 'Back'")),
    },
)
