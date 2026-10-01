# Profile — Android offline test cases (step 5)

> Scope/selection: the one `android-stage` check of this module (owner, android-plan §2.5; `qa/mobile/ios/not-automated.md`) — CHK-PRF-030, log out offline. Source recon: [qa/shared/recon-2026-10-01-android-offline.md](../../../shared/recon-2026-10-01-android-offline.md) (recon A2). Format: [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md) · prompt `prompts/mobile/03`. Conventions, `logout-dialog.*` and the post-logout re-sign-in convention (Q-PRF-3): same as `../profile-test-cases.md`. No Android questions file exists yet for this module (`qa/mobile/12-profile/android/` has no `profile-questions.md`); any Android-specific D/Q raised here belongs there once filed.
>
> **Status: draft — waiting for the owner's validation (step 5 gate).**

---

## TC-PRF-009 — Log out offline: the dialog clears the session (Welcome); a cold start while still offline stays on Welcome — the session is actually cleared, not just hidden

| Field | Value |
|---|---|
| ID | TC-PRF-009 |
| Title | Log out offline: the dialog clears the session (Welcome); a cold start while still offline stays on Welcome — the session is actually cleared, not just hidden |
| Source CHK IDs | CHK-PRF-030 |
| Platforms | android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | foreground, signed in → offline → terminate + cold start (still offline) |
| Permissions | notifications: granted |
| Network | online Wi-Fi → offline (adb) for the rest of the TC; restored to online in Postconditions |
| Preconditions | signed in as `{{tech.email}}` (session created by the `ui_login` fixture); Profile screen open |
| Oracle | spec — SRS §3.1.5 FR-PROF-07 ("Confirming logout shall: Clear user session; Return the user to the Welcome screen"); spec — checklist CHK-PRF-030; D-OFF-6 (owner-pending, recon A2); observed (discovery, not proof) — recon A2 row 15, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | Wi-Fi and mobile data disabled |
| 2 | click | profile.logout | — | logout-dialog: "Log out", "Are you sure you want to log out?", Cancel, Log out — shown offline same as online |
| 3 | click | logout-dialog.confirm | — | welcome.root |
| 4 | expect-visible | welcome.root | — | visible — signed out while offline (FR-PROF-07) |
| 5 | open | app | terminate, then cold start (still offline) | — |
| 6 | expect-visible | welcome.root | — | visible — stays signed out after a cold start while still offline, proving the session was actually cleared, not just hidden |
| 7 | expect-hidden | jobs-list.root | — | hidden — no cached Jobs list reachable without a session |

**Postconditions / cleanup:** network restored to on (also guaranteed by the harness's `finally`, `Adb.offline()`); sign in again for the next test (`ui_login`), as the other logout TCs do (Q-PRF-3 convention, `../profile-test-cases.md`).
**Notes:** recon A2 row 15: in code, logout offline clears tokens, the user and the jobs/details cache; notes, photos, the sync queue and survey drafts are left on the device. This TC asserts only the session side (what CHK-PRF-030 and FR-PROF-07 ask for); it does not probe local notes/photos/drafts.
**Pending owner: D-OFF-6** — recon A2: "Вихід офлайн чистить сесію й кеш джоб; локальні нотатки / фото / чернетки лишаються на пристрої" (logout offline clears the session and jobs cache; local notes/photos/drafts remain on the device). Proposal: "Тест — сесія очищена (Welcome, після перезапуску теж). Чи мають зникати несинхронізовані нотатки / фото — твоє рішення" (the test checks the session is cleared — Welcome, and still Welcome after a restart — exactly as written above; whether unsynced local notes/photos must also be purged is the owner's decision, not asserted here).

---

## Aliases used

| Alias | Screen | android map | ios map |
|---|---|---|---|
| device.network | — (device control) | n/a — harness capability; `Adb.offline()` exists (`helpers/android/device.py`) | n/a |
| app | — (launch / relaunch) | n/a | n/a (`helpers/app.py`) |
| profile.logout, logout-dialog.confirm | profile, logout-dialog | yes (step 7) | yes |
| welcome.root, jobs-list.root | welcome, jobs-list | yes (step 7) | yes |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech.email}} | `automation/mobile/.env` → `APP_USER_EMAIL` | existing test technician, read-only; session via `ui_login` |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-PRF-030 | TC-PRF-009 | Pending owner: D-OFF-6 — session side only; local-data scope is the owner's call |

## Open questions

- Pending owner: **D-OFF-6** (CHK-PRF-030) — see the TC's "Pending owner" note; whether unsynced local notes/photos/drafts must be purged on an offline logout is undecided and not asserted by this TC either way.
- No `qa/mobile/12-profile/android/profile-questions.md` exists yet — if the owner's answer to D-OFF-6 introduces an Android-specific decision beyond the shared `../profile-questions.md`, it belongs in a new file there.
