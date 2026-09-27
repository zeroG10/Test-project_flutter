# Test cases — Notifications (mobile)

> Structured, alias-based test cases for the CHK IDs selected in [notifications-automation-plan.md](notifications-automation-plan.md).
> Format: [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: draft. Written after recon 12 ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md)) and the
> owner's decisions of 2026-09-27: D-NOTIF-1…5, Q-NOTIF-1…4 — [notifications-questions.md](notifications-questions.md).**

| Field | Value |
|---|---|
| Feature | The Notifications tab: title, empty state, rows (description, chevron, order), types from job changes, opening a job, read / unread and the tab's count, a job that can no longer be opened, the push banner, a long list |
| Source checklist | `qa/mobile/11-notifications/notifications-checklist.md` (CHK-NOTIF-001…031) |
| Devices / build | iPhone 17 · iOS 26.5 (simulator) · `[DEV] CT Mobile` 1.1.1 (178), `CLIENT_BUILD=true` · online |
| Owner | @mykola.zhuchenko · Last updated 2026-09-27 |

**Conventions**

- **Notifications come from the test's own jobs** (fixture `notif_job`). `POST /job` for the technician, status New, sends
  "New job assigned". A title changed through `PATCH /job` sends "Job updated". `statusType` `canceled` sends
  "Job cancelled". Deleting the job after the test deletes its notifications.
- **The technician has no other notifications.** If DEV holds some that no test made, TC-NOTIF-001 and TC-NOTIF-005 are
  `Blocked`: the empty state cannot be reached.
- **A row** (`notifications.row[<text>]`) is one element named `<M/d/yyyy>\n<h:mm a>\n<description>`. It is an `Other`
  when the job can be opened and an `Image` when it cannot (D-NOTIF-2). Rows are read from the page source by their rect.
  The chevron is an unnamed image at the row's right end (x ≈ 366).
- **Unread** = the red dot at the top right of the row's icon — pixels, `#EB0101` (recon 12: 6.8 % of the dot's box when
  unread, 0 % when read). The tab's count is part of its label: `'3\nNotifications\nTab 2 of 3'`.
- **The server copy** = `GET /notification?userId=<technician>` (`api.notifications`): title, body, status
  (`new` / `viewed`), createdAt.
- **The push permission** is switched in the Settings app: Apps → [DEV] CT Mobile → Notifications → Allow Notifications.
  It is always switched back on after the test.

---

## TC-NOTIF-001 — The Notifications tab: "Notification list", the tab selected, the empty state

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTIF-001, -002, -003, -026, -027 |
| Priority | P0 · smoke |
| Preconditions | signed in; no notification for the technician |
| Oracle | spec — SRS §3.1.4 (title, empty state texts) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.notifications | — | notifications.root "Notification list" |
| 2 | expect-selected | tabbar.notifications | — | the tab selected |
| 3 | expect-text | notifications.empty-title | — | No notifications yet |
| 4 | expect-text | notifications.empty-text | — | You'll see updates about your jobs here. |

## TC-NOTIF-002 — Rows from job changes: the server's description, the chevron only for a job that can be opened, newest first, the tab's count; "Job cancelled" arrives read

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTIF-011, -012, -013, -015, -016 |
| Priority | P0 |
| Preconditions | jobs `A` and `B` New (two "New job assigned"); then `A`'s title changed and `B` cancelled through the API |
| Oracle | spec — FR-NOT-01, -02, SRS §3.1.4 (types, texts); the server copy; D-NOTIF-1 (no title), D-NOTIF-3 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.notifications | then swipe notifications.root down (refresh) | — |
| 2 | expect-text | notifications.row | — | 4 rows, top to bottom: `B` "… was removed from your list", `A` "… was updated by Project Facilitator", `B` "… was assigned to you", `A` "… was assigned to you" — each description as its `body` on the server, same order as `createdAt` |
| 3 | expect-text | notifications.row | — | each starts with today's date and a time |
| 4 | expect-visible | notifications.chevron | — | on the two rows of `A`; none on the rows of `B` (cancelled) |
| 5 | expect-text | tabbar.notifications | — | count 3 ("Job cancelled" arrives read) |

## TC-NOTIF-003 — Opening an unread notification: the job's details; back on the list the row is read, the count goes down, the server marks it viewed

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTIF-019, -020, -022, -023, -024, -025 |
| Priority | P0 |
| Preconditions | job `C` New ("New job assigned", unread) |
| Oracle | spec — FR-NOT-03, -06, -07; the server copy (`status`) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.notifications | then refresh | the row of `C` unread (red dot); tab count 1 |
| 2 | click | notifications.row[C] | — | job-details.header `<C jobId> - <C title>` |
| 3 | click | job-details.back | — | notifications.root; tabbar.notifications visible |
| 4 | expect-visible | notifications.row[C] | — | read (no red dot); no tab count |
| 5 | expect-text | api.notifications | — | `C`'s notification `viewed` |

## TC-NOTIF-004 — A notification of a job that can no longer be opened: no chevron, the tap stays on the list and shows nothing, the row turns read

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTIF-021 |
| Priority | P2 |
| Preconditions | job `D` New, then cancelled through the API |
| Oracle | D-NOTIF-2 (accepted baseline: no message, no navigation); FR-NOT-03 (a cancelled job cannot be opened) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.notifications | then refresh | the "assigned" row of `D` unread, without a chevron |
| 2 | click | notifications.row[D assigned] | — | notifications.root stays for 3 s; no job-details.header |
| 3 | expect-visible | notifications.row[D assigned] | — | read; the server `viewed` |

## TC-NOTIF-005 — Push not allowed: the banner with its texts, together with the empty state; Go to Settings opens Settings; allowed again: no banner

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTIF-005, -006, -007, -008, -009, -028 |
| Priority | P2 |
| Preconditions | no notification for the technician; push allowed |
| Oracle | spec — FR-NOT-04, -05, SRS §3.1.4 (banner texts); D-NOTIF-4 (Settings opens; the exact page is checked by hand on a device) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | set | settings.allow-notifications | off (the Settings app) | — |
| 2 | click | tabbar.notifications | then refresh | notifications.banner: "Turn on push notifications", "Turn on push notifications to get alerts for job updates.", "Go to Settings" |
| 3 | expect-visible | notifications.empty-title | — | below the banner, not overlapping it |
| 4 | click | notifications.go-to-settings | — | the Settings app in front |
| 5 | set | settings.allow-notifications | on | — |
| 6 | click | tabbar.notifications | back in the app, refresh | no notifications.banner |

## TC-NOTIF-006 — A long list scrolls; a long job name wraps inside the screen; rows do not overlap

| Field | Value |
|---|---|
| Source CHK IDs | CHK-NOTIF-004, -014, -031 |
| Priority | P3 |
| Preconditions | 10 jobs New, the newest with a 90-character title |
| Oracle | spec — SRS §3.1.4 (scrollable list); D-NOTIF-5 (long names wrap); CHK-NOTIF-014 on this device only |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.notifications | then refresh | the long row first, its whole description in its name |
| 2 | expect-visible | notifications.row | — | every row inside the screen width; no two rows overlap; the long row taller than a short one |
| 3 | swipe | notifications.root | up until the oldest row | the oldest job's row shown (the list scrolls) |

## Aliases used

| Alias | ios map |
|---|---|
| tabbar.notifications | yes (recon 4) |
| notifications.root, .empty-title, .empty-text, .row, .chevron, .banner, .go-to-settings | `screens/notifications_map.py` (recon 12) |
| job-details.header, .back | yes |
| settings.allow-notifications | `screens/settings_map.py` — the system Settings app (recon 12) |
| api.notifications | not an element — `GET /notification?userId=` (admin, read-only) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-NOTIF-001…-003, -026, -027 | TC-NOTIF-001 | |
| CHK-NOTIF-011…-013, -015, -016 | TC-NOTIF-002 | -011: the type is in the description, no title (D-NOTIF-1) |
| CHK-NOTIF-019, -020, -022…-025 | TC-NOTIF-003 | -022: the red dot by pixels (Q-NOTIF-4) |
| CHK-NOTIF-021 | TC-NOTIF-004 | D-NOTIF-2 |
| CHK-NOTIF-005…-009, -028 | TC-NOTIF-005 | -008: Settings opens (D-NOTIF-4) |
| CHK-NOTIF-004, -014, -031 | TC-NOTIF-006 | -014 on this device only |

**Not here:**
- CHK-NOTIF-010 (the icon by type) — skipped with a comment: not in the tree, seen on the screenshot (Q-NOTIF-4).
- CHK-NOTIF-017, -018 ("Job starts today") — skipped with a comment: a server schedule at 8 AM (Q-NOTIF-1).
- CHK-NOTIF-029, -030 — offline, Android stage (Q-NOTIF-2).
