# Test cases — Submit deliverables (mobile)

> Structured, alias-based test cases for the CHK IDs selected in [submit-deliverables-automation-plan.md](submit-deliverables-automation-plan.md).
> Format: [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: automated and traced on iOS (run 2, 2026-09-26: 5 Passed, 1 Blocked — TC-DLV-004, Q-DLV-5); the owner sees
> them with the results. Written after recon 11 ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md)) and the
> owner's decisions of 2026-09-26: D-DLV-1…7, Q-DLV-1…6 — [submit-deliverables-questions.md](submit-deliverables-questions.md).**

| Field | Value |
|---|---|
| Feature | Submitting the deliverables of an In progress job: the confirmation dialog, Cancel, the survey check, the submission, the server record, the lock after submission, the photos and notes the server holds, a failed submission and Retry |
| Source checklist | `qa/mobile/07-submit-deliverables/submit-deliverables-checklist.md` (CHK-DLV-001…033) + CHK-ORDP-019…028, -038, -039, -041 (module 06) |
| Devices / build | iPhone 17 · iOS 26.5 (simulator) · `[DEV] CT Mobile` 1.1.1 (178), `CLIENT_BUILD=true` · online |
| Owner | @mykola.zhuchenko · Last updated 2026-09-26 |

**Conventions**

- **One job per test.** Created through `POST /job` directly In progress with the Short Survey (fixture `survey_job`),
  deleted after the test.
- **Completing the survey:** `survey.yes[1]` → `survey.text[1]` `QA-AUTO <case> answer` → `survey.save`. Afterwards the
  harness waits for the "Survey saved" snackbar to go; it covers `job-details.submit-deliverables`.
- **DEV and COPS (Q-DLV-5):** on DEV, `POST /job/{id}/submit` answers 500. By then the submission is already recorded:
  the job is Submitted on the server.
  - The app shows "Server error. Try again later." and keeps the job In progress until it is opened again.
  - Every test below checks the server and the reopened job; none checks that error.
  - The app's reaction to a *successful* answer is TC-DLV-004. The test detects the 500 itself and reports it as
    `Blocked`.
- **Submitted on the server** = `GET /job/{id}` → `statusType` `submitted`, `submissionDate` set (`api.job`).
- **The job opened again** = `job-details` pulled to refresh.

---

## TC-DLV-001 — The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable

| Field | Value |
|---|---|
| Source CHK IDs | CHK-DLV-001, -002, -004, -005, -006, -007, -008, -009 · CHK-ORDP-019, -020, -021, -022 |
| Priority | P0 · smoke |
| Preconditions | `{{job.progress}}` In progress, details open |
| Oracle | spec — SRS §3.1.3.4.1 (dialog texts, FR-SUB-01, -02); code `submit_deliverables_dialog.dart`; recon 11 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.submit-deliverables | — | — |
| 2 | expect-visible | submit-dialog.title | — | "Submit deliverables" |
| 3 | expect-text | submit-dialog.message | — | "You won't be able to edit it after submission." |
| 4 | expect-visible | submit-dialog.cancel | — | — |
| 5 | expect-visible | submit-dialog.submit | — | — |
| 6 | expect-visible | submit-dialog.layer | — | covers the whole window; job-details.header not reachable (modal) |
| 7 | click | submit-dialog.cancel | — | the dialog closes; job-details.header, status "In progress", job-details.submit-deliverables |
| 8 | expect-text | api.job | — | `in_progress`, no `submissionDate` |
| 9 | click | job-details.deliverable[Notes] | then notes.add-note `QA-AUTO after cancel`, Save | the note in the list (still editable) |

## TC-DLV-002 — With the survey not completed, Submit is refused with "Complete the survey before job submission."; nothing is submitted

| Field | Value |
|---|---|
| Source CHK IDs | CHK-DLV-010, -011, -012 |
| Priority | P0 |
| Preconditions | `{{job.progress}}` In progress, the survey untouched |
| Oracle | spec — FR-SUB-03, -07 (the message text), -08; D-DLV-1 (the button is active, the check comes after Submit) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.submit-deliverables | then submit-dialog.submit | — |
| 2 | expect-text | job-details.message | — | "Complete the survey before job submission." |
| 3 | expect-visible | job-details.submit-deliverables | — | the job stays In progress, no job-details.check-out |
| 4 | expect-text | api.job | — | `in_progress`, no `submissionDate`, no survey response |

## TC-DLV-003 — A completed job is submitted: "Submitting deliverables" while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart

| Field | Value |
|---|---|
| Source CHK IDs | CHK-DLV-013, -014, -015, -016, -017, -018, -019, -021, -022, -030, -031, -032, -033 · CHK-ORDP-023, -024, -025, -028, -041 |
| Priority | P0 · smoke |
| Preconditions | `{{job.progress}}` In progress; `gallery_photos` |
| Oracle | spec — FR-SUB-03 … -05, FR-IP-07; the submission record (D-DLV-4); recon 11. CHK-DLV-013 / CHK-ORDP-028 (locked, Check out after the submission) are checked on the job opened again — on DEV the app learns of the submission only then (Q-DLV-5); moved here from TC-DLV-004 by the owner, 2026-09-26 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-hidden | job-details.check-out | — | no Check out before the submission |
| 2 | click | survey.yes[1] | then survey.text[1] `QA-AUTO submit answer`, survey.save | — |
| 3 | click | job-details.deliverable[Photo report] | the gallery flow, cell 1, `QA-AUTO submit photo`, Save; back | — |
| 4 | click | job-details.deliverable[Notes] | `QA-AUTO submit note`, Save; back | — |
| 5 | click | job-details.submit-deliverables | then submit-dialog.submit | job-details.submitting "Submitting deliverables", disabled |
| 6 | expect-text | api.job | — | `submitted`; `submissionDate` within the seconds of the tap; `user` = the technician; the survey answers (Yes, `QA-AUTO submit answer`); photos: `QA-AUTO submit photo`; notes: `QA-AUTO submit note` |
| 7 | swipe | job-details.root | down (refresh) | status "Submitted"; job-details.check-out enabled; no job-details.submit-deliverables |
| 8 | click | job-details.deliverable[Survey] | — | the survey does not open (3 s) |
| 9 | click | job-details.deliverable[Photo report] | — | the photo report does not open (3 s) |
| 10 | click | job-details.deliverable[Notes] | — | the notes do not open (3 s) |
| 11 | open | app | terminate + launch → the job | status "Submitted", Check out; job-details.deliverable[Survey] still does not open |

## TC-DLV-004 — The app's reaction to a successful submission: "Deliverables sent to review successfully", "Successful", then Check out, locked at once

| Field | Value |
|---|---|
| Source CHK IDs | CHK-DLV-020 · CHK-ORDP-026, -027 |
| Priority | P1 |
| Preconditions | `{{job.progress}}` In progress, the survey completed |
| Oracle | spec — SRS §3.1.3.4.1 (success notification), FR-SUB-04, FR-IP-07; code `job_detail_content.dart` ("Successful" 1.5 s); D-DLV-2 |
| Environment | **`Blocked` on DEV** (Q-DLV-5, owner 2026-09-26). `POST /job/{id}/submit` answers 500 because of COPS; the backend and the PM know. The test submits. If the app then shows job-details.message "Server error. Try again later." while the server holds the job Submitted, the test is reported `Blocked` with that reason. Once the server answers 201, the rows below are checked. |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.submit-deliverables | then submit-dialog.submit | — |
| 2 | expect-text | job-details.message | — | "Deliverables sent to review successfully" |
| 3 | expect-visible | job-details.successful | — | "Successful" (about 1.5 s) |
| 4 | expect-visible | job-details.check-out | — | then Check out; no job-details.submit-deliverables |
| 5 | click | job-details.deliverable[Survey] | — | the survey does not open |

## TC-DLV-005 — After edits and deletions, the server holds after submission exactly the photos and notes left on the phone

| Field | Value |
|---|---|
| Source CHK IDs | CHK-DLV-032 |
| Priority | P0 |
| Preconditions | `{{job.progress}}` In progress; `gallery_photos` |
| Oracle | spec — FR-SUB (deliverables metadata: Photo report, Notes), FR-PH-M-09, FR-NOT-06, -08; the owner's request after modules 09 / 10 (2026-09-26); recon 11 (а) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.yes[1] | then survey.text[1] `QA-AUTO edits answer`, survey.save | — |
| 2 | click | photo-report.add-photo | `QA-AUTO photo A` (cell 1), then `QA-AUTO photo B` (cell 0) | 2 photos |
| 3 | click | photo-report.photo[QA-AUTO photo A] | append ` edited`, Save | — |
| 4 | click | photo-report.delete[QA-AUTO photo B] | then photo-delete-dialog.delete | 1 photo: `QA-AUTO photo A edited` |
| 5 | click | notes.add-note | `QA-AUTO note A`, then `QA-AUTO note B` | 2 notes |
| 6 | click | notes.menu[QA-AUTO note A] | Edit, append ` edited`, Save | — |
| 7 | click | notes.menu[QA-AUTO note B] | Delete, Delete | 1 note: `QA-AUTO note A edited` |
| 8 | click | job-details.submit-deliverables | then submit-dialog.submit | — |
| 9 | expect-text | api.job | — | `submitted`; photos: exactly `QA-AUTO photo A edited`; notes: exactly `QA-AUTO note A edited` |

## TC-DLV-006 — A failed submission: "Job is not found." with Retry; the job is not submitted; Retry sends it again and nothing is lost

| Field | Value |
|---|---|
| Source CHK IDs | CHK-DLV-027, -028, -029 · CHK-ORDP-038, -039 |
| Priority | P1 |
| Preconditions | `{{job.progress}}` In progress, the survey completed |
| Oracle | spec — FR-IP-11, FR-SUB-07 (error, retry); D-DLV-5 (the message for a cancelled job); Q-DLV-2 (the failure made on the server); recon 11 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | set | api.job | `statusType` `canceled` (`PATCH /job/{id}`) | — |
| 2 | click | job-details.submit-deliverables | then submit-dialog.submit | job-details.message "Job is not found."; job-details.retry |
| 3 | expect-visible | job-details.submit-deliverables | — | the app keeps the job In progress; no Check out |
| 4 | expect-text | api.job | — | `canceled`, no `submissionDate` (not submitted) |
| 5 | set | api.job | `statusType` `in_progress` | — |
| 6 | click | job-details.retry | — | job-details.submitting "Submitting deliverables" (sent again) |
| 7 | expect-text | api.job | — | `submitted`; the survey answers kept |

## Aliases used

| Alias | ios map |
|---|---|
| job-details.submit-deliverables, .check-out, .status, .deliverable, .header, .root | yes (modules 04–06) |
| job-details.submitting, .successful, .message, .retry | `screens/job_details_map.py` (recon 11) |
| submit-dialog.* | `screens/submit_dialog_map.py` (recon 11) |
| survey.*, photo-report.*, photo-metadata.*, notes.*, note-*.* | modules 08 / 09 / 10 |
| api.job | not an element — `GET /job/{id}` (read) and `PATCH /job/{id}` (TC-DLV-006, the test's own job) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-DLV-001, -002, -004…-009 · CHK-ORDP-019…-022 | TC-DLV-001 | |
| CHK-DLV-010…-012 | TC-DLV-002 | |
| CHK-DLV-013…-019, -021, -022, -030…-033 · CHK-ORDP-023…-025, -028, -041 | TC-DLV-003 | -013 / ORDP-028 on the job opened again (owner, 2026-09-26) |
| CHK-DLV-020 · CHK-ORDP-026, -027 | TC-DLV-004 | `Blocked` on DEV (Q-DLV-5) |
| CHK-DLV-032 | TC-DLV-003, TC-DLV-005 | all deleted → D-DLV-7 (remark, no test) |
| CHK-DLV-027…-029 · CHK-ORDP-038, -039 | TC-DLV-006 | |

**Not here:**
- CHK-DLV-003 (the checkmark icon) — skipped with a comment: not in the accessibility tree, seen on the screenshot (D-DLV-6).
- CHK-DLV-023…-026 — offline, Android stage (Q-DLV-1).
