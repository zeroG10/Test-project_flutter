# Automation plan — Notifications (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/11-notifications/notifications-checklist.md`
> (31 items, `CHK-NOTIF-001…031`, imported 2026-09-26). Date: 2026-09-26. Owner: mykola.zhuchenko.
> **Status: draft — recon 12 and the owner's word on [notifications-questions.md](notifications-questions.md) pending.**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| Feature code | `NOTIF` |
| Scope decision (proposed) | the Notifications tab: title, empty state, the list (content, order, chevron), opening a job, read / unread and the tab's count, the push banner and "Go to Settings"; "Job starts today" (a server schedule at 8 AM) and offline are not automated |
| Oracle model | accepted production baseline; SRS §3.1.4 (FR-NOT-01…09), §3.3.2; the technician's notifications on the server (`GET /notification?userId=` — admin, read-only) |
| App code read | `notifications_page.dart`, `notification_item_widget.dart`, `push_banner_widget.dart`, `notifications_bloc.dart`, `notifications_repository_impl.dart`, `notifications_api_service.dart`, `app_shell.dart` (the tab badge), `job_details_page.dart` (read only, `development` @ 85a84f3) |

**How the app shows notifications (code):**
- It loads `GET /notification?page=1&pageSize=100` and sorts by `createdAt`, newest first. It reloads on refresh and when
  the app comes back to the foreground.
- A row shows:
  - the date | time;
  - the **description** (`body`) — **not the title** (D-NOTIF-1);
  - an icon by type: New job assigned, Job starts today, Job updated, Job cancelled; any other title counts as Job updated;
  - a red dot while unread;
  - a chevron **only when the job can be opened** (its status is New, In progress or Submitted).
- Tapping marks the notification read (`PATCH /notification/{id}/viewed`) and opens the job's details when the job can
  be opened; otherwise nothing happens (D-NOTIF-2).
- The tab shows a badge with the number of unread notifications.
- The push banner: "Turn on push notifications" / "Turn on push notifications to get alerts for job updates." /
  "Go to Settings". It shows when the system notification permission is not granted.
- The empty state: "No notifications yet" / "You'll see updates about your jobs here."
- A failed load: the "no internet" view with Retry.

**Test data (seen on DEV, 2026-09-26):** `POST /job` with the technician creates "New job assigned" with the body
"<title> <jobId> was assigned to you"; deleting the job deletes its notification. The technician has no other
notifications, so the empty state can be reached.

## Step 3–4 — Candidate matrix (31 items)

| CHK ID | Scenario (short) | Level | Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|
| CHK-NOTIF-001…003 | opens from the tab; "Notification list"; the tab selected | E2E UI | Good Candidate | P0 | TC-NOTIF-001 | |
| CHK-NOTIF-026, -027 | empty state and its texts | E2E UI | Good Candidate | P1 | TC-NOTIF-001 | no notification for the technician (test jobs only) |
| CHK-NOTIF-010…-013, -016 | a row: icon by type, title, description with the job, chevron; as the server holds it | E2E UI + API | Good Candidate | P0 | TC-NOTIF-002 | icon by type / the red dot — only if the tree or pixels tell them (recon 12); title — D-NOTIF-1 |
| CHK-NOTIF-015 | newest first | E2E UI + API | Good Candidate | P1 | TC-NOTIF-002 | |
| CHK-NOTIF-004 | the list scrolls when long | E2E UI | Good Candidate | P2 | TC-NOTIF-002 | ~10 test jobs |
| CHK-NOTIF-019, -020 | a row opens the job's details; back → the list, tab bar there | E2E UI | Good Candidate | P0 | TC-NOTIF-003 | |
| CHK-NOTIF-022…-025 | unread distinguishable; read after opening; still read on return; the tab's count goes down | E2E UI + API | Good Candidate | P1 | TC-NOTIF-003 | the tab's count is in its label; the dot — recon 12 |
| CHK-NOTIF-021 | a job no longer available | E2E UI + API | After recon | P2 | TC-NOTIF-004 | D-NOTIF-2: no message, no navigation, no chevron; which API change makes it (cancel) — recon 12 |
| CHK-NOTIF-005…-009, -028 | push banner (texts, Go to Settings → the app's settings), hidden when allowed, with the empty state | E2E UI | After recon | P2 | TC-NOTIF-005 | the system permission is switched in the Settings app (recon 12) |
| CHK-NOTIF-011 (Job updated / Job cancelled) | the other types | E2E UI + API | After recon | P2 | TC-NOTIF-002 | which API change sends them — recon 12 |
| CHK-NOTIF-017, -018 | "Job starts today" only on the job's day, at 8 AM | Manual / server | Not Recommended | P3 | — | a server schedule; cannot be triggered (Q-NOTIF-1) |
| CHK-NOTIF-014, -031 | readable on small screens; long names wrap without breaking the layout | E2E UI | After recon | P3 | TC-NOTIF-002 | a long title: the row stays inside the screen; small screens → tablet / Android stage |
| CHK-NOTIF-029, -030 | offline | Manual (Android stage) | Needs Device | P2 | — | as modules 08–10 |

## Step 5b — Selected (draft)

**Certain: 16 of 31 → 3 TCs.** Up to 11 more after recon 12: CHK-NOTIF-005…009, -011 (types), -014, -021, -028, -031.

| TC | Covers |
|---|---|
| TC-NOTIF-001 | the tab → "Notification list", tab selected; no notification → the empty state |
| TC-NOTIF-002 | test jobs → rows: description with the job, chevron, newest first, as on the server; the list scrolls |
| TC-NOTIF-003 | unread → tap → the job's details → back: read, the tab's count down by one |
| TC-NOTIF-004 *(after recon)* | a notification of a job that can no longer be opened: no chevron, the tap stays on the list |
| TC-NOTIF-005 *(after recon)* | push not allowed → the banner and its texts → Go to Settings → the app's settings; allowed → no banner |

**The rest:** "Job starts today" (2) — a server schedule; offline (2) — Android stage.

## Step 9 — Test data

One or more jobs per test through `POST /job` for the technician (each one sends "New job assigned"), deleted after the
test — their notifications go with them (seen on DEV). Other types: changes made through `PATCH /job` on the test's own
job, if recon 12 shows they send notifications.

## Step 16 — Recommendation

Recon 12 → the owner's word on the questions → test cases → harness.
