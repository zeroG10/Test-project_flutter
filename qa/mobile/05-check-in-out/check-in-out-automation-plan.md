# Automation plan — Check-in / Check-out (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/05-check-in-out/check-in-out-checklist.md`
> (40 items, `CHK-CHIO-001…040`, imported 2026-09-24) **plus CHK-ORDD-023…047** moved here from module 04 (owner,
> Q-ORDD-1). The **Selected CHK IDs** table is the contract for `prompts/mobile/03`. Date: 2026-09-24. Owner:
> mykola.zhuchenko. **Status: draft — waits for the owner (Q-CHIO-1…4 in [check-in-out-questions.md](check-in-out-questions.md))
> and recon 6.**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| App build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Feature codes | `CHIO` (+ `ORDD` 023…047) |
| Scope decision | breadth, as modules 01–04; status transitions New → In progress and Submitted → (after check-out) are part of the job-status block agreed for modules 03–07 |
| Oracle model | accepted production baseline; SRS §3.1.3.3 (FR-CIO-01…10) and §3.1.3.1.1 (FR-LOC-01…14) explain; Figma 2451:83073 / 2451:83083 decide the confirmation screens; D-ORDD-9 (the app's location flow) accepted 2026-09-24; **the server record** (`GET /job/{id}`: status, `checkInDate`, `userLocation`, `checkOutDate`, `checkOutLocation`) decides what was stored |

## Step 0 — Input quality

**Overall: Medium.** Stable IDs; the confirmation screens in code and Figma agree word for word; the check-in start on
the simulator is known from recon 5b (system prompt → "Location disabled" on refusal). **Unknown until recon 6:** whether
the app accepts the simulator's location at all (it blocks mocked fixes — D-ORDD-9; iOS marks simulated fixes), the
status after check-out (D-CHIO-4), the manual-entry dialog on a device without a fix (15 s timeout in code), and the
shape of `userLocation` / `checkOutLocation` after real check-ins. Network-error items need network control the iOS
simulator does not give (Q-CHIO-3); PF e-mails are not visible to the app (Q-CHIO-2).

## Step 1 — Readiness: **Ready with conditions**

Text locators for every button and text of the two confirmation screens and the location dialogs; the X of the
confirmation screen is an unlabelled `IconButton` (app code audit §3 — the only unnamed button in its app bar).
Conditions: recon 6 (Q-CHIO-1); the owner's word on Q-CHIO-2…4.

## Step 2 — Approach: **Hybrid (UI-first; API for setup, cleanup and the stored record)**

Jobs are created through `POST /job` directly in the status a test needs (New for check-in, Submitted for check-out);
check-in / check-out happen **only through the UI**; the stored result is read back through `GET /job/{id}` (status,
dates, `userLocation`, `checkOutLocation`). The device location is set per test with `xcrun simctl location`
(at the job site / far away / none); the location permission is reset with `xcrun simctl privacy` (as TC-ORDD-005).

## Step 3–4 — Candidate matrix (40 + 25 items)

Status legend as in the Auth plan. **needs recon 6** = decided by what recon 6 shows; **Q-4** = depends on Q-CHIO-4
(the simulator's location blocked as mocked).

| CHK ID | Scenario (short) | Automation Level | ROI | Stability | Risk | Automation Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|---|---|---|
| CHK-CHIO-001 | check-in confirmation screen shown | E2E UI + API setup | H | M | H | Good Candidate | P0 | TC-CHIO-001 | reached through manual entry (no location) — works on the simulator whatever Q-4 says |
| CHK-CHIO-002 | check-out confirmation screen shown | E2E UI + API setup | H | M | H | Good Candidate | P1 | TC-CHIO-003 | from a **Submitted** job (D-CHIO-1) |
| CHK-CHIO-003 | X cancels | E2E UI + API setup | M | M | M | Medium Candidate | P2 | TC-CHIO-002 | unlabelled X — the only unnamed app-bar button |
| CHK-CHIO-004…006 | title, primary message, supporting text | E2E UI + API setup | M | H | L | Good Candidate | P1 | TC-CHIO-001, -003 | texts as Figma (D-CHIO-3) |
| CHK-CHIO-007 | Cancel aborts check-in, status unchanged | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-002 | status from `GET /job/{id}` |
| CHK-CHIO-008 | Cancel aborts check-out, status unchanged | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-004 | |
| CHK-CHIO-009 | X = Cancel | E2E UI + API | M | M | M | Medium Candidate | P2 | TC-CHIO-002 | as -003 |
| CHK-CHIO-010 | check-in time recorded | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-001 | `checkInDate` within the test's window |
| CHK-CHIO-011, -012 | GPS captured, method GPS | E2E UI + API | H | L | H | Q-4 | P1 | TC-CHIO-007 | the simulator's fix may be blocked as mocked |
| CHK-CHIO-013 | method Manual without GPS | E2E UI + API | H | M | H | Good Candidate | P1 | TC-CHIO-001 | `userLocation.method` |
| CHK-CHIO-014 | status In progress after check-in | E2E UI + API | H | H | H | Good Candidate | P0 | TC-CHIO-001 | UI badge + server |
| CHK-CHIO-015 | e-mail to PF after check-in | Manual | M | – | M | Q-CHIO-2 | P3 | — | not visible to the app |
| CHK-CHIO-016 | check-out time recorded | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-003 | `checkOutDate` |
| CHK-CHIO-017, -018 | GPS on check-out, method GPS | E2E UI + API | H | L | H | Q-4 | P2 | TC-CHIO-007 | as -011 |
| CHK-CHIO-019 | manual check-out | E2E UI + API | H | M | H | Good Candidate | P1 | TC-CHIO-003 | `checkOutLocation.method` |
| CHK-CHIO-020 | status after check-out | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-003 | value from recon 6 (D-CHIO-4) |
| CHK-CHIO-021 | e-mail to PF after check-out | Manual | M | – | M | Q-CHIO-2 | P3 | — | |
| CHK-CHIO-022 | check-in starts the location flow | E2E UI + API setup | H | H | H | Good Candidate | P1 | TC-ORDD-005 | already proven (recon 5b, run 2) — tag the existing test |
| CHK-CHIO-023 | check-out starts the location flow | E2E UI + API setup | H | M | H | Good Candidate | P2 | TC-CHIO-003 | |
| CHK-CHIO-024 | manual allowed when GPS denied / unavailable | E2E UI + API | H | M | H | Good Candidate (partial) | P1 | TC-CHIO-001 | **unavailable** → manual entry; **denied** → no manual entry (D-CHIO-5) |
| CHK-CHIO-025, -026 | manual check-in / check-out flagged | E2E UI + API | H | M | H | Good Candidate | P1 | TC-CHIO-001, -003 | `method` in the record |
| CHK-CHIO-027…032 | errors, retry, no timestamp → no completion | Manual | M | – | H | Q-CHIO-3 | P3 | — | network / server fault injection not available on the simulator |
| CHK-CHIO-033, -034 | record keeps Order ID and User ID | E2E UI + API | M | M | M | Medium Candidate (partial) | P2 | TC-CHIO-001, -003 | the record is on the job (Order ID); `GET /job/{id}` returns `userId` null (docs/api/dev-test-data.md) |
| CHK-CHIO-035 | action type stored correctly | E2E UI + API | M | H | M | Good Candidate | P2 | TC-CHIO-001, -003 | check-in → `userLocation`, check-out → `checkOutLocation` |
| CHK-CHIO-036 | timestamp = confirmation time | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-001 | ±60 s of the tap |
| CHK-CHIO-037 | GPS coordinates stored | E2E UI + API | H | L | H | Q-4 | P2 | TC-CHIO-007 | |
| CHK-CHIO-038 | responsive during slow GPS / network | Manual | L | – | L | Q-CHIO-3 | P3 | — | |
| CHK-CHIO-039 | rapid taps → one event | E2E UI + API | M | L | H | needs recon 6 | P2 | TC-CHIO-006 | a double tap on Confirm; the server keeps one record — the app's request count from its debug log is diagnosis only |
| CHK-CHIO-040 | no action invalid for the status | E2E UI + API setup | H | H | H | Good Candidate | P1 | TC-CHIO-005 | New → Check in only; In progress → neither; Submitted → Check out only |
| CHK-ORDD-023 | own "Enable Location Services" prompt first | — | – | – | – | Skipped (D-ORDD-9) | – | — | the app shows the system prompt directly (recon 5b) |
| CHK-ORDD-024 | the prompt explains why | E2E UI + API setup | M | H | M | Good Candidate | P2 | TC-ORDD-005 | the system prompt's text is the app's usage description — tag the existing test |
| CHK-ORDD-025, -026 | Enable → OS dialog; Cancel → continue without GPS | — | – | – | – | Skipped (D-ORDD-9) | – | — | no own prompt; Cancel ends the check-in |
| CHK-ORDD-027 | "Location disabled" when location is off | E2E UI + API setup | M | M | M | Good Candidate (partial) | P2 | TC-ORDD-005 | shown after a refusal (recon 5b); device-wide Location Services off — needs recon 6 |
| CHK-ORDD-028 | Go to settings opens the settings | E2E UI + API setup | M | M | L | Good Candidate | P3 | TC-CHIO-008 | Settings app in the foreground |
| CHK-ORDD-029 | Cancel → flow continues without GPS | — | – | – | – | Skipped (D-ORDD-9) | – | — | Cancel ends the check-in |
| CHK-ORDD-030…035 | GPS captured, compared, mismatch alert, Got it / Cancel | E2E UI + API | H | L | H | Q-4 | P1 | TC-CHIO-007, -009 | location at the site / 5 km away |
| CHK-ORDD-036…040 | manual prompt, text input, saved, flagged, job goes on | E2E UI + API | H | M | H | Good Candidate | P1 | TC-CHIO-001 | no location on the simulator → 15 s → "Enter location manually" |
| CHK-ORDD-041 | a notice when location cannot be read | E2E UI + API setup | M | M | M | Good Candidate | P2 | TC-CHIO-001 | the manual dialog's "We can't detect your location automatically" |
| CHK-ORDD-042 | "GPS not confirmed" flag | E2E UI + API | M | M | M | Good Candidate (partial) | P2 | TC-CHIO-001 | `method` = manual is the flag the server keeps — recon 6 |
| CHK-ORDD-043 | permission failure does not stop the job | — | – | – | – | Skipped (D-ORDD-9) | – | — | refusal → the check-in is cancelled until the setting changes |
| CHK-ORDD-044 | record has the method | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-001 | |
| CHK-ORDD-045, -046 | coordinates, horizontal accuracy with GPS | E2E UI + API | H | L | H | Q-4 | P2 | TC-CHIO-007 | |
| CHK-ORDD-047 | accurate timestamp | E2E UI + API | H | H | H | Good Candidate | P1 | TC-CHIO-001 | as CHK-CHIO-036 |

## Step 5 — Best first candidates

1. TC-CHIO-001 — manual check-in end to end (no location): the path the simulator can always run; P0.
2. TC-CHIO-005 — which action each status allows (status block of modules 03–07).
3. TC-CHIO-003 / -004 — check-out from Submitted, and its Cancel.
4. TC-CHIO-002 — Cancel / X leave the job New.
5. TC-CHIO-007 / -009 — GPS at / away from the site (after Q-CHIO-4).

## Step 5b — Selected CHK IDs (handoff to prompts/mobile/03)

**Draft: about 29 of 40 CHIO + 14 of 25 ORDD in ~9 TCs**, final after recon 6 and Q-CHIO-1…4. GPS-dependent items (Q-4):
CHK-CHIO-011, -012, -017, -018, -037; CHK-ORDD-030…035, -045, -046.

## Step 6 — Manual-only / Skipped

Manual: CHK-CHIO-015, -021 (Q-CHIO-2), -027…-032, -038 (Q-CHIO-3). Skipped (D-ORDD-9, accepted): CHK-ORDD-023, -025, -026,
-029, -043.

## Step 7 — API support

| CHK / TC | Scenario | API action | Endpoint (operationId) | Notes |
|---|---|---|---|---|
| all | jobs in New / In progress / Submitted | create before, delete in `finally` | `POST /job` (`JobController_create`, `statusType`) → `DELETE /job/{id}` (`JobController_remove`) — verified | a check-in / check-out changes the job; each such TC gets its own job |
| all | the stored result | read | `GET /job/{id}` (`JobController_findOne`): `statusType`, `checkInDate`, `userLocation`, `checkOutDate`, `checkOutLocation` | shapes confirmed in recon 6 |

## Step 8 — Stable selectors

Text for every button and text (confirmation screens, location dialogs, manual entry: "Enter location manually",
field hint "Enter address or coordinates (lat, lng)", "Confirm"); the X of the confirmation screens is unnamed
(testability defect, as TD-ORDD-001); the system prompt through `respectSystemAlerts` (module 04 pages reused).

## Step 9 — Test data

About 8 jobs per module run: New × 4–5 (each check-in consumes one), In progress × 1, Submitted × 2; all `QA-AUTO-*`,
deleted in `finally`. Device location set per test (`xcrun simctl location … set <lat,lng>` / `clear`); location
permission reset per test where the system prompt is needed.

## Step 10 — Authentication & session

`ui_login` (relaunch, login only when signed out); no test signs out.

## Step 11 — Isolation

Every TC that checks in or out owns its job. The simulator's location and the app's location permission are global
state: each TC sets both at its start and the module restores "location set at the job site, permission granted"
at the end.

## Step 12 — Plan

Tests `automation/mobile/tests/shared/test_check_in_out.py`; maps `confirm_check_map.py` (both confirmation screens),
`manual_location_map.py`, reuse of `location_dialogs_map.py`; helper `AppControl.set_location(lat, lng | None)`;
fixture `check_seed`. Estimate ~9 TCs × 1.5–2.5 h ≈ 14–22 h incl. recon 6.

## Step 13–14 — Runtime notes, CI

The manual path waits the app's 15 s GPS timeout on purpose; alert auto-accept is off during every location flow
(module 04 lesson). CI: nothing new.

## Step 15 — Risks

| Category | Risk | Impact | Action |
|---|---|---|---|
| Technical | the simulator's fix is blocked as mocked | no GPS path on iOS | Q-CHIO-4: Blocked on iOS + Android / device, or the app's debug toggle |
| Data | a check-in / check-out that the backend follows with e-mails to the PF | mail to `qa-auto+pf@example.com` (a reserved test domain) | PF address in the reserved example.com domain |
| Environment | global simulator state (location, permission) leaks between tests | order-dependent results | set at every TC start; restore at module end |

## Step 16 — Final recommendation

Recon 6 first (Q-CHIO-1), then the owner's word on Q-CHIO-2…4, then the test cases. **First sprint:** TC-CHIO-001…005.
