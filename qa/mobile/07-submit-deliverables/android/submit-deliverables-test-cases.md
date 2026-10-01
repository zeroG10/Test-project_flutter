# Submit deliverables — Android offline test cases (step 5)

> Scope/selection: owner, android-plan §2.5 — automate all 36 `android-stage` checks
> (`qa/mobile/ios/not-automated.md`). This file covers the Submit deliverables module's offline
> group: CHK-DLV-023, -024, -025, -026 (Q-DLV-1,
> `../submit-deliverables-questions.md`, closed 2026-09-26: "офлайн ... на етапі Android"). Format:
> [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md) + the mobile rows
> from [test-cases-mobile.md](../../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`.
> IDs continue the file's numbering from
> [../submit-deliverables-test-cases.md](../submit-deliverables-test-cases.md) (last: TC-DLV-006) —
> below starts at TC-DLV-007. Source recon:
> [qa/shared/recon-2026-10-01-android-offline.md](../../../shared/recon-2026-10-01-android-offline.md)
> (recon A2, 2026-10-01) — discovery of what is on screen, never the oracle; oracle = SRS + owner
> decisions. Q-DLV-5 (DEV answers `POST /job/{id}/submit` with 500 although the submission is
> recorded) carries over unchanged — see Conventions.
>
> **Status: validated by the owner 2026-10-01 (step 5 gate: D-OFF-1…9 answered, no remarks on the TCs).**

| Field | Value |
|---|---|
| Feature | Submitting deliverables of an In progress job without network: the Submit button disabled with its offline message, the deliverables made offline staying on the device (also after a cold start), and the "Connection restored" dialog once the network is back |
| Source checklist | `qa/mobile/07-submit-deliverables/submit-deliverables-checklist.md` — CHK-DLV-023, -024, -025, -026 |
| Platform | android |
| Devices / build | Pixel 7 · Android 16 (API 36), emulator `Pixel_7_API_36` (`-dns-server 8.8.8.8,1.1.1.1`) · Appium 3.4.2 + UiAutomator2 · `[DEV] CT Mobile` 1.1.1 (178) debug, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko · Last updated 2026-10-01 |

**Conventions**

- **One job per test**, created through `POST /job` directly In progress with the Short Survey
  (fixture `{{job.progress}}`, as the online file), while the device is still online; deleted after
  the test.
- **Network is a step**: `open | device.network | off` / `on` (`Adb.offline()` /
  `Adb.online()`, `helpers/android/device.py`). A TC that ends offline by design still leaves the
  network **ON** afterwards — `Adb.offline()` restores it in `finally`, no extra step needed. A TC
  that proves "network back" makes the `on` step part of the scenario.
- **Completing the survey** (as the online file): `survey.yes[1]` → `survey.text[1]` `<text>` →
  `survey.save`; the harness waits for the "Survey saved" snackbar.
- **The offline banner covers the top content strip** (`offline-banner.*`, D-OFF-7, recon row 16).
  TC-DLV-008 taps the cached job card after a cold start and closes the banner first
  (`offline-banner.close`), as the photo report / notes android files already do.
- **`job-details.offline-message`** is the per-screen "Offline. Data will sync when the connection
  is restored." line above the Submit button (recon row 8, SRS §3.1.3.4 Primary Action Area) —
  distinct from the global `offline-banner.*`, which also shows on this screen (recon row 1).
- **DEV and COPS (Q-DLV-5, unchanged on Android)**: `POST /job/{id}/submit` answers 500 although
  the server records the submission (job Submitted, time, survey, photos, notes). TC-DLV-009 checks
  the server record, exactly as the existing 07 TCs do (TC-DLV-003), not the app's own success
  toast — that reaction is TC-DLV-004, already `Blocked` on DEV and staying `Blocked` on Android
  (`docs/notes/android-plan.md` §4, step 5 note).

---

## TC-DLV-007 — Offline on an In progress job with complete deliverables: Submit deliverables is disabled with its offline message, and a tap sends nothing

| Field | Value |
|---|---|
| ID | TC-DLV-007 |
| Title | Offline on an In progress job with complete deliverables: Submit deliverables is disabled with its offline message, and a tap sends nothing |
| Source CHK IDs | CHK-DLV-023, CHK-DLV-024 |
| Platforms | android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, signed in |
| Permissions | n/a |
| Network | online Wi-Fi (Preconditions) → offline (adb) |
| Preconditions | `{{job.progress}}` In progress, details open; survey completed while online (`survey.yes[1]` → `survey.text[1]` `QA-AUTO offline-submit answer` → `survey.save`); `job-details.submit-deliverables` enabled (deliverables complete, online) |
| Oracle | spec — SRS §3.1.3.4 Primary Action Area / FR-IP-05 "The Submit Deliverables button shall be enabled only when: All required deliverables are completed (Survey); The device is online."; FR-IP-06 "If the device is offline, the system shall: Disable submission; Display a clear offline message; ..."; CHK-DLV-023, CHK-DLV-024; observed (discovery, not proof) — recon A2 row 8, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network disabled |
| 2 | expect-visible | job-details.offline-message | — | "Offline. Data will sync when the connection is restored." (CHK-DLV-024) |
| 3 | expect-disabled | job-details.submit-deliverables | — | disabled while offline (CHK-DLV-023) |
| 4 | click | job-details.submit-deliverables | — | disabled control — no dialog opens, no request sent |
| 5 | expect-hidden | submit-dialog.title | — | the confirmation dialog never appears |
| 6 | expect-text | api.job | — | `in_progress`, no `submissionDate` — nothing was sent while offline |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness. Job deleted.
**Notes:** FR-IP-05's "enabled only when ... online" and FR-IP-06's "disable submission" describe the same rule from both sides; this TC proves the disabled state and that a tap on a disabled control is a no-op, not just the label.

---

## TC-DLV-008 — Offline: deliverables added without network (survey answer, a note, a photo) stay on the device, also after a cold start

| Field | Value |
|---|---|
| ID | TC-DLV-008 |
| Title | Offline: deliverables added without network (survey answer, a note, a photo) stay on the device, also after a cold start |
| Source CHK IDs | CHK-DLV-025 |
| Platforms | android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, then a cold start partway through (terminate + relaunch, still offline) |
| Permissions | n/a |
| Network | offline (adb) throughout, including the cold start |
| Preconditions | `{{job.progress}}` In progress, details open, device online at job creation; no deliverable completed yet — everything in this TC is created offline |
| Oracle | spec — SRS §3.3.1 Offline Functionality "Save in-progress surveys and photos"; FR-IP-04 "Progress on deliverables shall be saved automatically locally on a device."; FR-IP-09 "All deliverables created while offline shall be stored locally."; CHK-DLV-025; observed (discovery, not proof) — recon A2 rows 9, 10, 11, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network disabled |
| 2 | click | survey.yes[1] | then survey.text[1] `QA-AUTO offline survey`, survey.save | saved offline; back on job-details (FR-SUR-12 "fully functional offline") |
| 3 | click | job-details.deliverable[Photo report] | the gallery flow, cell 1, `QA-AUTO offline photo`, Save; back | "Photo added successfully"; back on job-details |
| 4 | click | job-details.deliverable[Notes] | then notes.add-note `QA-AUTO offline note`, Save | the note in the list; back on job-details |
| 5 | open | app | terminate + launch (still offline) | app relaunches offline |
| 6 | click | offline-banner.close | then jobs-list.card[{{job.progress.jobId}}] | banner closed first (D-OFF-7); job-details reopened from the cache |
| 7 | click | job-details.deliverable[Survey] | — | opens |
| 8 | expect-text | survey.text[1] | — | `QA-AUTO offline survey` — survived the cold start (CHK-DLV-025) |
| 9 | click | job-details.deliverable[Photo report] | — | opens |
| 10 | expect-visible | photo-report.photo[QA-AUTO offline photo] | — | survived the cold start |
| 11 | click | job-details.deliverable[Notes] | — | opens |
| 12 | expect-text | notes.row[1] | — | `QA-AUTO offline note` — survived the cold start |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness. Job deleted.
**Notes:** none of the three deliverables was ever sent to the server in this TC (the device never went online) — persistence here is purely local storage, as FR-IP-04 / FR-IP-09 describe.
**Resolved D-OFF-7** — Owner 2026-10-01: a UI remark, not a bug — tests close the banner (✕) before taps in the covered strip.

---

## TC-DLV-009 — Network back: the "Connection restored" dialog names the job; Submit from the dialog is recorded on the server

| Field | Value |
|---|---|
| ID | TC-DLV-009 |
| Title | Network back: the "Connection restored" dialog names the job; Submit from the dialog is recorded on the server |
| Source CHK IDs | CHK-DLV-026 |
| Platforms | android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | warm start, signed in |
| Permissions | n/a |
| Network | offline (adb) → online Wi-Fi (step 3) |
| Preconditions | `{{job.progress}}` In progress, details open; survey completed while online (as TC-DLV-007) |
| Oracle | spec — SRS FR-IP-06 "...Inform users once connectivity is restored, that order wasn't submitted, so he can resubmit it; Automatically submit data once connectivity is restored if the submission progress was interrupted."; FR-SUB-06 "...Automatically submit deliverables when connectivity is restored"; CHK-DLV-026; D-OFF-2 (owner-pending, recon A2); observed (discovery, not proof) — recon A2 row 12, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network disabled |
| 2 | expect-disabled | job-details.submit-deliverables | — | disabled offline (baseline, CHK-DLV-023) |
| 3 | open | device.network | on | network restored |
| 4 | wait-for | connection-restored.title | — | visible within a generous wait (recon: ≈15 s) |
| 5 | expect-text | connection-restored.message | — | contains: "unfinished job" and {{job.progress.jobId}}; "Submit your deliverables now" — names the job (CHK-DLV-026) |
| 6 | expect-visible | connection-restored.cancel | — | Cancel present |
| 7 | expect-visible | connection-restored.submit | — | Submit present |
| 8 | click | connection-restored.submit | — | submission starts from the dialog |
| 9 | expect-text | api.job | — | within ~15–20 s: `submitted`; `submissionDate` set; the survey answer recorded — the submission is recorded on the server (Q-DLV-5: DEV still answers `POST /job/{id}/submit` with 500; the app's own success toast is checked separately by TC-DLV-004, `Blocked` on DEV) |

**Postconditions / cleanup:** network ON. Job deleted.
**Notes:** this reuses TC-DLV-003's server-record oracle, with the "Connection restored" dialog as the trigger instead of the normal Submit flow.
**Resolved D-OFF-2** — Owner 2026-10-01: «ок» — the "Connection restored" dialog + Submit counts as FR-IP-06; an interrupted submission's auto-resume stays Blocked (DEV submit 500).

---

## Aliases used

| Alias | Screen | android map | ios map |
|---|---|---|---|
| device.network | — (device control) | n/a — harness capability; `Adb.offline()` / `Adb.online()` exists (`helpers/android/device.py`) | n/a — no network control on the iOS simulator |
| app | — (launch / terminate / relaunch) | n/a | n/a |
| job-details.deliverable, .submit-deliverables, .root | job-details | yes (modules 04–06) | yes |
| job-details.offline-message | job-details (new) | **MISSING** — new (recon A2 row 8, 2026-10-01) | **MISSING** |
| submit-dialog.title | submit-dialog | yes (module 07, `screens/submit_dialog_map.py`) | yes |
| survey.yes[1], .text[1], .save | survey | yes (module 08) | yes |
| photo-report.photo[<text>] | photo-report | yes (module 09) | yes |
| notes.add-note, .row[1] | notes | yes (module 10) | yes |
| jobs-list.card[{{jobId}}] | jobs-list | yes (module 03, step 3) | yes |
| offline-banner.message | offline banner (new, any screen) | **MISSING** — new (recon A2 row 1, 2026-10-01); not used by a step in this file | **MISSING** |
| offline-banner.try-again | offline banner | **MISSING** — new (recon A2 row 1, 2026-10-01); not used by a step in this file | **MISSING** |
| offline-banner.close | offline banner | **MISSING** — new (recon A2 row 16 / D-OFF-7, 2026-10-01) | **MISSING** |
| connection-restored.title, .message, .cancel, .submit | connection-restored dialog (new) | **MISSING** — new (recon A2 row 12, 2026-10-01) | **MISSING** |
| api.job | — (not a screen element) | `GET /job/{id}` (`JobController_findOne`) — same alias as the online file | same |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{job.progress}} | `automation/mobile/fixtures/test_data.py` | In progress job, same fixture as the online file; one per test, deleted after |
| gallery_photos | `automation/mobile/fixtures/test_data.py` | pushed to the emulator gallery, same fixture as module 09 |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-DLV-023, CHK-DLV-024 | TC-DLV-007 | |
| CHK-DLV-025 | TC-DLV-008 | survey deep-checked (text); photo and note checked by presence after the cold start; **Resolved D-OFF-7** — Owner 2026-10-01: a UI remark, not a bug — tests close the banner (✕) before taps in the covered strip.
| CHK-DLV-026 | TC-DLV-009 | D-OFF-2, pending owner |

## Open questions

- Resolved **D-OFF-2** (owner 2026-10-01: «ок» — dialog + Submit accepted)
  "automatically submit ... when connectivity is restored" (FR-SUB-06, FR-IP-06), but the app
  requires a manual tap on the "Connection restored" dialog — awaiting the owner's validation of
  the recon's proposed reading (step 5 gate).
- Resolved **D-OFF-7** (owner 2026-10-01: UI remark, not a bug)
  a cold start; this TC closes it before tapping, as the photo report / notes android files already
  do — owner's call: UX note or bug (recon D-OFF-7), decided once for all modules it touches.
- TC-DLV-004 (the app's own success-toast reaction to a successful submission) stays `Blocked` on
  Android too — DEV answers 500 regardless of platform (Q-DLV-5, `docs/notes/android-plan.md` §4).
