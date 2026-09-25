# Automated traceability — mobile

Generated: 2026-09-25 06:43 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/09-photo-report/photo-report-checklist.md` — 54 items
- Results (allure): `automation/mobile/allure-results-09` — 8 tests (7 passed, 1 failed, 0 skipped)

## Run context — the limits of every verdict below

- Target: `iOS simulator iPhone 17 · iOS 26.5 · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true`
- Harness commit (this repo): `704490b`
- Environment label (pytest): `iOS · iPhone 17 · iOS 26.5 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=ios tests/shared/test_photo_report.py (module 09 run 2, 2026-09-25; one In progress job per test; gallery: 2 test photos)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-PHR-001 | Check that the Photo Report screen opens from the In Progress Order screen when… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-002 | Check that the Photo Report screen displays the title “Photo report” and a back… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-003 | Check that the empty state is displayed when no photos are added, including pla… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-004 | Check that the empty state displays the primary action button “Add photo”. | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-005 | Check that tapping “Add photo” from the empty state initiates the Add photo flo… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-006 | Check that when photos exist, the Photo Report screen displays a grid of photo… | 2 — `tests.shared.test_photo_report#test_several_photos (TC-PHR-003 Several photos show as a grid, and Add photo stays available)`; `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed<br>allure: passed |
| CHK-PHR-007 | Check that each photo thumbnail displays a preview image and a short descriptio… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-008 | Check that the Add photo button is available in the populated state and remains… | 1 — `tests.shared.test_photo_report#test_several_photos (TC-PHR-003 Several photos show as a grid, and Add photo stays available)` | Passed | allure: passed |
| CHK-PHR-009 | Check that tapping Add photo opens a source selection bottom sheet with Camera… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-010 | Check that selecting Camera opens the device camera and allows capturing a new… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-011 | Check that selecting Gallery opens the device gallery and allows selecting an e… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-012 | Check that the Add/Edit Photo screen opens after a photo is captured or selecte… | 1 — `tests.shared.test_photo_report#test_editor_opens (TC-PHR-007 The photo editor opens with Crop and Markup, and ✓ leads to 'Add photo')` | Passed | allure: passed |
| CHK-PHR-013 | Check that the Add/Edit Photo screen displays a contextual title (“Add photo” o… | 2 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)`; `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed<br>allure: passed |
| CHK-PHR-014 | Check that the selected photo is displayed in a full-width preview area. | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-015 | Check that the screen provides back navigation to discard or confirm changes ac… | 1 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed |
| CHK-PHR-016 | Check that the Crop tool allows adjusting a crop frame over the photo. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-017 | Check that a grid overlay is displayed during cropping for alignment assistance. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-018 | Check that confirming crop applies the crop to the photo preview. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-019 | Check that cancelling crop restores the photo to its previous state. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-020 | Check that the Markup tool allows freehand drawing on top of the photo. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-021 | Check that the Markup tool provides a selectable color palette. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-022 | Check that the Markup tool supports adjustable stroke size. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-023 | Check that undo removes the last markup action. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-024 | Check that redo restores the previously undone markup action. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-025 | Check that the photo description field allows multi-line text input. | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-026 | Check that the description field enforces a maximum length of 500 characters. | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-027 | Check that the character counter updates correctly as text is entered. | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-028 | Check that the description field is optional and does not block saving when emp… | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-029 | Check that the Tags section displays multi-select tag chips sourced from the Ad… | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-030 | Check that the user can select one or more tags for a photo. | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-031 | Check that selecting a tag visually marks it as selected. | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-032 | Check that deselecting a tag removes it from the photo metadata. | 1 — `tests.shared.test_photo_report#test_description_and_tags (TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen)` | Passed | allure: passed |
| CHK-PHR-033 | Check that tapping Save persists the photo, edits, description, and tags locall… | 2 — `tests.shared.test_photo_report#test_photos_after_restart (TC-PHR-006 Photos and descriptions survive an app restart)`; `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed<br>allure: passed |
| CHK-PHR-034 | Check that tapping Save returns the user to the Photo Report screen. | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-035 | Check that the newly added or edited photo appears immediately in the Photo Rep… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-036 | Check that previously saved data is preloaded when editing an existing photo. | 1 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed |
| CHK-PHR-037 | Check that navigating back without saving discards unsaved changes to the photo. | 1 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed |
| CHK-PHR-038 | Check that an optional warning is displayed before discarding unsaved changes i… | 1 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed |
| CHK-PHR-039 | Check that tapping the delete icon on a photo opens the Delete Photo confirmati… | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-040 | Check that the Delete Photo pop-up displays the title “Delete photo” and destru… | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-041 | Check that the pop-up displays Cancel and Delete actions. | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-042 | Check that tapping Cancel closes the pop-up and preserves the photo and metadat… | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-043 | Check that tapping Delete permanently removes the photo and all associated meta… | 1 — `tests.shared.test_photo_report#test_deleted_photo_leaves_the_server (TC-PHR-008 A deleted photo is removed from the job on the server)` | Failed | allure: failed — AssertionError: the deleted photo is still on the job: ['51ab4bcc-3ef3-44ed-b1ac-3d5e9fe26ec2'] |
| CHK-PHR-044 | Check that the Photo Report grid updates immediately after photo deletion. | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-045 | Check that photos can be added, edited, tagged, and deleted while offline. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-046 | Check that photos and metadata are stored locally when added offline. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-047 | Check that photos are automatically uploaded when connectivity is restored. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-048 | Check that failed uploads are retried automatically without user data loss. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-049 | Check that deleting an unsynced photo removes it from local storage immediately. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-050 | Check that deleting a synced photo queues the deletion and syncs it when online. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-051 | Check that an error message is displayed if photo upload fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-052 | Check that the original photo is preserved if photo editing fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-053 | Check that photo edits and metadata are retained locally if saving fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-054 | Check that the user can retry saving or syncing after an error. | 0 |  | no tagged test — not run (manual / exploratory), never green |

**Summary:** total 54 · automated 34 · Passed 33 · Failed 1 · Blocked 0 · Not run 20 (= total − Passed − Failed − Blocked)

## Failed rows → defects

| CHK ID | Test | Defect |
|---|---|---|
| CHK-PHR-043 | TC-PHR-008 — the deleted photo is still on the job on the server | [BUG-PHR-001](bugs/BUG-PHR-001.md) (draft — the owner validates) |

**Not automated (20):**
- CHK-PHR-010 (camera) and CHK-PHR-016…-024 (crop / markup): skipped with a comment — the owner verified them manually (Q-PHR-2, Q-PHR-3).
- CHK-PHR-045…-050: offline, Android stage.
- CHK-PHR-051…-054: skipped with a comment (Q-PHR-4).
