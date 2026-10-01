# Order list — Android offline test cases (step 5)

> Scope/selection: owner, android-plan §2.5 — automate all 36 `android-stage` checks
> (`qa/mobile/ios/not-automated.md`). This file covers the Order list module's offline group:
> CHK-ORDL-031, -032, -033, -034, -035, -064, -065. Format:
> [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md) + the mobile rows
> from [test-cases-mobile.md](../../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`.
> IDs continue the file's numbering from [../order-list-test-cases.md](../order-list-test-cases.md)
> (last: TC-ORDL-015) — below starts at TC-ORDL-016. Source recon:
> [qa/shared/recon-2026-10-01-android-offline.md](../../../shared/recon-2026-10-01-android-offline.md)
> (recon A2, 2026-10-01) — discovery of what is on screen, never the oracle; oracle = SRS + owner
> decisions. Android Order list differences unrelated to offline:
> [../android/order-list-questions.md](order-list-questions.md) (D-ORDL-A1…A3 — none of them
> affect this file).
>
> **Status: validated by the owner 2026-10-01 (step 5 gate: D-OFF-1…9 answered, no remarks on the TCs).**

| Field | Value |
|---|---|
| Feature | The Jobs list and the weekly calendar without network: cached data, the offline banner, retry, recovery when connectivity returns, and the empty state with no cache |
| Source checklist | `qa/mobile/03-order-list/order-list-checklist.md` — CHK-ORDL-031, -032, -033, -034, -035, -064, -065 |
| Platform | android |
| Devices / build | Pixel 7 · Android 16 (API 36), emulator `Pixel_7_API_36` (`-dns-server 8.8.8.8,1.1.1.1`) · Appium 3.4.2 + UiAutomator2 · `[DEV] CT Mobile` 1.1.1 (178) debug, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko · Last updated 2026-10-01 |

**Conventions**

- **One job per test**, created through `POST /job` (`JobController_create`, `userId={{tech.user_id}}`)
  as the online file does — status `new`, today — `{{job.new}}` — while the device is still online;
  deleted after the test. TC-ORDL-018 additionally creates `{{job.offline_created}}` **mid-test**,
  through the API, while the device stays offline.
- **Network is a step**: `open | device.network | off` / `on` (`Adb.offline()` /
  `Adb.online()`, `helpers/android/device.py`). A TC that ends offline by design still leaves the
  network **ON** afterwards — `Adb.offline()` restores it in `finally`, no extra step needed. A TC
  that proves "network back" makes the `on` step part of the scenario.
- **Priming the cache**: before going offline, the list is pulled to refresh and — separately — the
  calendar is refreshed too (BUG-ORDL-001: a list refresh does not reach the calendar), so both
  caches hold the seed job before the device goes offline.
- **The offline banner** (`offline-banner.*`, recon row 1) appears on every screen; its settled
  message is "No internet connection." (the first ~5 s show a different, transient text — recon
  row 1). No step in this file taps the top content strip the banner covers (D-OFF-7 — see the
  photo report / notes android files), so no TC here needs `offline-banner.close`.
- **The cold-start wait**: recon row 6 measured the cache appearing 10–15 s after a cold start
  offline (the app waits out a 10 s network timeout first — D-OFF-8, already the subject of
  BUG-ORDL-002 for list ordering, not re-asserted here); the TCs below allow a generous ~20–30 s
  wait.
- **Card / date format**: as the online file — a card is found by its `jobId`, never by type;
  dates are the device time zone.

---

## TC-ORDL-016 — Offline: the cached list and the cached calendar are shown with the offline banner, including after a cold start

| Field | Value |
|---|---|
| ID | TC-ORDL-016 |
| Title | Offline: the cached list and the cached calendar are shown with the offline banner, including after a cold start |
| Source CHK IDs | CHK-ORDL-031, CHK-ORDL-064, CHK-ORDL-033 |
| Platforms | android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, signed in; a cold start (terminate + relaunch, still offline) partway through |
| Permissions | notifications: granted |
| Network | online Wi-Fi (priming) → offline (adb) for the rest of the TC |
| Preconditions | signed in; seed job `{{job.new}}` (status `new`, today) exists; the list pulled to refresh and the calendar refreshed separately while still online (BUG-ORDL-001), so both caches are primed before the device goes offline |
| Oracle | spec — SRS §3.1.2.1 FR-ORD-09 "Cached orders shall be displayed when offline, if available."; FR-CAL-W-10 "When offline, cached calendar and order data shall be displayed if available."; §3.3.1 "...display a 'No Internet connection' message."; CHK-ORDL-031, CHK-ORDL-064, CHK-ORDL-033; observed (discovery, not proof) — recon A2 rows 1, 6, 7, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network disabled |
| 2 | swipe | jobs-list.root | down | pull to refresh while offline |
| 3 | expect-visible | jobs-list.card[{{job.new.jobId}}] | — | cached card still shown, no crash (CHK-ORDL-031) |
| 4 | expect-text | offline-banner.message | — | contains: "No internet connection." — the banner's settled message (CHK-ORDL-033; the transient "Slow or no internet connection…" phase is not asserted) |
| 5 | click | jobs-list.view-toggle | — | calendar, today selected |
| 6 | expect-visible | jobs-calendar.card[{{job.new.jobId}}] | — | cached calendar card shown (CHK-ORDL-064) |
| 7 | expect-visible | offline-banner.message | — | banner shown on the calendar too |
| 8 | open | app | terminate + launch (still offline) | app relaunches offline |
| 9 | wait-for | jobs-list.card[{{job.new.jobId}}] | — | visible within ~20–30 s (recon: 10–15 s; D-OFF-8) — cache shown after the cold start |
| 10 | expect-visible | offline-banner.message | — | still shown after the cold start |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness (`Adb.offline()` `finally`). Job deleted.
**Notes:** the card order after the cold start is not asserted — D-OFF-8 / BUG-ORDL-002 (the cached list is reversed vs. the online order; already the regression check in TC-ORDL-014). This TC only proves the cards and the banner are present.

---

## TC-ORDL-017 — Offline: pulling the list and tapping "Try again" keep the cached list, no crash

| Field | Value |
|---|---|
| ID | TC-ORDL-017 |
| Title | Offline: pulling the list and tapping "Try again" keep the cached list, no crash |
| Source CHK IDs | CHK-ORDL-034 |
| Platforms | android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | offline (adb) throughout (after the initial online load in Preconditions) |
| Preconditions | signed in; seed job `{{job.new}}` exists; the list pulled to refresh once while online (cache primed) |
| Oracle | spec — SRS §3.1.2.1 FR-ORD-08 "If orders fail to load due to a network error: An error message shall be displayed; The user shall be able to retry loading the list."; CHK-ORDL-034; observed (discovery, not proof) — recon A2 rows 1, 6, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network disabled |
| 2 | swipe | jobs-list.root | down | pull to refresh while offline (retry attempt 1) |
| 3 | expect-visible | jobs-list.card[{{job.new.jobId}}] | — | same cached list shown, no crash |
| 4 | expect-visible | offline-banner.try-again | — | "Try again" control present on the banner |
| 5 | click | offline-banner.try-again | — | retry tapped |
| 6 | expect-visible | jobs-list.card[{{job.new.jobId}}] | — | list unchanged, no crash |
| 7 | expect-visible | offline-banner.message | — | banner persists (network still off) |
| 8 | swipe | jobs-list.root | down | pull to refresh again (retry attempt 2) |
| 9 | expect-visible | jobs-list.card[{{job.new.jobId}}] | — | still stable — no crash after repeated retries (CHK-ORDL-034) |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness. Job deleted.
**Notes:** recon row 6: "«потягнути» офлайн — без помилки, список той самий" (pulling offline — no error, the same list) — this TC adds the banner's own "Try again" control to the same proof.

---

## TC-ORDL-018 — Network back: a job created through the API while offline appears in the list by itself, without a manual pull

| Field | Value |
|---|---|
| ID | TC-ORDL-018 |
| Title | Network back: a job created through the API while offline appears in the list by itself, without a manual pull |
| Source CHK IDs | CHK-ORDL-035 |
| Platforms | android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | offline (adb) → online Wi-Fi (step 5) |
| Preconditions | signed in; Jobs list open, already refreshed online; no `{{job.offline_created}}` job exists yet — it is created mid-test, through the API, while the device is offline |
| Oracle | spec — SRS §3.3.1 Offline Functionality "Automatic sync when connectivity is restored."; CHK-ORDL-035; not directly exercised in recon A2 (see Notes) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network disabled |
| 2 | expect-visible | offline-banner.message | — | offline banner shown |
| 3 | set | api.job | create via `POST /job` (`JobController_create`) → `{{job.offline_created}}` | created on the server; the device stays offline |
| 4 | expect-hidden | jobs-list.card[{{job.offline_created.jobId}}] | — | not shown yet — device still offline, nothing to sync |
| 5 | open | device.network | on | network restored; a "Connection restored" dialog for In progress jobs in the app's cache (also earlier ones deleted on the server — D-OFF-10) is closed with `connection-restored.cancel` if it comes within ~25 s |
| 6 | wait-for | jobs-list.card[{{job.offline_created.jobId}}] | — | visible within a generous wait (~30 s) — the app refreshes the list on reconnect, no manual pull (CHK-ORDL-035) |
| 7 | expect-hidden | offline-banner.message | — | banner gone now that the network is back |

**Postconditions / cleanup:** network ON. `{{job.offline_created}}` deleted.
**Notes:** recon A2 row 12 observed a reconnect-refresh behaviour only for the submit-deliverables "Connection restored" dialog (a different screen, module 07's TC-DLV-009), not for the Order list auto-refreshing on a newly created job. This TC is the first check of that specific flow; per doctrine rule 1/4, a red run first asks whether the expectation is wrong before anything is filed as a bug.

---

## TC-ORDL-019 — Offline with no jobs for the technician: list and calendar show "No jobs" with the offline banner

| Field | Value |
|---|---|
| ID | TC-ORDL-019 |
| Title | Offline with no jobs for the technician: list and calendar show "No jobs" with the offline banner |
| Source CHK IDs | CHK-ORDL-032, CHK-ORDL-065 |
| Platforms | android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | offline (adb) throughout |
| Preconditions | signed in; the technician has **no** active job — checked through `GET /job` (`JobController_findAll`, `userId={{tech.user_id}}`); leftover `QA-AUTO-*` jobs deleted first; if a foreign job is found the TC is **Blocked**, not Failed; the list pulled to refresh once while online, so there is no cached job data (matching the "no cache" scenario) |
| Oracle | spec — checklist CHK-ORDL-032 "...an appropriate message or indicator when no cached data is available offline. (placeholder for UX decision)", CHK-ORDL-065 (same, for the calendar) — no SRS FR defines the no-cache state; D-OFF-5 (owner-pending, recon A2); observed (discovery, not proof) — recon A2 rows 6, 7, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network disabled |
| 2 | expect-text | jobs-list.empty-state | — | "No jobs" — the same empty state as online (D-ORDL-2/3, accepted baseline for the online text) |
| 3 | expect-visible | offline-banner.message | — | banner shown over the empty state (CHK-ORDL-032) |
| 4 | click | jobs-list.view-toggle | — | calendar, today selected |
| 5 | expect-text | jobs-calendar.empty-state | — | "No jobs" — the empty state shown offline too (CHK-ORDL-065) |
| 6 | expect-visible | offline-banner.message | — | banner shown on the calendar too |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness. Nothing created.
**Notes:** the checklist text ("No orders") is the Sheet's literal wording; the app and the accepted online baseline both say "No jobs" (D-ORDL-2/3) — this TC follows the app, as the online file does throughout.
**Resolved D-OFF-5** — Owner 2026-10-01: «ок» — "No jobs" + the offline banner is the accepted UX decision.

---

## Aliases used

| Alias | Screen | android map | ios map |
|---|---|---|---|
| device.network | — (device control) | n/a — harness capability; `Adb.offline()` / `Adb.online()` exists (`helpers/android/device.py`) | n/a — no network control on the iOS simulator |
| app | — (launch / terminate / relaunch) | n/a | n/a |
| jobs-list.root, .view-toggle, .card[{{jobId}}], .empty-state | jobs-list | yes (step 3, 2026-09-29) | see `../order-list-test-cases.md` |
| jobs-calendar.root, .card[{{jobId}}], .empty-state | jobs-calendar | yes (step 3, 2026-09-29) | see `../order-list-test-cases.md` |
| offline-banner.message | offline banner (new, any screen) | **MISSING** — new (recon A2 row 1, 2026-10-01) | **MISSING** |
| offline-banner.try-again | offline banner | **MISSING** — new (recon A2 row 1, 2026-10-01) | **MISSING** |
| offline-banner.close | offline banner | **MISSING** — new (recon A2 row 16 / D-OFF-7, 2026-10-01); not used by a step in this file | **MISSING** |
| api.job | — (not a screen element) | `GET /job` / `POST /job` — same alias family as the online file | same |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech}}, {{tech.user_id}} | `automation/mobile/.env`, `GET /technician` | existing test technician, read-only — as the online file |
| {{job.new}} | `POST /job`, status `new`, today | as the online file's `jobs_seed`; one per test here, deleted after |
| {{job.offline_created}} | **new** — `POST /job`, created mid-test while the device is offline (TC-ORDL-018) | deleted through `DELETE /job/{id}` in cleanup |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-ORDL-031, CHK-ORDL-064, CHK-ORDL-033 | TC-ORDL-016 | one flow proves all three (list → pull offline → calendar → cold start) |
| CHK-ORDL-034 | TC-ORDL-017 | |
| CHK-ORDL-035 | TC-ORDL-018 | not directly exercised in recon A2 — see Notes |
| CHK-ORDL-032, CHK-ORDL-065 | TC-ORDL-019 | D-OFF-5, pending owner |

## Open questions

- Resolved **D-OFF-5** (owner 2026-10-01: «ок» — accepted)
  the owner's validation that "No jobs" (the same empty state as online) + the offline banner is
  the accepted reading of "an appropriate message or indicator... (placeholder for UX decision)"
  (step 5 gate).
- TC-ORDL-018 (CHK-ORDL-035) was not directly exercised in recon A2 — the recon's one reconnect
  observation (row 12) is the submit-deliverables "Connection restored" dialog on a different
  screen (module 07). This TC is the first check of the Order list's own reconnect-refresh
  behaviour; per doctrine, a red run first asks whether the expectation is wrong before any bug is
  filed.
- D-OFF-8 (reversed cache order, 10–15 s cold-start delay) is informational only in this file —
  already the subject of BUG-ORDL-002 for list ordering — and is not re-asserted by TC-ORDL-016's
  cold-start wait.
