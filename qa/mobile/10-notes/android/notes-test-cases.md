# Notes — Android offline test cases (step 5)

> Scope/selection: owner, android-plan §2.5 — automate all 36 `android-stage` checks
> (`qa/mobile/ios/not-automated.md`). This file covers the Notes screen's offline group:
> CHK-NOTE-043…-047. Format: [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md)
> + the mobile rows from [test-cases-mobile.md](../../../_templates/test-cases-mobile.md) · prompt
> `prompts/mobile/03`. IDs continue the file's numbering from `../notes-test-cases.md` (last:
> TC-NOTE-007; TC-NOTE-008 / -009 were removed there, 2026-09-26 — this file reuses TC-NOTE-008).
>
> **Status: validated by the owner 2026-10-01 (step 5 gate: D-OFF-1…9 answered, no remarks on the TCs).**

| Field | Value |
|---|---|
| Feature | The Notes of an In progress job without network: create / edit / delete offline, an unsynced delete never reaching the server, persistence after a cold start, automatic sync when connectivity returns, and the server state after submission for a synced note deleted offline (D-OFF-3, as BUG-PHR-001) |
| Source checklist | `qa/mobile/10-notes/notes-checklist.md` — CHK-NOTE-043, -044, -045, -046, -047 |
| Platform | android |
| Devices / build | Pixel 7 · Android 16 (API 36), emulator `Pixel_7_API_36` (`-dns-server 8.8.8.8,1.1.1.1`) · Appium 3.4.2 + UiAutomator2 · `[DEV] CT Mobile` 1.1.1 (178) debug, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko · Last updated 2026-10-01 |

**Conventions**

- **One job per test**, created through `POST /job` directly In progress (fixture `{{job.progress}}`,
  Short Survey) while the device is still online; deleted after the test.
- **Network is a step**: `open | device.network | off` / `on` (`Adb.offline()`,
  `helpers/android/device.py`). A TC that ends offline by design still leaves the network **ON**
  afterwards — `Adb.offline()` restores it in `finally`, no extra step needed. A TC that proves
  "network back" makes the `on` step part of the scenario.
- **The offline banner covers the top content strip** (`offline-banner.*`, D-OFF-7, recon row 16)
  — it sits over the first note row's ⋮. Before the first `notes.menu[…]` tap while offline, a TC
  closes it: `click | offline-banner.close`.
- **A note row** joins its date, text and ⋮ in one label (TD-NOTE-001); `notes.row[<text>]` and
  `notes.menu[<text>]` address a row by its text, as module 07's TC-DLV-005 already does for this
  screen (`notes.menu[QA-AUTO note A]`) — clearer than a position index once ordering is in
  question offline.
- **The server copy** = `GET /job/{id}` (`JobController_findOne`) → `notes` (`api.jobNotes`, same
  alias as the online file) / the whole job (`api.job`, same alias as module 07). Recon row 12
  observed sync landing within about 15 s; the TCs below allow a generous 15–20 s wait.
- **Submission on DEV answers 500 although the server records it** (Q-DLV-5,
  `qa/mobile/07-submit-deliverables/submit-deliverables-questions.md`): `POST /job/{id}/submit`
  returns 500, the app keeps the job In progress, a second open shows it Submitted. TC-NOTE-010
  checks the server record the same way the existing 07 TCs do, not the app's success message.

---

## TC-NOTE-008 — Offline: create a note, edit it, then delete a second note at once — kept after a cold start, still offline

| Field | Value |
|---|---|
| ID | TC-NOTE-008 |
| Title | Offline: create a note, edit it, then delete a second note at once — kept after a cold start, still offline |
| Source CHK IDs | CHK-NOTE-043, CHK-NOTE-046, CHK-NOTE-044 |
| Platforms | android |
| Priority | P0 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start, then cold start at step 9 (terminate + relaunch, still offline) |
| Permissions | n/a |
| Network | offline (Wi-Fi + mobile data off) |
| Preconditions | `{{job.progress}}` In progress, details open, device online |
| Oracle | spec — SRS §3.1.3.4.5 FR-NOT-09 "Notes creation, editing, and deletion shall be fully supported offline."; CHK-NOTE-043, CHK-NOTE-046, CHK-NOTE-044; recon row 10 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network off |
| 2 | click | job-details.deliverable[Notes] | — | opens offline; offline-banner.message visible ("No internet connection.") |
| 3 | click | notes.add-note | `QA-AUTO offline keep`, Save | notes.toast "Note added successfully" — create works offline |
| 4 | click | notes.menu[QA-AUTO offline keep] | then note-menu.edit, append ` edited`, Save | notes.toast "Note saved successfully" — edit works offline |
| 5 | click | notes.add-note | `QA-AUTO offline throwaway`, Save | — a second note, to be deleted unsynced |
| 6 | click | offline-banner.close | — | banner closed — the ⋮ is reachable (D-OFF-7) |
| 7 | click | notes.menu[QA-AUTO offline throwaway] | then note-menu.delete, note-delete-dialog.delete | notes.toast "Note deleted successfully" — delete works offline |
| 8 | expect-hidden | notes.row[QA-AUTO offline throwaway] | — | removed from local storage at once, still offline (CHK-NOTE-046) |
| 9 | open | app | terminate + launch → the job → Notes | still offline (cold start) |
| 10 | expect-text | notes.row[1] | — | `QA-AUTO offline keep edited` kept after the cold start, still offline (CHK-NOTE-044) |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness (`Adb.offline()` `finally`). Job deleted.
**Notes:** CHK-NOTE-046's "never reaches the server" half is closed in TC-NOTE-009 step 3, once the device is back online.
**Resolved D-OFF-7** — Owner 2026-10-01: a UI remark, not a bug — tests close the banner (✕) before taps in the covered strip.

## TC-NOTE-009 — Network back: notes created and edited offline are synced to the server; the note deleted while unsynced never reaches it

| Field | Value |
|---|---|
| ID | TC-NOTE-009 |
| Title | Network back: notes created and edited offline are synced to the server; the note deleted while unsynced never reaches it |
| Source CHK IDs | CHK-NOTE-045 |
| Platforms | android |
| Priority | P0 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start |
| Permissions | n/a |
| Network | offline → online (toggled in this TC) |
| Preconditions | as TC-NOTE-008 — `{{job.progress}}`, offline; `QA-AUTO offline keep edited` kept; `QA-AUTO offline throwaway` deleted unsynced |
| Oracle | spec — SRS §3.1.3.4.5 FR-NOT-10 "Offline note changes shall sync automatically when connectivity is restored."; CHK-NOTE-045; recon row 12 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | on | network restored; the app's "Connection restored" dialog for the unfinished In progress job comes within ~15 s and is closed with `connection-restored.cancel` (recon A2 row 12; the dialog itself is TC-DLV-009) |
| 2 | expect-hidden | offline-banner.message | within ~5 s | the banner clears once connectivity returns |
| 3 | expect-text | api.jobNotes | — | within ~15–20 s (generous wait; recon row 12): exactly 1 note, text `QA-AUTO offline keep edited`; no `QA-AUTO offline throwaway` — the unsynced delete never reached the server (CHK-NOTE-046) |

**Postconditions / cleanup:** network ON. Job deleted.

## TC-NOTE-010 — A synced note deleted offline: network back → submit deliverables → the server has no such note (D-OFF-3)

| Field | Value |
|---|---|
| ID | TC-NOTE-010 |
| Title | A synced note deleted offline: network back → submit deliverables → the server has no such note (D-OFF-3) |
| Source CHK IDs | CHK-NOTE-047 |
| Platforms | android |
| Priority | P1 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start |
| Permissions | n/a |
| Network | online → offline → online (toggled in this TC) |
| Preconditions | `{{job.progress}}` In progress, Short Survey already completed (setup, as module 07's TC-DLV-003), details open, device online; a note `QA-AUTO synced then deleted` already added and present on the server (`GET /job/{id}` → `notes`) — setup, not a step here |
| Oracle | spec — SRS §3.1.3.4.5 FR-NOT-10 "Offline note changes shall sync automatically when connectivity is restored." (the "queued delete" reading); CHK-NOTE-047; accepted baseline — D-OFF-3 (as BUG-PHR-001: the final server state is checked after submission, not during In progress; recon 10 found the same mechanism for notes — a draft `BUG-NOTE-001` not filed, owner 2026-09-26); recon row 13 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network off |
| 2 | click | job-details.deliverable[Notes] | — | opens offline |
| 3 | click | offline-banner.close | — | banner closed — the ⋮ is reachable (D-OFF-7) |
| 4 | click | notes.menu[QA-AUTO synced then deleted] | then note-menu.delete, note-delete-dialog.delete | notes.row[QA-AUTO synced then deleted] gone — removed locally; the deletion is not sent while offline |
| 5 | click | notes.back | — | job-details |
| 6 | open | device.network | on | network restored; the app's "Connection restored" dialog for the unfinished In progress job comes within ~15 s and is closed with `connection-restored.cancel` (recon A2 row 12; the dialog itself is TC-DLV-009) |
| 7 | click | job-details.submit-deliverables | then submit-dialog.submit | submission sent (DEV answers 500 — Q-DLV-5; the server record is checked regardless, as the existing 07 TCs do) |
| 8 | expect-text | api.job | — | within ~15–20 s: `submitted`; `notes` has no `QA-AUTO synced then deleted` — the deletion is applied with the job update at submission, not as its own queued sync (D-OFF-3, as BUG-PHR-001) |

**Postconditions / cleanup:** network ON. Job deleted.
**Notes:** this is the same server-state check module 07 already performs after submission (TC-DLV-005); this TC adds the offline-delete trigger. Mirrors photo report's TC-PHR-010 — same mechanism, same owner decision (D-OFF-3).
**Resolved D-OFF-3** — Owner 2026-10-01: «перевір» — the server state is checked after the submission (as BUG-PHR-001).

---

## Aliases used

| Alias | android map |
|---|---|
| job-details.deliverable, .submit-deliverables | yes (module 06 / 07) |
| submit-dialog.submit | yes (module 07, `screens/submit_dialog_map.py`) |
| notes.header, .add-note, .row, .menu, .back, .toast | yes — `screens/notes_map.py` (recon 10 / A1) |
| note-menu.edit, .delete · note-editor.field, .save · note-delete-dialog.delete | yes — `screens/notes_map.py` |
| offline-banner.message | MISSING — new (recon row 1, 2026-10-01) |
| offline-banner.try-again | MISSING — new (recon row 1, 2026-10-01); not used by a step in this file |
| offline-banner.close | MISSING — new (recon row 16 / D-OFF-7, 2026-10-01) |
| api.jobNotes | not an element — `GET /job/{id}` (`JobController_findOne`) → `notes` |
| api.job | not an element — `GET /job/{id}` (`JobController_findOne`), same alias as module 07 |
| device.network | not a screen element — `Adb.offline()` / network back-on, `helpers/android/device.py` |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{job.progress}} | `automation/mobile/fixtures/test_data.py` | In progress job, same fixture as the online file |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-NOTE-043, -046, -044 | TC-NOTE-008 (+ -009 for -046's server half) | |
| CHK-NOTE-045 | TC-NOTE-009 | |
| CHK-NOTE-047 | TC-NOTE-010 | D-OFF-3, pending owner |

## Open questions

- D-OFF-3 (CHK-NOTE-047) — pending the owner's confirmation that the server state is checked
  after submission, not as an independently queued delete sync (see TC-NOTE-010); the same
  question is open for CHK-PHR-050 (`../../09-photo-report/android/photo-report-test-cases.md`)
  and the draft `BUG-NOTE-001` (not filed).
- D-OFF-7 (banner over the first row's ⋮) — pending the owner's call: UX note or bug (see
  TC-NOTE-008 / -010).

> **Reviewer note (Opus, 2026-10-01):** every "network on" step on an In progress job now also closes the "Connection restored" dialog (`connection-restored.cancel` — MISSING in maps, added with the 07 aliases); it lies over the screen otherwise. Step numbers unchanged.
