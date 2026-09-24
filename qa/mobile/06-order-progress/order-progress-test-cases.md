# Test cases — Order progress / In progress (mobile)

> Structured, alias-based test cases for the CHK IDs selected in
> [order-progress-automation-plan.md](order-progress-automation-plan.md). Format:
> [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: draft — written after recon 7 ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md));
> automated on the owner's "виконуй" (2026-09-24), validation by the owner together with the first results.**

| Field | Value |
|---|---|
| Feature | The In progress state of a job: status, timer, deliverables rows and their screens, info block, primary action |
| Source checklist | `qa/mobile/06-order-progress/order-progress-checklist.md` (CHK-ORDP-001…042) |
| Devices / build | iPhone 17 · iOS 26.5 (simulator) · `[DEV] CT Mobile` 1.1.1 (178), `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko · Last updated 2026-09-24 |

**Conventions**

- **A job In progress = checked in through the UI** on this device (fixture `in_progress_job`: a New job from `POST /job`,
  then Check in → Confirm with the mock-location switch ON, as TC-CHIO-001). A job created directly In progress through
  the API has no local check-in time: its timer counts from the job's last change and restarts on every update
  (recon 7; the app reads `checkInAt`, the server sends `checkInDate`) — see Q-ORDP-4.
- **The timer** is one element whose name holds the six digits and two colons separated by line breaks
  (`0\n0\n:\n0\n0\n:\n0\n5`, recon 6c / 7); the page joins it into `HH:MM:SS`.
- **Nothing is filled, uploaded or submitted** in this module (the submission flow is module 07).
- **Back = the app bar's `Back` button**, not the edge swipe: Flutter ignores the swipe while a screen is still
  sliding in, so a swipe right after opening the details can do nothing (run 2 of TC-ORDP-005 — a harness defect, fixed).

---

## TC-ORDP-001 — A checked-in job shows the In progress screen: status, running timer, deliverables, info and "Submit deliverables"

| Field | Value |
|---|---|
| Source CHK IDs | CHK-ORDP-001, -002, -004, -005, -010, -011, -012, -014, -015, -017, -018 |
| Priority | P0 |
| Preconditions | `{{job.progress}}` checked in (fixture), details open |
| Oracle | spec — SRS §3.1.3.4; figma:2451:82704 (`Job details_In progress`); D-ORDP-1…5 accepted |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | job-details.status | — | In progress |
| 2 | expect-text | job-details.timer | — | `HH:MM:SS` |
| 3 | expect-text | job-details.timer | — | 3 s later: 3 s more (±2 s: whole seconds + the tree read) |
| 4 | expect-visible | job-details.deliverable[Survey] | — | with its icon (left) and chevron (right) |
| 5 | expect-visible | job-details.deliverable[Photo report] | — | with its icon and chevron |
| 6 | expect-visible | job-details.deliverable[Notes] | — | with its icon and chevron |
| 7 | expect-text | job-details.description | — | the job's scope, every line |
| 8 | expect-text | job-details.address | — | {{job.progress.address}} |
| 9 | expect-visible | job-details.on-map | — | tappable |
| 10 | expect-text | job-details.date | — | {{job.progress.date}} |
| 11 | expect-text | job-details.pf-name | — | {{pf.name}} |
| 12 | expect-visible | job-details.pf-phone[{{pf.phone}}] | — | a tappable phone |
| 13 | click | job-details.attachments | — | the Attachments screen |
| 14 | expect-visible | attachments.title | — | "Attachments" |
| 15 | click | attachments.back | — | back on the details |
| 16 | expect-visible | job-details.submit-deliverables | — | "Submit deliverables", enabled |

## TC-ORDP-002 — The timer keeps counting while the app is in the background

| Field | Value |
|---|---|
| Source CHK IDs | CHK-ORDP-003 |
| Priority | P2 |
| Preconditions | as TC-ORDP-001 |
| Oracle | spec — CHK-ORDP-003 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | job-details.timer | — | note the value |
| 2 | background | app | 10 s | the app comes back to the details |
| 3 | expect-text | job-details.timer | — | step 1 + the time spent in the background (±2 s), and = the time since the check-in stored on the server (`GET /job/{id}` → `checkInDate`, ±5 s) |

## TC-ORDP-003 — Survey, Photo report and Notes open their screens and come back

| Field | Value |
|---|---|
| Source CHK IDs | CHK-ORDP-006, -007, -008 |
| Priority | P1 |
| Preconditions | as TC-ORDP-001 |
| Oracle | spec — SRS §3.1.3.4 (deliverables navigate to their screens); recon 7 (screen titles) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Survey] | — | — |
| 2 | expect-text | deliverable-screen.title | — | Survey |
| 3 | expect-text | deliverable-screen.survey-name | — | {{survey.name}} (the job's survey) |
| 4 | click | deliverable-screen.back | — | the details |
| 5 | click | job-details.deliverable[Photo report] | — | — |
| 6 | expect-text | deliverable-screen.title | — | Photo report |
| 7 | click | deliverable-screen.back | — | the details |
| 8 | click | job-details.deliverable[Notes] | — | — |
| 9 | expect-text | deliverable-screen.title | — | Notes |
| 10 | click | deliverable-screen.back | — | the details, status In progress |

## TC-ORDP-004 — "On map" on the In progress screen opens the job's location

| Field | Value |
|---|---|
| Source CHK IDs | CHK-ORDP-013 |
| Priority | P3 |
| Preconditions | as TC-ORDP-001 |
| Oracle | D-ORDP-3 accepted (in-app browser, as TC-ORDD-003) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.on-map | — | — |
| 2 | expect-text | in-app-browser.url | — | maps.apple.com |
| 3 | expect-visible | in-app-browser.place[{{job.progress.street}}] | — | the job's street, within 40 s |
| 4 | click | in-app-browser.close | — | back on the details |

## TC-ORDP-005 — The primary action follows the status after leaving and reopening; a Submitted job's deliverables are read-only

| Field | Value |
|---|---|
| Source CHK IDs | CHK-ORDP-042 |
| Priority | P2 |
| Preconditions | `{{job.progress}}` checked in; `{{job.done}}` Submitted (API) |
| Oracle | spec — CHK-ORDP-042; code — deliverables are read-only once submitted |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.back | — | Jobs list (from the open details of `{{job.progress}}`) |
| 2 | click | jobs-list.card[{{job.progress.jobId}}] | — | "Submit deliverables", no "Check out" |
| 3 | click | job-details.back | — | Jobs list |
| 4 | click | jobs-list.card[{{job.done.jobId}}] | — | "Check out", no "Submit deliverables" |
| 5 | click | job-details.deliverable[Survey] | — | nothing opens within 3 s — the details stay (read-only) |

## TC-ORDP-006 — The PF phone on the In progress screen opens the dialer

| Field | Value |
|---|---|
| Source CHK IDs | CHK-ORDP-016 |
| Priority | P3 |
| Platforms | android (ios: **Blocked — iOS simulator limitation: no Phone app**, as TC-ORDD-004) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.pf-phone[{{pf.phone}}] | — | the dialer with the number |

## Aliases used

| Alias | ios map |
|---|---|
| job-details.back, .status, .description, .address, .on-map, .date, .pf-name, .pf-phone, .attachments, .check-out, .submit-deliverables | yes (modules 04 / 05) |
| job-details.timer | yes — `StaticText` top right whose name holds the digits and colons (the page joins them) |
| job-details.deliverable[{{name}}] | yes — `Other '<name>'`; icon and chevron = the two images inside its rect (`job-details.images`) |
| deliverable-screen.title, .survey-name, .back | yes — `Other` Header `Survey` / `Photo report` / `Notes`, the survey's name, `Button 'Back'` (recon 7) |
| attachments.title, .back; in-app-browser.url, .close, .place | yes (module 04) |
| jobs-list.card[{{jobId}}] | yes |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-ORDP-001, -002, -004, -005, -010, -011, -012, -014, -015, -017, -018 | TC-ORDP-001 | -005 icons / chevrons: presence of the row's images; -011 one address line (D-ORDP-2) |
| CHK-ORDP-003 | TC-ORDP-002 | |
| CHK-ORDP-006…-008 | TC-ORDP-003 | |
| CHK-ORDP-013 | TC-ORDP-004 | in-app browser (D-ORDP-3) |
| CHK-ORDP-042 | TC-ORDP-005 | |
| CHK-ORDP-016 | TC-ORDP-006 | iOS: Blocked (simulator limitation) |

**Not here:** CHK-ORDP-019…028, -038, -039, -041 — module 07 (owner, Q-ORDP-1). CHK-ORDP-029…037, -040 — manual, **verified
by the owner on iOS** (Q-ORDP-2). CHK-ORDP-009 — skipped, no completion indicator exists (D-ORDP-1).
