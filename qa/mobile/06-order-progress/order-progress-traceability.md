# Automated traceability — mobile

Generated: 2026-09-24 12:44 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/06-order-progress/order-progress-checklist.md` — 42 items
- Results (allure): `automation/mobile/allure-results-06` — 6 tests (5 passed, 0 failed, 1 skipped)

## Run context — the limits of every verdict below

- Target: `iOS simulator iPhone 17 · iOS 26.5 · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true`
- Harness commit (this repo): `b05cc3e`
- Environment label (pytest): `iOS · iPhone 17 · iOS 26.5 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=ios tests/shared/test_order_progress.py (module 06 run 3, 2026-09-24; {{job.progress}} checked in through the UI with the mock-location switch ON, OFF after)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-ORDP-001 | Check that the Order Details screen displays the “In progress” status badge whe… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-002 | Check that the elapsed time counter is displayed in HH:MM:SS format and updates… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-003 | Check that the elapsed time counter continues correctly after the app is minimi… | 1 — `tests.shared.test_order_progress#test_timer_after_background (TC-ORDP-002 The timer keeps counting while the app is in the background)` | Passed | allure: passed |
| CHK-ORDP-004 | Check that the Deliverables section displays three tappable items: Survey, Phot… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-005 | Check that each deliverable row displays an icon and a navigation chevron indic… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-006 | Check that tapping Survey navigates to the Survey data entry screen from the In… | 1 — `tests.shared.test_order_progress#test_deliverables_open_their_screens (TC-ORDP-003 Survey, Photo report and Notes open their screens and come back)` | Passed | allure: passed |
| CHK-ORDP-007 | Check that tapping Photo report navigates to the Photo report data entry screen… | 1 — `tests.shared.test_order_progress#test_deliverables_open_their_screens (TC-ORDP-003 Survey, Photo report and Notes open their screens and come back)` | Passed | allure: passed |
| CHK-ORDP-008 | Check that tapping Notes navigates to the Notes data entry screen from the In P… | 1 — `tests.shared.test_order_progress#test_deliverables_open_their_screens (TC-ORDP-003 Survey, Photo report and Notes open their screens and come back)` | Passed | allure: passed |
| CHK-ORDP-009 | Check that each deliverable displays a completion state indicator in the In Pro… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-010 | Check that the job scope text is displayed as multi-line instructions under the… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-011 | Check that the Location section displays site name and City, State information… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-012 | Check that the “On map” link is displayed in the Location section and is tappab… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-013 | Check that tapping “On map” opens an external maps application with the correct… | 1 — `tests.shared.test_order_progress#test_on_map_in_progress (TC-ORDP-004 'On map' on the In progress screen opens the job's location)` | Passed | allure: passed |
| CHK-ORDP-014 | Check that the Date & time section displays the scheduled date and time in the… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-015 | Check that the PF info section displays the PF name and a tappable phone number… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-016 | Check that tapping the PF phone number opens the device dialer with the number… | 1 — `tests.shared.test_order_progress#test_pf_phone_in_progress (TC-ORDP-006 The PF phone on the In progress screen opens the dialer)` | Blocked | allure: skipped — Skipped: Blocked: iOS simulator limitation — there is no Phone app, the tap cannot open a dialer (owner, 2026-09-24, as Q-ORDD-3). Runs in full on the Android… |
| CHK-ORDP-017 | Check that the Attachments row is displayed and navigates to the Attachments sc… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-018 | Check that the primary action button displays “Submit deliverables” when delive… | 1 — `tests.shared.test_order_progress#test_in_progress_screen (TC-ORDP-001 A checked-in job shows the In progress screen: status, running timer, deliverables, info and 'Submit deliverables')` | Passed | allure: passed |
| CHK-ORDP-019 | Check that tapping “Submit deliverables” displays a confirmation modal titled “… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-020 | Check that the confirmation modal informs the user they won’t be able to edit d… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-021 | Check that the confirmation modal displays both Cancel and Submit actions. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-022 | Check that tapping Cancel closes the confirmation modal without submitting deli… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-023 | Check that tapping Submit triggers deliverables submission to the backend and p… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-024 | Check that a “Submitting deliverables” progress state is displayed while submis… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-025 | Check that the Submit deliverables button is disabled while submission is in pr… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-026 | Check that a success toast “Deliverables sent to review successfully” is displa… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-027 | Check that the primary action area displays a success state label (e.g., “Succe… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-028 | Check that the primary action button changes to “Check out” after deliverables… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-029 | Check that the Submit deliverables button is disabled when the device is offlin… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-030 | Check that an offline informational message is displayed when the device is off… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-031 | Check that deliverables progress is saved locally while offline and remains ava… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-032 | Check that deliverables are automatically synced or submitted when connectivity… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-033 | Check that a “Connection restored” modal is displayed when network connectivity… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-034 | Check that the “Connection restored” modal lists the unfinished job name(s) and… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-035 | Check that the “Connection restored” modal provides Cancel and Submit actions. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-036 | Check that tapping Cancel closes the modal without submitting pending deliverab… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-037 | Check that tapping Submit starts deliverables submission for the listed unfinis… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-038 | Check that an error message is displayed when deliverables submission fails due… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-039 | Check that the user can retry submission after a deliverables submission failur… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-040 | Check that locally stored deliverables are preserved and retried automatically… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-041 | Check that deliverables cannot be edited after successful submission if the con… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDP-042 | Check that returning to the In Progress screen preserves the correct primary ac… | 1 — `tests.shared.test_order_progress#test_primary_action_follows_status (TC-ORDP-005 The primary action follows the status after leaving and reopening; a Submitted job's deliverables are read-only)` | Passed | allure: passed |

**Summary:** total 42 · automated 18 · Passed 17 · Failed 0 · Blocked 1 · Not run 24 (= total − Passed − Failed − Blocked)
