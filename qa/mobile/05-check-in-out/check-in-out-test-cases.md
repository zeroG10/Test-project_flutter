# Test cases — Check-in / Check-out (mobile)

> Structured, alias-based test cases for the CHK IDs selected in
> [check-in-out-automation-plan.md](check-in-out-automation-plan.md). Format:
> [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: draft — written after recon 6 / 6b / 6c ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md));
> automated on the owner's "виконуй" (2026-09-24), validation by the owner together with the first results.**

| Field | Value |
|---|---|
| Feature | Check-in / Check-out — confirmation screens, location validation (on site / away), the stored record, actions per status, the mock-location guard |
| Platform | cross-platform (Flutter app driven by native drivers) — iOS first, then Android |
| Source checklist | `qa/mobile/05-check-in-out/check-in-out-checklist.md` (CHK-CHIO-001…041) + CHK-ORDD-023…047 (from module 04) |
| Devices | iPhone 17 · iOS 26.5 (simulator); Android emulator in the Android phase |
| Build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko |
| Last updated | 2026-09-24 |

**Conventions used in this file**

- **The mock-location switch (owner, Q-CHIO-5).** The iOS simulator's location is always reported as simulated and the
  app refuses it ("Location could not be trusted", recon 6 / 6b). Every TC below that completes a location step runs
  with the app's own debug preference `flutter.mock_location_override_enabled` = true (the app's settings, written while
  it is closed — code and build unchanged) and restores it to false afterwards. **TC-CHIO-008 runs without it** and proves
  the guard itself. On a real device / the Android emulator the switch is not needed.
- **Device location** is set per TC with `xcrun simctl location <udid> set <lat>,<lng>`: *on site* = the job's
  coordinates (40.748440, -73.985664); *away* = 0.05° north (~5.5 km). The location permission is granted up front
  (`xcrun simctl privacy <udid> grant location <bundle>`), so no system prompt interrupts these TCs (the prompt itself is
  TC-ORDD-005).
- **The stored record** is read through `GET /job/{id}` (`JobController_findOne`): `statusType`, `checkInDate`,
  `userLocation`, `checkOutDate`, `checkOutLocation` (shapes from recon 6c).
- **Jobs** = the module seed `check_seed` (`POST /job` in the status each TC needs; `DELETE /job/{id}` in `finally`).
  Every TC that checks in or out owns its job.
- **Manual location entry** (CHK-CHIO-013, -019, -024 "unavailable", -025, -026; CHK-ORDD-036…042) — **not reachable on the
  simulator** (it always has a fix, recon 6b); **verified by the owner on a real device** (2026-09-24) → skipped here with
  that comment.

---

## TC-CHIO-001 — On site, check-in shows the confirmation screen, and Confirm starts the job with a GPS record

| Field | Value |
|---|---|
| ID | TC-CHIO-001 |
| Source CHK IDs | CHK-CHIO-001, -004, -005, -006, -010, -011, -012, -014, -022, -035, -036, -037; CHK-ORDD-030, -044, -045, -046, -047 |
| Platforms | ios, android |
| Priority | P0 |
| Preconditions | signed in; location permission granted; mock-location switch ON; device location **on site**; `{{job.gps}}` New |
| Oracle | spec — SRS §3.1.3.3 FR-CIO-01, -02, Data Requirements; §3.1.3.1.1 FR-LOC-08, -09; spec — figma:2451:83073 (`Job details_Confirm check in`); accepted D-CHIO-2 (location before confirmation); data — `GET /job/{id}` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.gps.jobId}}] | — | the details open |
| 2 | click | job-details.check-in | — | — |
| 3 | expect-text | confirm-check.title | — | Confirm check in |
| 4 | expect-text | confirm-check.primary | — | Check in and start |
| 5 | expect-text | confirm-check.supporting | — | Confirm you are on site to begin the job. |
| 6 | expect-visible | confirm-check.close | — | the X at the top left; `Cancel` and `Confirm` at the bottom |
| 7 | click | confirm-check.confirm | — | note the time of the tap |
| 8 | expect-text | job-details.status | — | In progress |
| 9 | api | `GET /job/{id}` (`JobController_findOne`) | — | `statusType` = `in_progress`; `checkInDate` within 60 s of step 7; `userLocation.method` = `gps`; `userLocation.coordinates` = the device location; `horizontalAccuracyM` present |

**Notes:** CHK-CHIO-015 (e-mail to the PF) — manual (Q-CHIO-2).

---

## TC-CHIO-002 — X and Cancel on the check-in confirmation leave the job New

| Field | Value |
|---|---|
| ID | TC-CHIO-002 |
| Source CHK IDs | CHK-CHIO-003, -007, -009 |
| Priority | P1 |
| Preconditions | as TC-CHIO-001; `{{job.cancel}}` New |
| Oracle | spec — SRS FR-CIO-03 ("Selecting Cancel or closing the screen shall: Abort the check-in; Leave the order status unchanged") |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.cancel.jobId}}] | — | the details open |
| 2 | click | job-details.check-in | — | "Confirm check in" |
| 3 | click | confirm-check.close | — | back on the details |
| 4 | expect-visible | job-details.check-in | — | Check in again; status New |
| 5 | click | job-details.check-in | — | "Confirm check in" |
| 6 | click | confirm-check.cancel | — | back on the details |
| 7 | expect-text | job-details.status | — | New |
| 8 | api | `GET /job/{id}` | — | `statusType` = `new`, no `checkInDate` |

---

## TC-CHIO-003 — Away from the site, check-in is stopped with "You are not at the job site"; Got it and Cancel leave the job New

| Field | Value |
|---|---|
| ID | TC-CHIO-003 |
| Source CHK IDs | CHK-ORDD-031, -032, -033, -034, -035 |
| Priority | P1 |
| Preconditions | as TC-CHIO-001 but device location **away** (~5.5 km); `{{job.far}}` New |
| Oracle | spec — SRS FR-LOC-09, -10; accepted D-ORDD-9 (the app's title "You are not at the job site", radius 100 m) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.far.jobId}}] | — | the details open |
| 2 | click | job-details.check-in | — | — |
| 3 | expect-text | not-at-site.title | — | You are not at the job site |
| 4 | expect-text | not-at-site.message | — | Your GPS location is accurate, but you don't appear to be at the registered job site. Please move to the site to check in. |
| 5 | click | not-at-site.got-it | — | back on the details |
| 6 | expect-text | job-details.status | — | New |
| 7 | click | job-details.check-in | — | the alert again |
| 8 | click | not-at-site.cancel | — | back on the details |
| 9 | api | `GET /job/{id}` | — | `statusType` = `new` |

---

## TC-CHIO-004 — On site, check-out from a Submitted job shows its confirmation, and Confirm completes the job with a GPS record

| Field | Value |
|---|---|
| ID | TC-CHIO-004 |
| Source CHK IDs | CHK-CHIO-002, -016, -017, -018, -020, -023 |
| Priority | P1 |
| Preconditions | as TC-CHIO-001; `{{job.submitted}}` Submitted |
| Oracle | spec — SRS FR-CIO-04, -05; figma:2451:83083 (`Job details_Confirm check out`); accepted D-CHIO-1 (check-out from Submitted), D-CHIO-4 (Completed); data — `GET /job/{id}` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.submitted.jobId}}] | — | the details open |
| 2 | click | job-details.check-out | — | — |
| 3 | expect-text | confirm-check.title | — | Confirm check out |
| 4 | expect-text | confirm-check.primary | — | Check out and finish |
| 5 | expect-text | confirm-check.supporting | — | Confirm you are ready to finish the job. |
| 6 | click | confirm-check.confirm | — | note the time of the tap |
| 7 | expect-visible | jobs-list.root | — | the Jobs list (the app returns there) |
| 8 | api | `GET /job/{id}` | — | `statusType` = `completed`; `checkOutDate` within 60 s of step 6; `checkOutLocation.method` = `gps`, its coordinates = the device location |

**Notes:** a completed job is no longer listed (module 03). CHK-CHIO-021 (e-mail) — manual (Q-CHIO-2).

---

## TC-CHIO-005 — Cancel on the check-out confirmation keeps the job Submitted

| Field | Value |
|---|---|
| ID | TC-CHIO-005 |
| Source CHK IDs | CHK-CHIO-008 |
| Priority | P1 |
| Preconditions | as TC-CHIO-004; `{{job.kept}}` Submitted |
| Oracle | spec — SRS FR-CIO-06 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.kept.jobId}}] | — | the details open |
| 2 | click | job-details.check-out | — | "Confirm check out" |
| 3 | click | confirm-check.cancel | — | back on the details |
| 4 | expect-visible | job-details.check-out | — | Check out is still offered |
| 5 | api | `GET /job/{id}` | — | `statusType` = `submitted`, no `checkOutDate` |

---

## TC-CHIO-006 — Each status offers only its own action: New → Check in, In progress → none, Submitted → Check out

| Field | Value |
|---|---|
| ID | TC-CHIO-006 |
| Source CHK IDs | CHK-CHIO-040 |
| Priority | P1 |
| Preconditions | signed in; `{{job.far}}` New (after TC-CHIO-003), `{{job.in_progress}}` In progress, `{{job.kept}}` Submitted |
| Oracle | spec — SRS FR-ORD-D-08, FR-CIO-04; accepted D-CHIO-1 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.far.jobId}}] | — | New: `Check in` shown, `Check out` not |
| 2 | back | — | — | Jobs list |
| 3 | click | jobs-list.card[{{job.in_progress.jobId}}] | — | In progress: neither `Check in` nor `Check out` (`Submit deliverables` is the action) |
| 4 | back | — | — | Jobs list |
| 5 | click | jobs-list.card[{{job.kept.jobId}}] | — | Submitted: `Check out` shown, `Check in` not |

---

## TC-CHIO-007 — Two quick taps on Confirm start the job once

| Field | Value |
|---|---|
| ID | TC-CHIO-007 |
| Source CHK IDs | CHK-CHIO-039 |
| Priority | P2 |
| Preconditions | as TC-CHIO-001; `{{job.double}}` New |
| Oracle | spec — checklist CHK-CHIO-039; data — `GET /job/{id}` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.double.jobId}}] | — | the details open |
| 2 | click | job-details.check-in | — | "Confirm check in" |
| 3 | double-tap | confirm-check.confirm | — | — |
| 4 | expect-text | job-details.status | — | In progress — one details screen, no error |
| 5 | api | `GET /job/{id}` | — | `statusType` = `in_progress`, one `checkInDate`, one `userLocation` |

**Notes:** **partial** — the server keeps one record per job, so a second request, if one was sent, would overwrite it
rather than add a duplicate; the test proves the visible outcome and the single stored state.

---

## TC-CHIO-008 — Without the switch, a simulated location is refused with "Location could not be trusted" and the job stays New

| Field | Value |
|---|---|
| ID | TC-CHIO-008 |
| Source CHK IDs | CHK-CHIO-041 |
| Priority | P1 |
| Preconditions | signed in; location permission granted; **mock-location switch OFF** (default); device location on site; `{{job.guard}}` New |
| Oracle | app — accepted D-ORDD-9 / D-CHIO-6 (the mock-location guard), recon 6 / 6b; owner decision Q-CHIO-5 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.guard.jobId}}] | — | the details open |
| 2 | click | job-details.check-in | — | — |
| 3 | expect-text | mock-location.title | — | Location could not be trusted |
| 4 | expect-text | mock-location.message | — | Your device is reporting a simulated (mock) location, so it cannot be used to verify you are on site. Turn off any mock-location app and try again. |
| 5 | click | mock-location.got-it | — | back on the details |
| 6 | api | `GET /job/{id}` | — | `statusType` = `new` |

**Notes:** on a real device this TC needs a mock-location app (Android: developer options); on the iOS simulator the
simulated location is enough.

---

## TC-CHIO-009 — After refusing location, "Go to settings" opens the device settings

| Field | Value |
|---|---|
| ID | TC-CHIO-009 |
| Source CHK IDs | CHK-ORDD-028 |
| Priority | P3 |
| Preconditions | signed in; location permission **reset** (not determined); `{{job.guard}}` New (after TC-CHIO-008) |
| Oracle | spec — SRS FR-LOC-06 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.guard.jobId}}] | — | the details open |
| 2 | click | job-details.check-in | — | the system prompt (as TC-ORDD-005) |
| 3 | click | location-prompt.dont-allow | — | "Location disabled" |
| 4 | click | location-disabled.go-to-settings | — | — |
| 5 | expect-visible | app | — | the Settings app is in the foreground |
| 6 | open | app | — | back to the app (the location permission is granted again for the next TCs) |

---

## Aliases used

| Alias | Screen | ios map |
|---|---|---|
| jobs-list.card[{{jobId}}], jobs-list.root | jobs-list | yes |
| job-details.check-in, .status, .check-out | job-details | yes / **MISSING** `Button 'Check out'` |
| confirm-check.title, .primary, .supporting, .cancel, .confirm, .close | confirmation screens | **MISSING** — `Other '<title>'` (Header), `StaticText`s, `Button 'Cancel'` / `'Confirm'`, X = the only unnamed app-bar button (recon 6c) |
| not-at-site.title, .message, .got-it, .cancel | app dialog | **MISSING** — texts as recon 6c |
| mock-location.title, .message, .got-it | app dialog | **MISSING** — texts as recon 6 |
| location-prompt.dont-allow, location-disabled.go-to-settings | system / app | yes (module 04) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-CHIO-001, -004…-006, -010…-012, -014, -035…-037 | TC-CHIO-001 | with the mock-location switch (Q-CHIO-5) |
| CHK-CHIO-022 | TC-CHIO-001, TC-ORDD-005 | |
| CHK-CHIO-003, -007, -009 | TC-CHIO-002 | |
| CHK-CHIO-002, -016…-018, -020, -023 | TC-CHIO-004 | Completed (D-CHIO-4) |
| CHK-CHIO-008 | TC-CHIO-005 | |
| CHK-CHIO-040 | TC-CHIO-006 | |
| CHK-CHIO-039 | TC-CHIO-007 | **partial** |
| CHK-CHIO-041 | TC-CHIO-008 | the guard, without the switch |
| CHK-ORDD-030, -044…-047 | TC-CHIO-001 | |
| CHK-ORDD-031…-035 | TC-CHIO-003 | |
| CHK-ORDD-028 | TC-CHIO-009 | |
| CHK-ORDD-024, -027 | TC-ORDD-005 | the system prompt's explanation; "Location disabled" after a refusal (**partial** — device-wide location off not reproduced) |

**Not automated, with reasons:** CHK-CHIO-013, -019, -024, -025, -026, CHK-ORDD-036…-042 — manual entry is unreachable on the
simulator; **verified by the owner on a real device**. CHK-CHIO-015, -021 — PF e-mail, manual (Q-CHIO-2). CHK-CHIO-027…-032,
-038 — network / server faults, manual (Q-CHIO-3). CHK-CHIO-033, -034 — `GET /job/{id}` does not return the user id of the
record (docs/api/dev-test-data.md), so "the correct User ID" cannot be proven through the API. CHK-ORDD-023, -025, -026, -029,
-043 — skipped, the app's flow differs (D-ORDD-9, accepted).
