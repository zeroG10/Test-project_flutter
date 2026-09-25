# Test cases — Notes (mobile)

> Structured, alias-based test cases for the CHK IDs selected in [notes-automation-plan.md](notes-automation-plan.md).
> Format: [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: draft — written after recon 10 ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md)) and the
> owner's decisions (2026-09-25: Q-NOTE-1…3 closed; BUG-NOTE-001 draft for validation).**

| Field | Value |
|---|---|
| Feature | The Notes of an In progress job: empty / list states, add, edit, delete, validation, toasts, persistence, read-only after submission, the server copy |
| Source checklist | `qa/mobile/10-notes/notes-checklist.md` (CHK-NOTE-001…052) |
| Devices / build | iPhone 17 · iOS 26.5 (simulator) · `[DEV] CT Mobile` 1.1.1 (178), `CLIENT_BUILD=true` · online |
| Owner | @mykola.zhuchenko · Last updated 2026-09-25 |

**Conventions**

- **One job per test**, created through `POST /job` directly In progress (fixture `survey_job`); a Submitted one for
  TC-NOTE-007. Deleted after the test.
- **A note row** is one element: its date, text and ⋮ in one label (TD-NOTE-001). `notes.row[n]` is the n-th row (newest
  first); `notes.menu[n]` is its ⋮, tapped at the row's right end.
- **The server copy** = `GET /job/{id}` → `notes` (`text`, no id).

---

## TC-NOTE-001 — The empty Notes screen leads to a saved note, with the Save rules and the success message

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-001, -002, -003, -004, -005, -006, -012, -013, -014, -015, -016, -020, -021, -022, -023 |
| Priority | P0 · smoke |
| Preconditions | `{{job.progress}}` In progress, details open |
| Oracle | spec — SRS §3.1.3.4.5–6 (empty state, "Add note", FR-NOT-ADD-01/02/05/06) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Notes] | — | — |
| 2 | expect-visible | notes.header | — | "Notes", with notes.back |
| 3 | expect-text | notes.empty-title | — | No notes have been added yet · Add note to the report to get started. |
| 4 | click | notes.add-note | — | note-editor.add-title "Add note" |
| 5 | expect-visible | note-editor.field | — | placeholder "Add note", counter "0/500" |
| 6 | expect-disabled | note-editor.save | — | — |
| 7 | fill | note-editor.field | `QA-AUTO note one` + a line break + `line two` | multi-line |
| 8 | expect-enabled | note-editor.save | — | — |
| 9 | click | note-editor.save | — | notes.toast "Note added successfully" |
| 10 | expect-text | notes.row[1] | — | today's date, `QA-AUTO note one` |
| 11 | expect-text | api.jobNotes | — | the note on the job |

## TC-NOTE-002 — The list: newest first, date and time, preview, ⋮, Add note available

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-007, -008, -009, -010, -011 |
| Priority | P1 |
| Preconditions | as TC-NOTE-001 |
| Oracle | spec — FR-NOT-02 (newest first); SRS §3.1.3.4.5 (date "01 Aug 2026 11:52", preview, ⋮ with Edit / Delete) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | notes.add-note | `QA-AUTO first`, Save | — |
| 2 | click | notes.add-note | `QA-AUTO second`, Save | — |
| 3 | click | notes.add-note | a 300-character note, Save | — |
| 4 | expect-text | notes.row | — | the 300-character note, `QA-AUTO second`, `QA-AUTO first` (newest first) |
| 5 | expect-text | notes.row[1] | — | date `dd MMM yyyy HH:mm` of now; the text shown as a preview |
| 6 | click | notes.menu[1] | — | note-menu: Edit, Delete |
| 7 | expect-visible | notes.add-note | — | — |

## TC-NOTE-003 — A note takes 500 characters; the 501st is refused; the counter follows

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-017, -018, -019 |
| Priority | P1 |
| Preconditions | the Add note screen |
| Oracle | spec — SRS §3.1.3.4.6 (limit 500, counter) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | fill | note-editor.field | `QA-AUTO` | counter "7/500" |
| 2 | fill | note-editor.field | 501 characters in all | the first 500 kept; counter "500/500" |

## TC-NOTE-004 — Editing: "Edit note" preloads the text; Save updates it in place with "Note saved successfully"; leaving without Save warns

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-024, -025, -026, -027, -028, -029 |
| Priority | P1 |
| Preconditions | two notes, `QA-AUTO older` and `QA-AUTO newer` |
| Oracle | spec — FR-NOT-05/06, FR-NOT-ADD-03/06; D-NOTE-1 (the warning), D-NOTE-4 (the time shown) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | notes.menu[2] | `QA-AUTO older` | note-menu |
| 2 | click | note-menu.edit | — | note-editor.edit-title "Edit note"; the text preloaded |
| 3 | fill | note-editor.field | append ` edited` | — |
| 4 | click | note-editor.back | — | note-unsaved-dialog "Unsaved Changes" |
| 5 | click | note-unsaved-dialog.leave | — | the list, `QA-AUTO older` unchanged |
| 6 | click | notes.menu[2] | then note-menu.edit, append ` edited` | — |
| 7 | click | note-editor.save | — | notes.toast "Note saved successfully" |
| 8 | expect-text | notes.row | — | `QA-AUTO newer`, `QA-AUTO older edited` — the order kept (creation time) |

## TC-NOTE-005 — Deleting from ⋮ and from "Edit note": the dialog, Cancel keeps, Delete removes with "Note deleted successfully"

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-030, -031, -032, -033, -034, -035, -036, -038, -039, -040 |
| Priority | P0 |
| Preconditions | two notes |
| Oracle | spec — FR-NOT-07/08; SRS §3.1.3.4.7 (the dialog text) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | notes.menu[1] | then note-menu.delete | note-delete-dialog: "Delete note", "Are you sure you want delete this note. All descriptions will be lost?", Cancel, Delete |
| 2 | click | note-delete-dialog.cancel | — | 2 notes |
| 3 | click | notes.menu[1] | then note-menu.delete | — |
| 4 | click | note-delete-dialog.delete | — | notes.toast "Note deleted successfully"; 1 note |
| 5 | click | notes.menu[1] | then note-menu.edit | "Edit note" with note-editor.delete-note |
| 6 | click | note-editor.delete-note | then note-delete-dialog.delete | notes.empty-title |

## TC-NOTE-006 — Notes survive an app restart

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-020 |
| Priority | P1 |
| Preconditions | a note `QA-AUTO keep` |
| Oracle | spec — FR-NOT-ADD-05 (persisted locally) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | terminate + launch → the job → Notes | — |
| 2 | expect-text | notes.row[1] | — | `QA-AUTO keep` |

## TC-NOTE-007 — After the deliverables are submitted, Notes cannot be opened or changed

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-042 |
| Priority | P1 |
| Preconditions | `{{job.done}}` Submitted, details open |
| Oracle | spec — FR-NOT-05; accepted baseline (as D-SRV-9) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Notes] | — | — |
| 2 | expect-hidden | notes.header | 3 s | the details stay |

## TC-NOTE-008 — An edited note is updated on the job on the server

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-028 |
| Priority | P1 |
| Preconditions | a note `QA-AUTO server note`, saved (on the server) |
| Oracle | spec — FR-NOT-06, FR-NOT-10 |
| Known defect | **BUG-NOTE-001** (draft) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | api.jobNotes | — | `QA-AUTO server note` |
| 2 | click | notes.menu[1] | then note-menu.edit, append ` edited`, note-editor.save | — |
| 3 | expect-text | api.jobNotes | — | `QA-AUTO server note edited` |

## TC-NOTE-009 — A deleted note is removed from the job on the server

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTE-037 |
| Priority | P1 |
| Preconditions | a note `QA-AUTO to delete`, saved (on the server) |
| Oracle | spec — FR-NOT-08 ("permanently remove the note from the order") |
| Known defect | **BUG-NOTE-001** (draft) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | api.jobNotes | — | `QA-AUTO to delete` |
| 2 | click | notes.menu[1] | then note-menu.delete, note-delete-dialog.delete | notes.empty-title |
| 3 | expect-text | api.jobNotes | — | no note |

## Aliases used

| Alias | ios map |
|---|---|
| job-details.deliverable | yes |
| notes.*, note-menu.*, note-editor.*, note-delete-dialog.*, note-unsaved-dialog.* | `screens/notes_map.py` (recon 10) |
| api.jobNotes | not an element — `GET /job/{id}` → `notes` |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-NOTE-001…-006, -012…-016, -020…-023 | TC-NOTE-001 (+ -006) | |
| CHK-NOTE-007…-011 | TC-NOTE-002 | |
| CHK-NOTE-017…-019 | TC-NOTE-003 | |
| CHK-NOTE-024…-029 | TC-NOTE-004 (+ -008 for -028 on the server) | BUG-NOTE-001 |
| CHK-NOTE-030…-036, -038…-040 | TC-NOTE-005 | |
| CHK-NOTE-037 | TC-NOTE-009 | BUG-NOTE-001 |
| CHK-NOTE-042 | TC-NOTE-007 | |

**Not here:**
- CHK-NOTE-041 — skipped with a comment: there is no "required notes" setting (owner, Q-NOTE-2).
- CHK-NOTE-043…-047 — offline, Android stage.
- CHK-NOTE-048…-052 — skipped with a comment (Q-NOTE-1).
