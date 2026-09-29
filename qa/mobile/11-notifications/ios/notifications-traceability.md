# Automated traceability — mobile

Generated: 2026-09-27 08:50 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/11-notifications/notifications-checklist.md` — 31 items
- Results (allure): `automation/mobile/allure-results-11` — 6 tests (6 passed, 0 failed, 0 skipped)

## Run context — the limits of every verdict below

- Target: `iOS simulator iPhone 17 · iOS 26.5 · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true`
- Harness commit (this repo): `9a2bc95`
- Environment label (pytest): `iOS · iPhone 17 · iOS 26.5 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=ios tests/shared/test_notifications.py (module 11 run 2, 2026-09-27; push permission switched in the Settings app and restored)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-NOTIF-001 | Check that the Notifications screen opens from the bottom navigation when the u… | 1 — `tests.shared.test_notifications#test_tab_and_empty_state (TC-NOTIF-001 The Notifications tab: 'Notification list', the tab selected, the empty state)` | Passed | allure: passed |
| CHK-NOTIF-002 | Check that the Notifications screen displays the title “Notification list” at t… | 1 — `tests.shared.test_notifications#test_tab_and_empty_state (TC-NOTIF-001 The Notifications tab: 'Notification list', the tab selected, the empty state)` | Passed | allure: passed |
| CHK-NOTIF-003 | Check that the Notifications bottom tab is visually selected when the Notificat… | 1 — `tests.shared.test_notifications#test_tab_and_empty_state (TC-NOTIF-001 The Notifications tab: 'Notification list', the tab selected, the empty state)` | Passed | allure: passed |
| CHK-NOTIF-004 | Check that the Notifications list is scrollable when the number of notification… | 1 — `tests.shared.test_notifications#test_long_list (TC-NOTIF-006 A long list scrolls; a long job name wraps inside the screen; rows do not overlap)` | Passed | allure: passed |
| CHK-NOTIF-005 | Check that the push notifications banner is displayed at the top of the Notific… | 1 — `tests.shared.test_notifications#test_push_banner (TC-NOTIF-005 Push not allowed: the banner with its texts, together with the empty state; Go to Settings opens Settings; allowed again: no banner)` | Passed | allure: passed |
| CHK-NOTIF-006 | Check that the push notifications banner displays the text “Turn on push notifi… | 1 — `tests.shared.test_notifications#test_push_banner (TC-NOTIF-005 Push not allowed: the banner with its texts, together with the empty state; Go to Settings opens Settings; allowed again: no banner)` | Passed | allure: passed |
| CHK-NOTIF-007 | Check that the banner displays the action “Go to Settings” as a tappable contro… | 1 — `tests.shared.test_notifications#test_push_banner (TC-NOTIF-005 Push not allowed: the banner with its texts, together with the empty state; Go to Settings opens Settings; allowed again: no banner)` | Passed | allure: passed |
| CHK-NOTIF-008 | Check that tapping “Go to Settings” opens the device notification settings page… | 1 — `tests.shared.test_notifications#test_push_banner (TC-NOTIF-005 Push not allowed: the banner with its texts, together with the empty state; Go to Settings opens Settings; allowed again: no banner)` | Passed | allure: passed |
| CHK-NOTIF-009 | Check that the push notifications banner is not displayed when push notificatio… | 1 — `tests.shared.test_notifications#test_push_banner (TC-NOTIF-005 Push not allowed: the banner with its texts, together with the empty state; Go to Settings opens Settings; allowed again: no banner)` | Passed | allure: passed |
| CHK-NOTIF-010 | Check that each notification item displays an icon that matches the notificatio… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTIF-011 | Check that each notification item displays a title (e.g., “New job assigned”, “… | 1 — `tests.shared.test_notifications#test_rows_from_job_changes (TC-NOTIF-002 Rows from job changes: the server's description, the chevron only for a job that can be opened, newest first, the tab's count; 'Job cancelled' arrives read)` | Passed | allure: passed |
| CHK-NOTIF-012 | Check that each notification item displays a description containing the related… | 1 — `tests.shared.test_notifications#test_rows_from_job_changes (TC-NOTIF-002 Rows from job changes: the server's description, the chevron only for a job that can be opened, newest first, the tab's count; 'Job cancelled' arrives read)` | Passed | allure: passed |
| CHK-NOTIF-013 | Check that each notification item displays a chevron indicating it can be opene… | 1 — `tests.shared.test_notifications#test_rows_from_job_changes (TC-NOTIF-002 Rows from job changes: the server's description, the chevron only for a job that can be opened, newest first, the tab's count; 'Job cancelled' arrives read)` | Passed | allure: passed |
| CHK-NOTIF-014 | Check that notification titles and descriptions are readable and do not overlap… | 1 — `tests.shared.test_notifications#test_long_list (TC-NOTIF-006 A long list scrolls; a long job name wraps inside the screen; rows do not overlap)` | Passed | allure: passed |
| CHK-NOTIF-015 | Check that notifications are displayed in reverse chronological order with the… | 1 — `tests.shared.test_notifications#test_rows_from_job_changes (TC-NOTIF-002 Rows from job changes: the server's description, the chevron only for a job that can be opened, newest first, the tab's count; 'Job cancelled' arrives read)` | Passed | allure: passed |
| CHK-NOTIF-016 | Check that each notification item contains a valid type, title, description, an… | 1 — `tests.shared.test_notifications#test_rows_from_job_changes (TC-NOTIF-002 Rows from job changes: the server's description, the chevron only for a job that can be opened, newest first, the tab's count; 'Job cancelled' arrives read)` | Passed | allure: passed |
| CHK-NOTIF-017 | Check that “Job starts today” notifications are generated only for jobs schedul… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTIF-018 | Check that “Job starts today” notifications appear at the expected time logic (… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTIF-019 | Check that tapping a notification item opens the related Job Details screen for… | 1 — `tests.shared.test_notifications#test_open_marks_read (TC-NOTIF-003 Opening an unread notification: the job's details; back on the list the row is read, the count goes down, the server marks it viewed)` | Passed | allure: passed |
| CHK-NOTIF-020 | Check that opening a notification keeps the bottom navigation available after r… | 1 — `tests.shared.test_notifications#test_open_marks_read (TC-NOTIF-003 Opening an unread notification: the job's details; back on the list the row is read, the count goes down, the server marks it viewed)` | Passed | allure: passed |
| CHK-NOTIF-021 | Check that if the related job is no longer available, tapping the notification… | 1 — `tests.shared.test_notifications#test_cancelled_job_row (TC-NOTIF-004 A notification of a job that can no longer be opened: no chevron, the tap stays on the list and shows nothing, the row turns read)` | Passed | allure: passed |
| CHK-NOTIF-022 | Check that unread notifications are visually distinguishable from read notifica… | 1 — `tests.shared.test_notifications#test_open_marks_read (TC-NOTIF-003 Opening an unread notification: the job's details; back on the list the row is read, the count goes down, the server marks it viewed)` | Passed | allure: passed |
| CHK-NOTIF-023 | Check that a notification is marked as read immediately after it is opened from… | 1 — `tests.shared.test_notifications#test_open_marks_read (TC-NOTIF-003 Opening an unread notification: the job's details; back on the list the row is read, the count goes down, the server marks it viewed)` | Passed | allure: passed |
| CHK-NOTIF-024 | Check that returning to the Notifications list shows the previously opened noti… | 1 — `tests.shared.test_notifications#test_open_marks_read (TC-NOTIF-003 Opening an unread notification: the job's details; back on the list the row is read, the count goes down, the server marks it viewed)` | Passed | allure: passed |
| CHK-NOTIF-025 | Check that the unread indicator count (badge dot on the Notifications tab, if i… | 1 — `tests.shared.test_notifications#test_open_marks_read (TC-NOTIF-003 Opening an unread notification: the job's details; back on the list the row is read, the count goes down, the server marks it viewed)` | Passed | allure: passed |
| CHK-NOTIF-026 | Check that the empty state is displayed when no notifications exist for the use… | 1 — `tests.shared.test_notifications#test_tab_and_empty_state (TC-NOTIF-001 The Notifications tab: 'Notification list', the tab selected, the empty state)` | Passed | allure: passed |
| CHK-NOTIF-027 | Check that the empty state displays the text “No notifications yet” and “You’ll… | 1 — `tests.shared.test_notifications#test_tab_and_empty_state (TC-NOTIF-001 The Notifications tab: 'Notification list', the tab selected, the empty state)` | Passed | allure: passed |
| CHK-NOTIF-028 | Check that the push notifications banner (if push disabled) can still be shown… | 1 — `tests.shared.test_notifications#test_push_banner (TC-NOTIF-005 Push not allowed: the banner with its texts, together with the empty state; Go to Settings opens Settings; allowed again: no banner)` | Passed | allure: passed |
| CHK-NOTIF-029 | Check that if the device is offline, the screen shows cached notifications if a… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTIF-030 | Check that if the device is offline, the screen shows cached notifications if a… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-NOTIF-031 | Check that long job names in notification descriptions are truncated gracefully… | 1 — `tests.shared.test_notifications#test_long_list (TC-NOTIF-006 A long list scrolls; a long job name wraps inside the screen; rows do not overlap)` | Passed | allure: passed |

**Summary:** total 31 · automated 26 · Passed 26 · Failed 0 · Blocked 0 · Not run 5 (= total − Passed − Failed − Blocked)

## Notes on this run

- **Not run (5), by the owner's decisions of 2026-09-27:**
  - CHK-NOTIF-010: the icon by type is not in the accessibility tree; it is seen on the screenshot. Skipped with a
    comment (Q-NOTIF-4).
  - CHK-NOTIF-017, -018: "Job starts today" is sent by a server schedule at 8 AM on the job's day and cannot be triggered
    on DEV. Skipped with a comment (Q-NOTIF-1).
  - CHK-NOTIF-029, -030: offline, Android stage (Q-NOTIF-2).
- **Accepted baseline (D-NOTIF-1…5):**
  - a row shows no title — the type is in the description;
  - a cancelled job's row opens nothing and shows nothing;
  - "Job cancelled" arrives read;
  - "Go to Settings" opens the Settings app — on the simulator its first page; the exact page is checked by hand on a
    device;
  - long names wrap.
- **How the checks decide:**
  - The unread red dot is decided by pixels (`#EB0101` in the dot's box).
  - The rows, descriptions and chevrons are read from the page source.
  - The tab's count comes from its label; the order and texts from `GET /notification` for the technician.
  - The push permission is switched in the Settings app and switched back on after the test.
- **Run history:**
  - Run 1: 4 passed, 2 broken by the harness. Rows off the screen come with an empty rect and were sorted first; six
    scrolls did not reach the app in Settings → Apps.
  - Run 2: 6 passed.
  - Prove-red (`--prove-red`): 6 of 6 failed, each at a check of this module (title, rows, row lookup, banner texts,
    long name).
  - No `QA-AUTO` job and no notification is left on DEV.
