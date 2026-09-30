# BUG-ORDL-003 — "Updated" stays on a job after its details were opened, until the calendar is refreshed

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-09-24 on the owner's go
> (mykola.zhuchenko: «заводь хай буде»). Found by the automated runs of TC-ORDL-005. Tracker: not configured, nothing sent
> anywhere.

## Summary

After a technician opens a job marked "Updated" and comes back, the job is marked viewed on the server, and the Jobs
list reloads, but the "Updated" banner stays on the job's card in the list and in the calendar. It goes away only
after the calendar itself is refreshed or the app is restarted.

## Layer

- [x] App (UI) — the server already has `isViewed = true` before the list reloads (evidence 2). By code reading
  (`lib/features/jobs/presentation/bloc/jobs/jobs_bloc.dart`, `_onListRefreshed`): the set of "Updated" jobs is built
  from the fresh list **plus the calendar week kept in memory** (`_allVisible(listData.items, latest.jobsByDay)`).
  Leaving the details requests a list reload only (`job_details_page.dart`, `PopScope` →
  `JobsListRefreshNotifier.requestRefresh()`), so the calendar week still holds the job with `isViewed = false` and
  keeps it in the set.
- [ ] Backend / API
- [ ] Unclear

## Severity / Priority

- **Severity:** S3 (minor) — **branch fired:** #3 — the indicator is wrong (a job the technician has already viewed
  looks changed again), but a workaround exists (pull to refresh inside the calendar, or restart the app).
- **Priority:** *proposal* P3 — owner / PM decide.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on iOS |
| Platforms checked | iOS ✓ reproduced · Android ✓ reproduced (Pixel 7 emulator · Android 16, debug APK 1.1.1 (178); module 01+03 Android runs, 2026-09-29/30; added under the Android plan rule: a repeating iOS bug goes into the same report) |
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

- Signed in as a technician.
- A job for today, status New, that the technician has not viewed (in the run: `POST /job` with `isViewed: false`,
  job `QA-AUTO-0924-104122-UNVIEWED`). The Jobs screen has loaded it: the card shows the red "Updated" banner.

## Steps to reproduce

1. On the Jobs list, pull down to refresh — the card shows "Updated".
2. Tap the calendar icon; pull down to refresh — today's card shows "Updated".
3. Tap the card — the job details open.
4. Go back to the calendar.
5. Tap the list icon; pull down to refresh.

## Actual result

After step 5 the card still shows the red "Updated" banner, although the server reports the job as viewed
(`GET /job/{id}`: `isViewed=True`, `updatedAt=2026-09-24T07:45:23.953Z` — the moment of step 3; the list refresh in
step 5 started at 07:45:26, UTC).
// [1-list-after-viewing-still-updated.png](evidence/BUG-ORDL-003/ios/1-list-after-viewing-still-updated.png)

## Expected result

SRS §3.1.3.1 FR-ORD-D-04: "An “Updated” indicator shall be displayed if the order content has changed since received
to a technician. Indicator disappears after a technician navigates outside a screen." — after step 4 the job is no
longer "Updated": the card in the list (and in the calendar) shows no banner.

## Frequency

- [x] Always — **3 of 3 attempts** (automated runs 1–3 of TC-ORDL-005, 2026-09-24, three separate seeds). Runs 2 and 3
  are confirmed by the drawn screen (banner fill 2.7 % of the screen, evidence 1) and by the server state
  (`isViewed=True`); run 1 by the screen tree only.
- Android: **3 of 3** (TC-ORDL-005, module 01+03 Android runs 4–6): the tree has "Updated" and it is drawn (banner fill
  2.45 % of the screen) after the details were opened; the server reports the job as viewed.

## Crash? ANR?

- [x] No crash

## Evidence

1. Screenshot after step 5: [evidence/BUG-ORDL-003/ios/1-list-after-viewing-still-updated.png](evidence/BUG-ORDL-003/ios/1-list-after-viewing-still-updated.png)
   (test jobs only, no personal data).
2. Server state after step 5 (attached to the run report): `isViewed=True updatedAt=2026-09-24T07:45:23.953Z`.
3. Step timeline from the run report (UTC): details opened 07:45:23.25–24.31; back 07:45:24.31; list refresh
   07:45:26.11–29.05; card read 07:45:29.60 — "Updated" present.
4. Android: [evidence/BUG-ORDL-003/android/list-after-viewing-still-updated.png](evidence/BUG-ORDL-003/android/list-after-viewing-still-updated.png)
   (run 6; test jobs only).
- **Not determined:** whether the calendar's own pull-to-refresh clears the banner — **by code reading only**, not
  observed.

## Workaround

Pull down to refresh inside the calendar view, or close and reopen the app (by code reading: both reload the calendar
week).

## Regression info

- Last known good version: unknown.
- First broken version: unknown.
- Recon 4 (2026-09-24) recorded "Updated gone after the details and a refresh" from the screen tree only; that reading
  is superseded by this evidence (the tree after a back navigation is unreliable — TD-JOBS-003).

## Related

- SRS §3.1.2.1 FR-ORD-06: "Special indicators (e.g., Updated) shall be displayed when applicable."
- SRS §3.1.3.1 FR-ORD-D-04 (quoted above).
- Checklist: `CHK-ORDL-022`, `CHK-ORDL-056` ([../order-list-checklist.md](../order-list-checklist.md)).
- Test case: `TC-ORDL-005` ([../order-list-test-cases.md](../order-list-test-cases.md)) — the regression check, red
  until the fix.
- Same root as [BUG-ORDL-001](BUG-ORDL-001.md) (a list reload does not reload the calendar week); a different symptom —
  here the wrong state shows **in the list itself** and on the normal "open a job, go back" path.
- Invariant: none fits — missing invariant: "a job the technician has viewed carries no 'Updated' after the next
  refresh".
- Tracker: not filed (no tracker configured).

> **When this bug is verified fixed:** re-verify with the steps above on the fixed build and keep the regression check
> TC-ORDL-005.
