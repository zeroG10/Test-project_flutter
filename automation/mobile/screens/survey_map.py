"""The survey form and its dialogs (module 08-survey, SRS §3.1.3.4.2, PRD CR-2).

Source: recon 8 (qa/shared/recon-dumps/ios-2026-09-24/recon8_*.xml). What the tree gives and what it
does not:
- question titles are NOT elements: every title of a card sits in the card's label as
  ``N. \\nTitle`` (TD-SRV-001) — the page parses them (``SurveyPage.titles``);
- fields carry only their hint: text ``Description``, date ``Select date``, time ``Select time``,
  number ``0``; a filled field loses the hint (the text is in ``value``). A field is therefore "the
  n-th of its kind in form order" — the page scrolls to it;
- Yes / No and single-choice options are Buttons named by the option (selected: ``value 1``, trait
  ``Selected``); checkboxes are Switches (``value 0/1``);
- a card of loose questions with one text field is itself the ``TextField`` (TD-SRV-002).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_FIELD = "type == 'XCUIElementTypeTextField' AND "

SURVEY = Screen(
    id="survey",
    anchor="header",
    elements={
        "header": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND name == 'Survey'",
            )
        ),  # fmt: skip
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "survey-name": El(
            ios=(_P, _TEXT + "name == {text}"), note="the survey's title, first line"
        ),
        "titles": El(
            ios=(_P, "name CONTAINS '. ' AND rect.width > 300"),
            note="labels of the cards: 'N. \\nTitle' pairs (TD-SRV-001) — parsed by the page",
        ),
        "save": El(ios=(_P, _BUTTON + "name == 'Save'")),
        "yes": El(ios=(_P, _BUTTON + "name == 'Yes'"), note="n-th in form order (radio 'Yes' too)"),
        "no": El(ios=(_P, _BUTTON + "name == 'No'"), note="n-th in form order (radio 'No' too)"),
        "option": El(ios=(_P, _BUTTON + "name == {text}"), note="a single-choice option"),
        "checkbox": El(
            ios=(_P, "type == 'XCUIElementTypeSwitch' AND name == {text}"),
            note="a multi-choice option (value 0 / 1)",
        ),
        "text": El(
            ios=(
                _P,
                _FIELD + "name != 'Select date' AND name != 'Select time' AND name != 'Hour' "
                "AND name != 'Minute' AND name != '0'",
            ),  # fmt: skip
            note="a text answer (incl. an 'Other' option's text), n-th in form order; a FILLED "
            "date or time field loses its hint and would count too — tests fill text first",
        ),
        "counter": El(
            ios=(_P, "name ENDSWITH 'characters remaining'"),
            note="'N characters remaining' / 'No characters remaining'",
        ),  # fmt: skip
        "required-error": El(ios=(_P, "name == 'This field is required'")),
        "date": El(ios=(_P, _FIELD + "name == 'Select date'"), note="an empty date field"),
        "time": El(ios=(_P, _FIELD + "name == 'Select time'"), note="an empty time field"),
        "upload-photo": El(ios=(_P, _BUTTON + "name == 'Upload photo'")),
        "thumbnail": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND name == {text}"),
            note="a photo's thumbnail, named by its description (TD-SRV-003)",
        ),
        "section": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND name BEGINSWITH {text}"),
            note="a section card's header (an Image named by the section / entry title)",
        ),
        "entry-headers": El(
            ios=(_P, "type == 'XCUIElementTypeImage' AND name BEGINSWITH {text}"),
            note="headers of a repeatable section's entries: '<section>', '<section> 2', …",
        ),
        "repeat": El(ios=(_P, _BUTTON + "name == 'Repeat section'")),
        "delete-entry": El(
            ios=(_P, _BUTTON + "name == 'Delete' AND rect.width < 60"),
            note="the trash icon of an added entry (the first has none)",
        ),  # fmt: skip
        "saved": El(ios=(_P, "name == 'Survey saved'"), note="snackbar after Save"),
    },
)

SURVEY_DATE_PICKER = Screen(
    id="survey-date-picker",
    anchor="ok",
    elements={
        "day": El(
            ios=(_P, _BUTTON + "name BEGINSWITH {text}"),
            note="'15, Tuesday, September 15, 2026' — pass '15, '",
        ),  # fmt: skip
        "ok": El(ios=(_P, _BUTTON + "name == 'OK'")),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
    },
)

SURVEY_TIME_PICKER = Screen(
    id="survey-time-picker",
    anchor="ok",
    elements={
        "text-mode": El(
            ios=(_P, _BUTTON + "name == 'Switch to text input mode'"),
            note="the dial is not in the tree — text input is",
        ),  # fmt: skip
        "hour": El(ios=(_P, _FIELD + "name == 'Hour'")),
        "minute": El(ios=(_P, _FIELD + "name == 'Minute'")),
        "ok": El(ios=(_P, _BUTTON + "name == 'OK'")),
    },
)

SURVEY_DELETE_DIALOG = Screen(
    id="survey-delete-dialog",
    anchor="title",
    elements={
        "title": El(ios=(_P, _TEXT + "name == 'Delete section'")),
        "message": El(ios=(_P, _TEXT + "name == {text}"), note="the dialog's question"),
        "cancel": El(ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(
            ios=(_P, _BUTTON + "name == 'Delete' AND rect.width > 60"),
            note="the dialog's button (the entry's trash icon is 48 wide)",
        ),  # fmt: skip
    },
)
