# Test cases — Order list (mobile)

> Structured, alias-based test cases for the CHK IDs selected in
> [order-list-automation-plan.md](order-list-automation-plan.md). Format:
> [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) ·
> [qa/_templates/test-cases-mobile.md](../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`.
> **Status: draft for the owner's validation — not automated yet.**

| Field | Value |
|---|---|
| Feature | Order list — Jobs list, weekly calendar, job links |
| Platform | cross-platform (Flutter app driven by native drivers) — iOS first, then Android |
| Source checklist | `qa/mobile/03-order-list/order-list-checklist.md` (CHK-ORDL-001…070) |
| Selection | `qa/mobile/03-order-list/order-list-automation-plan.md` → Selected CHK IDs (51) |
| Min OS | iOS 16.0 / Android 12.1 (SRS §2.4) — not run by decision; see [supported-devices.md](../../../docs/platform-specs/supported-devices.md) |
| Devices | iPhone 17 · iOS 26.5 (simulator); Pixel 7 · Android 15 / API 35 (emulator) — [device matrix](../../shared/device-matrix/device-matrix.md) |
| Build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko |
| Last updated | 2026-09-23 |

Execution statuses: **Passed / Failed / Skipped / Blocked / (empty)** — results go to `order-list-traceability.md`
(via `trace_results.py`), never into this file.

**Conventions used in this file** (as in the Auth test cases)

- **Priority:** P0 = smoke, every run · P1 = release regression · P2 = full suite · P3 = edge / scheduled.
- **Oracle model:** accepted production baseline (`docs/notes/decisions.md`, 2026-09-23). Where the SRS / checklist and
  the app + Figma disagree, the TC asserts the app — D-ORDL-1…9 accepted by the owner on 2026-09-23
  ([order-list-questions.md](order-list-questions.md)). All expectations were confirmed on the simulator in recon 4
  (2026-09-24, [qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md)).
- **A card is one text element**: `<date>\n<time>\n<status>\n<jobId> - <title>\n<address>`, with `Updated\n` on top
  when the job is unviewed — then the element type changes (Image), so a card is found by its `jobId`, never by type. `…card[{{jobId}}].<field>` is the parsed field — never a substring of the
  whole card (the address "New York" contains "New").
- **Dates and times** are the job's `scheduleDate` in the **device** time zone: date `d MMM y`, time `HH:mm`
  (card), day title `EEEE, d MMMM` (calendar).
- **Signed in** = the session-scoped `ui_login` fixture (UI login once per run, `{{tech}}`), Jobs list open.
- **Jobs** = the module seed `jobs_seed` (plan, Step 9): created through `POST /job` (`JobController_create`), removed
  through `DELETE /job/{id}` (`JobController_remove`) in `finally`. The seed is created after the Jobs screen loaded, so
  the list is pulled to refresh first — and **the calendar separately** (BUG-ORDL-001: a list refresh does not reach the
  calendar); the calendar TCs refresh it on purpose so their own checks are not hidden by that bug.
- **Job links** are the https links `https://copsfieldservices.dev.concerttech.com/redirect/<key>` returned by
  `POST /job/assign/{phone}` (`JobController_jobAssign`, field `message`), opened as a universal link — iOS simulator:
  `xcrun simctl openurl booted <url>`; Android: `adb shell am start -a android.intent.action.VIEW -d <url>`. The app's
  own scheme `ctflutter://jobs/<key>` does not carry the key (recon 4). Alert auto-accept is switched off for these steps.

---

## TC-ORDL-001 — With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the "No jobs" empty state

| Field | Value |
|---|---|
| ID | TC-ORDL-001 |
| Title | With no active jobs, the Jobs list shows its app bar, the bottom navigation with Jobs active, and the "No jobs" empty state |
| Source CHK IDs | CHK-ORDL-009, CHK-ORDL-011, CHK-ORDL-012, CHK-ORDL-026, CHK-ORDL-027, CHK-ORDL-028, CHK-ORDL-029 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; the technician has **no** active job — checked through `GET /job` (`JobController_findAll`, `userId={{tech.user_id}}`); leftover `QA-AUTO-*` jobs deleted first; if a foreign job is found the TC is **Blocked**, not Failed |
| Oracle | spec — SRS §3.1.2 UI Description, §3.1.2.1 Empty State; spec — figma:2451:83514 (`Jobs_List view_Empty`); accepted baseline D-ORDL-2 ("No jobs"), D-ORDL-3 ("Jobs") — owner, 2026-09-23 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | swipe | jobs-list.root | down | pull to refresh |
| 2 | expect-visible | jobs-list.root | — | title "Jobs list" |
| 3 | expect-visible | jobs-list.view-toggle | — | visible; right side of the app bar (calendar icon) |
| 4 | expect-visible | tabbar.jobs | — | visible; bottom area |
| 5 | expect-visible | tabbar.notifications | — | visible |
| 6 | expect-visible | tabbar.profile | — | visible |
| 7 | expect-visible | tabbar.jobs-selected | — | the Jobs tab is the selected one (tree: `traits` contains `Selected`) |
| 8 | expect-text | jobs-list.empty-state | — | No jobs |
| 9 | expect-text | jobs-list.empty-message | — | Your list of jobs is currently empty. New jobs from your Project Facilitator will appear here. |
| 10 | expect-visible | jobs-list.empty-image | — | an image above the title |
| 11 | expect-hidden | jobs-list.any-card | — | no job card |

**Postconditions / cleanup:** nothing to clean.
**Notes:** the picture itself (CHK-ORDL-027) is unlabelled — only its presence is asserted (partial). Runs before the
module seed exists.

---

## TC-ORDL-002 — The Jobs list stays reachable from the other bottom tabs

| Field | Value |
|---|---|
| ID | TC-ORDL-002 |
| Title | The Jobs list stays reachable from the other bottom tabs |
| Source CHK IDs | CHK-ORDL-013 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; Jobs list open |
| Oracle | spec — SRS §3.1.2 FR-ORD-04; spec — figma:2451:82604 (navigation bar Jobs / Notifications / Profile) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.notifications | — | — |
| 2 | expect-visible | notifications.root | — | Notifications screen |
| 3 | click | tabbar.jobs | — | — |
| 4 | expect-visible | jobs-list.root | — | back on the Jobs list |
| 5 | click | tabbar.profile | — | — |
| 6 | expect-visible | profile.root | — | Profile screen |
| 7 | click | tabbar.jobs | — | — |
| 8 | expect-visible | jobs-list.root | — | back on the Jobs list |

**Postconditions / cleanup:** nothing to clean.

---

## TC-ORDL-003 — A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details

| Field | Value |
|---|---|
| ID | TC-ORDL-003 |
| Title | A job assigned to the technician appears once as a card with its date, time, status, title and address, and opens its details |
| Source CHK IDs | CHK-ORDL-015, CHK-ORDL-016, CHK-ORDL-017, CHK-ORDL-018, CHK-ORDL-019, CHK-ORDL-024, CHK-ORDL-036 |
| Platforms | ios, android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; `{{job.new}}` in the seed (status `new`, today 12:00 local) |
| Oracle | spec — SRS §3.1.2.1 Order Card Elements, FR-ORD-01, FR-ORD-03; spec — figma:2451:82604 (card: date · time · status · "4567 - Cable installation" · address); accepted baseline D-ORDL-4 (one address line) — owner, 2026-09-23; data — the values sent in `POST /job` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | swipe | jobs-list.root | down | pull to refresh (the job was created after the list loaded) |
| 2 | expect-visible | jobs-list.card[{{job.new.jobId}}] | — | visible |
| 3 | expect-text | jobs-list.card[{{job.new.jobId}}].title | — | {{job.new.jobId}} - {{job.new.title}} |
| 4 | expect-text | jobs-list.card[{{job.new.jobId}}].date | — | {{job.new.date}} · {{job.new.time}} |
| 5 | expect-text | jobs-list.card[{{job.new.jobId}}].status | — | New |
| 6 | expect-text | jobs-list.card[{{job.new.jobId}}].address | — | {{job.new.address}} |
| 7 | swipe | jobs-list.root | down | refresh again |
| 8 | expect-text | jobs-list.card-count[{{job.new.jobId}}] | — | 1 — no duplicate after a refresh |
| 9 | click | jobs-list.card[{{job.new.jobId}}] | — | — |
| 10 | expect-text | job-details.header | — | {{job.new.jobId}} - {{job.new.title}} — the details of this job |
| 11 | back | — | — | Jobs list |
| 12 | expect-text | jobs-list.card-count[{{job.new.jobId}}] | — | 1 — no duplicate after navigation |

**Postconditions / cleanup:** the seed is removed after the module.
**Notes:** the bold style of the title line (CHK-ORDL-016) stays manual (partial). Site Name / City / State are one
address line in the app and in Figma (D-ORDL-4). Opening the details marks the job viewed — harmless here (the job was
created without `isViewed`).

---

## TC-ORDL-004 — Each job status shows its own badge; completed, canceled and expired jobs are not listed

| Field | Value |
|---|---|
| ID | TC-ORDL-004 |
| Title | Each job status shows its own badge; completed, canceled and expired jobs are not listed |
| Source CHK IDs | CHK-ORDL-015, CHK-ORDL-020 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; seed jobs `{{job.new}}`, `{{job.in_progress}}`, `{{job.submitted}}`, `{{job.completed}}`, `{{job.canceled}}`, `{{job.expired}}` (all today) |
| Oracle | spec — SRS §3.1.2.1 (status badge), FR-ORD-05; spec — figma:2451:82604 (badges New, In progress); app — badge labels and the Completed / Canceled filter (code, *recon*); accepted baseline D-ORDL-8 (Submitted listed) — owner, 2026-09-23 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | swipe | jobs-list.root | down | pull to refresh |
| 2 | expect-text | jobs-list.card[{{job.new.jobId}}].status | — | New |
| 3 | scroll-to | jobs-list.card[{{job.in_progress.jobId}}] | — | — |
| 4 | expect-text | jobs-list.card[{{job.in_progress.jobId}}].status | — | In progress |
| 5 | scroll-to | jobs-list.card[{{job.submitted.jobId}}] | — | — |
| 6 | expect-text | jobs-list.card[{{job.submitted.jobId}}].status | — | Submitted (D-ORDL-8, accepted) |
| 7 | expect-hidden | jobs-list.card[{{job.completed.jobId}}] | — | not listed (whole list scrolled) |
| 8 | expect-hidden | jobs-list.card[{{job.canceled.jobId}}] | — | not listed |
| 9 | expect-hidden | jobs-list.card[{{job.expired.jobId}}] | — | not listed (recon 4) |

**Postconditions / cleanup:** the seed is removed after the module.
**Notes:** "visually distinct" (CHK-ORDL-020) = a different label per status here; the badge colours stay manual
(partial). `expect-hidden` on a card means the whole list was scrolled to the end without finding it. The list order is
not asserted — no checklist item asks for it (Q-ORDL-4).

---

## TC-ORDL-005 — An unviewed job carries "Updated" in the list and in the calendar until its details are opened

| Field | Value |
|---|---|
| ID | TC-ORDL-005 |
| Title | An unviewed job carries "Updated" in the list and in the calendar until its details are opened |
| Source CHK IDs | CHK-ORDL-022, CHK-ORDL-056 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; seed job `{{job.unviewed}}` (status `new`, today, created with `isViewed=false`); no earlier test opened it |
| Oracle | spec — SRS §3.1.2.1 FR-ORD-06 ("Updated" when applicable), §3.1.2.2 card flags, §3.1.3.1 FR-ORD-D-04 ("Indicator disappears after a technician navigates outside a screen"); spec — figma:2451:82604 (card with "Updated"); app — the label follows the server's `isViewed`, opening the details marks the job viewed (code, *recon*) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | swipe | jobs-list.root | down | pull to refresh |
| 2 | expect-visible | jobs-list.card[{{job.unviewed.jobId}}].updated | — | "Updated" on the card |
| 3 | click | jobs-list.view-toggle | — | calendar, today selected |
| 4 | swipe | jobs-calendar.root | down | pull to refresh the calendar (BUG-ORDL-001) |
| 5 | expect-visible | jobs-calendar.card[{{job.unviewed.jobId}}].updated | — | "Updated" on the calendar card |
| 6 | click | jobs-calendar.card[{{job.unviewed.jobId}}] | — | — |
| 7 | expect-text | job-details.header | — | {{job.unviewed.jobId}} - {{job.unviewed.title}} |
| 8 | back | — | — | calendar |
| 9 | click | jobs-list.view-toggle | — | list |
| 10 | swipe | jobs-list.root | down | pull to refresh |
| 11 | expect-hidden | jobs-list.card[{{job.unviewed.jobId}}].updated | — | no "Updated" any more (SRS FR-ORD-D-04) |

**Postconditions / cleanup:** the seed is removed after the module.
**Notes:** "Unsubmitted" does not exist on the card (D-ORDL-5) — only "Updated" is asserted for CHK-ORDL-056.
Red today: step 11 fails — "Updated" stays after the viewing (runs 1–2, 2026-09-24; drawn screen + server `isViewed=true`) → [BUG-ORDL-003](bugs/BUG-ORDL-003.md) (filed on the owner's go, 2026-09-24). Recon 4 had read "gone" from the screen tree only; the tree after a back navigation is unreliable (TD-JOBS-003). Steps 2, 5 and 11 are therefore decided by the tree **and** the drawn banner together (its fill `#B80B22` on the screen with the card in view — pixels); both must agree.

---

## TC-ORDL-006 — The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back

| Field | Value |
|---|---|
| ID | TC-ORDL-006 |
| Title | The calendar toggle opens the weekly view with Sunday to Saturday, today selected and Jobs still active, and toggles back |
| Source CHK IDs | CHK-ORDL-010, CHK-ORDL-037, CHK-ORDL-039, CHK-ORDL-040, CHK-ORDL-042, CHK-ORDL-044 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; Jobs list open in list mode |
| Oracle | spec — SRS §3.1.2 (calendar icon), §3.1.2.2 UI Description, FR-CAL-W-02, FR-CAL-W-04; spec — figma:2451:82613 (`Jobs_Calendar view`: Sun … Sat, "Wednesday, 9 February") |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.view-toggle | — | — |
| 2 | expect-visible | jobs-calendar.root | — | the weekly view |
| 3 | expect-text | jobs-calendar.week-days | — | the 7 days of the current week, Sunday → Saturday, left to right |
| 4 | expect-text | jobs-calendar.selected-day-title | — | {{today}} as `EEEE, d MMMM` — today is selected |
| 5 | expect-visible | tabbar.jobs-selected | — | bottom navigation still shown, Jobs selected (`traits` contains `Selected`) |
| 6 | click | jobs-list.view-toggle | — | — |
| 7 | expect-visible | jobs-list.root | — | list mode |
| 8 | expect-hidden | jobs-calendar.root | — | no day cells |

**Postconditions / cleanup:** nothing to clean.
**Notes:** the highlight of the selected day (CHK-ORDL-045) is colour only — deferred. Month / year are not shown in
the app or in Figma (D-ORDL-6).

---

## TC-ORDL-007 — Selecting a date shows only that date's jobs, and a date without jobs shows "No jobs"

| Field | Value |
|---|---|
| ID | TC-ORDL-007 |
| Title | Selecting a date shows only that date's jobs, and a date without jobs shows "No jobs" |
| Source CHK IDs | CHK-ORDL-049, CHK-ORDL-050, CHK-ORDL-051, CHK-ORDL-052, CHK-ORDL-053, CHK-ORDL-054, CHK-ORDL-055, CHK-ORDL-060, CHK-ORDL-061, CHK-ORDL-062, CHK-ORDL-063 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; seed jobs `{{job.new}}` (today) and `{{job.other_day}}` (`{{day.with_job}}` — another day of the current week); `{{day.empty}}` — a day of the current week with no job |
| Oracle | spec — SRS §3.1.2.2 FR-CAL-W-01, FR-CAL-W-06, FR-CAL-W-08, card inherited from the list view; spec — figma:2451:82613, figma:2451:83469 (`Jobs_Calendar view_empty`); accepted baseline D-ORDL-2 (empty texts) — owner, 2026-09-23 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.view-toggle | — | calendar, today selected |
| 2 | swipe | jobs-calendar.root | down | pull to refresh the calendar (BUG-ORDL-001) |
| 3 | expect-text | jobs-calendar.card[{{job.new.jobId}}] | — | the same fields as its list card: {{job.new.date}} · {{job.new.time}} · New · {{job.new.jobId}} - {{job.new.title}} · {{job.new.address}} |
| 4 | expect-hidden | jobs-calendar.card[{{job.other_day.jobId}}] | — | not shown for today |
| 5 | click | jobs-calendar.day[{{day.with_job}}] | — | — |
| 6 | expect-text | jobs-calendar.selected-day-title | — | {{day.with_job}} as `EEEE, d MMMM` |
| 7 | expect-visible | jobs-calendar.card[{{job.other_day.jobId}}] | — | shown at once |
| 8 | expect-hidden | jobs-calendar.card[{{job.new.jobId}}] | — | hidden |
| 9 | click | jobs-calendar.day[{{day.empty}}] | — | — |
| 10 | expect-text | jobs-calendar.empty-state | — | No jobs |
| 11 | expect-text | jobs-calendar.empty-message | — | Your list of jobs is currently empty. New jobs from your Project Facilitator will appear here. |
| 12 | expect-hidden | jobs-calendar.any-card | — | no card — the empty state replaces the list |

**Postconditions / cleanup:** the seed is removed after the module.
**Notes:** the empty text is the general one, not "no jobs for the selected date" (D-ORDL-2). Card fields are compared
field by field with the list card format (CHK-ORDL-051…055).

---

## TC-ORDL-008 — The selected date survives a switch to the list and back, and a calendar card opens its job

| Field | Value |
|---|---|
| ID | TC-ORDL-008 |
| Title | The selected date survives a switch to the list and back, and a calendar card opens its job |
| Source CHK IDs | CHK-ORDL-058, CHK-ORDL-068 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; seed job `{{job.other_day}}` on `{{day.with_job}}` |
| Oracle | spec — SRS §3.1.2.2 FR-CAL-W-04, FR-CAL-W-07; spec — checklist CHK-ORDL-068 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.view-toggle | — | calendar |
| 2 | swipe | jobs-calendar.root | down | pull to refresh the calendar (BUG-ORDL-001) |
| 3 | click | jobs-calendar.day[{{day.with_job}}] | — | — |
| 4 | click | jobs-list.view-toggle | — | list |
| 5 | expect-visible | jobs-list.root | — | list mode |
| 6 | click | jobs-list.view-toggle | — | calendar again |
| 7 | expect-text | jobs-calendar.selected-day-title | — | {{day.with_job}} as `EEEE, d MMMM` — the selection is kept |
| 8 | click | jobs-calendar.card[{{job.other_day.jobId}}] | — | — |
| 9 | expect-text | job-details.header | — | {{job.other_day.jobId}} - {{job.other_day.title}} |
| 10 | back | — | — | — |
| 11 | expect-text | jobs-calendar.selected-day-title | — | {{day.with_job}} — back on the same calendar day |

**Postconditions / cleanup:** the seed is removed after the module.

---

## TC-ORDL-009 — Swiping the week strip moves to the next and the previous week

| Field | Value |
|---|---|
| ID | TC-ORDL-009 |
| Title | Swiping the week strip moves to the next and the previous week |
| Source CHK IDs | CHK-ORDL-043, CHK-ORDL-047, CHK-ORDL-048 |
| Platforms | ios, android |
| Priority | P3 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; Jobs list open in list mode |
| Oracle | spec — SRS §3.1.2.2 FR-CAL-W-02, FR-CAL-W-03; spec — figma:2451:82613 (no arrows); accepted baseline D-ORDL-7 (swipe instead of arrows), D-ORDL-12 (the same weekday stays selected) — owner, 2026-09-23 / 2026-09-24 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.view-toggle | — | calendar, current week |
| 2 | swipe | jobs-calendar.week | left | — |
| 3 | expect-text | jobs-calendar.week-days | — | the 7 days of the next week, Sunday → Saturday |
| 4 | expect-text | jobs-calendar.selected-day-title | — | the same weekday as before the swipe, one week later (e.g. Thursday → next Thursday) — D-ORDL-12 |
| 5 | swipe | jobs-calendar.week | right | — |
| 6 | expect-text | jobs-calendar.week-days | — | the current week again |
| 7 | swipe | jobs-calendar.week | right | — |
| 8 | expect-text | jobs-calendar.week-days | — | the 7 days of the previous week |

**Postconditions / cleanup:** nothing to clean.
**Notes:** the calendar pages from the first day of the previous month to the last day of the next month (code) —
one week back and forward is always inside that range.

---

## TC-ORDL-010 — The weekly calendar shows New, In progress and Submitted jobs and hides Completed, Canceled and Expired ones

| Field | Value |
|---|---|
| ID | TC-ORDL-010 |
| Title | The weekly calendar shows New, In progress and Submitted jobs and hides Completed, Canceled and Expired ones |
| Source CHK IDs | CHK-ORDL-057 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; the six status jobs of the seed (as TC-ORDL-004), all today |
| Oracle | spec — SRS §3.1.2.2 FR-CAL-W-05 ("Orders shall be visible by status: New, In Progress"); spec — checklist CHK-ORDL-057; accepted baseline D-ORDL-8 — Submitted is shown as well (owner, 2026-09-23: not described in the SRS, correct in the app) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.view-toggle | — | calendar, today selected |
| 2 | swipe | jobs-calendar.root | down | pull to refresh the calendar (BUG-ORDL-001) |
| 3 | expect-visible | jobs-calendar.card[{{job.new.jobId}}] | — | shown |
| 4 | expect-visible | jobs-calendar.card[{{job.in_progress.jobId}}] | — | shown |
| 5 | expect-visible | jobs-calendar.card[{{job.submitted.jobId}}] | — | shown (D-ORDL-8, accepted) |
| 6 | expect-hidden | jobs-calendar.card[{{job.completed.jobId}}] | — | not shown |
| 7 | expect-hidden | jobs-calendar.card[{{job.canceled.jobId}}] | — | not shown |
| 8 | expect-hidden | jobs-calendar.card[{{job.expired.jobId}}] | — | not shown (confirmed in recon 4) |

**Postconditions / cleanup:** the seed is removed after the module.

---

## TC-ORDL-011 — Signed out, a job link does not open the Jobs list: an unknown key shows "Link expired", a valid key leads to registration

| Field | Value |
|---|---|
| ID | TC-ORDL-011 |
| Title | Signed out, a job link does not open the Jobs list: an unknown key shows "Link expired", a valid key leads to registration |
| Source CHK IDs | CHK-ORDL-003, CHK-ORDL-038 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; app data reset (logged out) |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | no session; `{{link.invalid}}` = `https://copsfieldservices.dev.concerttech.com/redirect/QA-AUTO-INVALID-<ts>` (a key never issued); `{{link.other_phone}}` — the https link from `POST /job/assign/{phone}` for `{{other.phone}}` (reserved `+1 202 555 01xx`, no account) |
| Oracle | spec — SRS §3.1.2.0 (job link: registered → job list, not registered → registration; invalid → error), FR-ORD-01; spec — checklist CHK-ORDL-003; accepted baseline D-ORDL-9 (dialog wording) — owner, 2026-09-23; observed in recon 4 (2026-09-24) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | cold start | Welcome |
| 2 | open | app | job link {{link.invalid}} | — |
| 3 | expect-text | link-expired.title | — | Link expired |
| 4 | expect-text | link-expired.message | — | This link is no longer valid. |
| 5 | click | link-expired.ok | — | — |
| 6 | expect-visible | welcome.root | — | still signed out |
| 7 | open | app | job link {{link.other_phone}} | — |
| 8 | expect-visible | registration.root | — | the registration form opens — the number has no account |
| 9 | expect-hidden | jobs-list.root | — | the Jobs list (and its calendar) never opens |

**Postconditions / cleanup:** nothing created; reset app data.
**Notes:** SRS §3.1.2.0 wording is longer ("…(72 hours passed). Please contact your Project Facilitator.") — D-ORDL-9.
Step 8 follows the app code and recon 4: the key validates to a phone without an account → Registration (for a
registered phone the app would open Login). Closes MISS-06 of the Auth coverage review.

---

## TC-ORDL-012 — A job link for another phone number shows the mismatch dialog; Cancel keeps the session, Log out ends it

| Field | Value |
|---|---|
| ID | TC-ORDL-012 |
| Title | A job link for another phone number shows the mismatch dialog; Cancel keeps the session, Log out ends it |
| Source CHK IDs | CHK-ORDL-004, CHK-ORDL-005, CHK-ORDL-006, CHK-ORDL-007, CHK-ORDL-008 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in as `{{tech}}`; `{{link.other_phone}}` — the https link from `POST /job/assign/{phone}` for `{{other.phone}}` (reserved `+1 202 555 01xx`, not the technician's) — owner go 2026-09-24 |
| Oracle | spec — SRS §3.1.2.1 FR-ORD-01-1; spec — figma:2451:82555 (`Basic dialog/True`: title, text, Cancel, Log out); spec — checklist CHK-ORDL-004…008; human — owner, 2026-09-24: on a device the dialog stays until a button is tapped; accepted baseline D-ORDL-9 (title in sentence case) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | job link {{link.other_phone}} | — |
| 2 | expect-text | phone-mismatch.title | — | Assigned to a different phone number |
| 3 | expect-text | phone-mismatch.message | — | The jobs you are trying to access are assigned to a different phone number. To continue, please log out and sign in with the phone number linked to this job. |
| 4 | expect-visible | phone-mismatch.cancel | — | Cancel |
| 5 | expect-visible | phone-mismatch.log-out | — | Log out |
| 6 | click | phone-mismatch.cancel | — | — |
| 7 | expect-visible | jobs-list.root | — | dialog closed, still signed in |
| 8 | open | app | job link {{link.other_phone}} | the dialog again |
| 9 | click | phone-mismatch.log-out | — | — |
| 10 | expect-visible | welcome.root | — | signed out |
| 11 | open | app | terminate, then cold start | — |
| 12 | expect-visible | welcome.root | — | the session really ended |

**Postconditions / cleanup:** the session is gone — this TC runs **last** in the module; the next module signs in again
(one more OTP). The link expires by itself (72 h); nothing to delete.
**Platform-specific — iOS simulator testing specific, not an app defect:** on the iOS simulator the dialog appears
(steps 2–5 observed in recon 4) but closes by itself after ~0.6 s — 4 of 4 attempts, with and without alert
auto-accept; on a device it stays until a button is tapped (owner, 2026-09-24). So on the iOS simulator steps 4–12 are
**Blocked** with the reason "iOS simulator specific: the dialog closes by itself; on a device it stays (Q-ORDL-8)". On Android the link opens the app directly (App Links) — run
in full. A further idea for iOS: open the link from Notes / Messages on the simulator instead of `simctl openurl`.

---

## TC-ORDL-013 — A job link for the technician's own phone opens the Jobs list

| Field | Value |
|---|---|
| ID | TC-ORDL-013 |
| Title | A job link for the technician's own phone opens the Jobs list |
| Source CHK IDs | CHK-ORDL-002 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in as `{{tech}}`; `{{link.own_phone}}` — the https link from `POST /job/assign/{phone}` for `{{tech.phone}}` (the test account's phone is not real — no SMS is delivered; owner, 2026-09-24) |
| Oracle | spec — SRS §3.1.2.0 ("If the user is registered, the link will open the job list screen within the mobile application"); spec — checklist CHK-ORDL-002; observed in recon 4 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.profile | — | leave the list, so the link must bring it back |
| 2 | expect-visible | profile.root | — | Profile |
| 3 | open | app | job link {{link.own_phone}} | — |
| 4 | expect-visible | jobs-list.root | — | the Jobs list opens |
| 5 | expect-hidden | phone-mismatch.title | — | no mismatch dialog — the phones match |
| 6 | expect-hidden | link-expired.title | — | no error |

**Postconditions / cleanup:** nothing to clean (the link expires by itself).
**Notes:** CHK-ORDL-030 ("jobs assigned via the link appear after synchronization") is **not** automated: on DEV,
without COPS, `synchronize` attaches nothing whatever the delivery channel (recon 4); the owner verified the SMS and the
email link flows manually on production (2026-09-24) — reported as a manual check, not as an automated verdict.

---

## TC-ORDL-014 — The Jobs list is ordered by scheduled date, earliest first

| Field | Value |
|---|---|
| ID | TC-ORDL-014 |
| Title | The Jobs list is ordered by scheduled date, earliest first |
| Source CHK IDs | CHK-ORDL-069 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; seed jobs created **not in date order** — `{{job.other_day}}` (a later day) first, `{{job.yesterday}}` second, today's jobs last — so an order by creation time and an order by date differ |
| Oracle | spec — SRS §3.1.2.1 FR-ORD-02 ("Orders shall be sorted by a date and time (ascending order)"); human — owner, 2026-09-24: the order is judged by the date only, the time within a date is not considered; spec — checklist CHK-ORDL-069 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | swipe | jobs-list.root | down | pull to refresh |
| 2 | expect-text | jobs-list.card-order | {{job.yesterday.jobId}}, {{job.new.jobId}}, {{job.other_day.jobId}} | these three appear top → bottom in this order |
| 3 | expect-text | jobs-list.card-dates | — | the dates of all `QA-AUTO-<run>` cards never decrease from top to bottom (times within one date are not compared) |

**Postconditions / cleanup:** the seed is removed after the module.
**Known issue:** [BUG-ORDL-002](bugs/BUG-ORDL-002.md) (P4) — the list is ordered by **creation time, newest first**
(probe 2026-09-24: dates 24 → 23 → 25). The TC keeps the SRS / owner expectation and **stays red** as the regression check.

---

## TC-ORDL-015 — Jobs that the refreshed list shows are shown in the calendar on their dates

| Field | Value |
|---|---|
| ID | TC-ORDL-015 |
| Title | Jobs that the refreshed list shows are shown in the calendar on their dates |
| Source CHK IDs | CHK-ORDL-070 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | warm start, signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in; the Jobs screen opened **before** the seed was created; seed jobs `{{job.new}}` (today) and `{{job.other_day}}` (`{{day.with_job}}`); no calendar refresh since the seed (runs right after TC-ORDL-004) |
| Oracle | spec — SRS §3.1.2.2 ("This screen complements the Orders List view"; FR-CAL-W-01 orders grouped by the selected date); spec — checklist CHK-ORDL-070 (owner, 2026-09-24) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | swipe | jobs-list.root | down | pull to refresh the list |
| 2 | expect-visible | jobs-list.card[{{job.new.jobId}}] | — | the list shows the job |
| 3 | click | jobs-list.view-toggle | — | calendar, today selected |
| 4 | expect-visible | jobs-calendar.card[{{job.new.jobId}}] | — | the calendar shows it on today — no separate calendar refresh |
| 5 | click | jobs-calendar.day[{{day.with_job}}] | — | — |
| 6 | expect-visible | jobs-calendar.card[{{job.other_day.jobId}}] | — | shown on its day |

**Postconditions / cleanup:** the seed is removed after the module.
**Known issue:** [BUG-ORDL-001](bugs/BUG-ORDL-001.md) — today the calendar shows "No jobs" at step 4 (recon 4, 2 of 2).
The TC keeps the expectation and **stays red** as the regression check for that bug (owner, 2026-09-24).

---

## Aliases used

Screen maps come in step 5 of the module; `MISSING` = not in a map yet — every entry below was **seen in recon 4**
(`qa/shared/recon-dumps/ios-2026-09-24/`), so the ios column is a work order, not an unknown.

| Alias | Screen | android map | ios map |
|---|---|---|---|
| app | — (launch / relaunch / job link) | n/a | n/a (`helpers/app.py`; job-link helper **MISSING** — `simctl openurl`) |
| jobs-list.root, .empty-state | jobs-list | step 7 | yes |
| jobs-list.view-toggle | jobs-list | step 7 | **MISSING** — the only unnamed button in the app bar, y ≈ 66 (TD-JOBS-001) |
| jobs-list.empty-message, .empty-image, .any-card | jobs-list | step 7 | **MISSING** — texts as recon 4; image unlabelled |
| jobs-list.card[{{jobId}}] (+ `.title`, `.date`, `.status`, `.address`, `.updated`) | jobs-list | step 7 | **MISSING** — `name CONTAINS jobId`, any type (StaticText, or Image with "Updated"); fields by the page parser |
| jobs-list.card-count[{{jobId}}], .card-order, .card-dates | jobs-list | step 7 | **MISSING** — page methods over the parsed cards (scrolling the whole list) |
| jobs-calendar.root, .week, .week-days, .day[{{date}}], .selected-day-title | jobs-calendar | step 7 | **MISSING** — day cells `'Thursday, September 24, 2026'`, title `'Thursday, 24 September'` |
| jobs-calendar.card[{{jobId}}] (+ fields, `.updated`), .any-card, .empty-state, .empty-message | jobs-calendar | step 7 | **MISSING** — same card format as the list |
| tabbar.jobs, .notifications, .profile | tab bar (shared) | step 7 | **MISSING** as `tabbar.*` — today `jobs-list.tab-*` (move) |
| tabbar.jobs-selected | tab bar | step 7 | **MISSING** — `name ENDSWITH 'Tab 1 of 3' AND traits CONTAINS 'Selected'` |
| notifications.root, profile.root | notifications, profile | step 7 | **MISSING** — `Other 'Notification list'`, `Other 'Profile'` |
| job-details.header | job-details | step 7 | **MISSING** — `Other '<jobId> - <title>'` |
| link-expired.title, .message, .ok | dialog | step 7 | **MISSING** — `Link expired`, `This link is no longer valid.`, `OK` |
| phone-mismatch.title, .message, .cancel, .log-out | dialog | step 7 | **MISSING** — texts as Figma 2451:82555; `Cancel`, `Log out` |
| welcome.root, registration.root | welcome, registration | step 7 | yes |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech}}, {{tech.email}}, {{tech.phone}} | `automation/mobile/.env` | existing test technician, read-only; the phone is not real |
| {{tech.user_id}} | `GET /technician` (`search={{tech.email}}`) → `user.id` | what `POST /job` needs as `userId` |
| {{job.new}}, {{job.in_progress}}, {{job.submitted}}, {{job.completed}}, {{job.canceled}}, {{job.expired}} | `jobs_seed`, `POST /job` with `statusType`, today | `jobId` `QA-AUTO-<run>-<kind>`, `surveyId` = Short Survey, address and coordinates of recon 3b; distinct times (09:00…14:00) |
| {{job.other_day}} | `jobs_seed` | status `new` on `{{day.with_job}}` |
| {{job.unviewed}} | `jobs_seed` | status `new`, today, `isViewed=false` |
| {{job.yesterday}} | `jobs_seed` | status `new`, yesterday; **creation order of the seed:** `other_day` → `yesterday` → today's jobs (TC-ORDL-014) |
| {{job.*.date}}, {{job.*.time}} | derived from `scheduleDate` in the device time zone | `d MMM y`, `HH:mm` |
| {{today}}, {{day.with_job}}, {{day.empty}} | computed from the device date | "other day" and "empty day" are chosen inside the current Sunday–Saturday week; the empty day is neither today, the other day nor yesterday |
| {{link.invalid}} | generated | `https://copsfieldservices.dev.concerttech.com/redirect/QA-AUTO-INVALID-<ts>`; nothing created |
| {{link.other_phone}}, {{other.phone}} | `POST /job/assign/{phone}` → `message` (https link) | reserved `+1 202 555 01xx`; owner go 2026-09-24 |
| {{link.own_phone}} | `POST /job/assign/{phone}` for `{{tech.phone}}` → `message` | owner go 2026-09-24 (phone not real) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-ORDL-001 | TC-AUTH-005 | tag on the existing test (owner, 2026-09-24) |
| CHK-ORDL-002 | TC-ORDL-013 | |
| CHK-ORDL-003, -038 | TC-ORDL-011 | |
| CHK-ORDL-004…008 | TC-ORDL-012 | steps after the dialog appears: Blocked on the iOS simulator (Q-ORDL-8) |
| CHK-ORDL-009, -011, -026, -029 | TC-ORDL-001 | |
| CHK-ORDL-012 | TC-ORDL-001 | "Jobs" tab (D-ORDL-3) |
| CHK-ORDL-027 | TC-ORDL-001 | **partial** — picture presence only |
| CHK-ORDL-028 | TC-ORDL-001 | "No jobs" (D-ORDL-2) |
| CHK-ORDL-013 | TC-ORDL-002 | |
| CHK-ORDL-015 | TC-ORDL-003, TC-ORDL-004 | |
| CHK-ORDL-016 | TC-ORDL-003 | **partial** — bold manual |
| CHK-ORDL-017, -018 | TC-ORDL-003 | one address line (D-ORDL-4) |
| CHK-ORDL-019, -024, -036 | TC-ORDL-003 | |
| CHK-ORDL-020 | TC-ORDL-004 | **partial** — labels asserted, colours manual |
| CHK-ORDL-022 | TC-ORDL-005 | |
| CHK-ORDL-056 | TC-ORDL-005 | "Updated" only (D-ORDL-5) |
| CHK-ORDL-010, -037, -039, -040, -042, -044 | TC-ORDL-006 | |
| CHK-ORDL-049…055, -060, -063 | TC-ORDL-007 | |
| CHK-ORDL-061, -062 | TC-ORDL-007 | app texts (D-ORDL-2) |
| CHK-ORDL-058, -068 | TC-ORDL-008 | |
| CHK-ORDL-043, -047, -048 | TC-ORDL-009 | swipe instead of arrows (D-ORDL-7); same weekday selected (D-ORDL-12) |
| CHK-ORDL-057 | TC-ORDL-010 | Submitted shown too — correct per the owner (D-ORDL-8) |
| CHK-ORDL-070 | TC-ORDL-015 | red today — BUG-ORDL-001 (regression check) |
| CHK-ORDL-030 | — | **manual — verified by the owner on production** (2026-09-24); not automatable on DEV without COPS |
| CHK-ORDL-069 | TC-ORDL-014 | red today — BUG-ORDL-002 (regression check) |

**Total: 51 CHK IDs in 15 TCs** (+ CHK-ORDL-001 via TC-AUTH-005; 3 partial). Not covered here, with reasons, in the
plan: -030 (manual, owner), -014, -021, -041 (control / label does not exist), -023, -066
(manual), -025, -045, -046, -059 (deferred), -031…-035, -064, -065 (network — Android phase), -067 (load).

## Open questions

- D-ORDL-1…9, -12 — accepted; D-ORDL-11 — bug BUG-ORDL-001; D-ORDL-10 — bug BUG-ORDL-002 (P4).
  All in [order-list-questions.md](order-list-questions.md).
