# Automated traceability — mobile

Generated: 2026-09-25 18:23 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/10-notes/notes-checklist.md` — 52 items
- Results (allure): `automation/mobile/allure-results-10` — 9 tests (7 passed, 2 failed, 0 skipped)

## Run context — the limits of every verdict below

- Target: `iOS simulator iPhone 17 · iOS 26.5 · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true`
- Harness commit (this repo): `61dabbb`
- Environment label (pytest): `iOS · iPhone 17 · iOS 26.5 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=ios tests/shared/test_notes.py (module 10 run 1, 2026-09-25; one In progress job per test, a Submitted one for TC-NOTE-007)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-NOTE-001 | Check that the Notes screen opens from the In Progress Order screen when the us… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-002 | Check that the Notes screen displays the title “Notes” and a back navigation co… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-003 | Check that the empty state is displayed when no notes exist, including placehol… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-004 | Check that the empty state displays the primary action button “Add note”. | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-005 | Check that tapping “Add note” from the empty state navigates the user to the Ad… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-006 | Check that when notes exist, the Notes screen displays a scrollable list of not… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-007 | Check that each note item displays its creation date and time in the format sho… | 1 — `tests.shared.test_notes#test_notes_list (TC-NOTE-002 The list: newest first, date and time, preview, ⋮, Add note available)` | Passed | allure: passed |
| CHK-NOTE-008 | Check that each note item displays a preview of the note text truncated if it e… | 1 — `tests.shared.test_notes#test_notes_list (TC-NOTE-002 The list: newest first, date and time, preview, ⋮, Add note available)` | Passed | allure: passed |
| CHK-NOTE-009 | Check that notes are ordered chronologically by creation time with the newest n… | 1 — `tests.shared.test_notes#test_notes_list (TC-NOTE-002 The list: newest first, date and time, preview, ⋮, Add note available)` | Passed | allure: passed |
| CHK-NOTE-010 | Check that each note item displays a context menu (⋮) for note actions. | 1 — `tests.shared.test_notes#test_notes_list (TC-NOTE-002 The list: newest first, date and time, preview, ⋮, Add note available)` | Passed | allure: passed |
| CHK-NOTE-011 | Check that the Add note button remains visible and accessible when the notes li… | 1 — `tests.shared.test_notes#test_notes_list (TC-NOTE-002 The list: newest first, date and time, preview, ⋮, Add note available)` | Passed | allure: passed |
| CHK-NOTE-012 | Check that the Add note screen displays the title “Add note” and a back navigat… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-013 | Check that the note input field displays the placeholder text “Add note”. | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-014 | Check that the note input field supports multi-line text input. | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-015 | Check that the Save button is disabled when the note input field is empty. | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-016 | Check that the Save button becomes enabled when at least one character is enter… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-017 | Check that the note input field enforces a maximum length of 500 characters. | 1 — `tests.shared.test_notes#test_note_limit (TC-NOTE-003 A note takes 500 characters; the 501st is refused; the counter follows)` | Passed | allure: passed |
| CHK-NOTE-018 | Check that further input is prevented when the 500-character limit is reached. | 1 — `tests.shared.test_notes#test_note_limit (TC-NOTE-003 A note takes 500 characters; the 501st is refused; the counter follows)` | Passed | allure: passed |
| CHK-NOTE-019 | Check that the character counter updates correctly as the user types. | 1 — `tests.shared.test_notes#test_note_limit (TC-NOTE-003 A note takes 500 characters; the 501st is refused; the counter follows)` | Passed | allure: passed |
| CHK-NOTE-020 | Check that tapping Save persists the new note locally and associates it with th… | 2 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)`; `tests.shared.test_notes#test_notes_after_restart (TC-NOTE-006 Notes survive an app restart)` | Passed | allure: passed<br>allure: passed |
| CHK-NOTE-021 | Check that the user is returned to the Notes List screen after saving a new not… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-022 | Check that the new note appears immediately in the Notes List without requiring… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-023 | Check that a success message “Note added successfully” is displayed after savin… | 1 — `tests.shared.test_notes#test_add_note (TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success message)` | Passed | allure: passed |
| CHK-NOTE-024 | Check that selecting Edit from a note’s context menu opens the Edit note screen. | 1 — `tests.shared.test_notes#test_edit_note (TC-NOTE-004 Editing: 'Edit note' preloads the text; Save updates it in place with 'Note saved successfully'; leaving without Save warns)` | Passed | allure: passed |
| CHK-NOTE-025 | Check that the Edit note screen displays the title “Edit note”. | 1 — `tests.shared.test_notes#test_edit_note (TC-NOTE-004 Editing: 'Edit note' preloads the text; Save updates it in place with 'Note saved successfully'; leaving without Save warns)` | Passed | allure: passed |
| CHK-NOTE-026 | Check that the existing note content is preloaded into the note input field. | 1 — `tests.shared.test_notes#test_edit_note (TC-NOTE-004 Editing: 'Edit note' preloads the text; Save updates it in place with 'Note saved successfully'; leaving without Save warns)` | Passed | allure: passed |
| CHK-NOTE-027 | Check that editing a note preserves its original creation timestamp. | 1 — `tests.shared.test_notes#test_edit_note (TC-NOTE-004 Editing: 'Edit note' preloads the text; Save updates it in place with 'Note saved successfully'; leaving without Save warns)` | Passed | allure: passed |
| CHK-NOTE-028 | Check that saving an edited note updates the note content and last-modified tim… | 2 — `tests.shared.test_notes#test_edited_note_on_server (TC-NOTE-008 An edited note is updated on the job on the server)`; `tests.shared.test_notes#test_edit_note (TC-NOTE-004 Editing: 'Edit note' preloads the text; Save updates it in place with 'Note saved successfully'; leaving without Save warns)` | Failed | allure: failed — AssertionError: the server holds ['QA-AUTO server note']<br>allure: passed |
| CHK-NOTE-029 | Check that a success message “Note saved successfully” is displayed after editi… | 1 — `tests.shared.test_notes#test_edit_note (TC-NOTE-004 Editing: 'Edit note' preloads the text; Save updates it in place with 'Note saved successfully'; leaving without Save warns)` | Passed | allure: passed |
| CHK-NOTE-030 | Check that the Delete note action is available from the note context menu in th… | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-031 | Check that the Delete note action is available from the Edit note screen. | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-032 | Check that initiating a delete action opens the Delete Note confirmation pop-up. | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-033 | Check that the Delete Note pop-up displays a destructive-action icon and the ti… | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-034 | Check that the warning message about irreversible deletion is displayed in the… | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-035 | Check that the pop-up displays both Cancel and Delete actions. | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-036 | Check that tapping Cancel closes the pop-up and preserves the note content. | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-037 | Check that tapping Delete permanently removes the note from the order. | 1 — `tests.shared.test_notes#test_deleted_note_leaves_server (TC-NOTE-009 A deleted note is removed from the job on the server)` | Failed | allure: failed — AssertionError: the deleted note is still on the job: ['QA-AUTO to delete'] |
| CHK-NOTE-038 | Check that the Notes List updates immediately after successful note deletion. | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-039 | Check that a success message “Note deleted successfully” is displayed after del… | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-040 | Check that deleted notes are no longer accessible for viewing or editing. | 1 — `tests.shared.test_notes#test_delete_note (TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes with 'Note deleted successfully')` | Passed | allure: passed |
| CHK-NOTE-041 | Check that deleting a required note updates the deliverables completion state a… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-042 | Check that notes cannot be edited or deleted after deliverables are submitted. | 1 — `tests.shared.test_notes#test_submitted_notes_read_only (TC-NOTE-007 After the deliverables are submitted, Notes cannot be opened or changed)` | Passed | allure: passed |
| CHK-NOTE-043 | Check that notes can be created, edited, and deleted while the device is offlin… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-044 | Check that offline note changes are stored locally on the device. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-045 | Check that locally stored note changes are synced automatically when connectivi… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-046 | Check that deleting an unsynced note removes it from local storage immediately. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-047 | Check that deleting a synced note queues the deletion and syncs it when the dev… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-048 | Check that an error message is displayed if saving a note fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-049 | Check that the note content is preserved when a save error occurs. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-050 | Check that the user can retry saving the note after a failure. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-051 | Check that an error message is displayed if note deletion fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTE-052 | Check that the note is retained when deletion fails and the user can retry. | 0 |  | no tagged test — not run (manual / exploratory), never green |

**Summary:** total 52 · automated 41 · Passed 39 · Failed 2 · Blocked 0 · Not run 11 (= total − Passed − Failed − Blocked)

## Failed rows → defects

| CHK ID | Test | Defect |
|---|---|---|
| CHK-NOTE-028 | TC-NOTE-008 — the server keeps the old text after an edit (TC-NOTE-004 passed: the app shows the edit) | [BUG-NOTE-001](bugs/BUG-NOTE-001.md) (draft — the owner validates) |
| CHK-NOTE-037 | TC-NOTE-009 — the deleted note is still on the job on the server | [BUG-NOTE-001](bugs/BUG-NOTE-001.md) |

**Not automated (11):**
- CHK-NOTE-041: skipped with a comment — there is no "required notes" setting (owner, Q-NOTE-2).
- CHK-NOTE-043…-047: offline, Android stage.
- CHK-NOTE-048…-052: skipped with a comment (owner, Q-NOTE-1).
