# Automation plan — Submit deliverables (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/07-submit-deliverables/submit-deliverables-checklist.md`
> (33 items, `CHK-DLV-001…033`, imported 2026-09-26). The 13 checks handed over by module 06 are planned here too:
> CHK-ORDP-019…028, -038, -039, -041 (see [order-progress-automation-plan.md](../06-order-progress/order-progress-automation-plan.md)).
> Date: 2026-09-26. Owner: mykola.zhuchenko.
> **Status: accepted by the owner 2026-09-26 (D-DLV-1…4 accepted, Q-DLV-1…4 closed, recon 11 allowed) —
> [submit-deliverables-questions.md](submit-deliverables-questions.md).**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| Feature code | `DLV` (+ `ORDP` for the handed-over checks) |
| Scope decision (proposed) | the "Submit deliverables" dialog, Cancel, the survey check, the submission and its states, the lock after submission, the server record, and what the server holds for photos and notes after submission (the owner's request, 2026-09-26); offline → Android stage; failures — only if recon 11 finds a safe server-side trigger (Q-DLV-2) |
| Oracle model | accepted production baseline; SRS §3.1.3.4 (FR-IP-05…12), §3.1.3.4.1 (FR-SUB-01…08); the job on the server (`GET /job/{id}` → `statusType`, `submissionDate`, `surveyResponse`, `photos`, `notes`; `GET /job/{id}/submission`) |
| App code read | `job_details_page.dart`, `job_detail_content.dart`, `submit_deliverables_dialog.dart`, `job_detail_bloc.dart`, `job_detail_repository_impl.dart`, `job_api_service.dart` (read only, `development` @ 85a84f3) |

**How the app submits (code):**
1. Submit deliverables → the dialog → Submit.
2. The app re-reads the job.
3. It checks the survey is complete; if not: "Complete the survey before job submission." and nothing is sent.
4. It checks the device is online.
5. It uploads the survey photos.
6. It calls `POST /job/{id}/response` with:
   - `response`: the survey;
   - `photoIds`: the photos left on the phone, **only if there is at least one**;
   - `notes`: every note left, with its current text, **only if there is at least one**.
7. It calls `POST /job/{id}/submit`.

While this runs, the button reads "Submitting deliverables" and is disabled. On success:
- "Successful" shows for 1.5 s, then "Check out";
- a snackbar says "Deliverables sent to review successfully".

On a failure, a red snackbar with Retry.

## Step 3–4 — Candidate matrix (33 + 13 items)

| CHK ID | Scenario (short) | Level | Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|
| CHK-DLV-001, -004…-006 · CHK-ORDP-019…021 | the dialog opens: title, "You won't be able to edit it after submission.", Cancel, Submit | E2E UI | Good Candidate | P0 | TC-DLV-001 | code: `submit_deliverables_dialog.dart` |
| CHK-DLV-002, -003 | the dialog is modal over a dimmed screen; the checkmark icon | E2E UI | After recon | P3 | TC-DLV-001 | visual; automated only if the tree shows them (Q-DLV-4), else skipped with a comment |
| CHK-DLV-007…-009 · CHK-ORDP-022 | Cancel: back on the job, nothing sent (server still In progress, no `submissionDate`), deliverables still editable | E2E UI + API | Good Candidate | P0 | TC-DLV-001 | |
| CHK-DLV-010…-012 | Submit with an incomplete survey: refused with "Complete the survey before job submission."; nothing submitted (no partial submission) | E2E UI + API | Good Candidate | P0 | TC-DLV-002 | D-DLV-1 (the button is active; the check comes after Submit) |
| CHK-DLV-017, -020…-022 · CHK-ORDP-023, -026, -028 | Submit: sent; "Deliverables sent to review successfully"; the job Submitted; Check out appears (not before) | E2E UI + API | Good Candidate | P0 | TC-DLV-003 | |
| CHK-DLV-018, -019 · CHK-ORDP-024, -025, -027 | "Submitting deliverables", the button disabled while it runs, "Successful" for 1.5 s | E2E UI | After recon | P2 | TC-DLV-003 | brief states; automated only if recon 11 shows they can be caught reliably, else manual (D-DLV-2) |
| CHK-DLV-030…-033 | the server record: the job and technician, `submissionDate` ≈ the tap, the survey / photos / notes, status Submitted | API | Good Candidate | P1 | TC-DLV-003 | D-DLV-4 (no separate "event" record) |
| CHK-DLV-013…-016 · CHK-ORDP-041 | locked after submission: Survey, Photo report and Notes do not open, also after leaving the job and after an app restart | E2E UI | Good Candidate | P0 | TC-DLV-004 | as TC-SRV-016 / TC-NOTE-007, but on a job submitted through the app |
| CHK-DLV-032 | the photos and notes on the server after submission match the phone after add / edit / delete | E2E UI + API | Good Candidate | P0 | TC-DLV-005 | the owner's request (modules 09 / 10) |
| CHK-DLV-032 | every photo and note deleted before submission → none on the server | E2E UI + API | Good Candidate | P0 | TC-DLV-006 | code: the lists are not sent when empty — Q-DLV-3 |
| CHK-DLV-027…-029 · CHK-ORDP-038, -039 | a failed submission: error, Retry, not marked submitted, data kept | E2E UI + API | After recon | P2 | TC-DLV-007 | a failure only from the server side (Q-DLV-2); otherwise skipped with a comment |
| CHK-DLV-023…-026 | offline: submission blocked, message, data kept, sent when back online | Manual (Android stage) | Needs Device | P2 | — | Q-DLV-1; D-DLV-3 (no automatic submission) |

## Step 5b — Selected (draft)

**Certain: 30 of 46 → 6 TCs.** Of these, 22 are DLV and 8 are ORDP. Up to 12 more after recon 11, in two groups:
- CHK-DLV-002, -003, -018, -019 and CHK-ORDP-024, -025, -027;
- TC-DLV-007.

| TC | Covers |
|---|---|
| TC-DLV-001 | the dialog; Cancel keeps the job In progress; nothing on the server; a note can still be added |
| TC-DLV-002 | the survey not complete → "Complete the survey before job submission."; the server unchanged |
| TC-DLV-003 | a completed survey + a photo + a note → Submit → success message, Check out; the server: Submitted, `submissionDate`, the technician, survey / photo / note |
| TC-DLV-004 | after submission: Survey, Photo report, Notes locked; still locked after leaving the job and after an app restart |
| TC-DLV-005 | 2 photos + 2 notes → edit one of each, delete one of each → Submit → the server holds exactly the one photo (edited description) and the one note (edited text) |
| TC-DLV-006 | a photo and a note added, then all deleted → Submit → the server holds no photos and no notes |
| TC-DLV-007 *(if recon 11 allows)* | a failed submission → error with Retry; still In progress; fixed → Retry succeeds, nothing lost |

**The rest:** 4 offline (Android stage).

## Step 9 — Test data

- One job per test, created through `POST /job` directly In progress with the *Short Survey* (2 questions: Yes/No and
  text). The fixture is `survey_job("short")`; the job is deleted after the test.
- TC-DLV-005 / -006 use the gallery photos (fixture `gallery_photos`).
- Whether the server accepts `POST /job/{id}/submit` on a job that was never checked in is checked in recon 11. If it
  does not, the jobs go through a check-in in the UI (fixture `in_progress_job`, module 06).

## Step 16 — Recommendation

Owner's word on the questions → recon 11 → test cases → harness. The harness reuses the module 06 / 08 / 09 / 10 pages:
job details, survey, photo report, notes.
