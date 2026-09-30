# Automated traceability — mobile

Generated: 2026-09-30 06:57 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/03-order-list/order-list-checklist.md` — 70 items
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
| CHK-ORDL-001 | Check that the Orders List screen is displayed as the primary landing screen af… | 1 — `tests.shared.test_authentication#test_login_with_email (TC-AUTH-005 Login with email and the OTP opens the Jobs list)` | Passed | allure: passed |
| CHK-ORDL-002 | Check that the Orders List screen is opened when a registered user accesses the… | 1 — `tests.shared.test_order_list#test_own_phone_link_opens_jobs (TC-ORDL-013 A job link for the technician's own phone opens the Jobs list)` | Passed | allure: passed |
| CHK-ORDL-003 | Check that the Orders List screen is not displayed for unauthenticated users an… | 1 — `tests.shared.test_order_list#test_signed_out_job_links (TC-ORDL-011 Signed out, a job link does not open the Jobs list: an unknown key shows 'Link expired', a valid key leads to registration)` | Passed | allure: passed |
| CHK-ORDL-004 | Check that an error modal with the title “Assigned to a Different Phone Number”… | 1 — `tests.shared.test_order_list#test_mismatch_dialog_shown (TC-ORDL-012 A job link for another phone number shows the mismatch dialog)` | Passed | allure: passed |
| CHK-ORDL-005 | Check that the error modal displays explanatory text instructing the user to lo… | 1 — `tests.shared.test_order_list#test_mismatch_dialog_shown (TC-ORDL-012 A job link for another phone number shows the mismatch dialog)` | Passed | allure: passed |
| CHK-ORDL-006 | Check that the error modal displays both “Cancel” and “Log out” action buttons. | 1 — `tests.shared.test_order_list#test_mismatch_dialog_shown (TC-ORDL-012 A job link for another phone number shows the mismatch dialog)` | Passed | allure: passed |
| CHK-ORDL-007 | Check that tapping “Cancel” closes the modal without logging the user out. | 1 — `tests.shared.test_order_list#test_mismatch_cancel_and_log_out (TC-ORDL-012 Mismatch dialog: Cancel keeps the session, Log out ends it)` | Passed | allure: passed |
| CHK-ORDL-008 | Check that tapping “Log out” logs the user out and navigates them to the authen… | 1 — `tests.shared.test_order_list#test_mismatch_cancel_and_log_out (TC-ORDL-012 Mismatch dialog: Cancel keeps the session, Log out ends it)` | Passed | allure: passed |
| CHK-ORDL-009 | Check that the top app bar is displayed on the Orders List screen with a calend… | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | Passed | allure: passed |
| CHK-ORDL-010 | Check that tapping the calendar icon switches the view from List view to Calend… | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | Passed | allure: passed |
| CHK-ORDL-011 | Check that the bottom navigation bar is displayed on the Orders List screen. | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | Passed | allure: passed |
| CHK-ORDL-012 | Check that the Orders tab is highlighted as active in the bottom navigation bar. | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | Passed | allure: passed |
| CHK-ORDL-013 | Check that the Orders List screen remains accessible at all times via the botto… | 1 — `tests.shared.test_order_list#test_jobs_reachable_from_tabs (TC-ORDL-002 The Jobs list stays reachable from the other bottom tabs)` | Passed | allure: passed |
| CHK-ORDL-014 | Check that status filter buttons “New”, “In Progress”, and “Completed” are disp… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-015 | Check that a list of order cards is displayed when orders are available for the… | 2 — `tests.shared.test_order_list#test_status_badges (TC-ORDL-004 Each job status shows its own badge; completed, canceled and expired jobs are not listed)`; `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | Passed | allure: passed<br>allure: passed |
| CHK-ORDL-016 | Check that each order card displays the Job ID as the primary bold element. | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | Passed | allure: passed |
| CHK-ORDL-017 | Check that each order card displays the Site Name for the order. | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | Passed | allure: passed |
| CHK-ORDL-018 | Check that each order card displays the City and State location information. | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | Passed | allure: passed |
| CHK-ORDL-019 | Check that each order card displays the scheduled date and scheduled time. | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | Passed | allure: passed |
| CHK-ORDL-020 | Check that each order card displays a visually distinct order status badge (e.g… | 1 — `tests.shared.test_order_list#test_status_badges (TC-ORDL-004 Each job status shows its own badge; completed, canceled and expired jobs are not listed)` | Passed | allure: passed |
| CHK-ORDL-021 | Check that special indicators such as “Unsubmitted” are displayed on the order… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-022 | Check that special indicators such as “Updated” are displayed on the order card… | 1 — `tests.shared.test_order_list#test_updated_label_until_viewed (TC-ORDL-005 An unviewed job carries 'Updated' in the list and in the calendar until its details are opened)` | Failed | allure: failed — AssertionError: card QA-AUTO-0930-095153-UNVIEWED: 'Updated' in the tree True, drawn True (banner fill 0.0245); expected False |
| CHK-ORDL-023 | Check that order status badges and indicators remain readable across different… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-024 | Check that tapping an order card navigates the user to the corresponding Order… | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | Passed | allure: passed |
| CHK-ORDL-025 | Check that only a single navigation event is triggered when an order card is ta… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-069 | Check that order cards on the Orders List screen are sorted by scheduled date a… | 1 — `tests.shared.test_order_list#test_list_ordered_by_date (TC-ORDL-014 The Jobs list is ordered by scheduled date, earliest first)` | Failed | allure: failed — AssertionError: list order ['QA-AUTO-0930-095153-NEW', 'QA-AUTO-0930-095153-YESTERDAY', 'QA-AUTO-0930-095153-OTHERDAY'], expected by date ['QA-AUTO-0930-095153… |
| CHK-ORDL-026 | Check that an empty state is displayed when no orders are assigned to the user. | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | Passed | allure: passed |
| CHK-ORDL-027 | Check that the empty state displays a placeholder illustration or icon. | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | Passed | allure: passed |
| CHK-ORDL-028 | Check that the empty state displays the title text “No orders”. | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | Passed | allure: passed |
| CHK-ORDL-029 | Check that the empty state displays an informational message explaining that no… | 1 — `tests.shared.test_order_list#test_empty_jobs_list (TC-ORDL-001 With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the 'No jobs' empty state)` | Passed | allure: passed |
| CHK-ORDL-030 | Check that orders assigned via a valid access link appear in the Orders List af… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-031 | Check that cached orders are displayed on the Orders List screen when the devic… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-032 | Check that the Orders List screen displays an appropriate message or indicator… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-033 | Check that an error message is displayed when the orders list fails to load due… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-034 | Check that the user is able to retry loading the Orders List after a network er… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-035 | Check that the Orders List screen recovers correctly after connectivity is rest… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-036 | Check that the Orders List screen does not display duplicate orders after refre… | 1 — `tests.shared.test_order_list#test_job_card_and_details (TC-ORDL-003 A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details)` | Passed | allure: passed |
| CHK-ORDL-037 | Check that the Calendar (Weekly) view is displayed when the user switches from… | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | Passed | allure: passed |
| CHK-ORDL-038 | Check that the Calendar (Weekly) view is accessible only to authenticated users. | 1 — `tests.shared.test_order_list#test_signed_out_job_links (TC-ORDL-011 Signed out, a job link does not open the Jobs list: an unknown key shows 'Link expired', a valid key leads to registration)` | Passed | allure: passed |
| CHK-ORDL-039 | Check that the bottom navigation bar remains visible with the Orders tab highli… | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | Passed | allure: passed |
| CHK-ORDL-040 | Check that the user can switch back from the Calendar (Weekly) view to the Orde… | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | Passed | allure: passed |
| CHK-ORDL-041 | Check that the current month and year are displayed in the date selector sectio… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-042 | Check that the default selected date is today when today falls within the curre… | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | Passed | allure: passed |
| CHK-ORDL-043 | Check that the first day of the week is selected by default when today does not… | 1 — `tests.shared.test_order_list#test_week_swipe (TC-ORDL-009 Swiping the week strip moves to the next and the previous week)` | Passed | allure: passed |
| CHK-ORDL-044 | Check that the days of the selected week (Sunday to Saturday) are displayed in… | 1 — `tests.shared.test_order_list#test_calendar_toggle (TC-ORDL-006 The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back)` | Passed | allure: passed |
| CHK-ORDL-045 | Check that the selected date is visually highlighted in the week selector. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-046 | Check that days containing scheduled orders are visually indicated in the week… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-047 | Check that tapping the previous week arrow navigates to the previous calendar w… | 1 — `tests.shared.test_order_list#test_week_swipe (TC-ORDL-009 Swiping the week strip moves to the next and the previous week)` | Passed | allure: passed |
| CHK-ORDL-048 | Check that tapping the next week arrow navigates to the next calendar week. | 1 — `tests.shared.test_order_list#test_week_swipe (TC-ORDL-009 Swiping the week strip moves to the next and the previous week)` | Passed | allure: passed |
| CHK-ORDL-049 | Check that orders are displayed only for the currently selected date in the Cal… | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-050 | Check that the order list updates immediately when a different date is selected. | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-051 | Check that the Calendar view displays order cards using the same layout and ele… | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-052 | Check that each order card displays the Job ID as the primary identifier. | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-053 | Check that each order card displays the Site Name and City, State information. | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-054 | Check that each order card displays the scheduled start date and time. | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-055 | Check that each order card displays the order status badge (New or In Progress). | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-056 | Check that special flags such as “Updated” or “Unsubmitted” are displayed on or… | 1 — `tests.shared.test_order_list#test_updated_label_until_viewed (TC-ORDL-005 An unviewed job carries 'Updated' in the list and in the calendar until its details are opened)` | Failed | allure: failed — AssertionError: card QA-AUTO-0930-095153-UNVIEWED: 'Updated' in the tree True, drawn True (banner fill 0.0245); expected False |
| CHK-ORDL-057 | Check that only orders with status New or In Progress are displayed in the Cale… | 1 — `tests.shared.test_order_list#test_calendar_statuses (TC-ORDL-010 The weekly calendar shows New, In progress and Submitted jobs and hides Completed, Canceled and Expired ones)` | Passed | allure: passed |
| CHK-ORDL-058 | Check that tapping an order card in the Calendar view navigates the user to the… | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | Passed | allure: passed |
| CHK-ORDL-059 | Check that multiple rapid taps on an order card do not trigger duplicate naviga… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-060 | Check that an empty state is displayed when no orders are scheduled for the sel… | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-061 | Check that the empty state displays the title text “No orders”. | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-062 | Check that the empty state displays informational text explaining that no order… | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-063 | Check that the empty state is shown instead of an empty list when no orders are… | 1 — `tests.shared.test_order_list#test_calendar_date_selection (TC-ORDL-007 Selecting a date shows only that date's jobs, and a date without jobs shows 'No jobs')` | Passed | allure: passed |
| CHK-ORDL-064 | Check that cached calendar and order data is displayed when the device is offli… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-065 | Check that the Calendar (Weekly) view displays an appropriate state when offlin… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-066 | Check that switching between weeks does not cause UI flickering or layout shift… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-067 | Check that the Calendar (Weekly) view handles a large number of orders without… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDL-068 | Check that the selected date and order list state are preserved when switching… | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | Passed | allure: passed |
| CHK-ORDL-070 | Check that jobs shown in the Orders List after a refresh are also shown in the… | 1 — `tests.shared.test_order_list#test_calendar_follows_list_refresh (TC-ORDL-015 Jobs that the refreshed list shows are shown in the calendar on their dates)` | Failed | allure: failed — selenium.common.exceptions.TimeoutException: Message: ('-android uiautomator', 'new UiSelector().descriptionContains("QA-AUTO-0930-095315-LATE")') not visible… |

**Summary:** total 70 · automated 52 · Passed 48 · Failed 4 · Blocked 0 · Not run 18 (= total − Passed − Failed − Blocked)

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
| CHK-SPL-001 | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | failed |
| CHK-SPL-002 | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | failed |
| CHK-SPL-003 | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | failed |
| CHK-SPL-005 | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | failed |
| CHK-SPL-007 | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | failed |
| CHK-SPL-008 | 1 — `tests.shared.test_splash#test_session_hands_over_to_jobs (TC-SPL-002 With a valid session, the splash hands over to the Jobs list and Welcome never appears)` | passed |
| CHK-SPL-009 | 1 — `tests.shared.test_splash#test_deleted_account_session_ends (TC-SPL-003 A session whose account was deleted on the server ends on Welcome after a cold start)` | failed |
| CHK-SPL-011 | 1 — `tests.shared.test_splash#test_cold_start_splash_then_welcome (TC-SPL-001 Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself)` | failed |
| CHK-SPL-012 | 1 — `tests.shared.test_splash#test_session_hands_over_to_jobs (TC-SPL-002 With a valid session, the splash hands over to the Jobs list and Welcome never appears)` | passed |

> **Resolved (2026-09-30) — every Failed row and the orphans:**
> - **CHK-ORDL-022, -056 → [BUG-ORDL-003](../bugs/BUG-ORDL-003.md)** ("Updated" stays after the details were opened) —
>   reproduced on Android 3 of 3 (runs 4–6).
> - **CHK-ORDL-069 → [BUG-ORDL-002](../bugs/BUG-ORDL-002.md)** (the list follows creation order, not the date) —
>   4 of 4 (runs 3–6).
> - **CHK-ORDL-070 → [BUG-ORDL-001](../bugs/BUG-ORDL-001.md)** (the calendar misses jobs the refreshed list shows) —
>   runs 5 and 6, and recon A1.
> - **Blocked 0:** the mismatch dialog's Cancel / Log out test (TC-ORDL-012, CHK-ORDL-007, -008) was Blocked on iOS and
>   **passes on Android**.
> - Orphans: CHK-SPL-* belong to module 01 (`01-splash/android/`), CHK-AUTH-* to module 02
>   (`02-authentication/android/`), CHK-ORDD-001/-002 to module 04 (its Android run) — the shared 01+03 run, as on iOS.

