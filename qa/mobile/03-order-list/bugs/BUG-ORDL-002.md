# BUG-ORDL-002 — The Jobs list is ordered by when a job was created, not by its scheduled date

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-09-24 on the owner's go
> (mykola.zhuchenko: «якщо не так як в СРС то заведи, але low пріоріті»). Tracker: not configured, nothing sent anywhere.

## Summary

The Jobs list shows the most recently created job on top, whatever its scheduled date; jobs are not sorted by their
scheduled date, so a job for tomorrow can sit below a job for yesterday.

## Layer

- [ ] App (UI)
- [ ] Backend / API
- [x] Unclear — the app shows the jobs in the order the list request returns them: `GET /job/technician` is called with
  `page` and `pageSize` only, and the app does not sort on the device (`lib/features/jobs/data/api/job_api_service.dart`,
  `jobs_repository_impl.dart`). Either the app should ask for / apply an order by schedule date, or the endpoint's
  default order should be by schedule date. `GET /job` documents `orderBy` / `orderByColumn`; `/job/technician` does not.

## Severity / Priority

- **Severity:** S3 (minor) — **branch fired:** #3 — the list does not follow the documented order, a workaround exists
  (the weekly calendar groups jobs by date).
- **Priority:** P4 (low) — set by the owner, 2026-09-24.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on iOS |
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

- Signed in as a technician with no other active jobs.
- Three jobs assigned to the technician, created in this order: one for **tomorrow**, then one for **yesterday**, then one
  for **today** (in the probe: `POST /job` with the technician's `userId`, status New, 12:00 each).

## Steps to reproduce

1. Open the Jobs list.
2. Pull down to refresh.
3. Read the dates on the cards from top to bottom.

## Actual result

Top to bottom: 24 Sep (today) → 23 Sep (yesterday) → 25 Sep (tomorrow) — the reverse of the creation order; the dates
are in no order. // [list-order-follows-creation-not-date.png](evidence/BUG-ORDL-002/list-order-follows-creation-not-date.png)

## Expected result

Jobs are listed by scheduled date, earliest first (the time within one date is not considered — owner, 2026-09-24).

## Frequency

- [x] Always — **3 of 3 observations**: two recon runs (jobs created in date order, so the list looked sorted by date,
  newest first) and one probe with jobs created out of date order (2026-09-24), which showed the creation order.

## Crash? ANR?

- [x] No crash

## Evidence

- Screenshot: [evidence/BUG-ORDL-002/list-order-follows-creation-not-date.png](evidence/BUG-ORDL-002/list-order-follows-creation-not-date.png)
  (test jobs only).
- Screen tree: `qa/shared/recon-dumps/ios-2026-09-24/recon4f_sort_probe.xml`.
- Probe: `automation/mobile/scripts/recon/recon_4.py`, pass `sort`; report
  [qa/shared/recon-2026-09-24-ios.md](../../../shared/recon-2026-09-24-ios.md).

## Workaround

Use the weekly calendar to see the jobs of a given date.

## Regression info

- Last known good version: unknown.
- First broken version: unknown.
- Why it is easy to miss: jobs are usually created roughly in the order of their dates, so on real data the list looks
  sorted.

## Related

- SRS §3.1.2.1 FR-ORD-02: "Orders shall be grouped and filterable by status: • New • In Progress Orders shall be sorted by
  a date and time (ascending order)"
- Checklist: `CHK-ORDL-069` ([../order-list-checklist.md](../order-list-checklist.md)), added 2026-09-24.
- Test case: `TC-ORDL-014` ([../order-list-test-cases.md](../order-list-test-cases.md)) — red until the fix.
- Question: `D-ORDL-10` in [../order-list-questions.md](../order-list-questions.md).
- Invariant: none fits — missing invariant: "the Jobs list is ordered by scheduled date".
- Tracker: not filed (no tracker configured).

> **When this bug is verified fixed:** re-run TC-ORDL-014 on the fixed build, then add the invariant above.
