# Automation plan — Notes (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/10-notes/notes-checklist.md` (52 items,
> `CHK-NOTE-001…052`, imported 2026-09-25). Date: 2026-09-25. Owner: mykola.zhuchenko.
> **Status: draft — waits for the owner (Q-NOTE-1…3 in [notes-questions.md](notes-questions.md)).**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| Feature code | `NOTE` |
| Scope decision (proposed) | the Notes screen of an In progress job: empty / list states, order, add / edit / delete (menu and edit page), validation, toasts, persistence, read-only after submission, the server copy; offline and failures → Android stage / skipped (Q-NOTE-1) |
| Oracle model | accepted production baseline; SRS §3.1.3.4.5–7 (FR-NOT, FR-NOT-ADD); recon 7 / 10; the job's notes on the server (`GET /job/{id}` → `notes`) |

## Step 3–4 — Candidate matrix (52 items)

| CHK ID | Scenario (short) | Level | Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|
| CHK-NOTE-001…006 | opens; title, back; empty state + Add note; list | E2E UI | Good Candidate | P0 | TC-NOTE-001 | recon 7 |
| CHK-NOTE-007…011 | date & time, preview, newest first, ⋮, Add note stays | E2E UI | Good Candidate | P1 | TC-NOTE-002 | |
| CHK-NOTE-012…016 | Add note: title, placeholder, multi-line, Save disabled / enabled | E2E UI | Good Candidate | P0 | TC-NOTE-001 | |
| CHK-NOTE-017…019 | 500 limit, counter | E2E UI | Good Candidate | P1 | TC-NOTE-003 | |
| CHK-NOTE-020…023 | Save: persisted with the job, back to the list, at once, "Note added successfully" | E2E UI + API | Good Candidate | P0 | TC-NOTE-001 | + the server copy |
| CHK-NOTE-024…029 | Edit: from ⋮, title, preloaded, creation time kept, updated, "Note saved successfully" | E2E UI + API | Good Candidate | P1 | TC-NOTE-004 | |
| CHK-NOTE-030…040 | Delete: from ⋮ and from Edit note; dialog; Cancel; Delete; list; toast; gone | E2E UI + API | Good Candidate | P0 | TC-NOTE-005 | |
| CHK-NOTE-041 | a required note | — | Skipped (D-NOTE-3) | – | — | no such setting (Q-NOTE-2) |
| CHK-NOTE-042 | no edit / delete after submission | E2E UI + API setup | Good Candidate | P1 | TC-NOTE-007 | a Submitted job: Notes does not open (as TC-SRV-016) |
| CHK-NOTE-043…047 | offline | Manual (Android stage) | Needs Device | P2 | — | Q-NOTE-1 |
| CHK-NOTE-048…052 | failures | Manual | Not Recommended (automation) | P3 | — | Q-NOTE-1 |

## Step 5b — Selected (draft)

**41 of 52 → 7 TCs**:

| TC | Covers |
|---|---|
| TC-NOTE-001 | empty state → Add note (placeholder, Save disabled → enabled) → Save → "Note added successfully" → the list; the server |
| TC-NOTE-002 | three notes: newest first, date & time format, preview, ⋮, Add note visible |
| TC-NOTE-003 | 500 / 501 and the counter |
| TC-NOTE-004 | edit from ⋮: "Edit note", preloaded, the creation time kept, "Note saved successfully"; the server; leaving without Save warns |
| TC-NOTE-005 | delete from ⋮ (Cancel / Delete) and from "Edit note"; "Note deleted successfully"; the server |
| TC-NOTE-006 | notes after an app restart |
| TC-NOTE-007 | a Submitted job: Notes cannot be opened (read-only) |

**The rest:** 1 skipped (D-NOTE-3), 5 offline (Android stage), 5 failures (Q-NOTE-1).

## Step 9 — Test data

One job per test, In progress (a Submitted one for TC-NOTE-007), deleted after it — the job's notes go with it.

## Step 16 — Recommendation

Owner's word on Q-NOTE-1…3 → recon 10 → test cases → harness (the module 09 page pattern).
