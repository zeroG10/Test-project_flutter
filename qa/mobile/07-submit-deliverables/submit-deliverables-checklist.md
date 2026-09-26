# QA Checklist: Submit Deliverables

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-26 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Submit Deliverables / Pop-up Display & UI

1. [CHK-DLV-001] Check that the Submit Deliverables confirmation pop-up is displayed when the user initiates deliverables submission from the In Progress Order screen.
2. [CHK-DLV-002] Check that the Submit Deliverables pop-up is displayed as a modal dialog above the current screen with a semi-transparent background overlay.
3. [CHK-DLV-003] Check that the Submit Deliverables pop-up displays a visual confirmation icon (checkmark).
4. [CHK-DLV-004] Check that the Submit Deliverables pop-up displays the title “Submit deliverables”.
5. [CHK-DLV-005] Check that the warning message “You won’t be able to edit it after submission.” is displayed on the pop-up.
6. [CHK-DLV-006] Check that the Submit Deliverables pop-up displays both action buttons: Cancel and Submit.

## Submit Deliverables / Cancel Behavior

1. [CHK-DLV-007] Check that tapping Cancel closes the pop-up and returns the user to the In Progress Order screen.
2. [CHK-DLV-008] Check that tapping Cancel does not trigger any submission request to the backend.
3. [CHK-DLV-009] Check that deliverables remain editable after cancelling the Submit Deliverables pop-up.

## Submit Deliverables / Submit Preconditions & Validation

1. [CHK-DLV-010] Check that tapping Submit triggers validation that all required deliverables are complete before submission starts.
2. [CHK-DLV-011] Check that submission is blocked and an error message is shown when at least one required deliverable is incomplete. (placeholder for exact error text)
3. [CHK-DLV-012] Check that partial submissions are not allowed and the system does not submit only a subset of deliverables.

## Submit Deliverables / Locking & Read-only Rules

1. [CHK-DLV-013] Check that deliverables are locked from further editing immediately after Submit is confirmed.
2. [CHK-DLV-014] Check that submitted deliverables are marked as read-only after successful submission.
3. [CHK-DLV-015] Check that the user cannot modify Survey, Photo report, or Notes after deliverables are locked.
4. [CHK-DLV-016] Check that the application preserves the locked state after leaving and returning to the order screen.

## Submit Deliverables / Submission Execution & States

1. [CHK-DLV-017] Check that confirming Submit initiates deliverables upload to the backend system.
2. [CHK-DLV-018] Check that a submission progress state is displayed while deliverables are being uploaded. (placeholder if UI uses “Submitting deliverables” state)
3. [CHK-DLV-019] Check that the user cannot trigger a second submission while an active submission is in progress.
4. [CHK-DLV-020] Check that a success toast or banner “Deliverables sent to review successfully” is displayed after successful submission.
5. [CHK-DLV-021] Check that the order state is updated to Submitted after successful deliverables submission.
6. [CHK-DLV-022] Check that the Check out action becomes enabled only after deliverables are successfully submitted.

## Submit Deliverables / Offline Behavior

1. [CHK-DLV-023] Check that deliverables submission is prevented when the device is offline.
2. [CHK-DLV-024] Check that an appropriate offline message is displayed when the user attempts to submit deliverables while offline. (placeholder for exact message)
3. [CHK-DLV-025] Check that deliverables remain stored locally when submission is attempted while offline.
4. [CHK-DLV-026] Check that deliverables are automatically submitted when connectivity is restored after an offline submission attempt.

## Submit Deliverables / Error Handling & Retry

1. [CHK-DLV-027] Check that an error message is displayed when deliverables submission fails due to network or backend issues.
2. [CHK-DLV-028] Check that the user is allowed to retry submission after a failed submission attempt.
3. [CHK-DLV-029] Check that deliverables are not marked as successfully submitted when a submission attempt fails.

## Submit Deliverables / Data Recording

1. [CHK-DLV-030] Check that each submission event records the correct Order ID and User ID.
2. [CHK-DLV-031] Check that each submission event records a submission timestamp matching the actual submit time.
3. [CHK-DLV-032] Check that each submission event records deliverables metadata included in the submission payload.
4. [CHK-DLV-033] Check that each submission event records the correct submission status as Success or Failed depending on outcome.
