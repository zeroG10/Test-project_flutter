# Survey — Android offline test cases (step 5)

> Scope/selection: owner, android-plan §2.5 — automate all 36 `android-stage` checks
> (`qa/mobile/ios/not-automated.md`). This file covers the Survey screen's offline group:
> CHK-SRV-023…-027. Format: [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md)
> + the mobile rows from [test-cases-mobile.md](../../../_templates/test-cases-mobile.md) · prompt
> `prompts/mobile/03`. IDs continue the file's numbering from `../survey-test-cases.md` (last:
> TC-SRV-016).
>
> **Status: validated by the owner 2026-10-01 (step 5 gate: D-OFF-1…9 answered, no remarks on the TCs).**

| Field | Value |
|---|---|
| Feature | The Survey of an In progress job without network: fully functional offline (answer, change an answer, Save), a photo question kept offline and after a cold start, sync of answers and photo when connectivity returns |
| Source checklist | `qa/mobile/08-survey/survey-checklist.md` — CHK-SRV-023, -024, -025, -026, -027 |
| Platform | android |
| Devices / build | Pixel 7 · Android 16 (API 36), emulator `Pixel_7_API_36` (`-dns-server 8.8.8.8,1.1.1.1`) · Appium 3.4.2 + UiAutomator2 · `[DEV] CT Mobile` 1.1.1 (178) debug, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko · Last updated 2026-10-01 |

**Conventions**

- **One job per test**, created through `POST /job` directly In progress with the survey kind
  named in Preconditions (`{{job.short}}`, `{{job.mo3}}`, `{{job.photo}}` — same fixtures as
  `../survey-test-cases.md`), while the device is still online; deleted after the test.
- **Network is a step**: `open | device.network | off` / `on` — the harness toggles Wi‑Fi and
  mobile data together (`Adb.offline()`, `helpers/android/device.py`). A TC that ends offline by
  design still leaves the network **ON** afterwards: `Adb.offline()` restores it in `finally`,
  with no extra step needed in the TC body. A TC that proves "network back" makes the `on` step
  part of the scenario itself.
- **The offline banner** (`offline-banner.message` / `.try-again` / `.close`, recon row 1) is not
  yet in any screen map — `MISSING` below. It is not reached by a tap in this file (the survey's
  interactive elements sit lower on the form than the strip it covers, recon row 16), so no TC
  needs to close it first; `offline-banner.close` is still an alias to build (see `09`/`10` for
  where closing it is load-bearing).
- **Fields have no names** (TD-SRV-001), same conventions as the online file: `survey.yes[n]` /
  `survey.no[n]` / `survey.text[n]` / `survey.upload-photo[n]` address the n-th field of that kind
  in form order. The photo flow after `survey.upload-photo[n]`:
  `photo-picker.grid` (cell k) → `photo-editor.done` → `photo-metadata.description` →
  `photo-metadata.save`.
- **The server copy** = `GET /job/{id}` (`JobController_findOne`) → `surveyResponse`
  (`api.surveyResponse`, same alias as the online file), read after the device is back online.
  Recon row 12 observed the sync landing within about 15 s; the TCs below allow a generous
  15–20 s wait rather than a fixed sleep.

---

## TC-SRV-017 — Offline: the survey is reachable and fully functional — answer, change the answer, and Save all work with no network

| Field | Value |
|---|---|
| ID | TC-SRV-017 |
| Title | Offline: the survey is reachable and fully functional — answer, change the answer, and Save all work with no network |
| Source CHK IDs | CHK-SRV-024, CHK-SRV-025 |
| Platforms | android |
| Priority | P0 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start (job already open from an earlier online session) |
| Permissions | n/a — no permission involved |
| Network | offline (Wi-Fi + mobile data off) |
| Preconditions | `{{job.short}}` In progress (Short Survey), details open, device online |
| Oracle | spec — SRS §3.1.3.4.2 FR-SUR-12 "The survey shall be fully functional offline."; CHK-SRV-024, CHK-SRV-025; recon row 9 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network off |
| 2 | click | job-details.deliverable[Survey] | — | survey opens offline; offline-banner.message visible ("No internet connection.") |
| 3 | expect-visible | survey.header | — | visible — the form is reachable with no network |
| 4 | click | survey.yes[1] | Good? | Yes selected |
| 5 | fill | survey.text[1] | Text? — `QA-AUTO offline answer` | — |
| 6 | expect-enabled | survey.save | — | — |
| 7 | click | survey.no[1] | Good? (change the answer) | No selected, Yes not — the change is accepted offline |
| 8 | click | survey.save | — | "Survey saved" — accepted with no network error |
| 9 | expect-visible | job-details.header[{{job.short.titleLine}}] | — | back on the job; survey stored locally |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness (`Adb.offline()` `finally`) — nothing extra in the TC. Job deleted.
**Notes:** proves FR-SUR-12 end to end on one short survey; the Mo3 / photo surveys are exercised by TC-SRV-018/-019 and the online file.

## TC-SRV-018 — Offline: a photo attached to a survey photo question is kept, also after a cold start while still offline

| Field | Value |
|---|---|
| ID | TC-SRV-018 |
| Title | Offline: a photo attached to a survey photo question is kept, also after a cold start while still offline |
| Source CHK IDs | CHK-SRV-026, CHK-SRV-023 |
| Platforms | android |
| Priority | P1 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start, then cold start at step 5 (terminate + relaunch, still offline) |
| Permissions | n/a — the Android Photo Picker needs no runtime permission (recon D-PHR-A1) |
| Network | offline (Wi-Fi + mobile data off) |
| Preconditions | `{{job.photo}}` In progress (Photo Upload Test Survey), details open, device online; `gallery_photos` |
| Oracle | spec — SRS §3.1.3.4.2 FR-SUR-12 "fully functional offline" + FR-SUR-11-1 "automatically saved ... regardless of whether a manual Save action is performed"; CHK-SRV-026, CHK-SRV-023; recon row 9 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network off |
| 2 | click | job-details.deliverable[Survey] | — | survey opens offline |
| 3 | click | survey.upload-photo[1] | cell 0 (Site overview photos), `QA-AUTO offline photo` — then the photo flow (conventions) | survey.thumbnail[QA-AUTO offline photo] |
| 4 | expect-visible | survey.thumbnail[QA-AUTO offline photo] | — | stored locally while offline (CHK-SRV-026) |
| 5 | open | app | terminate + launch → the job → Survey | still offline (cold start) |
| 6 | expect-visible | survey.thumbnail[QA-AUTO offline photo] | — | kept after the cold start, still offline (CHK-SRV-023) |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness (`Adb.offline()` `finally`). Job deleted.
**Notes:** no Save is tapped — persistence across the cold start relies on the same auto-save path as the online file's TC-SRV-005, not on an explicit Save.

## TC-SRV-019 — Network back: the survey answers and the attached photo from TC-SRV-018 are synced to the server within about 15 s

| Field | Value |
|---|---|
| ID | TC-SRV-019 |
| Title | Network back: the survey answers and the attached photo from TC-SRV-018 are synced to the server within about 15 s |
| Source CHK IDs | CHK-SRV-027 |
| Platforms | android |
| Priority | P0 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start |
| Permissions | n/a — the Android Photo Picker needs no runtime permission (recon D-PHR-A1) |
| Network | offline → online (toggled in this TC) |
| Preconditions | as TC-SRV-018 (`{{job.photo}}`, offline, `QA-AUTO offline photo` in Site overview photos), plus every other required field of the survey answered offline — Equipment close-up photo, the Per-room photos entry's Room name text and Room photo, Additional comments text (same fill sequence as `../survey-test-cases.md` TC-SRV-014) — Save not yet tapped |
| Oracle | spec — SRS §3.1.3.4.2 FR-SUR-13 "Survey data and attached photos shall sync automatically when connectivity is restored."; CHK-SRV-027; recon row 12 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.save | — | "Survey saved" — accepted offline, queued for sync |
| 2 | open | device.network | on | network restored; the app's "Connection restored" dialog for the unfinished In progress job comes within ~15 s and is closed with `connection-restored.cancel` (recon A2 row 12; the dialog itself is TC-DLV-009) |
| 3 | expect-hidden | offline-banner.message | within ~5 s | the banner clears once connectivity returns |
| 4 | expect-text | api.surveyResponse | — | within ~15–20 s (generous wait; recon row 12): `jobId` = the job's; every required answer present; Site overview photos has 1 file, note `QA-AUTO offline photo` |

**Postconditions / cleanup:** network ON. Job deleted.
**Notes:** the wait is bounded (15–20 s), not a fixed sleep; recon observed the sync landing within about 15 s on this build.

---

## Aliases used

| Alias | android map |
|---|---|
| job-details.deliverable, .header | yes (module 06) |
| survey.header, .save, .yes, .no, .text, .upload-photo, .thumbnail | yes — `screens/survey_map.py` (recon 8 / A1) |
| photo-picker.grid · photo-editor.done · photo-metadata.description, .save | yes — `screens/survey_photo_map.py` |
| offline-banner.message | MISSING — new (recon row 1, 2026-10-01) |
| offline-banner.try-again | MISSING — new (recon row 1, 2026-10-01); not used by a step in this file |
| offline-banner.close | MISSING — new (recon row 1, 2026-10-01); not used by a step in this file (nothing it covers is tapped here, see Conventions) |
| api.surveyResponse | not an element — `GET /job/{id}` (`JobController_findOne`) → `surveyResponse` |
| device.network | not a screen element — `Adb.offline()` / network back-on, `helpers/android/device.py` |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{job.short}}, {{job.mo3}}, {{job.photo}} | `automation/mobile/fixtures/test_data.py` | same survey-kind fixtures as `../survey-test-cases.md` |
| {{job.short.titleLine}} | `automation/mobile/fixtures/test_data.py` | the job's details header line |
| gallery_photos | `automation/mobile/fixtures/test_data.py` | pushed to the emulator gallery (`Adb.push_media`) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-SRV-024, -025 | TC-SRV-017 | |
| CHK-SRV-026, -023 | TC-SRV-018 | |
| CHK-SRV-027 | TC-SRV-019 | |

## Open questions

- None identified. No `D-OFF-n` item from the recon applies directly to this file's CHK group
  (D-OFF-7, the banner covering top content, does not block any tap used here — see Conventions).

> **Reviewer note (Opus, 2026-10-01):** every "network on" step on an In progress job now also closes the "Connection restored" dialog (`connection-restored.cancel` — MISSING in maps, added with the 07 aliases); it lies over the screen otherwise. Step numbers unchanged.
