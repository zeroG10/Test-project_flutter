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
| Source checklist | `qa/mobile/03-order-list/order-list-checklist.md` (CHK-ORDL-001…068) |
| Selection | `qa/mobile/03-order-list/order-list-automation-plan.md` → Selected CHK IDs (48) |
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
  ([order-list-questions.md](order-list-questions.md)). Expectations marked *(recon)* come from the app code and are
  confirmed on the simulator before the test is written.
- **A card is one text element**: `<date>\n<time>\n<status>\n<jobId> - <title>\n<address>` (recon 3b), with
  `Updated` on top when the job is unviewed. `…card[{{jobId}}].<field>` is the parsed field — never a substring of the
  whole card (the address "New York" contains "New").
- **Dates and times** are the job's `scheduleDate` in the **device** time zone: date `d MMM y`, time `HH:mm`
  (card), day title `EEEE, d MMMM` (calendar).
- **Signed in** = the session-scoped `ui_login` fixture (UI login once per run, `{{tech}}`), Jobs list open.
- **Jobs** = the module seed `jobs_seed` (plan, Step 9): created through `POST /job` (`JobController_create`), removed
  through `DELETE /job/{id}` (`JobController_remove`) in `finally`.

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
| 7 | expect-visible | tabbar.jobs-selected | — | the Jobs tab is the selected one *(recon: tree state or pixels)* |
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
| 9 | expect-hidden | jobs-list.card[{{job.expired.jobId}}] | — | not listed *(recon 3b: the technician's 8 expired jobs were not listed)* |

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
| Oracle | spec — SRS §3.1.2.1 FR-ORD-06 ("Updated" when applicable), §3.1.2.2 card flags; spec — figma:2451:82604 (card with "Updated"); app — the label follows the server's `isViewed`, opening the details marks the job viewed (code, *recon*) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | swipe | jobs-list.root | down | pull to refresh |
| 2 | expect-visible | jobs-list.card[{{job.unviewed.jobId}}].updated | — | "Updated" on the card |
| 3 | click | jobs-list.view-toggle | — | calendar, today selected |
| 4 | expect-visible | jobs-calendar.card[{{job.unviewed.jobId}}].updated | — | "Updated" on the calendar card |
| 5 | click | jobs-calendar.card[{{job.unviewed.jobId}}] | — | — |
| 6 | expect-text | job-details.header | — | {{job.unviewed.jobId}} - {{job.unviewed.title}} |
| 7 | back | — | — | calendar |
| 8 | click | jobs-list.view-toggle | — | list |
| 9 | swipe | jobs-list.root | down | pull to refresh |
| 10 | expect-hidden | jobs-list.card[{{job.unviewed.jobId}}].updated | — | no "Updated" any more |

**Postconditions / cleanup:** the seed is removed after the module.
**Notes:** "Unsubmitted" does not exist on the card (D-ORDL-5) — only "Updated" is asserted for CHK-ORDL-056.

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
| 5 | expect-visible | tabbar.jobs-selected | — | bottom navigation still shown, Jobs selected |
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
| 2 | expect-text | jobs-calendar.card[{{job.new.jobId}}] | — | the same fields as its list card: {{job.new.date}} · {{job.new.time}} · New · {{job.new.jobId}} - {{job.new.title}} · {{job.new.address}} |
| 3 | expect-hidden | jobs-calendar.card[{{job.other_day.jobId}}] | — | not shown for today |
| 4 | click | jobs-calendar.day[{{day.with_job}}] | — | — |
| 5 | expect-text | jobs-calendar.selected-day-title | — | {{day.with_job}} as `EEEE, d MMMM` |
| 6 | expect-visible | jobs-calendar.card[{{job.other_day.jobId}}] | — | shown at once |
| 7 | expect-hidden | jobs-calendar.card[{{job.new.jobId}}] | — | hidden |
| 8 | click | jobs-calendar.day[{{day.empty}}] | — | — |
| 9 | expect-text | jobs-calendar.empty-state | — | No jobs |
| 10 | expect-text | jobs-calendar.empty-message | — | Your list of jobs is currently empty. New jobs from your Project Facilitator will appear here. |
| 11 | expect-hidden | jobs-calendar.any-card | — | no card — the empty state replaces the list |

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
| 2 | click | jobs-calendar.day[{{day.with_job}}] | — | — |
| 3 | click | jobs-list.view-toggle | — | list |
| 4 | expect-visible | jobs-list.root | — | list mode |
| 5 | click | jobs-list.view-toggle | — | calendar again |
| 6 | expect-text | jobs-calendar.selected-day-title | — | {{day.with_job}} as `EEEE, d MMMM` — the selection is kept |
| 7 | click | jobs-calendar.card[{{job.other_day.jobId}}] | — | — |
| 8 | expect-text | job-details.header | — | {{job.other_day.jobId}} - {{job.other_day.title}} |
| 9 | back | — | — | — |
| 10 | expect-text | jobs-calendar.selected-day-title | — | {{day.with_job}} — back on the same calendar day |

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
| Oracle | spec — SRS §3.1.2.2 FR-CAL-W-02, FR-CAL-W-03; spec — figma:2451:82613 (no arrows); accepted baseline D-ORDL-7 (swipe instead of arrows) — owner, 2026-09-23 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | jobs-list.view-toggle | — | calendar, current week |
| 2 | swipe | jobs-calendar.week | left | — |
| 3 | expect-text | jobs-calendar.week-days | — | the 7 days of the next week, Sunday → Saturday |
| 4 | expect-text | jobs-calendar.selected-day-title | — | {{next_week.sunday}} — the first day of the week *(recon; D-ORDL-7)* |
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
| 2 | expect-visible | jobs-calendar.card[{{job.new.jobId}}] | — | shown |
| 3 | expect-visible | jobs-calendar.card[{{job.in_progress.jobId}}] | — | shown |
| 4 | expect-visible | jobs-calendar.card[{{job.submitted.jobId}}] | — | shown (D-ORDL-8, accepted) |
| 5 | expect-hidden | jobs-calendar.card[{{job.completed.jobId}}] | — | not shown |
| 6 | expect-hidden | jobs-calendar.card[{{job.canceled.jobId}}] | — | not shown |
| 7 | expect-hidden | jobs-calendar.card[{{job.expired.jobId}}] | — | not shown |

**Postconditions / cleanup:** the seed is removed after the module.

---

## TC-ORDL-011 — Signed out, a job link does not open the Jobs list

| Field | Value |
|---|---|
| ID | TC-ORDL-011 |
| Title | Signed out, a job link does not open the Jobs list |
| Source CHK IDs | CHK-ORDL-003, CHK-ORDL-038 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; app data reset (logged out) |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | no session; `{{link.invalid}}` = `ctflutter://jobs/QA-AUTO-INVALID-<ts>` (a key that was never issued) |
| Oracle | spec — SRS §3.1.2.0 (job link: validity, "Link expired" error), FR-ORD-01 (list for the authenticated user); spec — checklist CHK-ORDL-003; accepted baseline D-ORDL-9 (dialog wording) — owner, 2026-09-23 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | cold start | Welcome |
| 2 | open | app | deep link {{link.invalid}} | — |
| 3 | expect-text | link-expired.title | — | Link expired *(recon)* |
| 4 | expect-text | link-expired.message | — | This link is no longer valid. *(recon)* |
| 5 | click | link-expired.ok | — | — |
| 6 | expect-visible | welcome.root | — | still signed out |
| 7 | expect-hidden | jobs-list.root | — | the Jobs list (and its calendar) never opens |

**Postconditions / cleanup:** nothing created (the app only asks the server to validate the key).
**Notes:** SRS §3.1.2.0 wording is longer ("…(72 hours passed). Please contact your Project Facilitator.") — D-ORDL-9.
Closes MISS-06 of the Auth coverage review.

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
| Preconditions | signed in as `{{tech}}`; `{{link.other_phone}}` — the key taken from the **response** of `POST /job/assign/{phone}` (`JobController_jobAssign`: `message` = `https://…/redirect/<key>`) for `{{other.phone}}` (reserved `+1 202 555 01xx`, not the technician's); no SMS or email is read — **method waits for the owner (Q-ORDL-2)** |
| Oracle | spec — SRS §3.1.2.1 FR-ORD-01-1; spec — figma:2451:82555 (`Basic dialog/True`: title, text, Log out); spec — checklist CHK-ORDL-004…008; accepted baseline D-ORDL-9 (title in sentence case) — owner, 2026-09-23 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | deep link `ctflutter://jobs/{{link.other_phone}}` | — |
| 2 | expect-text | phone-mismatch.title | — | Assigned to a different phone number |
| 3 | expect-text | phone-mismatch.message | — | The jobs you are trying to access are assigned to a different phone number. To continue, please log out and sign in with the phone number linked to this job. |
| 4 | expect-visible | phone-mismatch.cancel | — | Cancel |
| 5 | expect-visible | phone-mismatch.log-out | — | Log out |
| 6 | click | phone-mismatch.cancel | — | — |
| 7 | expect-visible | jobs-list.root | — | dialog closed, still signed in |
| 8 | open | app | deep link `ctflutter://jobs/{{link.other_phone}}` | the dialog again |
| 9 | click | phone-mismatch.log-out | — | — |
| 10 | expect-visible | welcome.root | — | signed out |
| 11 | open | app | terminate, then cold start | — |
| 12 | expect-visible | welcome.root | — | the session really ended |

**Notes:** the link is opened the way the app receives it from a message — the app handles `ctflutter://jobs/<key>` and
`https://…/redirect/<key>` alike (the key is the last path segment); the recon tries the https link first. SMS / email
delivery of the link is out of scope (backend + Twilio; checked manually on production by the owner).
**Postconditions / cleanup:** the session is gone — this TC runs **last** in the module; the next module signs in again
(one more OTP). The link expires by itself (72 h); nothing to delete.

---

## Aliases used

Screen maps come in step 5 of the module; `MISSING` = to be added from the module recon.

| Alias | Screen | android map | ios map |
|---|---|---|---|
| app | — (launch / relaunch / deep link) | n/a | n/a (`helpers/app.py`; deep link helper **MISSING**) |
| jobs-list.root, .empty-state | jobs-list | step 7 | yes |
| jobs-list.view-toggle | jobs-list | step 7 | **MISSING** — the only unnamed button in the app bar (TD-JOBS-001) |
| jobs-list.empty-message, .empty-image, .any-card | jobs-list | step 7 | **MISSING** |
| jobs-list.card[{{jobId}}] (+ `.title`, `.date`, `.status`, `.address`, `.updated`) | jobs-list | step 7 | **MISSING** — `name CONTAINS jobId`; fields by the page parser |
| jobs-list.card-count[{{jobId}}] | jobs-list | step 7 | **MISSING** — page method |
| jobs-calendar.root, .week, .week-days, .day[{{date}}], .selected-day-title | jobs-calendar | step 7 | **MISSING** — day cells are named by the full date (recon 3b) |
| jobs-calendar.card[{{jobId}}] (+ fields, `.updated`), .any-card, .empty-state, .empty-message | jobs-calendar | step 7 | **MISSING** |
| tabbar.jobs, .notifications, .profile | tab bar (shared) | step 7 | **MISSING** as `tabbar.*` — today `jobs-list.tab-*` (move) |
| tabbar.jobs-selected | tab bar | step 7 | **MISSING** — state from the tree or pixels (recon) |
| notifications.root, profile.root | notifications, profile | step 7 | **MISSING** |
| job-details.header | job-details | step 7 | **MISSING** — the app-bar text `<jobId> - <title>` (dump `job_details_new.xml`) |
| link-expired.title, .message, .ok | dialog | step 7 | **MISSING** |
| phone-mismatch.title, .message, .cancel, .log-out | dialog | step 7 | **MISSING** |
| welcome.root | welcome | step 7 | yes |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech}}, {{tech.email}} | `automation/mobile/.env` | existing test technician, read-only |
| {{tech.user_id}} | `GET /technician` (`search={{tech.email}}`) → `user.id` | what `POST /job` needs as `userId` |
| {{job.new}}, {{job.in_progress}}, {{job.submitted}}, {{job.completed}}, {{job.canceled}}, {{job.expired}} | `jobs_seed`, `POST /job` with `statusType`, today 12:00 local | `jobId` `QA-AUTO-<run>-<kind>`, `surveyId` = Short Survey, address and coordinates of recon 3b |
| {{job.other_day}} | `jobs_seed` | status `new` on `{{day.with_job}}` |
| {{job.unviewed}} | `jobs_seed` | status `new`, today, `isViewed=false` |
| {{job.*.date}}, {{job.*.time}} | derived from `scheduleDate` in the device time zone | `d MMM y`, `HH:mm` |
| {{today}}, {{day.with_job}}, {{day.empty}}, {{next_week.sunday}} | computed from the device date | "other day" and "empty day" are chosen inside the current Sunday–Saturday week |
| {{link.invalid}} | generated | never issued, nothing created |
| {{link.other_phone}}, {{other.phone}} | `POST /job/assign/{phone}` → last segment of the returned URL | owner go (Q-ORDL-2) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-ORDL-001 | TC-AUTH-005 | tag added to the existing test — owner OK (Q-ORDL-5) |
| CHK-ORDL-003, -038 | TC-ORDL-011 | |
| CHK-ORDL-004…008 | TC-ORDL-012 | owner go for the link (Q-ORDL-2) |
| CHK-ORDL-009, -011, -026, -029 | TC-ORDL-001 | |
| CHK-ORDL-012 | TC-ORDL-001 | "Jobs" tab (D-ORDL-3); state readable after recon |
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
| CHK-ORDL-043, -047, -048 | TC-ORDL-009 | swipe instead of arrows (D-ORDL-7) |
| CHK-ORDL-057 | TC-ORDL-010 | Submitted shown too — correct per the owner (D-ORDL-8) |

**Total: 48 CHK IDs in 12 TCs** (+ CHK-ORDL-001 via TC-AUTH-005; 3 partial). Not covered here, with reasons, in the
plan: -002, -030 (own-phone link), -014, -021, -041 (control / label does not exist), -023, -066 (manual), -025,
-045, -046, -059 (deferred), -031…-035, -064, -065 (network — Android phase), -067 (load).

## Open questions

- D-ORDL-1…9 — accepted (owner, 2026-09-23). Q-ORDL-1…7 still open — [order-list-questions.md](order-list-questions.md).
- **Added 2026-09-24 (owner):** CHK-ORDL-069 (ascending sort, SRS FR-ORD-02) and CHK-ORDL-002 / -030 (job link for the
  technician's own phone — the phone is not real, no SMS arrives). Their TCs (TC-ORDL-014, TC-ORDL-013) are written after
  the recon shows the server order and what `synchronize` does.
