# Test cases — Photo report (mobile)

> Structured, alias-based test cases for the CHK IDs selected in [photo-report-automation-plan.md](photo-report-automation-plan.md).
> Format: [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: draft — written after recon 9 ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md)) and the
> owner's decisions (2026-09-25: Q-PHR-2…5 closed; Q-PHR-1 → BUG-PHR-001 draft for validation).**

| Field | Value |
|---|---|
| Feature | The Photo report of an In progress job: empty / populated states, adding from the gallery, description and tags, editing, deleting, persistence, the server copy |
| Source checklist | `qa/mobile/09-photo-report/photo-report-checklist.md` (CHK-PHR-001…054) |
| Devices / build | iPhone 17 · iOS 26.5 (simulator) · `[DEV] CT Mobile` 1.1.1 (178), `CLIENT_BUILD=true` · online · photos: the system picker |
| Owner | @mykola.zhuchenko · Last updated 2026-09-25 |

**Conventions**

- **One job per test**, created through `POST /job` directly In progress (fixture `survey_job`), deleted after it.
- **The gallery flow**: `photo-report.add-photo` → `photo-add-sheet.gallery` → `photo-picker.grid` (cell k, newest first)
  → `photo-editor.done` → the metadata page (`photo-metadata.*`). Cell 0 = the 4032×3024 test photo, cell 1 = a small one
  (fixture `gallery_photos`).
- **A photo in the grid** is an image named by its description and tags (TD-PHR-001); `photo-report.photo[n]` is the n-th
  in the grid, `photo-report.delete[n]` its delete icon.
- **The server copy** = `GET /job/{id}` → `photos` (`note`, `tags`).

---

## TC-PHR-001 — The empty Photo report leads through the gallery to a saved photo with its description

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-001, -002, -003, -004, -005, -006, -007, -009, -011, -013, -014, -033, -034, -035 |
| Priority | P0 · smoke |
| Preconditions | `{{job.progress}}` In progress, details open; `gallery_photos` |
| Oracle | spec — SRS §3.1.3.4.3 (empty state text), FR-PH-01, FR-PH-M-07; recon 9 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Photo report] | — | — |
| 2 | expect-visible | photo-report.header | — | "Photo report", with photo-report.back |
| 3 | expect-text | photo-report.empty-title | — | No photos have been added yet · Add photos to the report to get started. |
| 4 | click | photo-report.add-photo | — | photo-add-sheet: "Add photo" with Camera and Gallery |
| 5 | click | photo-add-sheet.gallery | then cell 1, photo-editor.done | photo-metadata.title "Add photo"; the photo preview; the description empty, "0 / 500" |
| 6 | fill | photo-metadata.description | `QA-AUTO photo one` | — |
| 7 | click | photo-metadata.save | — | back on photo-report |
| 8 | expect-visible | photo-report.photo[QA-AUTO photo one] | — | the photo with its description |
| 9 | expect-text | api.jobPhotos | — | 1 photo, note `QA-AUTO photo one` |

## TC-PHR-002 — Description up to 500 characters with a counter; tags are chosen and unchosen

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-025, -026, -027, -028, -029, -030, -031, -032 |
| Priority | P1 |
| Preconditions | as TC-PHR-001, up to the metadata page |
| Oracle | spec — FR-PH-M-04…06 (description ≤ 500, optional; tags from the Admin Panel) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-enabled | photo-metadata.save | — | the description is optional |
| 2 | fill | photo-metadata.description | 501 characters | the first 500 kept; counter "500 / 500" |
| 3 | click | photo-metadata.tag[Undamaged] | — | selected |
| 4 | click | photo-metadata.tag[tag1] | — | selected (two at once) |
| 5 | click | photo-metadata.tag[Undamaged] | — | not selected |
| 6 | click | photo-metadata.save | — | back on photo-report |
| 7 | expect-text | api.jobPhotos | — | the note (500 characters) and one tag, `tag1` |

## TC-PHR-003 — Several photos show as a grid, and Add photo stays available

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-006, -008 |
| Priority | P1 |
| Preconditions | as TC-PHR-001 |
| Oracle | spec — FR-PH-01; SRS §3.1.3.4.3 (populated state) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | photo-report.add-photo | the gallery flow, cell 1, no description | — |
| 2 | click | photo-report.add-photo | the gallery flow, cell 1, `QA-AUTO second` | — |
| 3 | click | photo-report.add-photo | the gallery flow, cell 1, `QA-AUTO third` | — |
| 4 | expect-text | photo-report.photo | — | 3 photos in the grid |
| 5 | expect-visible | photo-report.add-photo | — | still there |

## TC-PHR-004 — Editing: "Edit photo" preloads the photo's data; Save updates it; leaving without Save warns and keeps it

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-013, -015, -036, -037, -038 |
| Priority | P1 |
| Preconditions | a photo `QA-AUTO photo one` with tag `tag1` in the grid |
| Oracle | spec — FR-PH-M-08, -09; D-PHR-3 (the warning) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | photo-report.photo[QA-AUTO photo one] | — | photo-metadata.edit-title "Edit photo"; description and `tag1` preloaded |
| 2 | fill | photo-metadata.description | append `-edited` | — |
| 3 | click | photo-metadata.back | — | photo-unsaved-dialog: "Unsaved Changes" |
| 4 | click | photo-unsaved-dialog.leave | — | photo-report; the photo still `QA-AUTO photo one` |
| 5 | click | photo-report.photo[QA-AUTO photo one] | — | — |
| 6 | fill | photo-metadata.description | append `-edited` | — |
| 7 | click | photo-metadata.save | — | photo-report |
| 8 | expect-visible | photo-report.photo[QA-AUTO photo one-edited] | — | — |
| 9 | expect-text | api.jobPhotos | — | 1 photo, note `QA-AUTO photo one-edited`, tag `tag1` |

## TC-PHR-005 — Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-039, -040, -041, -042, -044 |
| Priority | P0 |
| Preconditions | two photos in the grid |
| Oracle | spec — FR-DEL-PH-01…03; D-PHR-1 (the message wording) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | photo-report.delete[1] | — | photo-delete-dialog: "Delete photo", "Are you sure you want to delete this photo. All descriptions will be lost?", Cancel, Delete |
| 2 | click | photo-delete-dialog.cancel | — | 2 photos |
| 3 | click | photo-report.delete[1] | — | — |
| 4 | click | photo-delete-dialog.delete | — | 1 photo |
| 5 | click | photo-report.delete[1] | then photo-delete-dialog.delete | photo-report.empty-title again |

## TC-PHR-006 — Photos and descriptions survive an app restart

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-033 |
| Priority | P1 |
| Preconditions | a photo `QA-AUTO keep` in the grid |
| Oracle | spec — FR-PH-05, FR-PH-M-07 (persisted locally) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | terminate + launch → the job → Photo report | — |
| 2 | expect-visible | photo-report.photo[QA-AUTO keep] | — | — |

## TC-PHR-007 — The photo editor opens with Crop and Markup, and ✓ leads to "Add photo"

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-012 |
| Priority | P2 |
| Preconditions | as TC-PHR-001 |
| Oracle | spec — FR-PH-M-01/02 (editor present); crop / markup themselves: manual, verified by the owner (Q-PHR-3) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | photo-report.add-photo | then photo-add-sheet.gallery, cell 1 | — |
| 2 | expect-visible | photo-editor.crop | — | Crop and Markup |
| 3 | click | photo-editor.done | — | photo-metadata.title "Add photo" |

## TC-PHR-008 — A deleted photo is removed from the job on the server

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PHR-043 |
| Priority | P1 |
| Preconditions | one photo `QA-AUTO to delete`, saved (on the server) |
| Oracle | spec — FR-DEL-PH-03, -04, -08 |
| Known defect | **BUG-PHR-001** (draft, owner's validation pending) — the app deletes on the device only |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | api.jobPhotos | — | the photo is on the server |
| 2 | click | photo-report.delete[1] | then photo-delete-dialog.delete | photo-report.empty-title |
| 3 | expect-text | api.jobPhotos | — | no photo on the job |

## Aliases used

| Alias | ios map |
|---|---|
| job-details.deliverable | yes |
| photo-report.header, .back, .empty-title, .add-photo, .photo, .delete · photo-add-sheet.gallery, .camera · photo-delete-dialog.* · photo-unsaved-dialog.* | `screens/photo_report_map.py` (recon 9) |
| photo-metadata.title, .edit-title, .description, .counter, .tag, .save, .back · photo-picker.grid · photo-editor.crop, .done | `screens/survey_photo_map.py` (recon 8 / 9) |
| api.jobPhotos | not an element — `GET /job/{id}` → `photos` |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-PHR-001…-007, -009, -011, -013, -014, -033…-035 | TC-PHR-001 (+ -003, -006) | |
| CHK-PHR-008 | TC-PHR-003 | |
| CHK-PHR-012 | TC-PHR-007 | |
| CHK-PHR-015, -036…-038 | TC-PHR-004 | |
| CHK-PHR-025…-032 | TC-PHR-002 | |
| CHK-PHR-039…-042, -044 | TC-PHR-005 | |
| CHK-PHR-043 | TC-PHR-008 | BUG-PHR-001 |

**Not here:**
- CHK-PHR-010 (camera) and CHK-PHR-016…-024 (crop / markup) — skipped with a comment: the owner verified them manually
  (Q-PHR-2, Q-PHR-3).
- CHK-PHR-045…-050 — offline, Android stage.
- CHK-PHR-051…-054 — skipped with a comment (Q-PHR-4).
