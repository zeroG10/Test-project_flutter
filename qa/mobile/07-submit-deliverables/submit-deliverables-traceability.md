# Automated traceability — mobile

Generated: 2026-09-26 12:41 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/07-submit-deliverables/submit-deliverables-checklist.md` — 33 items
- Results (allure): `automation/mobile/allure-results-07` — 6 tests (5 passed, 0 failed, 1 skipped)

## Run context — the limits of every verdict below

- Target: `iOS simulator iPhone 17 · iOS 26.5 · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true`
- Harness commit (this repo): `20d8ad3`
- Environment label (pytest): `iOS · iPhone 17 · iOS 26.5 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=ios tests/shared/test_submit_deliverables.py (module 07 run 3, 2026-09-26, after the owner moved CHK-DLV-013 / CHK-ORDP-028 to TC-DLV-003; DEV answers POST /job/{id}/submit with 500 — TC-DLV-004 Blocked, Q-DLV-5)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-DLV-001 | Check that the Submit Deliverables confirmation pop-up is displayed when the us… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-002 | Check that the Submit Deliverables pop-up is displayed as a modal dialog above… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-003 | Check that the Submit Deliverables pop-up displays a visual confirmation icon (… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-DLV-004 | Check that the Submit Deliverables pop-up displays the title “Submit deliverabl… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-005 | Check that the warning message “You won’t be able to edit it after submission.”… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-006 | Check that the Submit Deliverables pop-up displays both action buttons: Cancel… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-007 | Check that tapping Cancel closes the pop-up and returns the user to the In Prog… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-008 | Check that tapping Cancel does not trigger any submission request to the backen… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-009 | Check that deliverables remain editable after cancelling the Submit Deliverable… | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | Passed | allure: passed |
| CHK-DLV-010 | Check that tapping Submit triggers validation that all required deliverables ar… | 1 — `tests.shared.test_submit_deliverables#test_incomplete_survey_refused (TC-DLV-002 With the survey not completed, Submit is refused with 'Complete the survey before job submission.'; nothing is submitted)` | Passed | allure: passed |
| CHK-DLV-011 | Check that submission is blocked and an error message is shown when at least on… | 1 — `tests.shared.test_submit_deliverables#test_incomplete_survey_refused (TC-DLV-002 With the survey not completed, Submit is refused with 'Complete the survey before job submission.'; nothing is submitted)` | Passed | allure: passed |
| CHK-DLV-012 | Check that partial submissions are not allowed and the system does not submit o… | 1 — `tests.shared.test_submit_deliverables#test_incomplete_survey_refused (TC-DLV-002 With the survey not completed, Submit is refused with 'Complete the survey before job submission.'; nothing is submitted)` | Passed | allure: passed |
| CHK-DLV-013 | Check that deliverables are locked from further editing immediately after Submi… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-014 | Check that submitted deliverables are marked as read-only after successful subm… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-015 | Check that the user cannot modify Survey, Photo report, or Notes after delivera… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-016 | Check that the application preserves the locked state after leaving and returni… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-017 | Check that confirming Submit initiates deliverables upload to the backend syste… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-018 | Check that a submission progress state is displayed while deliverables are bein… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-019 | Check that the user cannot trigger a second submission while an active submissi… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-020 | Check that a success toast or banner “Deliverables sent to review successfully”… | 1 — `tests.shared.test_submit_deliverables#test_success_reaction (TC-DLV-004 The app's reaction to a successful submission: 'Deliverables sent to review successfully', 'Successful', then Check out, locked at once)` | Blocked | allure: skipped — Skipped: Blocked: DEV answers POST /job/{id}/submit with 500 although the submission is recorded (COPS; owner, Q-DLV-5, 2026-09-26) — the app shows 'Server err… |
| CHK-DLV-021 | Check that the order state is updated to Submitted after successful deliverable… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-022 | Check that the Check out action becomes enabled only after deliverables are suc… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-023 | Check that deliverables submission is prevented when the device is offline. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-DLV-024 | Check that an appropriate offline message is displayed when the user attempts t… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-DLV-025 | Check that deliverables remain stored locally when submission is attempted whil… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-DLV-026 | Check that deliverables are automatically submitted when connectivity is restor… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-DLV-027 | Check that an error message is displayed when deliverables submission fails due… | 1 — `tests.shared.test_submit_deliverables#test_failed_submission_and_retry (TC-DLV-006 A failed submission: 'Job is not found.' with Retry; the job is not submitted; Retry sends it again and nothing is lost)` | Passed | allure: passed |
| CHK-DLV-028 | Check that the user is allowed to retry submission after a failed submission at… | 1 — `tests.shared.test_submit_deliverables#test_failed_submission_and_retry (TC-DLV-006 A failed submission: 'Job is not found.' with Retry; the job is not submitted; Retry sends it again and nothing is lost)` | Passed | allure: passed |
| CHK-DLV-029 | Check that deliverables are not marked as successfully submitted when a submiss… | 1 — `tests.shared.test_submit_deliverables#test_failed_submission_and_retry (TC-DLV-006 A failed submission: 'Job is not found.' with Retry; the job is not submitted; Retry sends it again and nothing is lost)` | Passed | allure: passed |
| CHK-DLV-030 | Check that each submission event records the correct Order ID and User ID. | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-031 | Check that each submission event records a submission timestamp matching the ac… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |
| CHK-DLV-032 | Check that each submission event records deliverables metadata included in the… | 2 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)`; `tests.shared.test_submit_deliverables#test_server_matches_phone_after_submission (TC-DLV-005 After edits and deletions, the server holds after submission exactly the photos and notes left on the phone)` | Passed | allure: passed<br>allure: passed |
| CHK-DLV-033 | Check that each submission event records the correct submission status as Succe… | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | Passed | allure: passed |

**Summary:** total 33 · automated 28 · Passed 27 · Failed 0 · Blocked 1 · Not run 5 (= total − Passed − Failed − Blocked)

## Tagged tests with no checklist item

These CHK IDs appear in test tags but in none of the checklists above — a stale tag, a typo, or a missing `--checklist`. They count for nothing until resolved.

| CHK ID | Tests | Statuses |
|---|---|---|
| CHK-ORDP-019 | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | passed |
| CHK-ORDP-020 | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | passed |
| CHK-ORDP-021 | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | passed |
| CHK-ORDP-022 | 1 — `tests.shared.test_submit_deliverables#test_dialog_and_cancel (TC-DLV-001 The confirmation dialog; Cancel keeps the job In progress, sends nothing, deliverables stay editable)` | passed |
| CHK-ORDP-023 | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | passed |
| CHK-ORDP-024 | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | passed |
| CHK-ORDP-025 | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | passed |
| CHK-ORDP-026 | 1 — `tests.shared.test_submit_deliverables#test_success_reaction (TC-DLV-004 The app's reaction to a successful submission: 'Deliverables sent to review successfully', 'Successful', then Check out, locked at once)` | skipped |
| CHK-ORDP-027 | 1 — `tests.shared.test_submit_deliverables#test_success_reaction (TC-DLV-004 The app's reaction to a successful submission: 'Deliverables sent to review successfully', 'Successful', then Check out, locked at once)` | skipped |
| CHK-ORDP-028 | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | passed |
| CHK-ORDP-038 | 1 — `tests.shared.test_submit_deliverables#test_failed_submission_and_retry (TC-DLV-006 A failed submission: 'Job is not found.' with Retry; the job is not submitted; Retry sends it again and nothing is lost)` | passed |
| CHK-ORDP-039 | 1 — `tests.shared.test_submit_deliverables#test_failed_submission_and_retry (TC-DLV-006 A failed submission: 'Job is not found.' with Retry; the job is not submitted; Retry sends it again and nothing is lost)` | passed |
| CHK-ORDP-041 | 1 — `tests.shared.test_submit_deliverables#test_submission_recorded_and_locked (TC-DLV-003 A completed job is submitted: 'Submitting deliverables' while it runs; the server records the job, the time and every deliverable; the job opened again is Submitted with Check out and locked, also after an app restart)` | passed |

## Notes on this run

- **The CHK-ORDP rows above are not stale.** CHK-ORDP-019…028, -038, -039 and -041 belong to the module 06 checklist; module 06
  handed them over here. Their verdicts are traced in
  [order-progress-traceability.md](../06-order-progress/order-progress-traceability.md), built from module 06 run 3 plus
  this run.
- **Blocked: CHK-DLV-020** (and CHK-ORDP-026, -027), from TC-DLV-004.
  - Why: DEV answers `POST /job/{id}/submit` with 500, although the submission is recorded. The cause is COPS; the owner,
    the backend and the PM know (Q-DLV-5, 2026-09-26).
  - What the test does: it submits, sees "Server error. Try again later." while the server holds the job Submitted, and
    reports `Blocked` — never Passed.
  - What it would take: once the server answers 201, the same test checks the success message and "Successful".
- **CHK-DLV-013 / CHK-ORDP-028** are checked on the job opened again after the submission (TC-DLV-003); on DEV the app
  learns of the submission only then. The owner moved them there from TC-DLV-004 on 2026-09-26.
- **Not run (5):**
  - CHK-DLV-003: the checkmark is not in the accessibility tree; it is seen on the screenshot. Skipped with a comment
    (D-DLV-6).
  - CHK-DLV-023…026: offline, Android stage (Q-DLV-1).
- **Remark D-DLV-7:** delete every photo and note before submission, and the server keeps them after submission. The app
  does not send empty lists. The owner: a remark, no test, no bug.
- **Run history:**
  - Run 1: 4 passed, 2 broken by the harness. Right after the survey Save, the "Survey saved" snackbar took the tap on
    Submit deliverables; the harness now waits for it to leave.
  - Run 2: 5 passed, 1 Blocked.
  - Prove-red (`--prove-red`, harness `afae26c`): 6 of 6 failed, each at its first expected value (the job header).
  - Run 3: 5 passed, 1 Blocked. Only the CHK tags changed since run 2.
