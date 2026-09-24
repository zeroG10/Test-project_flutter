# Automation plan — Order list (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/03-order-list/order-list-checklist.md`
> (70 items: `CHK-ORDL-001…068` imported + `CHK-ORDL-069`, `-070` added 2026-09-24 on the owner's decisions). Reviewed copy for the module; the **Selected CHK IDs** table is the contract for
> `prompts/mobile/03` (test cases). Date: 2026-09-23. Owner: mykola.zhuchenko. **Status: draft — waits for the owner.**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| App build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Feature code | `ORDL` |
| Scope decision | breadth (owner, 2026-09-23) + the **job-status display block** agreed for modules 03–07: jobs created through the API directly in each status |
| Oracle model | accepted production baseline; SRS §3.1.2 + checklist explain; Figma `Jobs_List view` 2451:82604, `…_Empty` 2451:83514, `Jobs_Calendar view` 2451:82613, `…_empty` 2451:83469 decide the visual layer |

## Step 0 — Input quality

**Overall: Medium.** Stable IDs; recon 3b trees of the list and the calendar
(`qa/shared/recon-dumps/ios-2026-09-23/jobs_{list,calendar}.xml`); a verified data recipe (`POST /job` →
`DELETE /job/{id}`, `docs/api/dev-test-data.md`). A read-only look at the app code (`jobs_page.dart`,
`jobs_list_view.dart`, `jobs_calendar_view.dart`, `job_card.dart`, `jobs_bloc.dart`, `jobs_repository_impl.dart`,
`deep_link_service.dart`) and at the Figma frames shows **the checklist and the SRS are older than the app and the
design** in eight places (D-ORDL-1…8 in [order-list-questions.md](order-list-questions.md)): no status filters, "No
jobs" instead of "No orders", "Jobs" instead of "Orders", one address line instead of Site / City / State, no
"Unsubmitted" label, no month / year and no week arrows in the calendar. **These and D-ORDL-9 (link dialog wording) were
accepted by the owner on 2026-09-23** (the app is right; Submitted in the list and the calendar is correct). Offline items (7) assume network control the
iOS simulator does not offer.

## Step 1 — Readiness: **Ready with conditions**

Text locators for the title, tabs, day cells and cards (a card is one text element — its fields are parsed); the
list ↔ calendar toggle is the only unnamed button in the app bar (TD-JOBS-001). Conditions: a job fixture (new harness
code); the owner's word on the seed size (Q-ORDL-3) and on how TC-ORDL-012 gets its link (Q-ORDL-2); recon for two
unknowns (tab "selected" state in the tree, which day the calendar selects after a week swipe).

## Step 2 — Approach: **Hybrid (UI-first, API for setup / cleanup)**

Jobs are created through `POST /job` directly in the status a test needs and removed in `finally`; every assertion is
made through the UI. Deep links are opened with the app's own scheme `ctflutter://jobs/{key}` (no browser, no
universal-link verification).

## Step 3–4 — Candidate matrix (all 68 items)

Status legend as in the Auth plan. **deferred** = automatable, left out only by scope.

| CHK ID | Scenario (short) | Automation Level | ROI | Stability | Risk | Automation Status | Priority | Tags | TC | Reason / blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| CHK-ORDL-001 | Jobs list is the landing screen after login | E2E UI | H | H | H | Good Candidate | P0 | @smoke | TC-AUTH-005 | proven by TC-AUTH-005 — the tag is on that test (owner, 2026-09-24), no new test |
| CHK-ORDL-002 | registered user opens a valid job link → Jobs list | E2E UI + API setup | M | L | M | Needs Test Data Setup | P3 | @regression | — | selected 2026-09-24 (the account's phone is not real) — https link from `POST /job/assign/{tech phone}` opens the Jobs list (recon 4) → TC-ORDL-013 |
| CHK-ORDL-003 | not shown to unauthenticated users; auth flow instead | E2E UI | H | M | H | Good Candidate | P1 | @regression @critical | TC-ORDL-011 | signed-out job link → "Link expired" dialog → Welcome; the list never opens |
| CHK-ORDL-004 | mismatch modal title | E2E UI + API setup | M | M | M | Needs API Support | P2 | @regression | TC-ORDL-012 | key from `POST /job/assign/{phone}` for a reserved number — owner go (Q-ORDL-2) |
| CHK-ORDL-005 | mismatch modal text | E2E UI + API setup | M | M | M | Needs API Support | P2 | @regression | TC-ORDL-012 | as -004 |
| CHK-ORDL-006 | Cancel and Log out buttons | E2E UI + API setup | M | M | M | Needs API Support | P2 | @regression | TC-ORDL-012 | as -004 |
| CHK-ORDL-007 | Cancel closes, stays signed in | E2E UI + API setup | M | M | M | Needs API Support | P2 | @regression | TC-ORDL-012 | as -004 |
| CHK-ORDL-008 | Log out signs out → auth flow | E2E UI + API setup | M | M | H | Needs API Support | P2 | @regression | TC-ORDL-012 | as -004; ends the session → last test of the module |
| CHK-ORDL-009 | app bar with the calendar icon | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-001 | toggle unnamed (TD-JOBS-001) — the only unnamed button in the app bar |
| CHK-ORDL-010 | calendar icon switches to the weekly view | E2E UI | H | H | M | Good Candidate | P1 | @regression | TC-ORDL-006 | day cells named by full date |
| CHK-ORDL-011 | bottom navigation shown | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-001 | tab names readable |
| CHK-ORDL-012 | Orders tab highlighted as active | E2E UI | L | M | L | Medium Candidate | P2 | @regression | TC-ORDL-001 | the tab is "Jobs" (D-ORDL-3); selected state: tree or pixels — recon |
| CHK-ORDL-013 | list reachable from the bottom navigation at all times | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-ORDL-002 | Notifications / Profile → Jobs |
| CHK-ORDL-014 | status filter buttons New / In Progress / Completed | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | no such control in the app or in Figma (D-ORDL-1, accepted) — **Skipped** |
| CHK-ORDL-015 | cards shown when jobs exist | E2E UI + API setup | H | H | H | Good Candidate | P0 | @smoke @critical | TC-ORDL-003, TC-ORDL-004 | job fixture |
| CHK-ORDL-016 | Job ID as the bold primary line | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-003 | `<jobId> - <title>` asserted; bold stays manual (partial) |
| CHK-ORDL-017 | Site Name on the card | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-003 | the card shows one address line (D-ORDL-4) |
| CHK-ORDL-018 | City and State on the card | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-003 | as -017 |
| CHK-ORDL-019 | scheduled date and time | E2E UI | H | H | M | Good Candidate | P1 | @regression | TC-ORDL-003 | `d MMM y` · `HH:mm` in the device time zone |
| CHK-ORDL-020 | status badge visually distinct | E2E UI + API setup | H | H | H | Good Candidate | P1 | @regression @critical | TC-ORDL-004 | label per status asserted; colours stay manual (partial) |
| CHK-ORDL-021 | "Unsubmitted" indicator | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | no such label on the card in the app (D-ORDL-5, accepted) — **Skipped** |
| CHK-ORDL-022 | "Updated" indicator | E2E UI + API setup | M | M | M | Needs API Support | P2 | @regression | TC-ORDL-005 | job created with `isViewed=false` |
| CHK-ORDL-023 | badges readable across sizes | Manual only | L | L | L | Manual Only | — | @manual-only | — | visual; one phone configuration by decision |
| CHK-ORDL-024 | tapping a card opens its details | E2E UI | H | H | H | Good Candidate | P0 | @smoke | TC-ORDL-003 | details header `<jobId> - <title>` |
| CHK-ORDL-025 | rapid taps → one navigation | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (as the rapid-tap items in Auth) |
| CHK-ORDL-026 | empty state when no jobs | E2E UI | H | H | M | Good Candidate | P1 | @regression | TC-ORDL-001 | precondition: no active job for the technician (API check) |
| CHK-ORDL-027 | placeholder illustration | E2E UI | L | M | L | Medium Candidate | P2 | @regression | TC-ORDL-001 | image unlabelled — presence only (partial) |
| CHK-ORDL-028 | empty-state title "No orders" | E2E UI | M | H | L | Good Candidate | P1 | @regression | TC-ORDL-001 | app and Figma: "No jobs" (D-ORDL-2) |
| CHK-ORDL-029 | empty-state message | E2E UI | M | H | L | Good Candidate | P1 | @regression | TC-ORDL-001 | text as app and Figma |
| CHK-ORDL-030 | jobs from a valid link appear after sync | E2E UI + API | M | L | M | Needs Test Data Setup | P3 | @regression | — | **manual — verified by the owner on production** (SMS and email links, 2026-09-24); on DEV without COPS `synchronize` attaches nothing (recon 4) — not automatable here |
| CHK-ORDL-031 | cached jobs offline | Not applicable yet | L | L | M | Not Recommended Now | — | — | — | no network control on the iOS simulator — Android phase |
| CHK-ORDL-032 | offline without cache (UX placeholder) | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | as -031; expected state undefined in the checklist itself |
| CHK-ORDL-033 | error message on a network error | Not applicable yet | L | L | M | Not Recommended Now | — | — | — | as -031 |
| CHK-ORDL-034 | retry after a network error | Not applicable yet | L | L | M | Not Recommended Now | — | — | — | as -031 |
| CHK-ORDL-035 | recovers after connectivity returns | Not applicable yet | L | L | M | Not Recommended Now | — | — | — | as -031 |
| CHK-ORDL-036 | no duplicate cards after refresh or navigation | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-003 | count of cards per `jobId` |
| CHK-ORDL-037 | calendar shown after switching | E2E UI | H | H | M | Good Candidate | P1 | @regression | TC-ORDL-006 | — |
| CHK-ORDL-038 | calendar only for authenticated users | E2E UI | M | M | H | Good Candidate | P1 | @regression | TC-ORDL-011 | list and calendar share one page, unreachable signed out |
| CHK-ORDL-039 | bottom navigation with the Jobs tab active in the calendar | E2E UI | L | M | L | Medium Candidate | P2 | @regression | TC-ORDL-006 | as -012 |
| CHK-ORDL-040 | switch back to the list | E2E UI | H | H | M | Good Candidate | P1 | @regression | TC-ORDL-006 | same toggle |
| CHK-ORDL-041 | month and year in the date selector | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | no month / year in the app or in Figma (D-ORDL-6, accepted) — **Skipped** |
| CHK-ORDL-042 | today selected by default | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-006 | day title = today |
| CHK-ORDL-043 | first day selected when today is not in the week | E2E UI | M | M | L | Medium Candidate | P3 | @regression | TC-ORDL-009 | after a week swipe the same weekday stays selected (D-ORDL-12, accepted) |
| CHK-ORDL-044 | days Sunday … Saturday | E2E UI | M | H | L | Good Candidate | P1 | @regression | TC-ORDL-006 | full day names in the tree |
| CHK-ORDL-045 | selected day highlighted | E2E UI | L | L | L | Medium Candidate | P3 | @regression | — | **deferred** — colour only; a pixel oracle is possible |
| CHK-ORDL-046 | days with jobs marked | E2E UI | M | L | L | Medium Candidate | P3 | @regression | — | **deferred** — 8-px dot; a pixel oracle is possible |
| CHK-ORDL-047 | previous-week arrow | E2E UI | M | M | L | Medium Candidate | P3 | @regression | TC-ORDL-009 | no arrows — weeks change by swipe (D-ORDL-7) |
| CHK-ORDL-048 | next-week arrow | E2E UI | M | M | L | Medium Candidate | P3 | @regression | TC-ORDL-009 | as -047 |
| CHK-ORDL-049 | only jobs of the selected date | E2E UI + API setup | H | H | H | Good Candidate | P1 | @regression @critical | TC-ORDL-007 | jobs on two days of the week |
| CHK-ORDL-050 | list updates at once on a new date | E2E UI + API setup | H | H | M | Good Candidate | P1 | @regression | TC-ORDL-007 | — |
| CHK-ORDL-051 | calendar cards look like list cards | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-007 | same fields as the list card |
| CHK-ORDL-052 | Job ID on the calendar card | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-007 | — |
| CHK-ORDL-053 | Site Name, City, State on the calendar card | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-007 | one address line (D-ORDL-4) |
| CHK-ORDL-054 | date and time on the calendar card | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-007 | — |
| CHK-ORDL-055 | status badge on the calendar card | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-007 | — |
| CHK-ORDL-056 | Updated / Unsubmitted on the calendar card | E2E UI + API setup | M | M | L | Needs API Support | P2 | @regression | TC-ORDL-005 | "Updated" only (D-ORDL-5) |
| CHK-ORDL-057 | only New / In Progress in the calendar | E2E UI + API setup | H | H | H | Good Candidate | P1 | @regression @critical | TC-ORDL-010 | Submitted is shown as well — correct per the owner (D-ORDL-8); asserted as the app does it |
| CHK-ORDL-058 | calendar card opens its details | E2E UI | H | H | M | Good Candidate | P1 | @regression | TC-ORDL-008 | — |
| CHK-ORDL-059 | rapid taps on a calendar card | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** |
| CHK-ORDL-060 | empty state for a date without jobs | E2E UI | M | H | M | Good Candidate | P1 | @regression | TC-ORDL-007 | — |
| CHK-ORDL-061 | its title "No orders" | E2E UI | M | H | L | Good Candidate | P1 | @regression | TC-ORDL-007 | "No jobs" (D-ORDL-2) |
| CHK-ORDL-062 | its text explains "no orders for the selected date" | E2E UI | L | H | L | Good Candidate | P2 | @regression | TC-ORDL-007 | the app shows the general empty text (D-ORDL-2) |
| CHK-ORDL-063 | empty state instead of an empty list | E2E UI | M | H | L | Good Candidate | P1 | @regression | TC-ORDL-007 | — |
| CHK-ORDL-064 | cached calendar offline | Not applicable yet | L | L | M | Not Recommended Now | — | — | — | Android phase |
| CHK-ORDL-065 | offline without cache (UX placeholder) | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | Android phase; state undefined |
| CHK-ORDL-066 | no flicker when switching weeks | Manual only | L | L | L | Manual Only | — | @manual-only | — | subjective |
| CHK-ORDL-067 | many jobs without slowdown | Not applicable yet | L | L | M | Not Recommended Now | — | — | — | load on DEV is excluded (decision 2026-09-23) |
| CHK-ORDL-068 | selected date kept across list ↔ calendar | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | TC-ORDL-008 | — |
| CHK-ORDL-069 | cards sorted by scheduled date and time, ascending (added 2026-09-24) | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | — | SRS FR-ORD-02; the app does not sort on the device — the server order is observed in recon → TC-ORDL-014 after recon |
| CHK-ORDL-070 | jobs in the refreshed list are also in the calendar (added 2026-09-24) | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | TC-ORDL-015 | regression check for BUG-ORDL-001 — red until it is fixed |

## Step 5 — Best first candidates

1. TC-ORDL-003 — a created job appears as a card and opens its details: the entry into every later module; P0.
2. TC-ORDL-001 — empty state and the screen shell: the first thing a new technician sees.
3. TC-ORDL-004 + TC-ORDL-010 — the status block: which statuses are listed where (Submitted included, D-ORDL-8).
4. TC-ORDL-006 / -007 — calendar: switch, date selection, empty date.
5. TC-ORDL-011 — signed-out job link: security path, closes MISS-06 of the Auth review.

## Step 5b — Selected CHK IDs (handoff to prompts/mobile/03)

**50 of 70 → 14 test cases** (updated after recon 4), plus CHK-ORDL-001 through the existing TC-AUTH-005 (owner, 2026-09-24) = 51. CHK-ORDL-069 waits for D-ORDL-10.

| CHK ID | Automation Level | Priority | Automation Status | Blockers to clear before Prompt 07 | Note |
|---|---|---|---|---|---|
| CHK-ORDL-002 | E2E UI + API setup | P2 | Needs API Support | job-link helper (`simctl openurl`) | → TC-ORDL-013 |
| CHK-ORDL-003 | E2E UI | P1 | Good Candidate | job-link helper | → TC-ORDL-011 |
| CHK-ORDL-004…008 | E2E UI + API setup | P2 | Needs API Support | the dialog closes by itself on the iOS simulator → steps after it Blocked there (Q-ORDL-8); full run on Android | → TC-ORDL-012 |
| CHK-ORDL-009, -011 | E2E UI | P1 | Good Candidate | map: toggle, tab bar | → TC-ORDL-001 |
| CHK-ORDL-012 | E2E UI | P2 | Good Candidate | — (`traits` contains `Selected`, recon 4) | → TC-ORDL-001 |
| CHK-ORDL-026…029 | E2E UI | P1–P2 | Good / Medium | API check: no active job for the technician | → TC-ORDL-001 |
| CHK-ORDL-013 | E2E UI | P2 | Good Candidate | maps: Notifications / Profile anchors | → TC-ORDL-002 |
| CHK-ORDL-015 | E2E UI + API setup | P0 | Good Candidate | job fixture | → TC-ORDL-003, TC-ORDL-004 |
| CHK-ORDL-016…019, -024, -036 | E2E UI + API setup | P0–P1 | Good Candidate | job fixture; card parser | → TC-ORDL-003 |
| CHK-ORDL-020 | E2E UI + API setup | P1 | Good Candidate | job fixture (6 statuses) | → TC-ORDL-004 |
| CHK-ORDL-022, -056 | E2E UI + API setup | P2 | Needs API Support | job fixture with `isViewed=false` | → TC-ORDL-005 |
| CHK-ORDL-010, -037, -039, -040, -042, -044 | E2E UI | P1–P2 | Good / Medium | map: calendar | → TC-ORDL-006 |
| CHK-ORDL-049…055, -060…063 | E2E UI + API setup | P1–P2 | Good Candidate | jobs on two days of the week | → TC-ORDL-007 |
| CHK-ORDL-058, -068 | E2E UI + API setup | P1–P2 | Good Candidate | as -049 | → TC-ORDL-008 |
| CHK-ORDL-070 | E2E UI + API setup | P2 | Good Candidate | must run before any calendar refresh in the module | → TC-ORDL-015 |
| CHK-ORDL-043, -047, -048 | E2E UI | P3 | Medium Candidate | — (D-ORDL-7, -12 accepted) | → TC-ORDL-009 |
| CHK-ORDL-057 | E2E UI + API setup | P1 | Good Candidate | — (D-ORDL-8 accepted) | → TC-ORDL-010 |
| CHK-ORDL-038 | E2E UI | P1 | Good Candidate | as -003 | → TC-ORDL-011 |

## Step 6 — Manual-only

| CHK ID | Scenario | Reason | Revisit? |
|---|---|---|---|
| CHK-ORDL-023 | badges readable across sizes | visual, one phone configuration | if visual regression is added |
| CHK-ORDL-066 | no flicker between weeks | subjective | no |

Skipped: -014, -021, -041 (the control / label does not exist — D-ORDL-1, -5, -6, accepted). Not recommended now: -031…-035, -064,
-065 (network control — Android phase), -067 (load excluded). Manual (owner-verified on production): -030. Deferred: -025,
-059 (rapid taps), -045, -046 (colour-only markers).

## Step 7 — API support

| CHK / TC | Scenario | API action | Endpoint (operationId) | Priority | Notes |
|---|---|---|---|---|---|
| TC-ORDL-003…010 | jobs in given statuses / days | create before, delete in `finally` | `POST /job` (`JobController_create`) → `DELETE /job/{id}` (`JobController_remove`) — **verified 2026-09-22** | P0 | `userId` = the technician's `user.id`; `surveyId` = Short Survey (read-only); `jobId` `QA-AUTO-<run>-<kind>` |
| TC-ORDL-001 | "no active jobs" precondition | read | `GET /job` (`JobController_findAll`, `userId`, `statusType`) | P1 | leftover `QA-AUTO-*` jobs of the technician are deleted first |
| TC-ORDL-005 | "Updated" label | create with `isViewed=false` | `POST /job` | P2 | field present in `CreateJobDto` |
| TC-ORDL-011, -012, -013 | job links (another phone, own phone) | generate the link | `POST /job/assign/{phone}` (`JobController_jobAssign`) → `message` = `https://…/redirect/<key>` — **verified in recon 4** for a reserved number and the test account (201) | P2 | owner go 2026-09-24; opened as a universal link; no SMS / email is read |

## Step 8 — Stable selectors

Text for everything except: the list ↔ calendar toggle (TD-JOBS-001: the only unnamed button in the app bar), the
empty-state picture (unlabelled image — presence only), the selected-tab and selected-day state (recon: tree or
pixels). A card is **one** text element (`<date>\n<time>\n<status>\n<jobId> - <title>\n<address>`) — the page object
parses it into fields; the card is found by `name CONTAINS '<jobId>'`.

## Step 9 — Test data

| TC | Data | Source | Reusable | Cleanup |
|---|---|---|---|---|
| TC-ORDL-001, -002, -006, -009 | none; no active job for the technician | API read | — | leftover `QA-AUTO-*` jobs deleted before |
| TC-ORDL-003, -004, -005, -007, -008, -010 | **one module seed of 8 jobs**: new, in_progress, submitted, completed, canceled, expired (today, 12:00 local), one new job on another day of the current week, one new job with `isViewed=false` | `POST /job` × 8 | within the module | `DELETE /job/{id}` × 8 in `finally` (16 calls per run — DEV-gentle) |
| TC-ORDL-011 | a random key `QA-AUTO-INVALID-<ts>` | generated | — | nothing created |
| TC-ORDL-012 | link key for `+1 202 555 01xx` | `POST /job/assign/{phone}` | no | the link expires by itself (72 h); nothing to delete |

Address `QA test site, 350 5th Ave, New York, NY 10118`, coordinates 40.748440, -73.985664 (as in recon 3b).
Dates are built from the **device** date and time zone so the card and the calendar day match.

## Step 10 — Authentication & session

| Role | TCs | Login method | Notes |
|---|---|---|---|
| none (logged out) | TC-ORDL-011 | app data reset | runs before the session fixture |
| Field Technician | all others | `ui_login` fixture, once per run | TC-ORDL-012 logs out → it runs last; the next module logs in again (one extra OTP) |

## Step 11 — Isolation

| TC | Independent | Creates data | Cleanup | Setup / teardown |
|---|---|---|---|---|
| 001, 002, 006, 009 | yes | no | no | signed in, list open |
| 003, 004, 005, 007, 008, 010 | yes, given the seed | **jobs (module seed)** | **API delete in `finally`** | the seed is created on first use and removed after the module |
| 011 | yes | no | no | logged-out start |
| 012 | yes | link (server side) | none needed | ends the session |

Order-sensitive facts, written into the plan so nobody "fixes" them: TC-ORDL-005 is the only test that opens the
`isViewed=false` job (opening it clears "Updated"); TC-ORDL-001 runs before the seed exists.

## Step 12 — Plan

- Tests: `automation/mobile/tests/shared/test_order_list.py` (`@pytest.mark.shared`).
- Screen maps: extend `screens/jobs_list_map.py` (toggle, card, empty texts, empty image); new
  `screens/jobs_calendar_map.py` (day cells, selected-day title, week strip, cards, empty state), `tabbar_map.py`
  (shared tab bar, the three `jobs-list.tab-*` aliases move here), `job_details_map.py` (root / header / back — from
  `job_details_new.xml`, module 04 extends it), `notifications_map.py` / `profile_map.py` (root only),
  `link_dialogs_map.py` (link expired, phone mismatch).
- Pages: `JobsListPage.card_fields(job_id)`, `card_count(job_id)`, `pull_to_refresh()`, `toggle_view()`;
  `JobsCalendarPage.week_days()`, `select_day(date)`, `selected_day_title()`, `swipe_week(direction)`.
- Fixtures / helpers: `helpers/field_services_api.py` gets `create_job` / `delete_job` / `find_active_jobs`;
  fixture `jobs_seed` (module scope, `finally` cleanup, refuses to delete anything not `QA-AUTO-*`); helper
  `open_deep_link(url)` (`mobile: deepLink` on iOS, `am start` on Android).
- Order: 011 → 001 → 002 → 006 → 009 → 013 → (seed) 003 → 004 → **015** (before any calendar refresh) → 010 → 007 → 008 → 005 → 012.
- Job-link helper: `xcrun simctl openurl booted <https link>` (iOS), `adb shell am start -a android.intent.action.VIEW -d <link>` (Android); `defaultAlertAction` off for these steps (recon 4).
- Estimate: 12 TCs × ~1.5–2.5 h ≈ **20–28 h** incl. maps, the job fixture and stabilisation. Maintenance risk:
  **Medium** — the parsed card format and the unnamed toggle.

## Step 13 — Runtime notes

As the Auth plan. Specific here: the card list scrolls (a card is ~150 px) — `scroll-to` before assertions on lower
cards; jobs created after the list loaded appear only after pull-to-refresh — **in the list and, separately, in the
calendar** (BUG-ORDL-001); the toggle is ignored while the list is still loading (wait for the list first); dates and
times are compared in the device time zone.

## Step 14 — CI readiness

As the Auth plan. CI secrets additionally need nothing new (the API admin is already used for cleanup).

## Step 15 — Risks

| Category | Risk | Impact | Action | Owner |
|---|---|---|---|---|
| Data | seed jobs left on DEV if a run is killed | DEV clutter, a later empty-state test fails | `QA-AUTO-*` sweep before TC-ORDL-001 and in teardown | Automation QA |
| Data | someone else assigns a job to the shared test technician | empty-state and calendar tests see extra cards | tests assert only on their own `jobId`s; the empty-state test first checks via API and turns Blocked, not Failed | Automation QA |
| Technical | card text format changes | parser breaks loudly | one parser, unit-tested offline | Automation QA |
| Technical | a date near midnight / week boundary | a job lands on another day | 12:00 local; the "other day" is chosen inside the current week | Automation QA |
| Process | checklist older than the app (D-ORDL-1…9) | wrong expectations | **resolved** — the owner accepted the app, 2026-09-23 | Owner |
| Environment | `POST /job/assign/{phone}` may try to send an SMS | a message to a number | reserved 555-01xx range only, owner go | Owner |

## Step 16 — Final recommendation

D-ORDL-1…9 are accepted. Start after the owner's word on the job seed (8 jobs per run, Q-ORDL-3) and on the way
TC-ORDL-012 gets its link (Q-ORDL-2).
Then one recon pass with the seed on the simulator (list, statuses, calendar, both dialogs) before the maps.
**First sprint scope:** TC-ORDL-001…011 (TC-ORDL-012 after the owner's go).
