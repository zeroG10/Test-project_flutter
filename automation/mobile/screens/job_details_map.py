"""Job details (modules 03, 04-order-details, 06 and 07-submit-deliverables).

Source: recon 3b (job_details_new.xml), recon 4 (recon4_details_from_list.xml) and recon 5
(qa/shared/recon-dumps/ios-2026-09-24/recon5_details_full_top.xml): the app bar shows
'<jobId> - <title>' as an element of type Other; the back button is labelled 'Back'; every field
of the details is a StaticText named by its text; the PF phone, "On map", "Attachments (N)" and
"Check in" are Buttons named by their text. The "Updated" banner is not in the tree — pixels
(pages/job_details_page.py). Recon 11 (recon11_*.xml): the submission states and the snackbar.

Android (recon A1, qa/shared/recon-dumps/android-2026-09-29/job_details_new.xml,
job_details_in_progress.xml, job_details_submitted.xml, submitting.xml, submit_result.xml,
submit_incomplete_toast.xml, survey_saved_toast.xml): every field is a content-desc (Flutter
Semantics), Back/On map/Check in/Submit deliverables/PF phone are android.widget.Button, the rest
android.widget.View. The '<jobId> - <title>' text repeats twice in the tree (app-bar header, then
again as the body's first line, D-ORDD-1) — ``instance(0)``/``instance(1)`` tell them apart.
"""

from appium.webdriver.common.appiumby import AppiumBy

from screens import El, Screen

_P = AppiumBy.IOS_PREDICATE
_TEXT = "type == 'XCUIElementTypeStaticText' AND "
_BUTTON = "type == 'XCUIElementTypeButton' AND "
_U = AppiumBy.ANDROID_UIAUTOMATOR
_A = AppiumBy.ACCESSIBILITY_ID

JOB_DETAILS = Screen(
    id="job-details",
    anchor="root",
    elements={
        "root": El(
            ios=(_P, _BUTTON + "name BEGINSWITH 'Attachments ('"),
            android=(_U, 'new UiSelector().descriptionStartsWith("Attachments (")'),
            note="the Attachments row exists on every job's details (recon 3b, 4, 5). "
            "Android: same 'Attachments (' prefix, an ImageView (recon A1, all three job states)",
        ),
        "header": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == {text}"),
            android=(_U, "new UiSelector().description({text}).instance(0)"),
            note="parametrised by '<jobId> - <title>' — the app-bar title. Android: the same text "
            "repeats as title-line in the body (D-ORDD-1) — instance(0) is the app-bar one, first "
            "in document order (recon A1)",
        ),
        "back": El(ios=(_P, _BUTTON + "name == 'Back'"), android=(_A, "Back")),
        "status": El(
            ios=(_P, _TEXT + "name == {text} AND rect.y < 160"),
            android=(_A, "{text}"),
            note="the badge under the app bar (y 128 in recon 5); parametrised by the status "
            "label. Android: content-desc 'New' / 'In progress' / 'Submitted', unique per screen "
            "(recon A1)",
        ),
        "title-line": El(
            ios=(_P, _TEXT + "name == {text}"),
            android=(_U, "new UiSelector().description({text}).instance(1)"),
            note="'<jobId> - <title>' again, as the first line of the body (D-ORDD-1). Android: "
            "instance(1) — the second (body) occurrence, after the app-bar header (recon A1)",
        ),
        "description": El(
            ios=(_P, _TEXT + "name BEGINSWITH {text}"),
            android=(_U, "new UiSelector().descriptionStartsWith({text})"),
            note="one element, lines joined by '\\n' (recon 5): found by its first line; the page "
            "compares the whole text. Android: same '\\n'-joined content-desc (recon A1)",
        ),
        "location-title": El(ios=(_P, _TEXT + "name == 'Location'"), android=(_A, "Location")),
        "address": El(
            ios=(_P, _TEXT + "name == {text}"),
            android=(_A, "{text}"),
            note="the address sent in POST /job",
        ),
        "on-map": El(ios=(_P, _BUTTON + "name == 'On map'"), android=(_A, "On map")),
        "schedule-title": El(
            ios=(_P, _TEXT + "name == 'Scheduled date & time'"),
            android=(_A, "Scheduled date & time"),
        ),
        "date": El(
            ios=(_P, _TEXT + "name == {text}"),
            android=(_A, "{text}"),
            note="'d MMM y' in the device time zone. Android: same format, e.g. '29 Sep 2026' "
            "(recon A1)",
        ),
        "time": El(
            ios=(_P, _TEXT + "name == {text}"),
            android=(_A, "{text}"),
            note="'HH:mm' in the device time zone. Android: same format, e.g. '11:00' (recon A1)",
        ),
        "pf-title": El(ios=(_P, _TEXT + "name == 'PF info'"), android=(_A, "PF info")),
        "pf-name": El(
            ios=(_P, _TEXT + "name == {text}"),
            android=(_A, "{text}"),
            note="projectFacilitator.name",
        ),
        "pf-phone": El(
            ios=(_P, _BUTTON + "name == {text}"),
            android=(_A, "{text}"),
            note="projectFacilitator.phone as sent — a Button (tap = dial). Android: tapping "
            "opens the system Dialer app with the number pre-filled "
            "(com.google.android.dialer:id/digits, recon A1 dialer.xml) — out of this screen, "
            "report to the main session",
        ),
        "attachments": El(
            ios=(_P, _BUTTON + "name BEGINSWITH 'Attachments ('"),
            android=(_U, 'new UiSelector().descriptionStartsWith("Attachments (")'),
            note="'Attachments (N)' — N is the number of documents + photos. Android: same prefix, "
            "an ImageView (recon A1)",
        ),
        "timer": El(
            ios=(_P, _TEXT + "name CONTAINS ':' AND rect.x > 200 AND rect.y < 200"),
            android=(_U, 'new UiSelector().descriptionContains(":").instance(0)'),
            note="the In progress stopwatch, top right (@238,118): digits and colons joined by "
            "line breaks, e.g. '0\\n0\\n:\\n0\\n0\\n:\\n0\\n5' (recon 6c / 7) — read by the page. "
            "Android: same '\\n'-joined content-desc (recon A1, e.g. "
            "'0\\n0\\n:\\n2\\n9\\n:\\n3\\n2') — UiSelector cannot match a value containing '\\n' "
            "(screens/README.md), so the locator matches on ':' alone; instance(0) is the "
            "stopwatch, the first ':'-bearing element in document order, before the 'Scheduled "
            "date & time' value which also contains ':'",
        ),
        "deliverable": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == {text}"),
            android=(_A, "{text}"),
            note="'Survey' / 'Photo report' / 'Notes' rows of an In progress job (recon 6c / 7). "
            "Android: same content-desc, not clickable once Submitted (recon A1)",
        ),
        "images": El(
            ios=(_P, "type == 'XCUIElementTypeImage'"),
            android=(_U, 'new UiSelector().className("android.widget.ImageView")'),
            note="every image on the details — a deliverable row has its icon (x 43) and chevron "
            "(x 346) inside its rect (recon 7). Android: same icon+chevron ImageView pair per row, "
            "unlabelled (recon A1) — the page filters by the row's rect, as on iOS",
        ),
        "check-in": El(ios=(_P, _BUTTON + "name == 'Check in'"), android=(_A, "Check in")),
        "check-out": El(
            ios=(_P, _BUTTON + "name == 'Check out'"),
            android=(_A, "Check out"),
            note="only for a Submitted job (D-CHIO-1, recon 6)",
        ),
        "submit-deliverables": El(
            ios=(_P, _BUTTON + "name == 'Submit deliverables'"),
            android=(_A, "Submit deliverables"),
            note="the action of an In progress job (recon 6)",
        ),
        "submitting": El(
            ios=(_P, _BUTTON + "name == 'Submitting deliverables'"),
            android=(_A, "Submitting deliverables"),
            note="the action while the submission runs — disabled (recon 11: ~0.3–3 s). Android: "
            "same text, confirmed in recon A1 submitting.xml",
        ),
        "successful": El(
            ios=(_P, _BUTTON + "name == 'Successful'"),
            android=(_A, "Successful"),
            note="1.5 s after a successful submission, then Check out (code; D-DLV-2)",
        ),
        "message": El(
            ios=(_P, "type == 'XCUIElementTypeOther' AND name == {text} AND rect.y > 600"),
            android=(_A, "{text}"),
            note="the snackbar at the bottom, named by its text (~4 s; recon 11). Android: same "
            "content-desc texts confirmed in recon A1 (submit_result.xml 'Server error. Try again "
            "later.', submit_incomplete_toast.xml 'Complete the survey before job submission.', "
            "survey_saved_toast.xml 'Survey saved') — unique per screen, no y filter needed",
        ),
        "retry": El(
            ios=(_P, _BUTTON + "name == 'Retry'"),
            android=(_A, "Retry"),
            note="the action of a failed submission's snackbar (recon 11)",
        ),
        "checking-in": El(
            ios=(_P, _BUTTON + "name == 'Checking in'"),
            android=(_A, "Checking in"),
            note="the Check in button while the location is acquired (NotEnabled, recon 5)",
        ),
        "any-editable": El(
            ios=(
                _P,
                "type == 'XCUIElementTypeTextField' OR type == 'XCUIElementTypeTextView' "
                "OR type == 'XCUIElementTypeSecureTextField'",
            ),
            android=(_U, 'new UiSelector().className("android.widget.EditText")'),
            note="read-only screen: must match nothing (CHK-ORDD-010)",
        ),
    },
)

# Not reached in recon A1 (recon-2026-09-29-android.md: DEV always 500s on submit, so "Successful"
# never shows; "Checking in" was not caught either) — same Flutter text as iOS; confirm in step 4.
ANDROID_UNVERIFIED = {
    "job-details.successful": "not reached in recon A1 — DEV submit always 500s (Server error), "
    "'Successful' state never shown; same Flutter text as iOS",
    "job-details.checking-in": "not reached in recon A1 — the Check in → Confirm flow moved past "
    "it too fast to catch; same Flutter text as iOS",
}

# What a submission shows, read from the page source many times a second (recon 11: the
# "Submitting deliverables" state lasts ~0.3–3 s, "Successful" 1.5 s) — names of the Buttons above
# and the lowest y of a snackbar ("message").
SUBMIT_STATES = {
    "submitting": "Submitting deliverables",
    "successful": "Successful",
    "check-out": "Check out",
    "retry": "Retry",
}
MESSAGE_MIN_Y = 600
