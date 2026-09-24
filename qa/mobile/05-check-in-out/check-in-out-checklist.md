# QA Checklist: Check-In / Check-Out Flow

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-24 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Entry & Modal Presentation

1. [CHK-CHIO-001] Check that the Check-In Confirmation screen is displayed as a full-screen modal when the user initiates a check-in action from the Order Details screen.
2. [CHK-CHIO-002] Check that the Check-Out Confirmation screen is displayed as a full-screen modal when the user initiates a check-out action from an In Progress order.
3. [CHK-CHIO-003] Check that the confirmation modal displays a Close (X) icon that cancels the action.
4. [CHK-CHIO-004] Check that the confirmation modal displays a clear title indicating Check-In or Check-Out action.
5. [CHK-CHIO-005] Check that the confirmation modal displays a primary message describing the action being confirmed.
6. [CHK-CHIO-006] Check that the confirmation modal displays supporting explanatory text clarifying the effect of the action.

## Action Buttons & Cancellation

1. [CHK-CHIO-007] Check that the Cancel button aborts the check-in action and closes the confirmation modal without changing the order status.
2. [CHK-CHIO-008] Check that the Cancel button aborts the check-out action and closes the confirmation modal without changing the order status.
3. [CHK-CHIO-009] Check that tapping the Close (X) icon behaves the same as tapping Cancel.

## Check-In Confirmation Logic

1. [CHK-CHIO-010] Check that tapping Confirm on the Check-In screen records the check-in timestamp.
2. [CHK-CHIO-011] Check that tapping Confirm on the Check-In screen triggers GPS capture when location permission is enabled.
3. [CHK-CHIO-012] Check that the check-in method is flagged as GPS when location is successfully captured.
4. [CHK-CHIO-013] Check that the check-in method is flagged as Manual when GPS is unavailable or declined.
5. [CHK-CHIO-014] Check that the order status is updated to In Progress after successful check-in confirmation.
6. [CHK-CHIO-015] Check that an email notification is triggered to the Project Facilitator after a successful check-in.

## Check-Out Confirmation Logic

1. [CHK-CHIO-016] Check that tapping Confirm on the Check-Out screen records the check-out timestamp.
2. [CHK-CHIO-017] Check that tapping Confirm on the Check-Out screen triggers GPS capture when location permission is enabled.
3. [CHK-CHIO-018] Check that the check-out method is flagged as GPS when location is successfully captured.
4. [CHK-CHIO-019] Check that the check-out method is flagged as Manual when GPS is unavailable or declined.
5. [CHK-CHIO-020] Check that the order status is updated to Completed or the next workflow status after successful check-out.
6. [CHK-CHIO-021] Check that an email notification is triggered to the Project Facilitator after a successful check-out.

## Check-Out Confirmation Logic / Location Integration

1. [CHK-CHIO-022] Check that initiating Check-In triggers the location permission and validation flow defined in the Location Services specification.
2. [CHK-CHIO-023] Check that initiating Check-Out triggers the location permission and validation flow defined in the Location Services specification.
3. [CHK-CHIO-024] Check that manual Check-In or Check-Out is allowed when GPS permission is denied or location is unavailable.
4. [CHK-CHIO-025] Check that manual Check-In action іs clearly flagged in the recorded data.
5. [CHK-CHIO-026] Check that manual Check-Out action is clearly flagged in the recorded data.

## Check-Out Confirmation Logic / Error Handling & Retry

1. [CHK-CHIO-027] Check that an error message is displayed if the Check-In operation fails due to a system or network error.
2. [CHK-CHIO-028] Check that an error message is displayed if the Check-Out operation fails due to a system or network error.
3. [CHK-CHIO-029] Check that the user is allowed to retry Check-In after a failed Check-In attempt.
4. [CHK-CHIO-030] Check that the user is allowed to retry Check-Out after a failed Check-Out attempt.
5. [CHK-CHIO-031] Check that the Check-In action does not complete if required data such as timestamp cannot be recorded.
6. [CHK-CHIO-032] Check that the Check-Out action does not complete if required data such as timestamp cannot be recorded.

## Check-Out Confirmation Logic / Data Integrity

1. [CHK-CHIO-033] Check that each Check-In event stores the correct Order ID and User ID.
2. [CHK-CHIO-034] Check that each Check-Out event stores the correct Order ID and User ID.
3. [CHK-CHIO-035] Check that the recorded action type is correctly stored as Check-In or Check-Out.
4. [CHK-CHIO-036] Check that the recorded timestamp reflects the actual confirmation time of the action.
5. [CHK-CHIO-037] Check that GPS coordinates are stored when location is enabled and available.

## Check-Out Confirmation Logic / UX & Stability

1. [CHK-CHIO-038] Check that the confirmation modal remains responsive during slow GPS acquisition or network conditions.
2. [CHK-CHIO-039] Check that multiple rapid taps on the Confirm button do not trigger duplicate Check-In or Check-Out events.
3. [CHK-CHIO-040] Check that the user cannot initiate Check-In or Check-Out actions that are invalid for the current order status.
