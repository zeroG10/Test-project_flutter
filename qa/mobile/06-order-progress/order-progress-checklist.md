# QA Checklist: Order details_In progress state_screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-24 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## The Order Details / Header & Status

1. [CHK-ORDP-001] Check that the Order Details screen displays the “In progress” status badge when the job is active.
2. [CHK-ORDP-002] Check that the elapsed time counter is displayed in HH:MM:SS format and updates in real time on the In Progress screen.
3. [CHK-ORDP-003] Check that the elapsed time counter continues correctly after the app is minimized and reopened while the job remains In Progress.

## The Order Details / Deliverables Section UI

1. [CHK-ORDP-004] Check that the Deliverables section displays three tappable items: Survey, Photo report, and Notes.
2. [CHK-ORDP-005] Check that each deliverable row displays an icon and a navigation chevron indicating it is tappable.
3. [CHK-ORDP-006] Check that tapping Survey navigates to the Survey data entry screen from the In Progress screen.
4. [CHK-ORDP-007] Check that tapping Photo report navigates to the Photo report data entry screen from the In Progress screen.
5. [CHK-ORDP-008] Check that tapping Notes navigates to the Notes data entry screen from the In Progress screen.
6. [CHK-ORDP-009] Check that each deliverable displays a completion state indicator in the In Progress list when progress exists. (placeholder if indicator is added later)

## The Order Details / Order Information Section UI

1. [CHK-ORDP-010] Check that the job scope text is displayed as multi-line instructions under the deliverables section.
2. [CHK-ORDP-011] Check that the Location section displays site name and City, State information on the In Progress screen.
3. [CHK-ORDP-012] Check that the “On map” link is displayed in the Location section and is tappable.
4. [CHK-ORDP-013] Check that tapping “On map” opens an external maps application with the correct job site location.
5. [CHK-ORDP-014] Check that the Date & time section displays the scheduled date and time in the format shown in the design.
6. [CHK-ORDP-015] Check that the PF info section displays the PF name and a tappable phone number link.
7. [CHK-ORDP-016] Check that tapping the PF phone number opens the device dialer with the number prefilled.
8. [CHK-ORDP-017] Check that the Attachments row is displayed and navigates to the Attachments screen when tapped.

## The Order Details / Submit Deliverables Button & Confirmation

1. [CHK-ORDP-018] Check that the primary action button displays “Submit deliverables” when deliverables are not yet submitted and the job is In Progress.
2. [CHK-ORDP-019] Check that tapping “Submit deliverables” displays a confirmation modal titled “Submit deliverables”.
3. [CHK-ORDP-020] Check that the confirmation modal informs the user they won’t be able to edit deliverables after submission.
4. [CHK-ORDP-021] Check that the confirmation modal displays both Cancel and Submit actions.
5. [CHK-ORDP-022] Check that tapping Cancel closes the confirmation modal without submitting deliverables.
6. [CHK-ORDP-023] Check that tapping Submit triggers deliverables submission to the backend and prevents further edits to deliverables.

## The Order Details / Submission Progress & Success States

1. [CHK-ORDP-024] Check that a “Submitting deliverables” progress state is displayed while submission is in progress.
2. [CHK-ORDP-025] Check that the Submit deliverables button is disabled while submission is in progress.
3. [CHK-ORDP-026] Check that a success toast “Deliverables sent to review successfully” is displayed after successful submission.
4. [CHK-ORDP-027] Check that the primary action area displays a success state label (e.g., “Successful”) after submission completes.
5. [CHK-ORDP-028] Check that the primary action button changes to “Check out” after deliverables are successfully submitted.

## The Order Details / Offline / Poor Connection Behavior

1. [CHK-ORDP-029] Check that the Submit deliverables button is disabled when the device is offline on the In Progress screen.
2. [CHK-ORDP-030] Check that an offline informational message is displayed when the device is offline and submission is unavailable. (placeholder if text differs from SRS)
3. [CHK-ORDP-031] Check that deliverables progress is saved locally while offline and remains available after app restart.
4. [CHK-ORDP-032] Check that deliverables are automatically synced or submitted when connectivity is restored if submission was interrupted.

## The Order Details / Connection Restored Modal

1. [CHK-ORDP-033] Check that a “Connection restored” modal is displayed when network connectivity returns and there are unfinished jobs with pending submission.
2. [CHK-ORDP-034] Check that the “Connection restored” modal lists the unfinished job name(s) and identifiers as shown in the wireframes.
3. [CHK-ORDP-035] Check that the “Connection restored” modal provides Cancel and Submit actions.
4. [CHK-ORDP-036] Check that tapping Cancel closes the modal without submitting pending deliverables.
5. [CHK-ORDP-037] Check that tapping Submit starts deliverables submission for the listed unfinished job(s).
6. [CHK-ORDP-038] Check that an error message is displayed when deliverables submission fails due to network or server error.
7. [CHK-ORDP-039] Check that the user can retry submission after a deliverables submission failure without losing entered data.
8. [CHK-ORDP-040] Check that locally stored deliverables are preserved and retried automatically when syncing fails due to connectivity issues.
9. [CHK-ORDP-041] Check that deliverables cannot be edited after successful submission if the confirmation warning is accepted.
10. [CHK-ORDP-042] Check that returning to the In Progress screen preserves the correct primary action state based on submission status.
