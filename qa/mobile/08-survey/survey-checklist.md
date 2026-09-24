# QA Checklist: Survey screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-24 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Survey screen / Required Fields & Validation

1. [CHK-SRV-001] Check that all required survey questions are clearly marked as required in the survey form.
2. [CHK-SRV-002] Check that an inline validation error is displayed next to a required question when it is left unanswered.
3. [CHK-SRV-003] Check that validation errors disappear automatically when the user provides a valid value for the affected question.
4. [CHK-SRV-004] Check that the survey cannot be marked as completed until all required questions are answered.

## Survey screen / Input Constraints & Data Types

1. [CHK-SRV-005] Check that Yes/No questions allow selecting only one option at a time.
2. [CHK-SRV-006] Check that single-select (radio) questions allow selecting only one option from the list.
3. [CHK-SRV-007] Check that multi-select (checkbox) questions allow selecting multiple options simultaneously.
4. [CHK-SRV-008] Check that the free-text input field does not allow entering more than 500 characters.
5. [CHK-SRV-009] Check that the user is prevented from entering additional characters once the 500-character limit is reached.

## Survey screen / Auto-save Behavior (Critical)

1. [CHK-SRV-010] Check that survey responses are automatically saved locally as the user enters or modifies data.
2. [CHK-SRV-011] Check that survey data is automatically saved when the user navigates back without tapping Save.
3. [CHK-SRV-012] Check that survey data is automatically saved when the app is sent to background.
4. [CHK-SRV-013] Check that previously entered survey data is restored when the Survey screen is reopened.
5. [CHK-SRV-014] Check that survey data persists correctly after app restart while the order remains In Progress.

## Survey screen / Save Button Behavior

1. [CHK-SRV-015] Check that the Save button becomes enabled only when all required survey fields are valid.
2. [CHK-SRV-016] Check that tapping Save persists survey data locally and marks the survey as completed.
3. [CHK-SRV-017] Check that tapping Save returns the user to the In Progress Order Details screen.
4. [CHK-SRV-018] Check that the Survey deliverable is visually marked as completed on the In Progress screen after saving a valid survey.

## Survey screen / Photo Evidence Handling

1. [CHK-SRV-019] Check that the user can attach one or more photos as survey evidence.
2. [CHK-SRV-020] Check that attached photo thumbnails are displayed inside the Evidence section of the survey.
3. [CHK-SRV-021] Check that photos are compressed before upload while maintaining acceptable visual quality.
4. [CHK-SRV-022] Check that attached photos remain visible in the survey after navigating away and returning.
5. [CHK-SRV-023] Check that attached photos remain available after app restart while offline.

## Survey screen / Offline Mode & Sync

1. [CHK-SRV-024] Check that the survey is fully functional when the device is offline.
2. [CHK-SRV-025] Check that survey responses can be edited and saved while offline.
3. [CHK-SRV-026] Check that attached photos are stored locally when added offline.
4. [CHK-SRV-027] Check that survey data and photos are automatically synced when connectivity is restored.

## Survey screen / Error Handling & Recovery

1. [CHK-SRV-028] Check that an error message is displayed if survey data fails to save locally.
2. [CHK-SRV-029] Check that entered survey data is preserved when a save error occurs.
3. [CHK-SRV-030] Check that the user is allowed to retry saving the survey after a save failure.
4. [CHK-SRV-031] Check that a notification is displayed when a photo upload fails.
5. [CHK-SRV-032] Check that failed photo uploads are retained locally and retried automatically during sync.

## Survey screen / Read-only After Submission

1. [CHK-SRV-033] Check that all survey fields become read-only after deliverables are submitted.
2. [CHK-SRV-034] Check that the Save button is disabled or hidden after deliverables submission.
3. [CHK-SRV-035] Check that the user cannot modify survey responses after successful deliverables submission.

## Survey screen / Data Integrity

1. [CHK-SRV-036] Check that each saved survey includes the correct Order ID and Survey Template ID.
2. [CHK-SRV-037] Check that each survey response is saved with the correct Question IDs and answers.
3. [CHK-SRV-038] Check that attached photo references are included in the survey data payload.
4. [CHK-SRV-039] Check that the survey last modified timestamp is updated after each change.
5. [CHK-SRV-040] Check that the survey completion status is correctly stored after Save.
