# Photo report — Android offline test cases (step 5)

> Scope/selection: owner, android-plan §2.5 — automate all 36 `android-stage` checks
> (`qa/mobile/ios/not-automated.md`). This file covers the Photo report screen's offline group:
> CHK-PHR-045…-050. Format: [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md)
> + the mobile rows from [test-cases-mobile.md](../../../_templates/test-cases-mobile.md) · prompt
> `prompts/mobile/03`. IDs continue the file's numbering from `../photo-report-test-cases.md`
> (last: TC-PHR-007; TC-PHR-008 was removed there, 2026-09-26 — this file reuses the number).
>
> **Status: validated by the owner 2026-10-01 (step 5 gate: D-OFF-1…9 answered, no remarks on the TCs).**

| Field | Value |
|---|---|
| Feature | The Photo report of an In progress job without network: add / edit / tag / delete offline, an unsynced delete never reaching the server, persistence after a cold start, automatic upload when connectivity returns, and the server state after submission for a synced photo deleted offline (D-OFF-3 / BUG-PHR-001) |
| Source checklist | `qa/mobile/09-photo-report/photo-report-checklist.md` — CHK-PHR-045, -046, -047, -048, -049, -050 |
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
  — it sits over the first photo tile's delete icon. Before the first `photo-report.delete[…]`
  tap while offline, a TC closes it: `click | offline-banner.close`.
- **The gallery flow** (as the online file): `photo-report.add-photo` → `photo-add-sheet.gallery`
  → `photo-picker.grid` (cell k) → `photo-editor.done` → the metadata page (`photo-metadata.*`).
  One row bundles the short flow with its description / tag / Save, as the online file's
  TC-PHR-003 / -007 already do.
- **A photo in the grid** is named by its description (TD-PHR-001); `photo-report.photo[<text>]`
  and `photo-report.delete[<text>]` address it by that text, as module 07's TC-DLV-005 already
  does for this screen (`photo-report.delete[QA-AUTO photo B]`) — clearer than a position index
  once the list order is affected by the offline cache (D-OFF-8 applies to job lists, not
  necessarily to this grid, so indexing by content avoids relying on an unconfirmed order).
- **The server copy** = `GET /job/{id}` (`JobController_findOne`) → `photos` (`api.jobPhotos`,
  same alias as the online file) / the whole job (`api.job`, same alias as module 07). Recon row
  12 observed sync landing within about 15 s; the TCs below allow a generous 15–20 s wait.
- **Submission on DEV answers 500 although the server records it** (Q-DLV-5,
  `qa/mobile/07-submit-deliverables/submit-deliverables-questions.md`): `POST /job/{id}/submit`
  returns 500, the app keeps the job In progress, a second open shows it Submitted. TC-PHR-010
  checks the server record the same way the existing 07 TCs do, not the app's success message.

---

## TC-PHR-008 — Offline: add a photo from the gallery with description and tag, edit the description, then delete a second photo at once — kept after a cold start, still offline

| Field | Value |
|---|---|
| ID | TC-PHR-008 |
| Title | Offline: add a photo from the gallery with description and tag, edit the description, then delete a second photo at once — kept after a cold start, still offline |
| Source CHK IDs | CHK-PHR-045, CHK-PHR-049, CHK-PHR-046 |
| Platforms | android |
| Priority | P0 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start, then cold start at step 11 (terminate + relaunch, still offline) |
| Permissions | n/a — the Android Photo Picker needs no runtime permission (recon D-PHR-A1) |
| Network | offline (Wi-Fi + mobile data off) |
| Preconditions | `{{job.progress}}` In progress, details open, device online; `gallery_photos` |
| Oracle | spec — SRS §3.1.3.4.3 FR-PH-05 "Photos shall be stored locally and automatically uploaded when connectivity is restored." (the local-storage half); CHK-PHR-045, CHK-PHR-049, CHK-PHR-046; recon row 11 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network off |
| 2 | click | job-details.deliverable[Photo report] | — | opens offline; offline-banner.message visible ("No internet connection.") |
| 3 | click | photo-report.add-photo | the gallery flow, cell 1, `QA-AUTO offline keep`, tag `tag1`, Save | photo-report.photo[QA-AUTO offline keep] — add + tag work offline |
| 4 | click | photo-report.photo[QA-AUTO offline keep] | — | "Edit photo" opens, preloaded — edit works offline |
| 5 | fill | photo-metadata.description | append `-edited` | — |
| 6 | click | photo-metadata.save | — | photo-report.photo[QA-AUTO offline keep-edited] — edit accepted offline |
| 7 | click | photo-report.add-photo | the gallery flow, cell 1, `QA-AUTO offline throwaway`, Save | photo-report.photo[QA-AUTO offline throwaway] — a second photo, to be deleted unsynced |
| 8 | click | offline-banner.close | — | banner closed — the delete icon is reachable (D-OFF-7) |
| 9 | click | photo-report.delete[QA-AUTO offline throwaway] | then photo-delete-dialog.delete | photo-report.photo[QA-AUTO offline throwaway] gone — delete works offline |
| 10 | expect-hidden | photo-report.photo[QA-AUTO offline throwaway] | — | removed from local storage at once, still offline (CHK-PHR-049) |
| 11 | open | app | terminate + launch → the job → Photo report | still offline (cold start) |
| 12 | expect-visible | photo-report.photo[QA-AUTO offline keep-edited] | — | kept after the cold start, still offline (CHK-PHR-046) |

**Postconditions / cleanup:** device offline at TC end; network restored to ON by the harness (`Adb.offline()` `finally`). Job deleted.
**Notes:** CHK-PHR-049's "never reaches the server" half is closed in TC-PHR-009 step 3, once the device is back online.
**Resolved D-OFF-7** — Owner 2026-10-01: a UI remark, not a bug — tests close the banner (✕) before taps in the covered strip.

## TC-PHR-009 — Network back: the offline photo (with its description and tag) is uploaded automatically; the photo deleted while unsynced never reaches the server

| Field | Value |
|---|---|
| ID | TC-PHR-009 |
| Title | Network back: the offline photo (with its description and tag) is uploaded automatically; the photo deleted while unsynced never reaches the server |
| Source CHK IDs | CHK-PHR-047, CHK-PHR-048 |
| Platforms | android |
| Priority | P0 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start |
| Permissions | n/a |
| Network | offline → online (toggled in this TC) |
| Preconditions | as TC-PHR-008 — `{{job.progress}}`, offline; `QA-AUTO offline keep-edited` with tag `tag1` kept; `QA-AUTO offline throwaway` deleted unsynced |
| Oracle | spec — SRS §3.1.3.4.3 FR-PH-05 "...automatically uploaded when connectivity is restored." + FR-PH-06 "If upload fails: retain photo locally; retry automatically when possible."; CHK-PHR-047, CHK-PHR-048; recon row 12 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | on | network restored; the app's "Connection restored" dialog for the unfinished In progress job comes within ~15 s and is closed with `connection-restored.cancel` (recon A2 row 12; the dialog itself is TC-DLV-009) |
| 2 | expect-hidden | offline-banner.message | within ~5 s | the banner clears once connectivity returns |
| 3 | expect-text | api.jobPhotos | — | within ~15–20 s (generous wait; recon row 12): exactly 1 photo; note `QA-AUTO offline keep-edited`; tag `tag1`; no `QA-AUTO offline throwaway` — the unsynced delete never reached the server (CHK-PHR-049) |

**Postconditions / cleanup:** network ON. Job deleted.
**Notes:** FR-PH-06's retry is exercised by the same automatic-sync path; a forced mid-sync failure cannot be induced on the emulator without breaking the app's own storage or network mid-action (as the `cannot-cause` items in `qa/mobile/ios/not-automated.md`), so this TC proves the eventual-success path, not an injected failure.

## TC-PHR-010 — A synced photo deleted offline: network back → submit deliverables → the server's job has no such photo (D-OFF-3)

| Field | Value |
|---|---|
| ID | TC-PHR-010 |
| Title | A synced photo deleted offline: network back → submit deliverables → the server's job has no such photo (D-OFF-3) |
| Source CHK IDs | CHK-PHR-050 |
| Platforms | android |
| Priority | P1 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (emulator) |
| App state | warm start |
| Permissions | n/a |
| Network | online → offline → online (toggled in this TC) |
| Preconditions | `{{job.progress}}` In progress, Short Survey already completed (setup, as module 07's TC-DLV-003), details open, device online; a photo `QA-AUTO synced then deleted` already added and present on the server (`GET /job/{id}` → `photos`) — setup, not a step here |
| Oracle | spec — SRS §3.1.3.4.4 FR-DEL-PH-08 "If the photo has already been synced, deletion shall be queued and synced when connectivity is restored."; CHK-PHR-050; accepted baseline — D-OFF-3 (mirrors BUG-PHR-001: the final server state is checked after submission, not during In progress); recon row 13 — observed (discovery, not proof) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | off | network off |
| 2 | click | job-details.deliverable[Photo report] | — | opens offline |
| 3 | click | offline-banner.close | — | banner closed — the delete icon is reachable (D-OFF-7) |
| 4 | click | photo-report.delete[QA-AUTO synced then deleted] | then photo-delete-dialog.delete | photo-report.photo[QA-AUTO synced then deleted] gone — removed locally; the deletion is not sent while offline |
| 5 | click | photo-report.back | — | job-details |
| 6 | open | device.network | on | network restored; the app's "Connection restored" dialog for the unfinished In progress job comes within ~15 s and is closed with `connection-restored.cancel` (recon A2 row 12; the dialog itself is TC-DLV-009) |
| 7 | click | job-details.submit-deliverables | then submit-dialog.submit | submission sent (DEV answers 500 — Q-DLV-5; the server record is checked regardless, as the existing 07 TCs do) |
| 8 | expect-text | api.job | — | within ~15–20 s: `submitted`; `photos` has no `QA-AUTO synced then deleted` — the deletion is applied with the job update at submission, not as its own queued sync (D-OFF-3 / BUG-PHR-001 decision) |

**Postconditions / cleanup:** network ON. Job deleted.
**Notes:** this is the same server-state check module 07 already performs after submission (TC-DLV-005); this TC adds the offline-delete trigger.
**Resolved D-OFF-3** — Owner 2026-10-01: «перевір» — the server state is checked after the submission (as BUG-PHR-001).

---

## Aliases used

| Alias | android map |
|---|---|
| job-details.deliverable, .submit-deliverables, .back | yes (module 06 / 07) |
| submit-dialog.submit | yes (module 07, `screens/submit_dialog_map.py`) |
| photo-report.header, .add-photo, .photo, .delete, .back | yes — `screens/photo_report_map.py` (recon 9 / A1) |
| photo-add-sheet.gallery · photo-delete-dialog.delete | yes — `screens/photo_report_map.py` |
| photo-metadata.description, .save | yes — `screens/survey_photo_map.py` |
| photo-picker.grid · photo-editor.done | yes — `screens/survey_photo_map.py` |
| offline-banner.message | MISSING — new (recon row 1, 2026-10-01) |
| offline-banner.try-again | MISSING — new (recon row 1, 2026-10-01); not used by a step in this file |
| offline-banner.close | MISSING — new (recon row 16 / D-OFF-7, 2026-10-01) |
| api.jobPhotos | not an element — `GET /job/{id}` (`JobController_findOne`) → `photos` |
| api.job | not an element — `GET /job/{id}` (`JobController_findOne`), same alias as module 07 |
| device.network | not a screen element — `Adb.offline()` / network back-on, `helpers/android/device.py` |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{job.progress}} | `automation/mobile/fixtures/test_data.py` | In progress job, same fixture as the online file |
| gallery_photos | `automation/mobile/fixtures/test_data.py` | pushed to the emulator gallery (`Adb.push_media`) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-PHR-045, -049, -046 | TC-PHR-008 (+ -009 for -049's server half) | |
| CHK-PHR-047, -048 | TC-PHR-009 | |
| CHK-PHR-050 | TC-PHR-010 | D-OFF-3, pending owner |

## Open questions

- D-OFF-3 (CHK-PHR-050) — pending the owner's confirmation that the server state is checked
  after submission, not as an independently queued delete sync (see TC-PHR-010).
- D-OFF-7 (banner over the first tile's delete icon) — pending the owner's call: UX note or bug
  (see TC-PHR-008 / -010).

> **Reviewer note (Opus, 2026-10-01):** every "network on" step on an In progress job now also closes the "Connection restored" dialog (`connection-restored.cancel` — MISSING in maps, added with the 07 aliases); it lies over the screen otherwise. Step numbers unchanged.
