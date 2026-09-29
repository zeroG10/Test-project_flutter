# BUG-PHR-001 — what the server held (recon 9, 2026-09-25, DEV)

Job `QA-AUTO-R9-0925-0906-P1` (In progress). `GET /job/{id}` → `photos` after each step in the app:

| Step in the app | Photos in the app | `photos` on the server |
|---|---|---|
| 1. Add photo A, description "QA-AUTO photo one" | A | 1 — `0eee839e…` note "QA-AUTO photo one" |
| 2. Edit A: description "…-edited", tags Undamaged, tag1 | A | 1 — `c204a958…` (new file) note "QA-AUTO photo one-edited", 2 tags |
| 3. Add photo B, no description | A, B | **1 — `0e6e77b0…` (B only; A gone from the server)** |
| 4. Delete A (dialog → Delete) | B | 1 — `0e6e77b0…` (B) |
| 5. **Delete B (dialog → Delete)** | **none — "No photos have been added yet"** (screenshot) | **1 — `0e6e77b0…` (B, deleted in the app)** |
| 6. Add photo C "QA-AUTO keep" | C | 1 — `fe454f35…` (C only) |

The app's calls (code, read-only): a save uploads the file and links it with `POST /job/{id}/response {"photoIds": [<new id>]}`
(`photo_report_api_service.dart`); a delete only removes the row from the device database (`photo_report_repository_impl.dart`,
`deletePhoto`). Submitting deliverables sends `photoIds` of the photos left on the device, and nothing when there are none
(`job_detail_repository_impl.dart`: `photoIds: photoIds.isEmpty ? null : photoIds`).
