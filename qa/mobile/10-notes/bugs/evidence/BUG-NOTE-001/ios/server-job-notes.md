# BUG-NOTE-001 — what the server held (recon 10, 2026-09-25, DEV)

Job `QA-AUTO-R10-0925-2059-N1` (In progress). `GET /job/{id}` → `notes` after each step in the app:

| Step in the app | Notes in the app (newest first) | `notes` on the server |
|---|---|---|
| 1. Add "QA-AUTO note one" | note one | 1 — `{name: '', text: 'QA-AUTO note one'}` |
| 2. Add "QA-AUTO note two" | note two, note one | **1 — note two only (note one gone from the server)** |
| 3. Edit note two → "QA-AUTO note two edited" | note two edited, note one | **1 — still "QA-AUTO note two" (the edit did not arrive)** |
| 4. Delete note one (⋮ → Delete) | note two edited | 1 — "QA-AUTO note two" |
| 5. **Delete note two (Edit note → Delete note)** | **none — "No notes have been added yet"** (screenshot) | **1 — "QA-AUTO note two"** |

- A note on the server has no id (`GetJobNoteDto`: `name`, `text`).
- `GET /job/{id}/notes` returns 404 "Cannot GET /job/{id}/notes".
- The API contract (`docs/api/openapi.json`) has no notes endpoint at all, only `POST /job/{id}/response {notes}`.
- The app calls (code, read-only, `notes_api_service.dart`):
  - `GET /job/{id}/notes` to fetch;
  - `POST /job/{id}/response {"notes": [<the new note>]}` to create;
  - `PATCH /job/{id}/notes/{noteId}` to edit;
  - `DELETE /job/{id}/notes/{noteId}` to delete.
- Submitting deliverables sends the notes left on the device, and nothing when there are none
  (`job_detail_repository_impl.dart`, `_fetchNotesPayload`; `notes.isNotEmpty`).
