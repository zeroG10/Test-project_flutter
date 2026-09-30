# Automated traceability — mobile

Generated: 2026-09-30 06:57 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/01-splash/splash-checklist.md` — 15 items
- Results (allure): `automation/mobile/results/android/2026-09-30-0103-r6` — 20 tests (15 passed, 5 failed, 0 skipped)

## Run context — the limits of every verdict below

- Target: `Android emulator Pixel 7 · Android 16 (API 36) · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true, debug APK`
- Harness commit (this repo): `4de7949`
- Environment label (pytest): `Android · Pixel_7_API_36 · Android 16 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=android tests/shared/test_splash.py tests/shared/test_order_list.py tests/shared/test_authentication.py::test_login_with_email (run 6, 2026-09-30)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-SPL-001 | Check that the Splash Screen is displayed immediately after application launch… | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | Failed | allure: failed — AssertionError: a back on the splash changes nothing: the app left the foreground (app state 3, 4 = foreground) |
| CHK-SPL-002 | Check that the Splash Screen is displayed as a full-screen view with a white ba… | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | Failed | allure: failed — AssertionError: a back on the splash changes nothing: the app left the foreground (app state 3, 4 = foreground) |
| CHK-SPL-003 | Check that the Concert Technologies logo is displayed centered both vertically… | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | Failed | allure: failed — AssertionError: a back on the splash changes nothing: the app left the foreground (app state 3, 4 = foreground) |
| CHK-SPL-004 | Check that the logo on the Splash Screen is static and does not include any ani… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-SPL-005 | Check that no text labels, buttons, links, or input fields are displayed on the… | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | Failed | allure: failed — AssertionError: a back on the splash changes nothing: the app left the foreground (app state 3, 4 = foreground) |
| CHK-SPL-006 | Check that the system status bar (time, network, battery) is visible while the… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-SPL-007 | Check that no user interaction is possible on the Splash Screen, including taps… | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | Failed | allure: failed — AssertionError: a back on the splash changes nothing: the app left the foreground (app state 3, 4 = foreground) |
| CHK-SPL-008 | Check that the application validates an existing user session in the background… | 1 — `tests.shared.test_splash#test_session_hands_over_to_jobs (TC-SPL-002 With a valid session, the splash hands over to the Jobs list and Welcome never appears)` | Passed | allure: passed |
| CHK-SPL-009 | Check that the application verifies the authentication token status during the… | 1 — `tests.shared.test_splash#test_deleted_account_session_ends (TC-SPL-003 A session whose account was deleted on the server ends on Welcome after a cold start)` | Failed | allure: failed — selenium.common.exceptions.TimeoutException: Message: ('accessibility id', "Welcome to Concert\nTechnologies' Field Force") does not show "Welcome to Concert T… |
| CHK-SPL-010 | Check that essential application configuration and metadata are loaded while th… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-SPL-011 | Check that the application automatically navigates to the Login Screen after th… | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | Failed | allure: failed — AssertionError: a back on the splash changes nothing: the app left the foreground (app state 3, 4 = foreground) |
| CHK-SPL-012 | Check that the application automatically navigates to the Home / Jobs List or C… | 1 — `tests.shared.test_splash#test_session_hands_over_to_jobs (TC-SPL-002 With a valid session, the splash hands over to the Jobs list and Welcome never appears)` | Passed | allure: passed |
| CHK-SPL-013 | Check that the transition from the Splash Screen to the next screen occurs auto… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-SPL-014 | Check that the Splash Screen is displayed for the minimum required time needed… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-SPL-015 | Check that the Splash Screen handles slow initialization gracefully without vis… | 0 |  | no tagged test — not run (manual / exploratory), never green |

**Summary:** total 15 · automated 9 · Passed 2 · Failed 7 · Blocked 0 · Not run 6 (= total − Passed − Failed − Blocked)

## Tagged tests with no checklist item

These CHK IDs appear in test tags but in none of the checklists above — a stale tag, a typo, or a missing `--checklist`. They count for nothing until resolved.

| CHK ID | Tests | Statuses |
|---|---|---|
| CHK-AUTH-073 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-074 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-075 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-088 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-089 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-110 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-115 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-117 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-AUTH-119 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-ORDD-001 | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | passed |
| CHK-ORDD-002 | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | passed |
| CHK-ORDL-001 | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | passed |
| CHK-ORDL-002 | 1 — `tests.shared.test_order_list#test_own_phone_link_opens_jobs (TC-ORDL-013 A job link for the technician's own phone opens the Jobs list)` | passed |
| CHK-ORDL-003 | 1 — `tests.shared.test_order_list#test_signed_out_job_links (TC-ORDL-011 Signed out, a job link does not open the Jobs list: an unknown key shows 'Link expired', a valid key leads to registration)` | passed |
| CHK-ORDL-004 | 1 — `tests.shared.test_order_list#test_mismatch_dialog_shown (TC-ORDL-012 A job link for another phone number shows the mismatch dialog)` | passed |
| CHK-ORDL-005 | 1 — `tests.shared.test_order_list#test_mismatch_dialog_shown (TC-ORDL-012 A job link for another phone number shows the mismatch dialog)` | passed |
| CHK-ORDL-006 | 1 — `tests.shared.test_order_list#test_mismatch_dialog_shown (TC-ORDL-012 A job link for another phone number shows the mismatch dialog)` | passed |
| CHK-ORDL-007 | 1 — `tests.shared.test_order_list#test_mismatch_cancel_and_log_out (TC-ORDL-012 Mismatch dialog: Cancel keeps the session, Log out ends it)` | passed |
| CHK-ORDL-008 | 1 — `tests.shared.test_order_list#test_mismatch_cancel_and_log_out (TC-ORDL-012 Mismatch dialog: Cancel keeps the session, Log out ends it)` | passed |
| CHK-ORDL-009 | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | passed |
| CHK-ORDL-010 | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | passed |
| CHK-ORDL-011 | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | passed |
| CHK-ORDL-012 | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | passed |
| CHK-ORDL-013 | 1 — `tests.shared.test_order_list#test_jobs_reachable_from_tabs (TC-ORDL-002 The Jobs list stays reachable from the other bottom tabs)` | passed |
| CHK-ORDL-015 | 2 — `tests.shared.test_order_list#test_status_badges (TC-ORDL-004 Each job status shows its own badge; completed, canceled and expired jobs are not listed)`; `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | passed, passed |
| CHK-ORDL-016 | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | passed |
| CHK-ORDL-017 | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | passed |
| CHK-ORDL-018 | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | passed |
| CHK-ORDL-019 | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | passed |
| CHK-ORDL-020 | 1 — `tests.shared.test_order_list#test_status_badges (TC-ORDL-004 Each job status shows its own badge; completed, canceled and expired jobs are not listed)` | passed |
| CHK-ORDL-022 | 1 — `tests.shared.test_order_list#test_updated_label_until_viewed (TC-ORDL-005 An unviewed job carries 'Updated' in the list and in the calendar until its details are opened)` | failed |
| CHK-ORDL-024 | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | passed |
| CHK-ORDL-026 | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | passed |
| CHK-ORDL-027 | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | passed |
| CHK-ORDL-028 | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | passed |
| CHK-ORDL-029 | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | passed |
| CHK-ORDL-036 | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | passed |
| CHK-ORDL-037 | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | passed |
| CHK-ORDL-038 | 1 — `tests.shared.test_order_list#test_signed_out_job_links (TC-ORDL-011 Signed out, a job link does not open the Jobs list: an unknown key shows 'Link expired', a valid key leads to registration)` | passed |
| CHK-ORDL-039 | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | passed |
| CHK-ORDL-040 | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | passed |
| CHK-ORDL-042 | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | passed |
| CHK-ORDL-043 | 1 — `tests.shared.test_order_list#test_week_swipe (TC-ORDL-009 Swiping the week strip moves to the next and the previous week)` | passed |
| CHK-ORDL-044 | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | passed |
| CHK-ORDL-047 | 1 — `tests.shared.test_order_list#test_week_swipe (TC-ORDL-009 Swiping the week strip moves to the next and the previous week)` | passed |
| CHK-ORDL-048 | 1 — `tests.shared.test_order_list#test_week_swipe (TC-ORDL-009 Swiping the week strip moves to the next and the previous week)` | passed |
| CHK-ORDL-049 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-050 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-051 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-052 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-053 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-054 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-055 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-056 | 1 — `tests.shared.test_order_list#test_updated_label_until_viewed (TC-ORDL-005 An unviewed job carries 'Updated' in the list and in the calendar until its details are opened)` | failed |
| CHK-ORDL-057 | 1 — `tests.shared.test_order_list#test_calendar_statuses (TC-ORDL-010 The weekly calendar shows New, In progress and Submitted jobs and hides Completed, Canceled and Expired ones)` | passed |
| CHK-ORDL-058 | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | passed |
| CHK-ORDL-060 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-061 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-062 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-063 | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | passed |
| CHK-ORDL-068 | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | passed |
| CHK-ORDL-069 | 1 — `tests.shared.test_order_list#test_list_ordered_by_date (TC-ORDL-014 The Jobs list is ordered by scheduled date, earliest first)` | failed |
| CHK-ORDL-070 | 1 — `tests.shared.test_order_list#test_calendar_follows_list_refresh (TC-ORDL-015 Jobs that the refreshed list shows are shown in the calendar on their dates)` | failed |

> **Resolved (2026-09-30) — every Failed row and the orphans:**
> - **TC-SPL-001 carries six items; it failed at its last splash step**, so the tool marks all six Failed. In this run
>   the steps behind CHK-SPL-001 / -002 (the brand splash after the system one, 3.3 s), CHK-SPL-003 (logo centred on
>   the first brand frame) and CHK-SPL-005 (no labelled or clickable node in the tree, read during the splash) **passed**
>   (Allure steps of TC-SPL-001, run 6). The test failed at "the app stays in the foreground" after the system Back —
>   **CHK-SPL-007 → [BUG-SPL-002](../bugs/BUG-SPL-002.md)** (the Back closes the app on the splash; filed on the
>   owner's go, Q-SPL-A2, 2026-09-30).
>   CHK-SPL-011 (Welcome by itself) was not reached in this test. The verdicts above are the tool's and are not edited;
>   splitting TC-SPL-001 so that each item gets its own verdict is a proposal for the owner.
> - **CHK-SPL-009 → [BUG-SPL-001](../bugs/BUG-SPL-001.md)** — reproduced on Android 4 of 4 (runs 3–6).
> - Orphans: CHK-AUTH-* belong to module 02 (traced in `02-authentication/android/`), CHK-ORDL-* to module 03
>   (`03-order-list/android/`), CHK-ORDD-001/-002 to module 04 (its Android run) — the shared 01+03 run, as on iOS.

