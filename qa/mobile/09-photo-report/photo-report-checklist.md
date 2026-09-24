# QA Checklist: Photo report screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-24 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Photo report screen / Empty & Populated States

1. [CHK-PHR-001] Check that the Photo Report screen opens from the In Progress Order screen when the user taps the Photo report deliverable.
2. [CHK-PHR-002] Check that the Photo Report screen displays the title “Photo report” and a back navigation control.
3. [CHK-PHR-003] Check that the empty state is displayed when no photos are added, including placeholder illustration and informational text.
4. [CHK-PHR-004] Check that the empty state displays the primary action button “Add photo”.
5. [CHK-PHR-005] Check that tapping “Add photo” from the empty state initiates the Add photo flow.
6. [CHK-PHR-006] Check that when photos exist, the Photo Report screen displays a grid of photo thumbnails.
7. [CHK-PHR-007] Check that each photo thumbnail displays a preview image and a short description snippet if provided.
8. [CHK-PHR-008] Check that the Add photo button is available in the populated state and remains accessible.

## Photo report screen / Add Photo Entry Point (Camera / Gallery)

1. [CHK-PHR-009] Check that tapping Add photo opens a source selection bottom sheet with Camera and Gallery options.
2. [CHK-PHR-010] Check that selecting Camera opens the device camera and allows capturing a new photo.
3. [CHK-PHR-011] Check that selecting Gallery opens the device gallery and allows selecting an existing photo.
4. [CHK-PHR-012] Check that the Add/Edit Photo screen opens after a photo is captured or selected.

## Photo report screen / Add / Edit Photo Screen

1. [CHK-PHR-013] Check that the Add/Edit Photo screen displays a contextual title (“Add photo” or “Edit photo”).
2. [CHK-PHR-014] Check that the selected photo is displayed in a full-width preview area.
3. [CHK-PHR-015] Check that the screen provides back navigation to discard or confirm changes according to Save logic.

## Photo report screen / Photo Editing — Crop Tool

1. [CHK-PHR-016] Check that the Crop tool allows adjusting a crop frame over the photo.
2. [CHK-PHR-017] Check that a grid overlay is displayed during cropping for alignment assistance.
3. [CHK-PHR-018] Check that confirming crop applies the crop to the photo preview.
4. [CHK-PHR-019] Check that cancelling crop restores the photo to its previous state.

## Photo report screen / Photo Editing — Markup Tool

1. [CHK-PHR-020] Check that the Markup tool allows freehand drawing on top of the photo.
2. [CHK-PHR-021] Check that the Markup tool provides a selectable color palette.
3. [CHK-PHR-022] Check that the Markup tool supports adjustable stroke size.
4. [CHK-PHR-023] Check that undo removes the last markup action.
5. [CHK-PHR-024] Check that redo restores the previously undone markup action.

## Photo report screen / Photo Metadata — Description

1. [CHK-PHR-025] Check that the photo description field allows multi-line text input.
2. [CHK-PHR-026] Check that the description field enforces a maximum length of 500 characters.
3. [CHK-PHR-027] Check that the character counter updates correctly as text is entered.
4. [CHK-PHR-028] Check that the description field is optional and does not block saving when empty.

## Photo report screen / Photo Metadata — Tags

1. [CHK-PHR-029] Check that the Tags section displays multi-select tag chips sourced from the Admin Panel.
2. [CHK-PHR-030] Check that the user can select one or more tags for a photo.
3. [CHK-PHR-031] Check that selecting a tag visually marks it as selected.
4. [CHK-PHR-032] Check that deselecting a tag removes it from the photo metadata.

## Photo report screen / Save Behavior (Add / Edit Photo)

1. [CHK-PHR-033] Check that tapping Save persists the photo, edits, description, and tags locally.
2. [CHK-PHR-034] Check that tapping Save returns the user to the Photo Report screen.
3. [CHK-PHR-035] Check that the newly added or edited photo appears immediately in the Photo Report grid.
4. [CHK-PHR-036] Check that previously saved data is preloaded when editing an existing photo.
5. [CHK-PHR-037] Check that navigating back without saving discards unsaved changes to the photo.
6. [CHK-PHR-038] Check that an optional warning is displayed before discarding unsaved changes if implemented.

## Photo report screen / Delete Photo Pop-up

1. [CHK-PHR-039] Check that tapping the delete icon on a photo opens the Delete Photo confirmation pop-up.
2. [CHK-PHR-040] Check that the Delete Photo pop-up displays the title “Delete photo” and destructive warning message.
3. [CHK-PHR-041] Check that the pop-up displays Cancel and Delete actions.
4. [CHK-PHR-042] Check that tapping Cancel closes the pop-up and preserves the photo and metadata.
5. [CHK-PHR-043] Check that tapping Delete permanently removes the photo and all associated metadata.
6. [CHK-PHR-044] Check that the Photo Report grid updates immediately after photo deletion.

## Photo report screen / Offline Behavior & Sync

1. [CHK-PHR-045] Check that photos can be added, edited, tagged, and deleted while offline.
2. [CHK-PHR-046] Check that photos and metadata are stored locally when added offline.
3. [CHK-PHR-047] Check that photos are automatically uploaded when connectivity is restored.
4. [CHK-PHR-048] Check that failed uploads are retried automatically without user data loss.
5. [CHK-PHR-049] Check that deleting an unsynced photo removes it from local storage immediately.
6. [CHK-PHR-050] Check that deleting a synced photo queues the deletion and syncs it when online.

## Photo report screen / Error Handling & Data Integrity

1. [CHK-PHR-051] Check that an error message is displayed if photo upload fails.
2. [CHK-PHR-052] Check that the original photo is preserved if photo editing fails.
3. [CHK-PHR-053] Check that photo edits and metadata are retained locally if saving fails.
4. [CHK-PHR-054] Check that the user can retry saving or syncing after an error.
