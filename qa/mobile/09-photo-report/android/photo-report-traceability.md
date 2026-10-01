# Automated traceability — mobile

Generated: 2026-10-01 10:28 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/09-photo-report/photo-report-checklist.md` — 54 items
- Results (allure): `automation/mobile/results/android/2026-10-01-09-with-offline` — 10 tests (9 passed, 1 failed, 0 skipped)

## Run context — the limits of every verdict below

- Target: `Android emulator Pixel 7 · Android 16 (API 36) · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true, debug APK`
- Harness commit (this repo): `27385b9` for run 5, `284aa37` for the TC-PHR-001 rerun (see the run label); step 5 offline: `64da953` (offline-all-r1), `38cb0c2` (offline-0311-check)
- Environment label (pytest): `Android · Pixel_7_API_36 · Android 16 · build 1.1.1 (178)`
- Run label (suite / filter): `MERGED: step 4 — MERGED: module 09 run 5 (harness 27385b9, 6 tests) + TC-PHR-001 rerun (harness 284aa37: run.sh keeps the Mac awake — in run 5 the Mac slept 13.8 min during TC-PHR-001), 2026-09-30; one In progress job per test — + step 5 offline tests of this module (run offline-all-r1, harness 64da953; TC-ORDL-018 and TC-NOTIF-007 from offline-0311-check, harness 38cb0c2), 2026-10-01`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-PHR-001 | Check that the Photo Report screen opens from the In Progress Order screen when… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-002 | Check that the Photo Report screen displays the title “Photo report” and a back… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-003 | Check that the empty state is displayed when no photos are added, including pla… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-004 | Check that the empty state displays the primary action button “Add photo”. | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-005 | Check that tapping “Add photo” from the empty state initiates the Add photo flo… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-006 | Check that when photos exist, the Photo Report screen displays a grid of photo… | 2 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)`; `tests.shared.test_photo_report#test_several_photos (TC-PHR-003 Several photos show as a grid, and Add photo stays available)` | Passed | allure: passed<br>allure: passed |
| CHK-PHR-007 | Check that each photo thumbnail displays a preview image and a short descriptio… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-008 | Check that the Add photo button is available in the populated state and remains… | 1 — `tests.shared.test_photo_report#test_several_photos (TC-PHR-003 Several photos show as a grid, and Add photo stays available)` | Passed | allure: passed |
| CHK-PHR-009 | Check that tapping Add photo opens a source selection bottom sheet with Camera… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-010 | Check that selecting Camera opens the device camera and allows capturing a new… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-011 | Check that selecting Gallery opens the device gallery and allows selecting an e… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-012 | Check that the Add/Edit Photo screen opens after a photo is captured or selecte… | 1 — `tests.shared.test_photo_report#test_editor_opens (TC-PHR-007 The photo editor opens with Crop and Markup, and ✓ leads to 'Add photo')` | Passed | allure: passed |
| CHK-PHR-013 | Check that the Add/Edit Photo screen displays a contextual title (“Add photo” o… | 2 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)`; `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed<br>allure: passed |
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
| CHK-PHR-033 | Check that tapping Save persists the photo, edits, description, and tags locall… | 2 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)`; `tests.shared.test_photo_report#test_photos_after_restart (TC-PHR-006 Photos and descriptions survive an app restart)` | Passed | allure: passed<br>allure: passed |
| CHK-PHR-034 | Check that tapping Save returns the user to the Photo Report screen. | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-035 | Check that the newly added or edited photo appears immediately in the Photo Rep… | 1 — `tests.shared.test_photo_report#test_add_photo (TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its description)` | Passed | allure: passed |
| CHK-PHR-036 | Check that previously saved data is preloaded when editing an existing photo. | 1 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed |
| CHK-PHR-037 | Check that navigating back without saving discards unsaved changes to the photo. | 1 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed |
| CHK-PHR-038 | Check that an optional warning is displayed before discarding unsaved changes i… | 1 — `tests.shared.test_photo_report#test_edit_photo (TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without Save warns and keeps it)` | Passed | allure: passed |
| CHK-PHR-039 | Check that tapping the delete icon on a photo opens the Delete Photo confirmati… | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-040 | Check that the Delete Photo pop-up displays the title “Delete photo” and destru… | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-041 | Check that the pop-up displays Cancel and Delete actions. | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-042 | Check that tapping Cancel closes the pop-up and preserves the photo and metadat… | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-043 | Check that tapping Delete permanently removes the photo and all associated meta… | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-044 | Check that the Photo Report grid updates immediately after photo deletion. | 1 — `tests.shared.test_photo_report#test_delete_photo (TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid updates)` | Passed | allure: passed |
| CHK-PHR-045 | Check that photos can be added, edited, tagged, and deleted while offline. | 1 — `tests.android.test_offline_photo_report#test_photo_report_offline_add_edit_delete_cold_start (TC-PHR-008 Offline: add a photo from the gallery with description and tag, edit the description, then delete a second photo at once — kept after a cold start, still offline)` | Passed | allure: passed |
| CHK-PHR-046 | Check that photos and metadata are stored locally when added offline. | 1 — `tests.android.test_offline_photo_report#test_photo_report_offline_add_edit_delete_cold_start (TC-PHR-008 Offline: add a photo from the gallery with description and tag, edit the description, then delete a second photo at once — kept after a cold start, still offline)` | Passed | allure: passed |
| CHK-PHR-047 | Check that photos are automatically uploaded when connectivity is restored. | 1 — `tests.android.test_offline_photo_report#test_photo_report_offline_sync_on_network_back (TC-PHR-009 Network back: the offline photo (with its description and tag) is uploaded automatically; the photo deleted while unsynced never reaches the server)` | Passed | allure: passed |
| CHK-PHR-048 | Check that failed uploads are retried automatically without user data loss. | 1 — `tests.android.test_offline_photo_report#test_photo_report_offline_sync_on_network_back (TC-PHR-009 Network back: the offline photo (with its description and tag) is uploaded automatically; the photo deleted while unsynced never reaches the server)` | Passed | allure: passed |
| CHK-PHR-049 | Check that deleting an unsynced photo removes it from local storage immediately. | 1 — `tests.android.test_offline_photo_report#test_photo_report_offline_add_edit_delete_cold_start (TC-PHR-008 Offline: add a photo from the gallery with description and tag, edit the description, then delete a second photo at once — kept after a cold start, still offline)` | Passed | allure: passed |
| CHK-PHR-050 | Check that deleting a synced photo queues the deletion and syncs it when online. | 1 — `tests.android.test_offline_photo_report#test_photo_report_synced_delete_offline_removed_after_submission (TC-PHR-010 A synced photo deleted offline: network back → submit deliverables → the server's job has no such photo (D-OFF-3))` | Failed | allure: failed — AssertionError: ['QA-AUTO synced then deleted'] |
| CHK-PHR-051 | Check that an error message is displayed if photo upload fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-052 | Check that the original photo is preserved if photo editing fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-053 | Check that photo edits and metadata are retained locally if saving fails. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PHR-054 | Check that the user can retry saving or syncing after an error. | 0 |  | no tagged test — not run (manual / exploratory), never green |

**Summary:** total 54 · automated 40 · Passed 39 · Failed 1 · Blocked 0 · Not run 14 (= total − Passed − Failed − Blocked)

> **Notes (2026-09-30):**
> - All 34 automated items **Passed on Android**, as on iOS. BUG-PHR-001 stays not filed (owner, 2026-09-26) — no
>   Android mark needed.
> - Harness fixes over the Android runs: a grid photo without description or tag is found by its size (it has no
>   label); the metadata form scrolls with the finger inside its inset scroll view (x = 60 px; at x = 21 the drag missed
>   it — TC-PHR-002); the gallery cell is tapped only once the system picker's grid stops moving (its "… will only have
>   access to the photos you select" banner lands late and pushes the grid down — TC-PHR-001).
> - **Merged:** run 5 (6 tests) and a TC-PHR-001 rerun. Run 5's own TC-PHR-001 is left out: the Mac (on battery) went to
>   idle sleep for 13.8 min a minute into the run — the gesture in flight hung (Appium 500 after 830 s) and the job's
>   API cleanup hit a dead connection (the job was removed by hand right after, GET → 404). Environment, not the app:
>   `run.sh` now keeps the Mac awake (`caffeinate -i`). Run 4 (7 Blocked at the UI login) is left out too: after the
>   Mac changed networks the emulator kept the old DNS server; `run.sh` now refuses to start when the device cannot
>   resolve the API host.

> **Step 5 — offline (2026-10-01):** Step 5 (2026-10-01) added this module's `android-stage` checks — offline / slow network, Android only (owner, android-plan §2.5); test cases `../android/*-test-cases.md` (validated by the owner), tests `automation/mobile/tests/android/test_offline_*.py`, recon `qa/shared/recon-2026-10-01-android-offline.md`. CHK-PHR-045…049 **Passed** (TC-PHR-008, -009). **CHK-PHR-050 Failed** (TC-PHR-010): a synced photo deleted offline is still on the server after the connection returns AND after the submission (30 s polled; runs 0910-r1/-r2, offline-all-r1) — the owner asked to check this (D-OFF-3, «перевір»); evidence added to [BUG-PHR-001](../bugs/BUG-PHR-001.md) — **file? the owner decides**.
