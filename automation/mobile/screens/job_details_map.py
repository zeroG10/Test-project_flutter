"""Job details (modules 03 and 04-order-details).

Source: recon 3b (job_details_new.xml), recon 4 (recon4_details_from_list.xml) and recon 5
(qa/shared/recon-dumps/ios-2026-09-24/recon5_details_full_top.xml): the app bar shows
'<jobId> - <title>' as an element of type Other; the back button is labelled 'Back'; every field
of the details is a StaticText named by its text; the PF phone, "On map", "Attachments (N)" and
"Check in" are Buttons named by their text. The "Updated" banner is not in the tree — pixels
(pages/job_details_page.py).
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "

JOB_DETAILS = Screen(
    id="job-details",
    anchor="root",
    elements={
        "root": El(
            ios=(_P, _BUTTON + "name BEGINSWITH 'Attachments ('"),
            note="the Attachments row exists on every job's details (recon 3b, 4, 5)",
        ),
        "header": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == {text}"),
            note="parametrised by '<jobId> - <title>' — the app-bar title",
        ),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'")),
        "status": El(
            ios=(_P, _TEXT + "name == {text} AND rect.y < 160"),
            note="the badge under the app bar (y 128 in recon 5); parametrised by the status label",
        ),
        "title-line": El(
            ios=(_P, _TEXT + "name == {text}"),
            note="'<jobId> - <title>' again, as the first line of the body (D-ORDD-1)",
        ),
        "description": El(
            ios=(_P, _TEXT + "name BEGINSWITH {text}"),
            note="one element, lines joined by '\\n' (recon 5): found by its first line; the page "
            "compares the whole text",
        ),
        "location-title": El(ios=(_P, _TEXT + "name == 'Location'")),
        "address": El(ios=(_P, _TEXT + "name == {text}"), note="the address sent in POST /job"),
        "on-map": El(ios=(_P, _BUTTON + "name == 'On map'")),
        "schedule-title": El(ios=(_P, _TEXT + "name == 'Scheduled date & time'")),
        "date": El(ios=(_P, _TEXT + "name == {text}"), note="'d MMM y' in the device time zone"),
        "time": El(ios=(_P, _TEXT + "name == {text}"), note="'HH:mm' in the device time zone"),
        "pf-title": El(ios=(_P, _TEXT + "name == 'PF info'")),
        "pf-name": El(ios=(_P, _TEXT + "name == {text}"), note="projectFacilitator.name"),
        "pf-phone": El(
            ios=(_P, _BUTTON + "name == {text}"),
            note="projectFacilitator.phone as sent — a Button (tap = dial)",
        ),
        "attachments": El(
            ios=(_P, _BUTTON + "name BEGINSWITH 'Attachments ('"),
            note="'Attachments (N)' — N is the number of documents + photos",
        ),
        "check-in": El(ios=(_P, _BUTTON + "name == 'Check in'")),
        "checking-in": El(
            ios=(_P, _BUTTON + "name == 'Checking in'"),
            note="the Check in button while the location is acquired (NotEnabled, recon 5)",
        ),
        "any-editable": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeTextField' OR type == 'XCUIElementTypeTextView' "
                "OR type == 'XCUIElementTypeSecureTextField'",
            ),
            note="read-only screen: must match nothing (CHK-ORDD-010)",
        ),
    },
)
