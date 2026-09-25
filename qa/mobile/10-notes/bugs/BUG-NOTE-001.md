# BUG-NOTE-001 — Editing or deleting a note never reaches the server; each new note replaces the job's notes there

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). **Draft for the owner's validation.** Found in
> recon 10 (2026-09-25). Tracker: not configured, nothing sent anywhere. Sibling: [BUG-PHR-001](../../09-photo-report/bugs/BUG-PHR-001.md).

## Summary

The Notes screen shows the technician's notes correctly, but the job on the server does not follow it:
- it holds only the last note created;
- it keeps that note's old text after an edit;
- it keeps it after the note is deleted.

## Layer

- [ ] App
- [ ] Backend / API
- [x] Unclear — an app ↔ API contract mismatch.
  - The app edits and deletes notes through `PATCH` / `DELETE /job/{id}/notes/{noteId}`, and fetches them through
    `GET /job/{id}/notes` (`notes_api_service.dart`).
  - None of these exists in the API (`docs/api/openapi.json`); `GET` returns 404.
  - Notes on the server carry no id to address them by.
  - Creating a note posts `{"notes": [<only the new note>]}` to `POST /job/{id}/response`, and the server keeps only that one.

## Severity / Priority

- **Severity:** S2 (major) — **branch fired:** #2.
  - Edits and deletions of notes are silently lost on the server, and the technician cannot tell.
  - If every note is deleted, the submission sends no notes (`notes.isNotEmpty`), so a deleted note stays on the submitted
    job. This point is to be confirmed on the server in module 07.
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
| Permissions state | — |

## Preconditions

- Signed in as a technician.
- A job In progress (in the recon: created through `POST /job`, job `QA-AUTO-R10-0925-2059-N1`).

## Steps to reproduce

1. Open the job and tap Notes.
2. Tap Add note, type "Note one", tap Save.
3. Tap Add note, type "Note two", tap Save.
4. On "Note two", tap ⋮, then Edit; change the text to "Note two edited"; tap Save.
5. On "Note two edited", tap ⋮, then Edit, then Delete note, then Delete.
6. On "Note one", tap ⋮, then Delete, then Delete.
7. Read the job on the server (`GET /job/{id}` → `notes`) after each step.

## Actual result

- After step 3 the server holds only "Note two".
- After step 4 the server still holds "Note two", not the edited text.
- After step 6 the app shows "No notes have been added yet" // [screenshot](evidence/BUG-NOTE-001/app-notes-empty.png), and the
  server still holds "Note two" // [server log](evidence/BUG-NOTE-001/server-job-notes.md).

## Expected result

The notes on the job match what the technician keeps:
- FR-NOT-01 (all notes of the order);
- FR-NOT-06 (edits kept);
- FR-NOT-08: "Confirmed deletion shall permanently remove the note from the order";
- FR-NOT-10 (changes sync automatically).

## Frequency

Every edit and delete in recon 10 (2 of 2 deletes, 1 of 1 edit); every second note replaced the first (2 of 2 jobs).

## Workaround

None in the app. The submission re-sends the notes left on the device, which repairs the list only when at least one note
is left.

## Related

- CHK-NOTE-020 (associated with the order), CHK-NOTE-028 (edit updates the note), CHK-NOTE-037 (Delete removes it from the
  order), CHK-NOTE-047 (a synced delete is synced).
- SRS FR-NOT-01, -06, -08, -10.
- Sibling: BUG-PHR-001 (photos: the same `POST /job/{id}/response` replace-with-one and local-only delete).
- Module 07: confirm what a submission stores.
