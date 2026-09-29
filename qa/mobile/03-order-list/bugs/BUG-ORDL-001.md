# BUG-ORDL-001 — The weekly calendar keeps showing "No jobs" for jobs the refreshed Jobs list already shows

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-09-24 on the owner's go
> (mykola.zhuchenko, answer 3 to the recon 4 questions: «так заведи»). Tracker: not configured, nothing sent anywhere.

## Summary

Jobs assigned while the app is open appear in the Jobs list after a pull-to-refresh, but the weekly calendar still shows
"No jobs" for their dates until the calendar itself is pulled to refresh or the app is restarted.

## Layer

- [x] App (UI) — the list refresh reloads only the list; the calendar keeps the week it loaded when the Jobs screen
  opened (`lib/features/jobs/presentation/bloc/jobs/jobs_bloc.dart`: `JobsListRefreshed` fetches the list only;
  the calendar week is fetched on screen start, on its own pull-to-refresh, on a week change and on reconnect).
- [ ] Backend / API
- [ ] Unclear

## Severity / Priority

- **Severity:** S3 (minor) — **branch fired:** #3 — the calendar misses assigned jobs, but a workaround exists (pull to
  refresh inside the calendar, or restart the app).
- **Priority:** *proposal* P3 — owner / PM decide.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on iOS |
| Platforms checked | iOS ✓ reproduced · Android — not checked yet (step 7) |
| OS version | iOS 26.5 |
| Device | iPhone 17 |
| Form factor | phone |
| Device type | simulator |
| App version | `[DEV] CT Mobile` 1.1.1 (178), `development` @ 85a84f3 |
| Build type | debug (flavor `development`, `CLIENT_BUILD=true`) |
| Install method | sideload (simulator build) |
| Network | Wi-Fi (host network), DEV API |
| Locale | en |
| Orientation | portrait |
| User role | Field Technician (signed in) |
| Feature flags | — |
| Permissions state | notifications=granted |

## Preconditions

- Signed in as a technician; the Jobs list is open in list mode.
- While the app is open, new jobs are assigned to the technician for today and for another day of the current week
  (in the recon: `POST /job` with the technician's `userId`, statuses New / In progress / Submitted).

## Steps to reproduce

1. On the Jobs list, pull down to refresh.
2. Tap the calendar icon.
3. Look at today.
4. Tap the other day that has a new job.

## Actual result

After step 1 the list shows the new jobs. In the calendar, today and the other day both show "No jobs". Only a
pull-to-refresh inside the calendar (or a restart) brings the jobs into the calendar.
// [1-list-after-refresh-shows-jobs.png](evidence/BUG-ORDL-001/ios/1-list-after-refresh-shows-jobs.png),
[2-calendar-today-no-jobs.png](evidence/BUG-ORDL-001/ios/2-calendar-today-no-jobs.png),
[3-calendar-after-its-own-refresh.png](evidence/BUG-ORDL-001/ios/3-calendar-after-its-own-refresh.png)

## Expected result

The calendar shows every job assigned to the technician on its scheduled date whenever the list shows it — refreshing
the jobs refreshes both views.

## Frequency

- [x] Always — **2 of 2 attempts** (recon 4, 2026-09-24, two separate sets of 8 jobs; today and the other day both
  empty each time; the calendar's own pull-to-refresh fixed it in the attempt where it was tried).

## Crash? ANR?

- [x] No crash

## Evidence

- Screenshots: [evidence/BUG-ORDL-001/ios/](evidence/BUG-ORDL-001/ios/) — 1 and 2 from the first attempt, 3 from the second
  (different job ids, same steps). Test jobs only (`QA-AUTO-R4-*`).
- Screen trees: `qa/shared/recon-dumps/ios-2026-09-24/recon4_calendar_today.xml`, `recon4b_calendar_after_list_refresh.xml`,
  `recon4b_calendar_after_calendar_refresh.xml`.
- Recon report: [qa/shared/recon-2026-09-24-ios.md](../../../shared/recon-2026-09-24-ios.md), section Order list.

## Workaround

Pull down to refresh inside the calendar view, or close and reopen the app.

## Regression info

- Last known good version: unknown.
- First broken version: unknown.
- The same gap applies when the list is refreshed by the app itself (the list-refresh notifier used after a job link is
  synchronized) — by code reading, not observed.

## Related

- SRS §3.1.2.2: "Weekly View screen provides Field Technicians with a time-oriented view of assigned orders, organized
  by week and specific dates." and "This screen complements the Orders List view and supports planning and daily
  execution."
- SRS §3.1.2.2 FR-CAL-W-01: "The system shall display orders grouped by the selected calendar date within the current
  week."
- Checklist: `CHK-ORDL-049`, `CHK-ORDL-050` ([../order-list-checklist.md](../order-list-checklist.md)) — no item states
  the list / calendar consistency itself (CHK-ORDL-070 was added for it, 2026-09-24).
- Test cases: `TC-ORDL-015` — the regression check, red until the fix; `TC-ORDL-007`, `TC-ORDL-010`
  ([../order-list-test-cases.md](../order-list-test-cases.md)) refresh the calendar on purpose so their own checks are
  not hidden by this bug.
- Question: `D-ORDL-11` in [../order-list-questions.md](../order-list-questions.md).
- Invariant: none fits — missing invariant: "list and calendar show the same set of assigned jobs after any refresh".
- Tracker: not filed (no tracker configured).

> **When this bug is verified fixed:** re-verify with the steps above on the fixed build, add the invariant, and keep the
> regression check CHK-ORDL-070 / TC-ORDL-015.
