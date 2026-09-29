# BUG-PHR-001 — A photo deleted from the Photo report stays on the job on the server

> **Status: NOT FILED — owner's decision 2026-09-26:** deleting works in the app on a real device, possibly applied through the
> job update at submission; not a bug for now. The final server state is checked after submission in module 07.
>
> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Draft for the owner's validation (Q-PHR-1,
> owner 2026-09-25: «перевіриш, я провалідую»). Found in recon 9. Tracker: not configured, nothing sent anywhere.

## Summary

When a technician deletes a photo from the Photo report, the photo disappears from the app, but the job on the server
still holds it. The deletion never reaches the server.

## Layer

- [x] App — by code reading, a delete only removes the photo from the device database
  (`lib/features/photo_report/data/photo_report_repository_impl.dart`, `deletePhoto`). No call tells the server. The photo was
  already linked to the job when it was saved (`POST /job/{id}/response {"photoIds": [...]}`,
  `photo_report_api_service.dart`).
- [ ] Backend / API
- [ ] Unclear

## Severity / Priority

- **Severity:** S2 (major) — **branch fired:** #2.
  - The technician cannot remove a wrong photo from the job: the server keeps it, with no workaround in the app.
  - If every photo is deleted, the submission sends no photo list at all (`photoIds: … isEmpty ? null`), so the deleted
    photo stays on the submitted job. This last point is to be confirmed on the server in module 07 Submit deliverables.
- **Priority:** *proposal* P2 — owner / PM decide.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on iOS |
| OS version | iOS 26.5 |
| Device | iPhone 17 |
| Form factor | phone |
| Device type | simulator |
| App version | `[DEV] CT Mobile` 1.1.1 (178), `development` @ 85a84f3 |
| Build type | debug (flavor `development`, `CLIENT_BUILD=true`) |
| Install method | sideload (simulator build) |
| Network | Wi-Fi (host network), DEV API |
| Locale | en |
| Orientation | portrait |
| User role | Field Technician (signed in) |
| Feature flags | — |
| Permissions state | photos = the system picker (no prompt) |

## Preconditions

- Signed in as a technician.
- A job In progress (in the recon: created through `POST /job`, job `QA-AUTO-R9-0925-0906-P1`).
- At least one photo in the device gallery.

## Steps to reproduce

1. Open the job and tap Photo report.
2. Tap Add photo, choose Gallery and pick a photo.
3. Tap ✓ in the editor, then tap Save.
4. On the photo, tap the delete icon.
5. In "Delete photo", tap Delete.
6. Read the job on the server (`GET /job/{id}` → `photos`).

## Actual result

- The app shows "No photos have been added yet" // [screenshot](evidence/BUG-PHR-001/ios/app-photo-report-empty.png).
- The job on the server still has the deleted photo in `photos` (id, file location)
  // [server log](evidence/BUG-PHR-001/ios/server-job-photos.md), step 5.

## Expected result

A deleted photo is removed from the job everywhere and is not available for submission:
- SRS FR-DEL-PH-04: "Deleted photos shall no longer be available for editing or submission".
- FR-DEL-PH-08: "If the photo has already been synced, deletion shall be queued and synced".

## Frequency

2 of 2 deletions of a photo that the server held (recon 9, steps 4–5).

## Workaround

None in the app. Adding another photo replaces the server's list (see Notes), which does not help when the technician
wants no photo, or wants to keep the others.

## Notes (related observation, same mechanism)

Each save links **only the new photo** (`photoIds: [<new id>]`), and the server then holds only the last saved photo:
with two photos in the app, the server had one (step 3). The submission re-sends every photo left on the device, which
restores the list — if at least one is left. The owner may split this into its own report.

## Related

- CHK-PHR-043 (Delete removes the photo and all metadata), CHK-PHR-050 (a synced delete is queued and synced).
- SRS FR-DEL-PH-04, FR-DEL-PH-08, FR-PH-05.
- Q-PHR-1.
- Module 07: confirm what a submission stores.
