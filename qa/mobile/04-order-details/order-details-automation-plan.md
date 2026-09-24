# Automation plan — Order details (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/04-order-details/order-details-checklist.md`
> (89 items, `CHK-ORDD-001…089`, imported 2026-09-24). Reviewed copy for the module; the **Selected CHK IDs** table is
> the contract for `prompts/mobile/03` (test cases). Date: 2026-09-24. Owner: mykola.zhuchenko.
> **Status: draft — waits for the owner (Q-ORDD-1…5 in [order-details-questions.md](order-details-questions.md)).**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| App build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Feature code | `ORDD` |
| Scope decision | breadth, as modules 01–03; **the check-in process itself (CHK-ORDD-023…047) is proposed for module 05** (Q-ORDD-1) |
| Oracle model | accepted production baseline; SRS §3.1.3.1–3.1.3.2 + checklist explain; Figma `Jobs details_New` 2451:82657, `…_New_Updated` 2451:83368, `Job details_Atachments_Documents` 2451:83062, `…_Photos` 2451:83346, `…_Document details` 2451:83360 decide the visual layer |

## Step 0 — Input quality

**Overall: Medium.** Stable IDs; the details screen tree from recon 4 (`recon4b_details_unviewed.xml`: header,
status, title, description, Location / On map, Scheduled date & time, `Attachments (0)`, `Check in`); a verified job
recipe (`POST /job` → `DELETE /job/{id}`). A read-only look at the app code and the Figma frames shows **nine
discrepancies** (D-ORDD-1…9): one line `<jobId> - <title>`, no "Unsubmitted", "Updated" gone while still on the
screen, "On map" sends the address (not coordinates), only PDF opens in the app, "save" is the system share sheet
without a toast, the photo viewer closes with a back arrow, and a location flow that differs from the SRS in six
places. **Not seen live yet:** the attachments screen, both viewers, PF info, the first step after tapping Check in on
the simulator → recon 5 (Q-ORDD-5). No DEV job has a DOC or XLS attachment (API read, 73 of 100 jobs carry PDF / JPG).

## Step 1 — Readiness: **Ready with conditions**

Text locators for the header, sections, the `Attachments (N)` button, tabs, document names and `Check in`. Conditions:
the owner's word on the scope (Q-ORDD-1) and on the attachment files (Q-ORDD-2); recon 5 for the unseen screens; two
unlabelled icons (PDF viewer close and download — `IconButton` without a label, app code audit §3) located by their
place in the app bar, as the list ↔ calendar toggle (TD-JOBS-001).

## Step 2 — Approach: **Hybrid (UI-first, API for setup / cleanup)**

Jobs (and their attachment files) are created through the API directly with the data a test needs and removed in
`finally`; every assertion is made through the UI. The only API step inside a test is TC-ORDD-002 (the backend
changes the scheduled time — that *is* the scenario).

## Step 3–4 — Candidate matrix (all 89 items)

Status legend as in the Auth plan. **deferred → 05** = automated in module 05 with its check-in test cases (Q-ORDD-1).

| CHK ID | Scenario (short) | Automation Level | ROI | Stability | Risk | Automation Status | Priority | Tags | TC | Reason / blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| CHK-ORDD-001 | details open from the list or the calendar | E2E UI + API setup | H | H | H | Good Candidate | P0 | @smoke | TC-ORDD-001, TC-ORDL-008 | list in TC-ORDD-001; the calendar path already exists — tag TC-ORDL-008 |
| CHK-ORDD-002 | back returns without losing state | E2E UI + API setup | H | M | M | Good Candidate | P1 | @regression | TC-ORDD-001, TC-ORDL-008 | list: the card is still there; calendar: the selected day is kept (TC-ORDL-008 already checks it) |
| CHK-ORDD-003 | Order ID in the header | E2E UI + API setup | H | H | M | Good Candidate | P0 | @smoke | TC-ORDD-001 | header = `<jobId> - <title>` (D-ORDD-1) |
| CHK-ORDD-004 | title below the ID | E2E UI + API setup | M | H | L | Good Candidate | P1 | @regression | TC-ORDD-001 | one line with the ID (D-ORDD-1) |
| CHK-ORDD-005 | status badge visible | E2E UI + API setup | H | H | M | Good Candidate | P0 | @smoke | TC-ORDD-001 | `New` |
| CHK-ORDD-006 | "Updated" on the details of a changed job | E2E UI + API setup | M | L | M | Medium Candidate | P3 | @regression | TC-ORDD-009 | the banner lives only for the `mark-as-viewed` request (D-ORDD-3) — recon 5 decides |
| CHK-ORDD-007 | "Updated" gone after leaving the screen | E2E UI + API setup | M | M | M | Medium Candidate | P3 | @regression | TC-ORDD-009 | D-ORDD-3; on the list side BUG-ORDL-003 |
| CHK-ORDD-008 | description as multi-line text | E2E UI + API setup | M | H | L | Good Candidate | P1 | @regression | TC-ORDD-001 | a 3-line description, as in Figma |
| CHK-ORDD-009 | sections separated by dividers | Manual | L | – | L | Manual Only | P3 | @manual | — | visual (Figma) |
| CHK-ORDD-010 | all fields read-only | E2E UI + API setup | M | H | M | Good Candidate | P1 | @regression | TC-ORDD-001 | no editable element on the screen (tree) |
| CHK-ORDD-011 | full address in Location | E2E UI + API setup | H | H | M | Good Candidate | P1 | @regression | TC-ORDD-001 | — |
| CHK-ORDD-012 | "On map" opens a maps app | E2E UI + API setup | M | M | M | Good Candidate | P2 | @regression | TC-ORDD-003 | iOS simulator: Apple Maps comes to the foreground (Google Maps not installed) |
| CHK-ORDD-013 | the map shows the job location | E2E UI + API setup | M | L | M | Medium Candidate | P3 | @regression | TC-ORDD-003 | the app sends the address, not coordinates (D-ORDD-4); Maps' search text read from its own tree — recon 5 |
| CHK-ORDD-014 | date and time with icons | E2E UI + API setup | H | H | M | Good Candidate | P1 | @regression | TC-ORDD-001 | texts asserted; the icons are visual |
| CHK-ORDD-015 | date and time follow the backend | E2E UI + API | H | M | H | Good Candidate | P2 | @regression | TC-ORDD-002 | `PATCH /job/{id}` (`JobController_update`) + pull to refresh on the details |
| CHK-ORDD-016 | PF name | E2E UI + API setup | M | H | L | Good Candidate | P1 | @regression | TC-ORDD-001 | `projectFacilitator` in `POST /job` — its `id` rule checked in recon 5 |
| CHK-ORDD-017 | PF phone opens the dialer | E2E UI + API setup | M | M | L | Needs Device | P3 | @regression @android | TC-ORDD-004 | no Phone app on the iOS simulator → Blocked there; Android emulator has a dialer (Q-ORDD-3) |
| CHK-ORDD-018 | Attachments section present | E2E UI + API setup | H | H | M | Good Candidate | P1 | @regression | TC-ORDD-001 | `Attachments (N)` with the real count |
| CHK-ORDD-019 | Attachments opens its screen | E2E UI + API setup | H | H | M | Good Candidate | P1 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-020 | Check in shown for a New job | E2E UI + API setup | H | H | H | Good Candidate | P0 | @smoke | TC-ORDD-001 | — |
| CHK-ORDD-021 | Check in visible without scrolling | E2E UI + API setup | M | H | M | Good Candidate | P1 | @regression | TC-ORDD-001 | the button sits outside the scrolling content; asserted on a job whose content is taller than the screen |
| CHK-ORDD-022 | Check in starts the check-in flow | E2E UI + API setup | H | L | H | Medium Candidate | P2 | @regression | TC-ORDD-005 | what appears first on the simulator (OS location prompt, "Location could not be trusted") — recon 5; the job must stay New |
| CHK-ORDD-023…029 | location prompts: Enable / Location disabled / settings | E2E UI + API setup | M | L | H | Needs Environment Control | P2 | @regression | → 05 | **deferred → 05**; D-ORDD-9 (the app's flow differs); simulator location privacy is controllable (`xcrun simctl privacy`) |
| CHK-ORDD-030…035 | GPS capture, proximity, mismatch alert | E2E UI + API setup | H | L | H | Needs Environment Control | P1 | @regression | → 05 | **deferred → 05**; the simulator's fix is expected to be reported as mocked (iOS marks simulated locations) → GPS check-in blocked there by the app's design (D-ORDD-9) — recon 5 confirms |
| CHK-ORDD-036…040 | manual check-in | E2E UI + API setup | H | M | H | Needs Environment Control | P1 | @regression | → 05 | **deferred → 05**; manual entry appears only when no GPS fix is obtained |
| CHK-ORDD-041…047 | error notice, "GPS not confirmed" flag, check-in record (method, coordinates, accuracy, time) | E2E UI + API | H | M | H | Needs API Support | P1 | @regression | → 05 | **deferred → 05**; the record is read back through `GET /job/{id}` |
| CHK-ORDD-048 | cached details offline | E2E UI | M | L | M | Not Recommended now | P3 | @offline | — | no network control on the iOS simulator (Q-ORDD-4) — Android phase |
| CHK-ORDD-049 | check in offline, sync later | E2E UI | M | L | H | Not Recommended now | P3 | @offline | — | as -048; placeholder item; module 05 |
| CHK-ORDD-050 | responsive during slow GPS / network | Manual | L | L | L | Not Recommended now | P3 | @performance | — | subjective; network control |
| CHK-ORDD-051 | Attachments screen opens | E2E UI + API setup | H | H | M | Good Candidate | P1 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-052 | back returns to the details | E2E UI + API setup | M | H | L | Good Candidate | P1 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-053 | title "Attachments" | E2E UI + API setup | M | H | L | Good Candidate | P1 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-054 | two tabs Documents / Photos | E2E UI + API setup | M | H | L | Good Candidate | P1 | @regression | TC-ORDD-006 | Figma also has a hidden "Audio" tab; the app has two |
| CHK-ORDD-055 | Documents selected by default | E2E UI + API setup | M | M | L | Good Candidate | P2 | @regression | TC-ORDD-006 | selected state from the tree (`traits`, as the tab bar) — recon 5 |
| CHK-ORDD-056 | every attachment of the job listed | E2E UI + API setup | H | H | H | Good Candidate | P1 | @regression | TC-ORDD-006 | 2 documents + 2 photos |
| CHK-ORDD-057 | documents only under Documents | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-058 | photos only under Photos | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-059 | switching tabs changes the content | E2E UI + API setup | M | H | L | Good Candidate | P2 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-060 | document name with extension | E2E UI + API setup | M | H | L | Good Candidate | P2 | @regression | TC-ORDD-006 | — |
| CHK-ORDD-061 | file type identifiable | E2E UI + API setup | L | H | L | Good Candidate | P3 | @regression | TC-ORDD-006 | by the extension in the name; the icon is visual |
| CHK-ORDD-062 | a document opens in the in-app viewer | E2E UI + API setup | H | M | H | Good Candidate | P1 | @regression | TC-ORDD-007 | PDF (D-ORDD-5) |
| CHK-ORDD-063 | the viewer is full-screen | E2E UI + API setup | M | M | L | Medium Candidate | P2 | @regression | TC-ORDD-007 | the viewer's title is the file name; no tabs, no tab bar |
| CHK-ORDD-064 | vertical scrolling of pages | E2E UI + API setup | L | L | L | Deferred | P3 | @gesture | — | a 2-page PDF + a pixel comparison; after the first sprint |
| CHK-ORDD-065 | zoom in / out | E2E UI + API setup | L | L | L | Deferred | P3 | @gesture | — | two-finger gesture + pixels; after the first sprint |
| CHK-ORDD-066 | read-only viewer | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | TC-ORDD-007 | no editable element |
| CHK-ORDD-067 | Close (X) shown | E2E UI + API setup | M | M | L | Medium Candidate | P2 | @regression | TC-ORDD-007 | unlabelled icon (app code audit §3) — located by its place in the app bar → testability defect |
| CHK-ORDD-068 | Close returns to the Documents list | E2E UI + API setup | M | M | M | Medium Candidate | P2 | @regression | TC-ORDD-007 | as -067 |
| CHK-ORDD-069 | save a document locally | Manual | L | L | L | Not Recommended now | P3 | @manual | — | the system share sheet (D-ORDD-6), outside the app |
| CHK-ORDD-070 | success toast after saving | — | – | – | – | Skipped if D-ORDD-6 accepted | – | – | — | the app shows no toast (D-ORDD-6) |
| CHK-ORDD-071 | PDF, DOC and XLS supported | E2E UI + API setup | M | L | M | Needs Decision | P3 | @regression | — | only PDF opens in the app (D-ORDD-5); tagging it on the PDF test would over-claim — decided after D-ORDD-5 |
| CHK-ORDD-072 | unsupported format → message | E2E UI + API setup | L | L | L | Not Recommended now | P3 | @regression | — | placeholder item; the app's "Could not open document" |
| CHK-ORDD-073 | Photos tab is a grid of thumbnails | E2E UI + API setup | M | M | L | Good Candidate | P2 | @regression | TC-ORDD-008 | thumbnails side by side (tree positions) |
| CHK-ORDD-074 | thumbnails same size and spacing | E2E UI + API setup | L | M | L | Medium Candidate | P3 | @regression | TC-ORDD-008 | equal rects from the tree |
| CHK-ORDD-075 | a thumbnail opens the photo viewer | E2E UI + API setup | H | M | M | Good Candidate | P1 | @regression | TC-ORDD-008 | — |
| CHK-ORDD-076 | photo shown full-screen | E2E UI + API setup | M | M | L | Medium Candidate | P2 | @regression | TC-ORDD-008 | no tabs, no tab bar; the image fills the width (pixels) |
| CHK-ORDD-077 | pinch to zoom | E2E UI + API setup | L | L | L | Deferred | P3 | @gesture | — | as -065 |
| CHK-ORDD-078 | pan when zoomed | E2E UI + API setup | L | L | L | Deferred | P3 | @gesture | — | as -065 |
| CHK-ORDD-079 | Close (X) in the photo viewer | E2E UI + API setup | L | H | L | Good Candidate | P3 | @regression | TC-ORDD-008 | the app has a back arrow (D-ORDD-7) — asserted if accepted |
| CHK-ORDD-080 | closing returns to the Photos grid | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | TC-ORDD-008 | — |
| CHK-ORDD-081…083 | attachments offline | E2E UI | M | L | M | Not Recommended now | P3 | @offline | — | network control (Q-ORDD-4) |
| CHK-ORDD-084, -085 | network error message, retry | E2E UI | M | L | M | Not Recommended now | P3 | @offline | — | network control (Q-ORDD-4); the app's "Failed to load attachments" |
| CHK-ORDD-086 | no flicker when switching tabs | Manual | L | – | L | Manual Only | P3 | @manual | — | subjective |
| CHK-ORDD-087 | the selected tab survives opening / closing | E2E UI + API setup | M | H | M | Good Candidate | P2 | @regression | TC-ORDD-008 | Photos stays selected after the viewer closes |
| CHK-ORDD-088 | responsive with many attachments | Performance | L | L | L | Not Recommended now | P3 | @performance | — | load excluded (DEV-gentle, decision 2026-09-23) |
| CHK-ORDD-089 | attachments cached for offline | E2E UI | M | L | M | Not Recommended now | P3 | @offline | — | network control (Q-ORDD-4) |

## Step 5 — Best first candidates

1. TC-ORDD-001 — a New job with full data shows every part of the details and the Check in button: the entry into
   job execution; P0.
2. TC-ORDD-006 — the attachments screen: tabs, default tab, every file listed in its tab.
3. TC-ORDD-007 / -008 — the PDF viewer and the photo viewer open and close back to their tab.
4. TC-ORDD-002 — a schedule change made on the backend reaches the open details (data freshness).
5. TC-ORDD-005 — Check in starts the flow (after recon 5).

## Step 5b — Selected CHK IDs (handoff to prompts/mobile/03)

**44 of 89 → 9 test cases** (+ CHK-ORDD-001, -002 tagged on the existing TC-ORDL-008). **25 deferred → module 05**
(-023…-047, Q-ORDD-1). The rest: manual 3, not recommended now 11, gestures deferred 4, skipped 1 (-070 if D-ORDD-6
is accepted), needs decision 1 (-071) = 89. Final after the owner's answers and recon 5.

| CHK ID | Automation Level | Priority | Automation Status | Blockers to clear before Prompt 07 | Note |
|---|---|---|---|---|---|
| CHK-ORDD-001…005, -008, -010, -011, -014, -016, -018, -020, -021 | E2E UI + API setup | P0–P1 | Good Candidate | job fixture with description and PF; recon 5 (PF, tree) | → TC-ORDD-001 (-001, -002 also on TC-ORDL-008) |
| CHK-ORDD-015 | E2E UI + API | P2 | Good Candidate | `PATCH /job/{id}` helper | → TC-ORDD-002 |
| CHK-ORDD-012, -013 | E2E UI + API setup | P2–P3 | Good / Medium | Maps app state (`query_app_state`), return to the app | → TC-ORDD-003 |
| CHK-ORDD-017 | E2E UI + API setup | P3 | Needs Device | Android dialer; Blocked on the iOS simulator (Q-ORDD-3) | → TC-ORDD-004 |
| CHK-ORDD-022 | E2E UI + API setup | P2 | Medium Candidate | recon 5: the first step on the simulator | → TC-ORDD-005 |
| CHK-ORDD-019, -051…-061 | E2E UI + API setup | P1–P3 | Good Candidate | attachment files (Q-ORDD-2) | → TC-ORDD-006 |
| CHK-ORDD-062, -063, -066…-068 | E2E UI + API setup | P1–P2 | Good / Medium | unlabelled close icon (testability defect) | → TC-ORDD-007 |
| CHK-ORDD-073…-076, -079, -080, -087 | E2E UI + API setup | P1–P3 | Good / Medium | D-ORDD-7 accepted | → TC-ORDD-008 |
| CHK-ORDD-006, -007 | E2E UI + API setup | P3 | Medium Candidate | recon 5: how long the banner lives (D-ORDD-3) | → TC-ORDD-009 |

## Step 6 — Manual-only

| CHK ID | Scenario | Reason | Revisit? |
|---|---|---|---|
| CHK-ORDD-009 | dividers between sections | visual | if visual regression is added |
| CHK-ORDD-086 | no flicker between tabs | subjective | no |
| CHK-ORDD-069 | save a document through the share sheet | system UI outside the app (D-ORDD-6) | if the owner wants it automated |

Deferred → 05: -023…-047 (Q-ORDD-1). Not recommended now: -048…-050, -072, -081…-085, -089 (network control, placeholder
items — Android phase), -088 (load excluded). Deferred (gestures): -064, -065, -077, -078. Skipped if D-ORDD-6 is
accepted: -070. Needs decision: -071 (D-ORDD-5).

## Step 7 — API support

| CHK / TC | Scenario | API action | Endpoint (operationId) | Priority | Notes |
|---|---|---|---|---|---|
| all TCs | jobs with the data a test needs | create before, delete in `finally` | `POST /job` (`JobController_create`) → `DELETE /job/{id}` (`JobController_remove`) — **verified 2026-09-22** | P0 | fields used: `description`, `projectFacilitator` (`CreateJobProjectFacilitatorDto`: id, name, email, phone), `attachments` (`CreateJobAttachmentDto`: documents / photos of `{url, name, description}`), `isViewed` |
| TC-ORDD-006…008 | the files the attachments point to | upload before, delete after | `POST /file/upload` (`FileController_uploadFile`) → `DELETE /file/{id}` (`FileController_deleteFile`) — **not verified yet** (recon 5) | P1 | variant A of Q-ORDD-2; a 2-page PDF and two JPGs from `automation/mobile/fixtures/media/` |
| TC-ORDD-002 | the backend reschedules the job | change the date | `PATCH /job/{id}` (`JobController_update`, `scheduleDate`) — **not verified yet** | P2 | only on the test's own job |

## Step 8 — Stable selectors

Text for the header (`Other` named `<jobId> - <title>`, recon 4), status, section titles (`Location`, `Scheduled date &
time`, `PF info`), `On map`, `Attachments (N)`, `Check in`, tab names, document names, the viewer title (= file name).
Unlabelled: the PDF viewer's close and download icons (app code audit §3) — located by their place in the viewer's app
bar, recorded as testability defects TD-ORDD-001…002; photo thumbnails (images without a name, expected — located by
position in the grid). Every locator lives in `screens/job_details_map.py` (extended), new `attachments_map.py`,
`pdf_viewer_map.py`, `photo_viewer_map.py`.

## Step 9 — Test data

| TC | Data | Source | Reusable | Cleanup |
|---|---|---|---|---|
| TC-ORDD-001, -003…-008 | **job `full`**: New, today 12:00, a 3-line description, PF name + phone (`+1 202 555 01xx`), address + coordinates as module 03, 2 documents (`QA-AUTO safety.pdf` 2 pages, `QA-AUTO power.pdf`) + 2 photos (`QA-AUTO site 1.jpg`, `QA-AUTO site 2.jpg`) | `POST /file/upload` × 3 + `POST /job` | within the module | `DELETE /job/{id}`, `DELETE /file/{id}` × 3 in `finally` |
| TC-ORDD-002 | **job `reschedule`**: New, today 10:00 → moved by +1 day +2 h in the test | `POST /job` + `PATCH /job/{id}` | no | `DELETE /job/{id}` |
| TC-ORDD-009 | **job `unviewed`**: New, `isViewed=false` | `POST /job` | no (opening it clears "Updated") | `DELETE /job/{id}` |

`jobId` `QA-AUTO-<run>-<kind>`, as module 03; the sweep of leftover `QA-AUTO-*` jobs runs before the seed. Uploaded
files cannot be swept by name (no list endpoint in the spec) — their ids are kept by the fixture and deleted in
`finally`; a killed run leaves at most three small files (Step 15).

## Step 10 — Authentication & session

| Role | TCs | Login method | Notes |
|---|---|---|---|
| Field Technician | all | `ui_login` fixture (relaunch, login only when signed out) | no test signs out |

## Step 11 — Isolation

| TC | Independent | Creates data | Cleanup | Setup / teardown |
|---|---|---|---|---|
| 001, 003…008 | yes, given the seed | **job `full` + 3 files (module seed)** | **API delete in `finally`** | read-only use of the job: TC-ORDD-005 cancels the check-in, so the job stays New |
| 002 | yes | job `reschedule` | API delete | the only test that changes a job |
| 009 | yes | job `unviewed` | API delete | the only test that opens it |

Order-sensitive facts, written into the plan so nobody "fixes" them: TC-ORDD-005 must leave the job `full` in New (it
cancels the flow; if the flow ever completes a check-in, the next tests see In progress) — it runs last among the
tests on `full`.

## Step 12 — Plan

- Tests: `automation/mobile/tests/shared/test_order_details.py` (`@pytest.mark.shared`).
- Screen maps: extend `screens/job_details_map.py` (sections, PF, `On map`, `Attachments (N)`, `Check in`,
  "Updated" banner); new `attachments_map.py`, `pdf_viewer_map.py`, `photo_viewer_map.py`.
- Pages: `JobDetailsPage.fields()`, `open_attachments()`, `open_map()`, `tap_check_in()`, `pull_to_refresh()`;
  `AttachmentsPage.tab(name)`, `selected_tab()`, `documents()`, `photos()`; `PdfViewerPage.close()`;
  `PhotoViewerPage.back()`.
- Fixtures / helpers: `field_services_api.py` gets `upload_file` / `delete_file` / `update_job`; fixture
  `details_seed` (module scope, `finally` cleanup of jobs **and** files); helper `foreground_app()` for the Maps check.
- Order: 001 → 006 → 007 → 008 → 003 → 002 → 009 → 005 (Check in last on `full`); 004 on Android only.
- Estimate: 9 TCs × ~1.5–2.5 h ≈ **14–22 h** incl. recon 5, maps, the file fixture and stabilisation. Maintenance risk:
  **Medium** — the unlabelled viewer icons and the system Maps app.

## Step 13 — Runtime notes

As modules 01–03 (relaunch before each test, video only on demand). Specific here: the details content scrolls
(`scroll-to` before assertions on PF info and Attachments); a back navigation leaves the Jobs tree stale (TD-JOBS-003)
— assertions after it use presence or pixels; opening Maps leaves the app — the test brings the app back
(`activate_app`) before it ends.

## Step 14 — CI readiness

As the Auth plan. Nothing new in the secrets; the fixture media files are in the repo.

## Step 15 — Risks

| Category | Risk | Impact | Action | Owner |
|---|---|---|---|---|
| Data | uploaded files left on DEV if a run is killed | ≤ 3 small files in the DEV bucket | ids deleted in `finally`; a killed run is logged with the ids | Automation QA |
| Data | `DELETE /job` might delete the files a job points to | shared files lost (variant B only) | variant A — only our own files (Q-ORDD-2) | Owner |
| Technical | the simulator's location is expected to be reported as mocked (recon 5 confirms) | GPS check-in impossible on the iOS simulator (by the app's design) | TC-ORDD-005 checks only that the flow starts; GPS paths in module 05 (Q-ORDD-1) | Automation QA |
| Technical | unlabelled close / download icons | locator by position | testability defects TD-ORDD-001…002 | Dev team |
| Process | checklist older than the app (D-ORDD-1…9) | wrong expectations | the owner decides D-ORDD-1…9 | Owner |

## Step 16 — Final recommendation

Decide Q-ORDD-1…4 and D-ORDD-1…9, then **recon 5** (Q-ORDD-5) with three seeded jobs and three uploaded files, then
the test cases. **First sprint scope:** TC-ORDD-001, -006, -007, -008, -002, -003 (TC-ORDD-005 and -009 after recon 5;
-004 on Android).
