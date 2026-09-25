# Automation plan — Photo report (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/09-photo-report/photo-report-checklist.md`
> (54 items, `CHK-PHR-001…054`, imported 2026-09-24). Date: 2026-09-24. Owner: mykola.zhuchenko.
> **Status: accepted by the owner 2026-09-25 (Q-PHR-2…5 closed; Q-PHR-1 checked in recon 9, validated by the owner) —
> [photo-report-questions.md](photo-report-questions.md).**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| Feature code | `PHR` |
| Scope decision (proposed) | the Photo report screen of an In progress job: empty / populated states, add from the gallery, description and tags, edit, delete, persistence, the server copy; camera, crop / markup details, offline and failures → manual / Android stage (Q-PHR-2…4) |
| Oracle model | accepted production baseline; SRS §3.1.3.4.3–4 (FR-PH, FR-PH-M, FR-DEL-PH); recon 7 / 8 / 9; the job on the server (`GET /job/{id}`) |

## Step 0–2 — Input, readiness, approach

**Input: Medium.**
- Known from code and recon 8: the empty state, the gallery picker, the editor (Crop / Markup, ✓), the "Add photo" page (description 500, tags from the server).
- Unknown until recon 9: the grid of the Photo report, "Edit photo", the delete dialog, and where the job's photos show on the server.

**Readiness:** Ready with conditions (Q-PHR-1…5).

**Approach:**
- One job per test, created directly In progress; the timer is not asserted.
- Photos come from the simulator gallery.
- Every change is checked on the screen and then on the server.

## Step 3–4 — Candidate matrix (54 items)

| CHK ID | Scenario (short) | Level | Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|
| CHK-PHR-001…005 | opens from In progress; title, back; empty state + "Add photo" starts the flow | E2E UI | Good Candidate | P0 | TC-PHR-001 | recon 7 |
| CHK-PHR-006…008 | populated: grid of thumbnails, description snippet, Add photo still there | E2E UI | Good Candidate | P1 | TC-PHR-001, -003 | recon 9 |
| CHK-PHR-009 | bottom sheet Camera / Gallery | E2E UI | Good Candidate | P1 | TC-PHR-001 | code |
| CHK-PHR-010 | camera | Manual | Needs Device | P2 | — | no camera on the simulator (Q-PHR-2) |
| CHK-PHR-011, -012 | gallery → the editor / "Add photo" | E2E UI | Good Candidate | P0 | TC-PHR-001 | recon 8 |
| CHK-PHR-013…015 | "Add photo" / "Edit photo" title, preview, back | E2E UI | Good Candidate | P1 | TC-PHR-001, -004 | |
| CHK-PHR-016…024 | crop, markup, palette, stroke, undo / redo | Manual (owner) | Not Recommended (automation) | P3 | TC-PHR-007 (opens only) | TD-PHOTO-001 (Q-PHR-3) |
| CHK-PHR-025…028 | description multi-line, 500, counter, optional | E2E UI | Good Candidate | P1 | TC-PHR-002 | |
| CHK-PHR-029…032 | tags: chips from the server, multi-select, selected state, deselect | E2E UI + API | Good Candidate | P1 | TC-PHR-002 | tags = DEV tag list |
| CHK-PHR-033…035 | Save persists, returns, appears at once | E2E UI + API | Good Candidate | P0 | TC-PHR-001 | + the server copy |
| CHK-PHR-036 | edit preloads | E2E UI | Good Candidate | P1 | TC-PHR-004 | |
| CHK-PHR-037, -038 | back without Save discards; warning | E2E UI | Good Candidate | P1 | TC-PHR-004 | "Unsaved Changes" (D-PHR-3) |
| CHK-PHR-039…044 | delete: dialog, Cancel keeps, Delete removes, grid updates | E2E UI + API | Good Candidate | P0 | TC-PHR-005 | server side — Q-PHR-1 |
| CHK-PHR-045…050 | offline | Manual (Android stage) | Needs Device | P2 | — | Q-PHR-4 |
| CHK-PHR-051…054 | failures: upload, editing, save, retry | Manual | Not Recommended (automation) | P3 | — | Q-PHR-4 |

## Step 5b — Selected (draft)

**34 of 54 → 7 TCs**:

| TC | Covers |
|---|---|
| TC-PHR-001 | empty state → Add photo → Camera / Gallery → gallery → editor → "Add photo" (empty fields, 0 / 500) → Save → the grid with the photo and its snippet; the server has it |
| TC-PHR-002 | description 500 / 501 + counter; tags: several selected, one deselected → saved as chosen (screen + server) |
| TC-PHR-003 | several photos: 3 in the grid, "Add photo" still available |
| TC-PHR-004 | edit: "Edit photo" preloaded → change → Save → grid updated; back without Save → "Unsaved Changes" → Leave → unchanged |
| TC-PHR-005 | delete: dialog title / message → Cancel keeps → Delete removes → grid / empty state; the server (Q-PHR-1) |
| TC-PHR-006 | photos and metadata after an app restart |
| TC-PHR-007 | the editor opens with Crop and Markup; ✓ leads to "Add photo" (the rest manual, TD-PHOTO-001) |

**The rest:**
- 10 manual (camera, crop / markup);
- 6 offline, Android stage;
- 4 failures — manual or skipped (Q-PHR-2…4).

## Step 9 — Test data

- **Jobs:** one job per test, In progress, deleted after it.
- **Photos:** from the simulator gallery (`gallery_photos`, as module 08). Uploaded files stay in DEV storage (accepted).
- **Tags:** the DEV tag list, read-only.

## Step 16 — Recommendation

Owner's word on Q-PHR-1…5 → recon 9 → test cases → harness (reuses the module 08 photo flow: picker, editor, metadata).
