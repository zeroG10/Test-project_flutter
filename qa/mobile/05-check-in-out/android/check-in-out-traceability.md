# Automated traceability — mobile

Generated: 2026-09-30 07:58 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/05-check-in-out/check-in-out-checklist.md` — 41 items
- Results (allure): `automation/mobile/results/android/2026-09-30-05-r2` — 10 tests (9 passed, 1 failed, 0 skipped)

## Run context — the limits of every verdict below

- Target: `Android emulator Pixel 7 · Android 16 (API 36) · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true, debug APK`
- Harness commit (this repo): `b5ae4b4`
- Environment label (pytest): `Android · Pixel_7_API_36 · Android 16 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=android tests/shared/test_check_in_out.py tests/shared/test_order_details.py::test_check_in_starts_flow (module 05 run 2, 2026-09-30; real emulator GPS, no mock switch — Q-CHIO-A1)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-CHIO-001 | Check that the Check-In Confirmation screen is displayed as a full-screen modal… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-002 | Check that the Check-Out Confirmation screen is displayed as a full-screen moda… | 1 — `tests.shared.test_check_in_out#test_check_out_on_site (TC-CHIO-004 On site, check-out from a Submitted job shows its confirmation, and Confirm completes the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-003 | Check that the confirmation modal displays a Close (X) icon that cancels the ac… | 1 — `tests.shared.test_check_in_out#test_check_in_cancelled (TC-CHIO-002 X and Cancel on the check-in confirmation leave the job New)` | Passed | allure: passed |
| CHK-CHIO-004 | Check that the confirmation modal displays a clear title indicating Check-In or… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-005 | Check that the confirmation modal displays a primary message describing the act… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-006 | Check that the confirmation modal displays supporting explanatory text clarifyi… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-007 | Check that the Cancel button aborts the check-in action and closes the confirma… | 1 — `tests.shared.test_check_in_out#test_check_in_cancelled (TC-CHIO-002 X and Cancel on the check-in confirmation leave the job New)` | Passed | allure: passed |
| CHK-CHIO-008 | Check that the Cancel button aborts the check-out action and closes the confirm… | 1 — `tests.shared.test_check_in_out#test_check_out_cancelled (TC-CHIO-005 Cancel on the check-out confirmation keeps the job Submitted)` | Passed | allure: passed |
| CHK-CHIO-009 | Check that tapping the Close (X) icon behaves the same as tapping Cancel. | 1 — `tests.shared.test_check_in_out#test_check_in_cancelled (TC-CHIO-002 X and Cancel on the check-in confirmation leave the job New)` | Passed | allure: passed |
| CHK-CHIO-010 | Check that tapping Confirm on the Check-In screen records the check-in timestam… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-011 | Check that tapping Confirm on the Check-In screen triggers GPS capture when loc… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-012 | Check that the check-in method is flagged as GPS when location is successfully… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-013 | Check that the check-in method is flagged as Manual when GPS is unavailable or… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-014 | Check that the order status is updated to In Progress after successful check-in… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-015 | Check that an email notification is triggered to the Project Facilitator after… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-016 | Check that tapping Confirm on the Check-Out screen records the check-out timest… | 1 — `tests.shared.test_check_in_out#test_check_out_on_site (TC-CHIO-004 On site, check-out from a Submitted job shows its confirmation, and Confirm completes the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-017 | Check that tapping Confirm on the Check-Out screen triggers GPS capture when lo… | 1 — `tests.shared.test_check_in_out#test_check_out_on_site (TC-CHIO-004 On site, check-out from a Submitted job shows its confirmation, and Confirm completes the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-018 | Check that the check-out method is flagged as GPS when location is successfully… | 1 — `tests.shared.test_check_in_out#test_check_out_on_site (TC-CHIO-004 On site, check-out from a Submitted job shows its confirmation, and Confirm completes the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-019 | Check that the check-out method is flagged as Manual when GPS is unavailable or… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-020 | Check that the order status is updated to Completed or the next workflow status… | 1 — `tests.shared.test_check_in_out#test_check_out_on_site (TC-CHIO-004 On site, check-out from a Submitted job shows its confirmation, and Confirm completes the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-021 | Check that an email notification is triggered to the Project Facilitator after… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-022 | Check that initiating Check-In triggers the location permission and validation… | 2 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)`; `tests.shared.test_order_details#test_check_in_starts_flow (TC-ORDD-005 Check in starts the check-in flow; refusing location and cancelling leaves the job New)` | Failed | allure: passed<br>allure: failed — AssertionError: the location prompt shows 'Allow [DEV] CT Mobile to access this device’s location?', without the explanation 'This app needs your location to v… |
| CHK-CHIO-023 | Check that initiating Check-Out triggers the location permission and validation… | 1 — `tests.shared.test_check_in_out#test_check_out_on_site (TC-CHIO-004 On site, check-out from a Submitted job shows its confirmation, and Confirm completes the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-024 | Check that manual Check-In or Check-Out is allowed when GPS permission is denie… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-025 | Check that manual Check-In action іs clearly flagged in the recorded data. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-026 | Check that manual Check-Out action is clearly flagged in the recorded data. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-027 | Check that an error message is displayed if the Check-In operation fails due to… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-028 | Check that an error message is displayed if the Check-Out operation fails due t… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-029 | Check that the user is allowed to retry Check-In after a failed Check-In attemp… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-030 | Check that the user is allowed to retry Check-Out after a failed Check-Out atte… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-031 | Check that the Check-In action does not complete if required data such as times… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-032 | Check that the Check-Out action does not complete if required data such as time… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-033 | Check that each Check-In event stores the correct Order ID and User ID. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-034 | Check that each Check-Out event stores the correct Order ID and User ID. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-035 | Check that the recorded action type is correctly stored as Check-In or Check-Ou… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-036 | Check that the recorded timestamp reflects the actual confirmation time of the… | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-037 | Check that GPS coordinates are stored when location is enabled and available. | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | Passed | allure: passed |
| CHK-CHIO-038 | Check that the confirmation modal remains responsive during slow GPS acquisitio… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-CHIO-039 | Check that multiple rapid taps on the Confirm button do not trigger duplicate C… | 1 — `tests.shared.test_check_in_out#test_confirm_double_tap (TC-CHIO-007 Two quick taps on Confirm start the job once)` | Passed | allure: passed |
| CHK-CHIO-040 | Check that the user cannot initiate Check-In or Check-Out actions that are inva… | 1 — `tests.shared.test_check_in_out#test_actions_per_status (TC-CHIO-006 Each status offers only its own action: New → Check in, In progress → none, Submitted → Check out)` | Passed | allure: passed |
| CHK-CHIO-041 | Check that check-in is refused with the "Location could not be trusted" message… | 1 — `tests.shared.test_check_in_out#test_mock_location_refused (TC-CHIO-008 Without the switch, a simulated location is refused with 'Location could not be trusted' and the job stays New)` | Passed | allure: passed |

**Summary:** total 41 · automated 25 · Passed 24 · Failed 1 · Blocked 0 · Not run 16 (= total − Passed − Failed − Blocked)

## Tagged tests with no checklist item

These CHK IDs appear in test tags but in none of the checklists above — a stale tag, a typo, or a missing `--checklist`. They count for nothing until resolved.

| CHK ID | Tests | Statuses |
|---|---|---|
| CHK-ORDD-022 | 1 — `tests.shared.test_order_details#test_check_in_starts_flow (TC-ORDD-005 Check in starts the check-in flow; refusing location and cancelling leaves the job New)` | failed |
| CHK-ORDD-024 | 1 — `tests.shared.test_order_details#test_check_in_starts_flow (TC-ORDD-005 Check in starts the check-in flow; refusing location and cancelling leaves the job New)` | failed |
| CHK-ORDD-027 | 1 — `tests.shared.test_order_details#test_check_in_starts_flow (TC-ORDD-005 Check in starts the check-in flow; refusing location and cancelling leaves the job New)` | failed |
| CHK-ORDD-028 | 1 — `tests.shared.test_check_in_out#test_go_to_settings (TC-CHIO-009 After refusing location, 'Go to settings' opens the device settings)` | passed |
| CHK-ORDD-030 | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | passed |
| CHK-ORDD-031 | 1 — `tests.shared.test_check_in_out#test_check_in_away (TC-CHIO-003 Away from the site, check-in is stopped with 'You are not at the job site'; Got it and Cancel leave the job New)` | passed |
| CHK-ORDD-032 | 1 — `tests.shared.test_check_in_out#test_check_in_away (TC-CHIO-003 Away from the site, check-in is stopped with 'You are not at the job site'; Got it and Cancel leave the job New)` | passed |
| CHK-ORDD-033 | 1 — `tests.shared.test_check_in_out#test_check_in_away (TC-CHIO-003 Away from the site, check-in is stopped with 'You are not at the job site'; Got it and Cancel leave the job New)` | passed |
| CHK-ORDD-034 | 1 — `tests.shared.test_check_in_out#test_check_in_away (TC-CHIO-003 Away from the site, check-in is stopped with 'You are not at the job site'; Got it and Cancel leave the job New)` | passed |
| CHK-ORDD-035 | 1 — `tests.shared.test_check_in_out#test_check_in_away (TC-CHIO-003 Away from the site, check-in is stopped with 'You are not at the job site'; Got it and Cancel leave the job New)` | passed |
| CHK-ORDD-044 | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | passed |
| CHK-ORDD-045 | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | passed |
| CHK-ORDD-046 | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | passed |
| CHK-ORDD-047 | 1 — `tests.shared.test_check_in_out#test_check_in_on_site (TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record)` | passed |

> **Resolved (2026-09-30):**
> - **CHK-CHIO-022 is Failed only because it is tagged on TC-ORDD-005**, which fails at its last step, CHK-ORDD-024
>   ([Q-ORDD-A4](../../04-order-details/android/order-details-questions.md): the Android prompt carries no explanation
>   from the app). The CHK-CHIO-022 step itself — after Check in the location permission flow starts (the system
>   prompt appears) — **passed** in this run. The verdict above is the tool's and is not edited.
> - Every check-in / check-out test passes on Android with the emulator's real GPS fixes and **without** the app's
>   mock-location switch (Q-CHIO-A1); the mock-location guard (TC-CHIO-008) is proven with a real mock provider.
>   TC-CHIO-009 reaches "Go to settings" after two refusals on Android (the first one may still be asked again —
>   "Location access required", D-CHIO-A3).
> - Orphans: CHK-ORDD-* belong to module 04 (`04-order-details/android/`, traced from the module 04 and 05 runs
>   together, as on iOS).

