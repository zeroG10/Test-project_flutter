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

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/survey_*.xml, 2026-09-29):
- labels live in ``content-desc``; question titles are MERGED into ONE View's desc
  (``"1. \\nWas the job completed successfully?\\n3. \\n…"``, MO3 — question "2." can stand in its
  own View too) — in the short survey (a single-field card) the titles sit in the HINT of the
  only EditText instead (``TD-SRV-001`` extends: on Android a title can be unreachable by any
  allowed locator — ``SurveyPage.titles_in()`` needs Android logic, see the handoff report);
- Yes / No are Buttons that become ImageViews once selected (``selected="true"``) — do not filter
  by className for them; radio options are RadioButtons, checkboxes are CheckBoxes, both named by
  the option and carrying ``checked``;
- EVERY EditText (description / date / time / number) is unlabelled and named only by its
  ``hint``, which UiSelector cannot match (``TD-A1``): a bare ``className("...EditText")`` cannot
  tell a text answer from a date/time field the way the iOS ``name`` filter does — per-field
  disambiguation needs page-level order/hint reading directly from ``page_source``
  (``SurveyPage.matches`` / ``nth`` / ``FORM_ORDER``), not a static locator; see the handoff report;
- "Repeat section", a section's delete dialog and "This field is required" were NOT reached in
  recon A1 (``ANDROID_UNVERIFIED`` below) — same Flutter text expected on both platforms.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, InAppBar, Screen

_P = AppiumBy.IOS_PREDICATE
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_FIELD = "type == 'XCUIElementTypeTextField' AND "

_AID = AppiumBy.ACCESSIBILITY_ID
_UI = AppiumBy.ANDROID_UIAUTOMATOR

SURVEY = Screen(
    id="survey",
    anchor="header",
    elements={
        "header": El(
            android=InAppBar("Survey"),
            ios=(
                _P,
                "type == 'XCUIElementTypeOther' AND traits CONTAINS 'Header' AND name == 'Survey'",
            ),
        ),  # fmt: skip
        "back": El(android=(_AID, "Back"), ios=(_P, _BUTTON + "name == 'Back'")),
        "survey-name": El(
            android=(_UI, "new UiSelector().descriptionStartsWith({text})"),
            ios=(_P, _TEXT + "name == {text}"),
            note="the survey's title, first line. Android: a survey with a section has "
            "'<survey name>_<section title>' in one content-desc (survey_mo3_1.xml) — pass just "
            "the survey title with descriptionStartsWith, not an exact match",
        ),
        "titles": El(
            android=(
                _UI,
                'new UiSelector().className("android.view.View").descriptionContains(". ")',
            ),
            ios=(_P, "name CONTAINS '. ' AND rect.width > 300"),
            note="labels of the cards: 'N. \\nTitle' pairs (TD-SRV-001) — parsed by the page. "
            "Android: titles are merged into one (or a few) View content-desc, but a single-field "
            "card (survey_short.xml) puts them in the EditText's hint instead, unreachable by any "
            "allowed locator — SurveyPage.titles_in() needs Android-specific parsing",
        ),
        "save": El(android=(_AID, "Save"), ios=(_P, _BUTTON + "name == 'Save'")),
        "yes": El(
            android=(_AID, "Yes"),
            ios=(_P, _BUTTON + "name == 'Yes'"),
            note="n-th in form order (radio 'Yes' too). Android: a Button that becomes an "
            'ImageView once selected (selected="true") — content-desc is unaffected, do not '
            "filter by className",
        ),
        "no": El(
            android=(_AID, "No"),
            ios=(_P, _BUTTON + "name == 'No'"),
            note="n-th in form order (radio 'No' too). Android: same class change as 'yes'",
        ),
        "option": El(
            android=(_AID, "{text}"),
            ios=(_P, _BUTTON + "name == {text}"),
            note="a single-choice option. Android: a RadioButton named by the option, 'checked' "
            "reflects state",
        ),
        "checkbox": El(
            android=(_AID, "{text}"),
            ios=(_P, "type == 'XCUIElementTypeSwitch' AND name == {text}"),
            note="a multi-choice option (value 0 / 1). Android: a CheckBox named by the option, "
            "'checked' reflects state",
        ),
        "text": El(
            android=(_UI, 'new UiSelector().className("android.widget.EditText")'),
            ios=(
                _P,
                _FIELD + "name != 'Select date' AND name != 'Select time' AND name != 'Hour' "
                "AND name != 'Minute' AND name != '0'",
            ),  # fmt: skip
            note="a text answer (incl. an 'Other' option's text), n-th in form order; a FILLED "
            "date or time field loses its hint and would count too — tests fill text first. "
            "Android (TD-A1): every EditText (text / date / time) is unlabelled, named only by "
            "its hint, which UiSelector cannot match — this locator cannot exclude date/time "
            "fields the way the iOS 'name' filter does; per-field kind needs page-level hint "
            "reading from page_source. A single-field card's EditText also refuses "
            "Appium set_text — only IME 'mobile: type' works (TD-SRV-002 extends)",
        ),
        "counter": El(
            android=(_UI, 'new UiSelector().descriptionMatches(".*characters remaining")'),
            ios=(_P, "name ENDSWITH 'characters remaining'"),
            note="'N characters remaining' / 'No characters remaining'. Android: UiSelector has "
            "no …EndsWith matcher, descriptionMatches(regex) instead",
        ),  # fmt: skip
        "required-error": El(
            android=(_AID, "This field is required"), ios=(_P, "name == 'This field is required'")
        ),
        "date": El(
            android=(_UI, 'new UiSelector().className("android.widget.EditText")'),
            ios=(_P, _FIELD + "name == 'Select date'"),
            note="an empty date field. Android (TD-A1): hint 'Select date', not matchable by "
            "UiSelector — same className("
            '"android.widget.EditText")'
            " as 'text'; see that note",
        ),
        "time": El(
            android=(_UI, 'new UiSelector().className("android.widget.EditText")'),
            ios=(_P, _FIELD + "name == 'Select time'"),
            note="an empty time field. Android (TD-A1): hint 'Select time', not matchable by "
            "UiSelector — same className("
            '"android.widget.EditText")'
            " as 'text'; see that note",
        ),
        "upload-photo": El(
            android=(_AID, "Upload photo"), ios=(_P, _BUTTON + "name == 'Upload photo'")
        ),
        "thumbnail": El(
            android=(_AID, "{text}"),
            ios=(_P, "type == 'XCUIElementTypeImage' AND name == {text}"),
            note="a photo's thumbnail, named by its description (TD-SRV-003)",
        ),
        "section": El(
            android=(
                _UI,
                'new UiSelector().className("android.widget.ImageView")'
                ".descriptionStartsWith({text})",
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND name BEGINSWITH {text}"),
            note="a section card's header (an Image named by the section / entry title). Android: "
            "an ImageView (survey_mo3_1.xml: 'On-Site Work Details')",
        ),
        "entry-headers": El(
            android=(
                _UI,
                'new UiSelector().className("android.widget.ImageView")'
                ".descriptionStartsWith({text})",
            ),
            ios=(_P, "type == 'XCUIElementTypeImage' AND name BEGINSWITH {text}"),
            note="headers of a repeatable section's entries: '<section>', '<section> 2', … "
            "(only a single, non-repeated entry was reached in recon A1 — '<section> 2' unproven)",
        ),
        "repeat": El(
            android=(_AID, "Repeat section"), ios=(_P, _BUTTON + "name == 'Repeat section'")
        ),
        "delete-entry": El(
            android=(_AID, "Delete"),
            ios=(_P, _BUTTON + "name == 'Delete' AND rect.width < 60"),
            note="the trash icon of an added entry (the first has none). Android: not reached in "
            "recon A1 — same Flutter text 'Delete' as iOS; iOS needed a width filter against the "
            "dialog's own Delete, confirm whether Android needs the same in step 4",
        ),  # fmt: skip
        "saved": El(
            android=(_AID, "Survey saved"),
            ios=(_P, "name == 'Survey saved'"),
            note="snackbar after Save",
        ),
    },
)

SURVEY_DATE_PICKER = Screen(
    id="survey-date-picker",
    anchor="ok",
    elements={
        "day": El(
            android=(_UI, "new UiSelector().descriptionStartsWith({text})"),
            ios=(_P, _BUTTON + "name BEGINSWITH {text}"),
            note="'15, Tuesday, September 15, 2026' — pass '15, ' (today: '…2026, Today')",
        ),  # fmt: skip
        "ok": El(android=(_AID, "OK"), ios=(_P, _BUTTON + "name == 'OK'")),
        "cancel": El(android=(_AID, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
    },
)

SURVEY_TIME_PICKER = Screen(
    id="survey-time-picker",
    anchor="ok",
    elements={
        "text-mode": El(
            android=(_AID, "Switch to text input mode"),
            ios=(_P, _BUTTON + "name == 'Switch to text input mode'"),
            note="the dial is not in the tree — text input is",
        ),  # fmt: skip
        "hour": El(
            android=(_UI, 'new UiSelector().className("android.widget.EditText").instance(0)'),
            ios=(_P, _FIELD + "name == 'Hour'"),
            note="hint 'Hour' — the first of the two EditTexts of the text-input picker "
            "(survey_time_picker_text.xml); TD-A1, UiSelector cannot match hint",
        ),
        "minute": El(
            android=(_UI, 'new UiSelector().className("android.widget.EditText").instance(1)'),
            ios=(_P, _FIELD + "name == 'Minute'"),
            note="hint 'Minute' — the second EditText of the text-input picker "
            "(survey_time_picker_text.xml); TD-A1, UiSelector cannot match hint",
        ),
        "ok": El(android=(_AID, "OK"), ios=(_P, _BUTTON + "name == 'OK'")),
        "am": El(
            android=(_AID, "AM"),
            note="Android only: the 12-hour picker's AM switch, a RadioButton "
            "(survey_time_picker_text.xml); it starts on the current half of the day",
        ),
        "pm": El(
            android=(_AID, "PM"),
            note="Android only: the 12-hour picker's PM switch (survey_time_picker_text.xml)",
        ),
    },
)

SURVEY_DELETE_DIALOG = Screen(
    id="survey-delete-dialog",
    anchor="title",
    elements={
        "title": El(android=(_AID, "Delete section"), ios=(_P, _TEXT + "name == 'Delete section'")),
        "message": El(
            android=(_AID, "{text}"),
            ios=(_P, _TEXT + "name == {text}"),
            note="the dialog's question",
        ),
        "cancel": El(android=(_AID, "Cancel"), ios=(_P, _BUTTON + "name == 'Cancel'")),
        "delete": El(
            android=(_AID, "Delete"),
            ios=(_P, _BUTTON + "name == 'Delete' AND rect.width > 60"),
            note="the dialog's button (the entry's trash icon is 48 wide on iOS). Android: not "
            "reached in recon A1 — same Flutter text 'Delete'; confirm width/position "
            "disambiguation against survey.delete-entry in step 4",
        ),  # fmt: skip
    },
)

# Not reached in recon A1 (qa/shared/recon-dumps/android-2026-09-29): same Flutter text as iOS,
# to confirm in step 4 (docs/notes/android-plan.md).
ANDROID_UNVERIFIED: dict[str, str] = {
    "survey.required-error": "not reached in recon A1 — same Flutter text as iOS; confirm in "
    "step 4",
    "survey.thumbnail": "not reached in recon A1 (no photo was carried through to a saved survey "
    "field in the dumps) — same Flutter naming (photo description) as iOS; confirm in step 4",
    "survey.repeat": "not reached in recon A1 — same Flutter text as iOS; confirm in step 4",
    "survey.delete-entry": "not reached in recon A1 — same Flutter text as iOS; confirm in step 4",
    "survey-delete-dialog.title": "not reached in recon A1 — same Flutter text as iOS; confirm in "
    "step 4",
    "survey-delete-dialog.message": "not reached in recon A1 — same Flutter text as iOS; confirm "
    "in step 4",
    "survey-delete-dialog.cancel": "not reached in recon A1 — same Flutter text as iOS; confirm in "
    "step 4",
    "survey-delete-dialog.delete": "not reached in recon A1 — same Flutter text as iOS; confirm in "
    "step 4",
}

# Document-order twins of the aliases the page takes "n-th in form order" (module 08 run 1):
# XCUITest's find_elements returns the off-screen matches FIRST (their rect is empty), so the n-th
# match of a query is not the n-th on the form. The page reads the order from the page source; these
# are the same conditions as the predicates above, per XCUIElementType.
FORM_ORDER: dict[str, dict] = {
    "yes": {"type": "Button", "name": "Yes"},
    "no": {"type": "Button", "name": "No"},
    "option": {"type": "Button", "name": "{text}"},
    "checkbox": {"type": "Switch", "name": "{text}"},
    "text": {
        "type": "TextField",
        "not_names": ("Select date", "Select time", "Hour", "Minute", "0"),
    },
    "date": {"type": "TextField", "name": "Select date"},
    "time": {"type": "TextField", "name": "Select time"},
    "upload-photo": {"type": "Button", "name": "Upload photo"},
    "repeat": {"type": "Button", "name": "Repeat section"},
    "delete-entry": {"type": "Button", "name": "Delete", "max_width": 60},
    "entry-headers": {"type": "Image", "prefix": "{text}"},
}
