# Notifications — Android offline test cases (step 5)

> Scope/selection: the two `android-stage` checks of this module (owner, android-plan §2.5; `qa/mobile/ios/not-automated.md`) — CHK-NOTIF-029 and CHK-NOTIF-030 (identical text: cached notifications offline, with an offline indicator/message if implemented). Merged into one TC: same flow, same oracle. Source recon: [qa/shared/recon-2026-10-01-android-offline.md](../../../shared/recon-2026-10-01-android-offline.md) (recon A2). Format: [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md) · prompt `prompts/mobile/03`. Conventions, the `notif_job` fixture and the server-copy check (`api.notifications`): same as `../notifications-test-cases.md`. Android texts/behaviour differences: [../android/notifications-questions.md](notifications-questions.md) (D-NOTIF-A1…A4 — none of them affect this TC).
>
> **Status: draft — waiting for the owner's validation (step 5 gate).**

---

## TC-NOTIF-007 — Offline: no cached rows, only the offline message and "Try again"; back online, "Try again" shows the list

| Field | Value |
|---|---|
| ID | TC-NOTIF-007 |
| Title | Offline: no cached rows, only the offline message and "Try again"; back online, "Try again" shows the list |
| Source CHK IDs | CHK-NOTIF-029, CHK-NOTIF-030 |
| Platforms | android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, foreground; signed in |
| Permissions | notifications: granted |
| Network | online Wi-Fi → offline (adb) → online |
| Preconditions | signed in as `{{tech}}`; one job created for the technician through the API (`notif_job` fixture, as `../notifications-test-cases.md`) so a "New job assigned" notification exists online before going offline |
| Oracle | spec — checklist CHK-NOTIF-029, CHK-NOTIF-030 ("shows cached notifications if available and displays an appropriate offline indicator/message if implemented"); spec — SRS §3.1.4 FR-NOT-08 ("If notifications fail to load, display a retry option"); spec — SRS §3.3.1 (global "No Internet connection" message); D-OFF-4 (owner-pending, recon A2); observed (discovery, not proof) — recon A2 row 14, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.notifications | then refresh | the list shows `notif_job`'s row online — at least 1 row |
| 2 | open | device.network | off | Wi-Fi and mobile data disabled |
| 3 | click | tabbar.notifications | then refresh | the screen reloads while offline |
| 4 | expect-hidden | notifications.row | — | hidden — no cached rows shown, even though one existed online (D-OFF-4: there is no cache) |
| 5 | expect-visible | notifications.offline-title | — | "No internet connection" (after the initial "Slow or no internet connection…", recon A2 row 1/14) |
| 6 | expect-visible | notifications.offline-text | — | the supporting offline message visible |
| 7 | expect-visible | notifications.try-again | — | "Try again" visible and tappable |
| 8 | open | device.network | on | Wi-Fi and mobile data enabled |
| 9 | click | notifications.try-again | — | retry requested |
| 10 | expect-visible | notifications.row | — | the list reappears — at least `notif_job`'s row |

**Postconditions / cleanup:** delete `notif_job` through the API (as `../notifications-test-cases.md` TC-NOTIF-002…004); network restored to on.
**Notes:** recon A2 row 14 observed "No internet connection" / the initial "Slow or no internet connection. Check the Internet settings and try again." / "Try again" in place of the list — the technician had 5 notifications online at the time and none of them appeared offline, confirming "no cache". This TC uses a single fixture notification (`notif_job`) instead, to keep the data owned by the test (doctrine: every test owns its data) while proving the same absence of a cache.
**Pending owner: D-OFF-4** — recon A2: "Сповіщення не кешуються: офлайн — повідомлення й «Try again»" (notifications are not cached; offline shows the message and "Try again"). Proposal: "Прийняти: «cached … if available» — кешу немає, повідомлення є; тест — повідомлення + «Try again» після повернення мережі показує список" (accept: "cached … if available" reads as "there is no cache, so only the message is shown"; the test checks the message + that "Try again" shows the list once back online — exactly as written above).

---

## Aliases used

| Alias | Screen | android map | ios map |
|---|---|---|---|
| device.network | — (device control) | n/a — harness capability; `Adb.offline()` exists (`helpers/android/device.py`) | n/a |
| tabbar.notifications, notifications.row | notifications (shared tab bar) | yes (step 7) | yes |
| notifications.offline-title, .offline-text, .try-again | notifications (new from recon A2) | **MISSING** | **MISSING** |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech}} | `automation/mobile/.env` → `APP_USER_EMAIL` etc. | existing test technician, read-only |
| `notif_job` | `automation/mobile/fixtures/test_data.py` (as `../notifications-test-cases.md`) | `POST /job` for the technician → "New job assigned"; deleted in `finally`, deletes its notification with it |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-NOTIF-029, CHK-NOTIF-030 | TC-NOTIF-007 | identical checklist text, one TC (same flow, same oracle); Pending owner: D-OFF-4 |

## Open questions

- Pending owner: **D-OFF-4** (CHK-NOTIF-029/030) — see the TC's "Pending owner" note; awaiting the owner's validation of the proposed reading of "cached … if available" (step 5 gate).
- `notifications.offline-title` / `.offline-text` / `.try-again` are new aliases (recon A2's "Нові елементи для карт" list) — testability work order, not a behavioural question.
