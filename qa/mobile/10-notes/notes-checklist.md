# QA Checklist: Notes screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-25 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Notes screen / Empty & Populated States

1. [CHK-NOTE-001] Check that the Notes screen opens from the In Progress Order screen when the user taps the Notes deliverable.
2. [CHK-NOTE-002] Check that the Notes screen displays the title “Notes” and a back navigation control.
3. [CHK-NOTE-003] Check that the empty state is displayed when no notes exist, including placeholder illustration and informational text.
4. [CHK-NOTE-004] Check that the empty state displays the primary action button “Add note”.
5. [CHK-NOTE-005] Check that tapping “Add note” from the empty state navigates the user to the Add note screen.
6. [CHK-NOTE-006] Check that when notes exist, the Notes screen displays a scrollable list of note items.

## Notes screen / Notes List — Content & Ordering

1. [CHK-NOTE-007] Check that each note item displays its creation date and time in the format shown in the wireframes.
2. [CHK-NOTE-008] Check that each note item displays a preview of the note text truncated if it exceeds the visible area.
3. [CHK-NOTE-009] Check that notes are ordered chronologically by creation time with the newest note displayed first.
4. [CHK-NOTE-010] Check that each note item displays a context menu (⋮) for note actions.
5. [CHK-NOTE-011] Check that the Add note button remains visible and accessible when the notes list is populated.

## Notes screen / Add Note Screen — New Note

1. [CHK-NOTE-012] Check that the Add note screen displays the title “Add note” and a back navigation control.
2. [CHK-NOTE-013] Check that the note input field displays the placeholder text “Add note”.
3. [CHK-NOTE-014] Check that the note input field supports multi-line text input.
4. [CHK-NOTE-015] Check that the Save button is disabled when the note input field is empty.
5. [CHK-NOTE-016] Check that the Save button becomes enabled when at least one character is entered in the note input field.

## Notes screen / Note Input Validation

1. [CHK-NOTE-017] Check that the note input field enforces a maximum length of 500 characters.
2. [CHK-NOTE-018] Check that further input is prevented when the 500-character limit is reached.
3. [CHK-NOTE-019] Check that the character counter updates correctly as the user types.

## Notes screen / Save Behavior — Add Note

1. [CHK-NOTE-020] Check that tapping Save persists the new note locally and associates it with the current order and user.
2. [CHK-NOTE-021] Check that the user is returned to the Notes List screen after saving a new note.
3. [CHK-NOTE-022] Check that the new note appears immediately in the Notes List without requiring a manual refresh.
4. [CHK-NOTE-023] Check that a success message “Note added successfully” is displayed after saving a new note.

## Notes screen / Edit Note Screen

1. [CHK-NOTE-024] Check that selecting Edit from a note’s context menu opens the Edit note screen.
2. [CHK-NOTE-025] Check that the Edit note screen displays the title “Edit note”.
3. [CHK-NOTE-026] Check that the existing note content is preloaded into the note input field.
4. [CHK-NOTE-027] Check that editing a note preserves its original creation timestamp.
5. [CHK-NOTE-028] Check that saving an edited note updates the note content and last-modified timestamp.
6. [CHK-NOTE-029] Check that a success message “Note saved successfully” is displayed after editing a note.

## Notes screen / Delete Note

1. [CHK-NOTE-030] Check that the Delete note action is available from the note context menu in the Notes List.
2. [CHK-NOTE-031] Check that the Delete note action is available from the Edit note screen.
3. [CHK-NOTE-032] Check that initiating a delete action opens the Delete Note confirmation pop-up.
4. [CHK-NOTE-033] Check that the Delete Note pop-up displays a destructive-action icon and the title “Delete note”.
5. [CHK-NOTE-034] Check that the warning message about irreversible deletion is displayed in the pop-up.
6. [CHK-NOTE-035] Check that the pop-up displays both Cancel and Delete actions.
7. [CHK-NOTE-036] Check that tapping Cancel closes the pop-up and preserves the note content.
8. [CHK-NOTE-037] Check that tapping Delete permanently removes the note from the order.
9. [CHK-NOTE-038] Check that the Notes List updates immediately after successful note deletion.
10. [CHK-NOTE-039] Check that a success message “Note deleted successfully” is displayed after deletion.
11. [CHK-NOTE-040] Check that deleted notes are no longer accessible for viewing or editing.
12. [CHK-NOTE-041] Check that deleting a required note updates the deliverables completion state accordingly. (if notes are configured as required)
13. [CHK-NOTE-042] Check that notes cannot be edited or deleted after deliverables are submitted.

## Notes screen / Offline Behavior & Sync

1. [CHK-NOTE-043] Check that notes can be created, edited, and deleted while the device is offline.
2. [CHK-NOTE-044] Check that offline note changes are stored locally on the device.
3. [CHK-NOTE-045] Check that locally stored note changes are synced automatically when connectivity is restored.
4. [CHK-NOTE-046] Check that deleting an unsynced note removes it from local storage immediately.
5. [CHK-NOTE-047] Check that deleting a synced note queues the deletion and syncs it when the device goes online.

## Notes screen / Error Handling & Data Integrity

1. [CHK-NOTE-048] Check that an error message is displayed if saving a note fails.
2. [CHK-NOTE-049] Check that the note content is preserved when a save error occurs.
3. [CHK-NOTE-050] Check that the user can retry saving the note after a failure.
4. [CHK-NOTE-051] Check that an error message is displayed if note deletion fails.
5. [CHK-NOTE-052] Check that the note is retained when deletion fails and the user can retry.
