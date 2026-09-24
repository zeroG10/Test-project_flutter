# Test cases — Order details (mobile)

> Structured, alias-based test cases for the CHK IDs selected in
> [order-details-automation-plan.md](order-details-automation-plan.md). Format:
> [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) ·
> [qa/_templates/test-cases-mobile.md](../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`.
> **Status: validated by the owner 2026-09-24; automated in `automation/mobile/tests/shared/test_order_details.py`.** Written after recon 5 / 5b
> ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md), section "Recon 5 і 5b").

| Field | Value |
|---|---|
| Feature | Order details — the job details screen, Check in start, Attachments (documents, photos, viewers) |
| Platform | cross-platform (Flutter app driven by native drivers) — iOS first, then Android |
| Source checklist | `qa/mobile/04-order-details/order-details-checklist.md` (CHK-ORDD-001…089) |
| Selection | `qa/mobile/04-order-details/order-details-automation-plan.md` → Selected CHK IDs |
| Min OS | iOS 16.0 / Android 12.1 (SRS §2.4) — not run by decision; see [supported-devices.md](../../../docs/platform-specs/supported-devices.md) |
| Devices | iPhone 17 · iOS 26.5 (simulator); Pixel 7 · Android 15 / API 35 (emulator) — [device matrix](../../shared/device-matrix/device-matrix.md) |
| Build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko |
| Last updated | 2026-09-24 |

Execution statuses: **Passed / Failed / Skipped / Blocked / (empty)** — results go to `order-details-traceability.md`
(via `trace_results.py`), never into this file.

**Conventions used in this file** (as modules 01–03)

- **Priority:** P0 = smoke, every run · P1 = release regression · P2 = full suite · P3 = edge / scheduled.
- **Oracle model:** accepted production baseline (`docs/notes/decisions.md`). Where the SRS / checklist and the app +
  Figma disagree, the TC asserts the app — D-ORDD-1…9 accepted by the owner on 2026-09-24
  ([order-details-questions.md](order-details-questions.md)).
- **Signed in** = the `ui_login` fixture; the Jobs list is open.
- **Jobs** = the module seed `details_seed`: created through `POST /job` (`JobController_create`), removed through
  `DELETE /job/{id}` (`JobController_remove`) in `finally`. The attachment files are our own: `POST /file/upload`
  (`FileController_uploadFile`) before, and **`DELETE /file/{id}` (`FileController_deleteFile`) before the job is
  deleted** — deleting the job first leaves the file in storage (recon 5 / 5b).
- **Open a job** = pull the Jobs list to refresh, tap the card `{{job.<kind>.jobId}}` (module 03 aliases).
- **The details screen** is one `SingleChildScrollView`; `Check in` sits outside it at the bottom. Texts are exact
  tree names (recon 5): the description is one element with its lines joined by a line break.
- **System prompts** (location permission) are read with the session setting `respectSystemAlerts: true` and alert
  auto-accept off for those steps (recon 5b).

---

## TC-ORDD-001 — A New job shows every part of its details and the Check in button; back returns to the list

| Field | Value |
|---|---|
| ID | TC-ORDD-001 |
| Title | A New job shows every part of its details and the Check in button; back returns to the list |
| Source CHK IDs | CHK-ORDD-001, CHK-ORDD-002, CHK-ORDD-003, CHK-ORDD-004, CHK-ORDD-005, CHK-ORDD-008, CHK-ORDD-010, CHK-ORDD-011, CHK-ORDD-014, CHK-ORDD-016, CHK-ORDD-018, CHK-ORDD-020, CHK-ORDD-021 |
| Platforms | ios, android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.full}}` in the seed (New, today 12:00 local, 3-line description, PF name + phone, 2 documents + 2 photos) |
| Oracle | spec — SRS §3.1.3.1 UI Description, FR-ORD-D-01, -02, -03, -08; spec — figma:2451:82657 (`Jobs details_New`); accepted baseline D-ORDD-1 (one line `<jobId> - <title>`) — accepted 2026-09-24; data — the values sent in `POST /job` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.full.jobId}}] | — | the details open (after a pull to refresh) |
| 2 | expect-text | job-details.header | — | {{job.full.jobId}} - {{job.full.title}} |
| 3 | expect-text | job-details.status | — | New |
| 4 | expect-text | job-details.title-line | — | {{job.full.jobId}} - {{job.full.title}} |
| 5 | expect-text | job-details.description | — | {{job.full.description}} — the three lines, in order |
| 6 | expect-visible | job-details.location-title | — | "Location" |
| 7 | expect-text | job-details.address | — | {{job.full.address}} |
| 8 | expect-visible | job-details.schedule-title | — | "Scheduled date & time" |
| 9 | expect-text | job-details.date | — | {{job.full.date}} |
| 10 | expect-text | job-details.time | — | {{job.full.time}} |
| 11 | expect-visible | job-details.pf-title | — | "PF info" |
| 12 | expect-text | job-details.pf-name | — | {{pf.name}} |
| 13 | expect-visible | job-details.pf-phone[{{pf.phone}}] | — | a tappable phone (button) |
| 14 | expect-text | job-details.attachments | — | Attachments (4) |
| 15 | expect-visible | job-details.check-in | — | enabled, fully inside the screen (bottom edge ≤ screen height) — without any scroll |
| 16 | expect-hidden | job-details.any-editable | — | no text field or text view on the screen |
| 17 | back | — | — | Jobs list |
| 18 | expect-visible | jobs-list.card[{{job.full.jobId}}] | — | the job's card is still there (presence — TD-JOBS-003) |

**Postconditions / cleanup:** the seed is removed after the module.
**Notes:** the date / time icons and the section dividers (CHK-ORDD-009) are visual — manual. The calendar path of
CHK-ORDD-001 / -002 is covered by TC-ORDL-008 (tag added there): a calendar card opens the details and back keeps the
selected day.

---

## TC-ORDD-002 — A schedule change made on the backend appears on the open details after a refresh

| Field | Value |
|---|---|
| ID | TC-ORDD-002 |
| Title | A schedule change made on the backend appears on the open details after a refresh |
| Source CHK IDs | CHK-ORDD-015 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.reschedule}}` in the seed (New, today 10:00 local) |
| Oracle | spec — SRS FR-ORD-D-06 ("Date and time information shall reflect the latest scheduled values provided by the system"); data — `PATCH /job/{id}` (`JobController_update`), recon 5: HTTP 200 `{"success":true}` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.reschedule.jobId}}] | — | the details open |
| 2 | expect-text | job-details.date | — | {{job.reschedule.date}} |
| 3 | expect-text | job-details.time | — | {{job.reschedule.time}} |
| 4 | api | `PATCH /job/{id}` (`JobController_update`) | `scheduleDate`, `startAt` = {{job.reschedule.new_when}} (+1 day, +2 h) | 200, `success: true` |
| 5 | swipe | job-details.root | down | pull to refresh |
| 6 | expect-text | job-details.date | — | {{job.reschedule.new_date}} |
| 7 | expect-text | job-details.time | — | {{job.reschedule.new_time}} |

**Postconditions / cleanup:** the job is removed with the seed.
**Notes:** the long description (18 lines) of this job also shows that Check in stays at the bottom when the content
is taller than the screen (recon 5) — asserted in TC-ORDD-001 step 15 on the short job; kept here as a note only.

---

## TC-ORDD-003 — "On map" opens the job's location in the in-app browser, and Close returns to the details

| Field | Value |
|---|---|
| ID | TC-ORDD-003 |
| Title | "On map" opens the job's location in the in-app browser, and Close returns to the details |
| Source CHK IDs | CHK-ORDD-012 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.full}}`; Google Maps **not** installed (simulator) |
| Oracle | spec — SRS FR-ORD-D-05 ("an in-app map view, or the device's default map application"); app — recon 5: `maps.apple.com` in an in-app browser (D-ORDD-4, accepted 2026-09-24) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.full.jobId}}] | — | the details open |
| 2 | click | job-details.on-map | — | — |
| 3 | expect-text | in-app-browser.url | — | maps.apple.com |
| 4 | click | in-app-browser.close | — | — |
| 5 | expect-text | job-details.header | — | {{job.full.jobId}} - {{job.full.title}} |

**Postconditions / cleanup:** none beyond the seed.
**Notes:** CHK-ORDD-013 (the map shows the right place) is **not** covered: the browser shows only the host, and the
page stays blank on the simulator (recon 5); the app sends the address, not coordinates (D-ORDD-4). Android: the
default maps app may open instead — the Android map of this TC is written in the Android phase.

---

## TC-ORDD-004 — Tapping the PF phone opens the dialer with the number

| Field | Value |
|---|---|
| ID | TC-ORDD-004 |
| Title | Tapping the PF phone opens the dialer with the number |
| Source CHK IDs | CHK-ORDD-017 |
| Platforms | android (ios: Blocked) |
| Priority | P3 |
| Automation | candidate (Android) |
| Device / OS | Android emulator from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.full}}` |
| Oracle | spec — SRS §3.1.3.1 ("PF Info: Name and phone number (with link to press and dial)") |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.full.jobId}}] | — | the details open |
| 2 | click | job-details.pf-phone[{{pf.phone}}] | — | — |
| 3 | expect-visible | dialer.number | — | the dialer shows {{pf.phone.digits}} |
| 4 | back | — | — | the app, details of the job |

**Postconditions / cleanup:** none.
**Notes:** **iOS: Blocked — iOS simulator limitation: there is no Phone app** (owner, Q-ORDD-3); the tap does nothing
there (recon 5).

---

## TC-ORDD-005 — Check in starts the check-in flow; refusing location and cancelling leaves the job New

| Field | Value |
|---|---|
| ID | TC-ORDD-005 |
| Title | Check in starts the check-in flow; refusing location and cancelling leaves the job New |
| Source CHK IDs | CHK-ORDD-022 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in; **location permission not decided** (iOS: `xcrun simctl privacy <udid> reset location <bundle>` before the launch) |
| Permissions | location: not determined |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.full}}` (New) |
| Oracle | spec — SRS FR-ORD-D-09 ("Selecting Check In shall initiate the check-in workflow"), FR-LOC-01 (location asked only on check-in); app — recon 5b (the prompt texts); data — `GET /job/{id}` status after the flow |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.full.jobId}}] | — | the details open |
| 2 | click | job-details.check-in | — | — |
| 3 | expect-visible | job-details.checking-in | — | "Checking in", disabled |
| 4 | expect-text | location-prompt.title | — | Allow "[DEV] CT Mobile" to use your location? — the system prompt (within 15 s) |
| 5 | click | location-prompt.dont-allow | — | — |
| 6 | expect-text | location-disabled.title | — | Location disabled |
| 7 | expect-text | location-disabled.message | — | To use GPS check-in, please enable location services in your device settings. You can still check in manually if you prefer. |
| 8 | click | location-disabled.cancel | — | — |
| 9 | expect-visible | job-details.check-in | — | "Check in" again, enabled |
| 10 | expect-text | job-details.status | — | New |
| 11 | api | `GET /job/{id}` (`JobController_findOne`) | — | `statusType` = `new` — no check-in was recorded |

**Postconditions / cleanup:** the permission stays "denied" until the next reinstall (every run starts with one).
**Notes:** the rest of the check-in flow (GPS, proximity, manual entry, the record) is module 05 (Q-ORDD-1). The app
shows no own prompt before the system one, and "Cancel" ends the check-in (D-ORDD-9 — decided in module 05). This TC
runs **last** on `{{job.full}}`: if the flow ever completed, the job would be In progress.

---

## TC-ORDD-006 — Attachments opens with Documents selected and lists the job's documents; Photos switches the tab

| Field | Value |
|---|---|
| ID | TC-ORDD-006 |
| Title | Attachments opens with Documents selected and lists the job's documents; Photos switches the tab |
| Source CHK IDs | CHK-ORDD-019, CHK-ORDD-051, CHK-ORDD-052, CHK-ORDD-053, CHK-ORDD-054, CHK-ORDD-055, CHK-ORDD-057, CHK-ORDD-059, CHK-ORDD-060, CHK-ORDD-061 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.full}}` with `{{doc.safety}}`, `{{doc.power}}`, `{{photo.1}}`, `{{photo.2}}` |
| Oracle | spec — SRS §3.1.3.2 Main Layout, FR-ORD-D-07, FR-ATT-02, FR-ATT-03, §3.1.3.2.1 (file name with extension); spec — figma:2451:83062 (`Job details_Atachments_Documents`) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.full.jobId}}] | — | the details open |
| 2 | click | job-details.attachments | — | — |
| 3 | expect-text | attachments.title | — | Attachments |
| 4 | expect-visible | attachments.back | — | the back control |
| 5 | expect-visible | attachments.tab[Documents] | — | the first of two tabs |
| 6 | expect-visible | attachments.tab[Photos] | — | the second of two tabs |
| 7 | expect-text | attachments.selected-tab | — | Documents |
| 8 | expect-visible | attachments.document[{{doc.safety.name}}] | — | "QA-AUTO safety.pdf" — name with its extension |
| 9 | expect-visible | attachments.document[{{doc.power.name}}] | — | "QA-AUTO power.pdf" |
| 10 | click | attachments.tab[Photos] | — | — |
| 11 | expect-text | attachments.selected-tab | — | Photos |
| 12 | expect-hidden | attachments.document[{{doc.safety.name}}] | — | no document under Photos |
| 13 | click | attachments.tab[Documents] | — | — |
| 14 | expect-visible | attachments.document[{{doc.safety.name}}] | — | the documents are back |
| 15 | click | attachments.back | — | — |
| 16 | expect-text | job-details.header | — | {{job.full.jobId}} - {{job.full.title}} |

**Postconditions / cleanup:** none beyond the seed.
**Notes:** CHK-ORDD-056 / -058 (every photo listed, photos only under Photos) need the thumbnails, which did not load
in recon 5b — **Q-ORDD-6**; they move into TC-ORDD-008. The file-type icon (CHK-ORDD-061) is visual; the extension in
the name is asserted.

---

## TC-ORDD-007 — A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents

| Field | Value |
|---|---|
| ID | TC-ORDD-007 |
| Title | A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents |
| Source CHK IDs | CHK-ORDD-062, CHK-ORDD-063, CHK-ORDD-066, CHK-ORDD-067, CHK-ORDD-068, CHK-ORDD-087 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate — **depends on Q-ORDD-6** |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.full}}` with `{{doc.safety}}` (our 2-page PDF) |
| Oracle | spec — SRS §3.1.3.2.1 Behavior, FR-ATT-06, FR-ATT-07; spec — figma:2451:83360 (`Job details_Atachments_Document details`); data — the uploaded PDF (page 1: a brand-colour block, page 2: a blue block) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.full.jobId}}] | — | the details open |
| 2 | click | job-details.attachments | — | Documents selected |
| 3 | click | attachments.document[{{doc.safety.name}}] | — | — |
| 4 | expect-text | pdf-viewer.title | — | QA-AUTO safety.pdf |
| 5 | expect-drawn | pdf-viewer.page | — | the first page is drawn: its brand-colour block is on screen (pixels, within 20 s) |
| 6 | expect-hidden | attachments.tab[Documents] | — | no tabs, no tab bar — the viewer fills the screen |
| 7 | expect-hidden | pdf-viewer.any-editable | — | no text field — read-only |
| 8 | expect-visible | pdf-viewer.close | — | the X control (unlabelled — located by its place, TD-ORDD-001) |
| 9 | click | pdf-viewer.close | — | — |
| 10 | expect-text | attachments.selected-tab | — | Documents — the tab did not reset |
| 11 | expect-visible | attachments.document[{{doc.safety.name}}] | — | the list |

**Postconditions / cleanup:** none beyond the seed.
**Notes:** in recon 5b the viewer opened (title, X) but **the page was not drawn within 5 s** — Q-ORDD-6. Page
scrolling and zoom (CHK-ORDD-064, -065) are deferred (gestures). Saving (CHK-ORDD-069, -070) is the system share
sheet without a toast (D-ORDD-6) — manual / skipped.

---

## TC-ORDD-008 — Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos

| Field | Value |
|---|---|
| ID | TC-ORDD-008 |
| Title | Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos |
| Source CHK IDs | CHK-ORDD-056, CHK-ORDD-058, CHK-ORDD-073, CHK-ORDD-074, CHK-ORDD-075, CHK-ORDD-076, CHK-ORDD-079, CHK-ORDD-080, CHK-ORDD-087 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate — **depends on Q-ORDD-6** |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.full}}` with `{{photo.1}}`, `{{photo.2}}` |
| Oracle | spec — SRS §3.1.3.2.2, FR-ATT-10; spec — figma:2451:83346 (`Job details_Atachments_Photos`); app — D-ORDD-7 (back arrow instead of X) accepted 2026-09-24 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.full.jobId}}] | — | the details open |
| 2 | click | job-details.attachments | — | — |
| 3 | click | attachments.tab[Photos] | — | Photos selected |
| 4 | expect-drawn | attachments.thumbnail[1..2] | — | two thumbnails side by side, same size (pixels; the thumbnails have no name in the tree) — no error icon |
| 5 | click | attachments.thumbnail[1] | — | — |
| 6 | expect-drawn | photo-viewer.image | — | the photo fills the screen width (pixels) |
| 7 | expect-hidden | attachments.tab[Photos] | — | no tabs — full screen |
| 8 | expect-visible | photo-viewer.back | — | the back arrow (D-ORDD-7) |
| 9 | click | photo-viewer.back | — | — |
| 10 | expect-text | attachments.selected-tab | — | Photos — the tab did not reset |

**Postconditions / cleanup:** none beyond the seed.
**Notes:** in recon 5b both thumbnails showed **the error icon** — Q-ORDD-6. Pinch / pan (CHK-ORDD-077, -078) are
deferred (gestures).

---

## TC-ORDD-009 — After the details of an unviewed job were opened, the details no longer show "Updated"

| Field | Value |
|---|---|
| ID | TC-ORDD-009 |
| Title | After the details of an unviewed job were opened, the details no longer show "Updated" |
| Source CHK IDs | CHK-ORDD-007 |
| Platforms | ios, android |
| Priority | P3 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.unviewed}}` (`isViewed=false`); no earlier test opened it |
| Oracle | spec — SRS FR-ORD-D-04 ("Indicator disappears after a technician navigates outside a screen"); data — `GET /job/{id}` `isViewed` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.card[{{job.unviewed.jobId}}] | — | the details open |
| 2 | back | — | — | Jobs list |
| 3 | api | `GET /job/{id}` (`JobController_findOne`) | — | `isViewed` = true (polled up to 10 s) |
| 4 | click | jobs-list.card[{{job.unviewed.jobId}}] | — | the details open again |
| 5 | expect-hidden | job-details.updated-banner | — | no "Updated" banner for 2 s (pixels: banner fill < 0.5 % — the tree does not show it) |

**Postconditions / cleanup:** none beyond the seed.
**Notes:** CHK-ORDD-006 (the banner **is** shown on the details) is **manual**: the app shows it only ~0.3 s after
opening and removes it while the technician is still on the screen (recon 5, D-ORDD-3) — too short for a stable
check. The list card keeps "Updated" after this (BUG-ORDL-003) — not asserted here.

---

## Aliases used

`MISSING` = not in a map yet — every entry was **seen in recon 5 / 5b** (`qa/shared/recon-dumps/ios-2026-09-24/recon5*`),
so the ios column is a work order, not an unknown.

| Alias | Screen | android map | ios map |
|---|---|---|---|
| jobs-list.card[{{jobId}}] | jobs-list | step 7 | yes |
| job-details.header | job-details | step 7 | yes |
| job-details.status, .title-line, .description, .location-title, .address, .schedule-title, .date, .time, .pf-title, .pf-name | job-details | step 7 | **MISSING** — `StaticText` by name (recon 5); date `d MMM y`, time `HH:mm` |
| job-details.on-map, .pf-phone[{{phone}}], .attachments, .check-in, .checking-in | job-details | step 7 | **MISSING** — `Button 'On map'`, `Button '<phone>'`, `Button 'Attachments (N)'` (`BEGINSWITH 'Attachments'`), `Button 'Check in'`, `Button 'Checking in'` (NotEnabled) |
| job-details.any-editable | job-details | step 7 | **MISSING** — `TextField OR TextView OR SecureTextField` |
| job-details.updated-banner | job-details | step 7 | **MISSING** — pixels only (banner fill #B80B22), as the list |
| job-details.root | job-details | step 7 | **MISSING** — the scrolling content (pull to refresh) |
| in-app-browser.url, .close | system in-app browser | step 7 | **MISSING** — `Button 'URL'` (value `maps.apple.com`), `Button 'Close'` |
| location-prompt.title, .dont-allow | system alert | step 7 | **MISSING** — `Alert` / `StaticText` "Allow “[DEV] CT Mobile” to use your location?", `Button 'Don’t Allow'`; needs `respectSystemAlerts` |
| location-disabled.title, .message, .cancel, .go-to-settings | app dialog | step 7 | **MISSING** — texts as recon 5b |
| attachments.title, .back | attachments | step 7 | **MISSING** — `Other 'Attachments'` (Header), `Button 'Back'` |
| attachments.tab[Documents], .tab[Photos], .selected-tab | attachments | step 7 | **MISSING** — `name BEGINSWITH 'Documents'` / `'Photos'`; selected = `traits CONTAINS 'Selected'` |
| attachments.document[{{name}}] | attachments | step 7 | **MISSING** — `Button '<file name>'` |
| attachments.thumbnail[n] | attachments | step 7 | **MISSING** — not in the tree; grid cells by position + pixels (Q-ORDD-6) |
| pdf-viewer.title, .close, .page, .any-editable | pdf viewer | step 7 | **MISSING** — `Other '<file name>'` (Header); X = the unnamed `Button` at the right of the app bar (TD-ORDD-001); page — pixels |
| photo-viewer.image, .back | photo viewer | step 7 | **MISSING** — not seen yet (Q-ORDD-6); back = `Button 'Back'` expected |
| dialer.number | Android dialer | step 7 | n/a (iOS: Blocked) |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech}}, {{tech.user_id}} | `.env`, `GET /technician` | as module 03 |
| {{job.full}} | `details_seed`: `POST /job` — New, today 12:00 local, description "Inspect and secure antenna mounts. / Replace cable entry seals. / Test signal transmission levels.", `projectFacilitator` {{pf}}, `attachments` 2 documents + 2 photos | `jobId` `QA-AUTO-<run>-FULL`; address and coordinates of module 03 |
| {{pf.name}}, {{pf.phone}} | fixed | `QA-AUTO PF Olive`, `+1 202 555 0147` (reserved range) |
| {{doc.safety}}, {{doc.power}} | `POST /file/upload` of `fixtures/media/qa_auto_2_pages.pdf` → `location`; two document entries with names `QA-AUTO safety.pdf`, `QA-AUTO power.pdf` (same file) | the file is deleted with `DELETE /file/{id}` **before** the job |
| {{photo.1}}, {{photo.2}} | `POST /file/upload` of `fixtures/media/site_photo.jpg`, `site_photo_2.jpg` | as above |
| {{job.reschedule}} | `details_seed`: New, today 10:00 local, an 18-line description | `new_when` = +1 day +2 h; `PATCH /job/{id}` in the test |
| {{job.unviewed}} | `details_seed`: New, today 13:00 local, `isViewed=false` | opened only by TC-ORDD-009 |
| {{job.*.date}}, {{job.*.time}} | from `scheduleDate` in the device time zone | `d MMM y`, `HH:mm` |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-ORDD-001, -002 | TC-ORDD-001, TC-ORDL-008 | list here; calendar path in TC-ORDL-008 (tag) |
| CHK-ORDD-003, -004 | TC-ORDD-001 | one line `<jobId> - <title>` (D-ORDD-1) |
| CHK-ORDD-005, -008, -010, -011, -016, -018, -020, -021 | TC-ORDD-001 | |
| CHK-ORDD-014 | TC-ORDD-001 | **partial** — texts; icons manual |
| CHK-ORDD-015 | TC-ORDD-002 | |
| CHK-ORDD-012 | TC-ORDD-003 | in-app browser `maps.apple.com` (D-ORDD-4) |
| CHK-ORDD-017 | TC-ORDD-004 | Android; iOS Blocked — simulator limitation |
| CHK-ORDD-022 | TC-ORDD-005 | |
| CHK-ORDD-019, -051…-055, -057, -059, -060 | TC-ORDD-006 | |
| CHK-ORDD-061 | TC-ORDD-006 | **partial** — extension; icon manual |
| CHK-ORDD-062, -063, -066…-068 | TC-ORDD-007 | depends on Q-ORDD-6 |
| CHK-ORDD-087 | TC-ORDD-007, TC-ORDD-008 | |
| CHK-ORDD-056, -058, -073…-076, -079, -080 | TC-ORDD-008 | depends on Q-ORDD-6; -079 back arrow (D-ORDD-7) |
| CHK-ORDD-007 | TC-ORDD-009 | |

**Total: 42 CHK IDs in 9 TCs** (2 partial). Changed from the plan after recon 5: **CHK-ORDD-006 → manual** (the banner
lives ~0.3 s), **CHK-ORDD-013 → not automated on the simulator** (blank page, host only). Not covered here, with
reasons, in the plan: -023…-047 (module 05), -009, -086, -069 (manual), -048…-050, -081…-085, -089 (manual, verified
by the owner on iOS), -064, -065, -077, -078 (gestures deferred), -070 (skipped — D-ORDD-6), -071 (manual — D-ORDD-5), -072, -088 (not recommended now).

## Open questions

- D-ORDD-1…9 — accepted by the owner 2026-09-24 ([order-details-questions.md](order-details-questions.md)).
- **Q-ORDD-6** — photos and PDFs of the attachments did not load in the app on the simulator (recon 5b); TC-ORDD-007
  and -008 depend on it.
