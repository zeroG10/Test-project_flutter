# BUG-NOTE-002 — A note created and then edited offline is not synced when the connection returns; it waits for the submission

> **Status: NOT FILED — owner's decision 2026-10-01:** «ні не заводь». The Failed row CHK-NOTE-045 (TC-NOTE-009)
> stays red with this decision as its explanation.

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md).
> Found by the Android offline test TC-NOTE-009 (step 5, 2026-10-01). Tracker: not configured, nothing sent anywhere.
> Siblings: [BUG-NOTE-001](BUG-NOTE-001.md) (edits / deletions of synced notes), [BUG-PHR-001](../../09-photo-report/bugs/BUG-PHR-001.md).

## Summary

A note created while the device is offline reaches the server within seconds once the connection returns — unless it was
also edited before that: then nothing is sent when the connection returns, and the note reaches the server only with the
job's submission.

## Layer

- [x] App (UI) — on reconnect the app's sync runs ("connection restored — starting sync…") but sends no note request at
  all ("ops queue — nothing to sync" and no notes call in the app's log, run `offline-note009-logs`); the edited unsynced
  note is evidently not left in the app's pending-sync state. Code not examined further (read-only).
- [ ] Backend / API
- [ ] Unclear

## Severity / Priority

- **Severity:** S3 (minor) — **branch fired:** #3 — the note is not lost (it arrives with the submission, checked), but
  the automatic sync the SRS requires does not happen; until the submission the office sees no note.
- **Priority:** *proposal* P3 — owner / PM decide.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on Android |
| Platforms checked | Android ✓ reproduced · iOS — not checked (the iOS simulator's network cannot be switched off; the code path is shared) |
| OS version | Android 16 (API 36) |
| Device | Pixel 7 (`Pixel_7_API_36`), emulator (Google APIs arm64) |
| App version | `[DEV] CT Mobile` 1.1.1 (178), `development` @ 85a84f3, debug, `CLIENT_BUILD=true` |
| Network | emulator; Wi-Fi + mobile data switched off, then on |
| User role | Field Technician, signed in |

## Preconditions

- An In progress job assigned to the technician; its Notes screen has no notes yet.
- The device is online.

## Steps to reproduce

1. Open the job and its Notes.
2. Switch the device's network off (Wi-Fi and mobile data).
3. Add a note "A" and save it.
4. Open the note's menu → Edit, change the text to "A x", save.
5. Switch the network back on and wait 30 s.
6. Look at the job's notes on the server (`GET /job/{id}` → `notes`).
7. Complete the survey and submit the deliverables; look at the server again.

## Actual result

Step 6: the server has no note (30 s later; 20–30 s in four attempts). Step 7: after the submission the server has "A x".
A note added offline WITHOUT step 4 is on the server within ~25 s of step 5 (two attempts, recon 2026-10-01).

## Expected result

Offline note changes are sent to the server automatically when the connection returns (SRS FR-NOT-10, FR-NOT-ADD-09):
at step 6 the server has "A x".

## Frequency

- [x] Always — **4 of 4**: TC-NOTE-009 in runs `offline-080910-r1`, `offline-10-check`, `offline-note009-logs`,
  `offline-all-r1`; plus a manual reproduction with the recon script (2026-10-01, steps 1–7 above).

## Crash? ANR?

- [x] No crash

## Evidence

- Automated test: `automation/mobile/tests/android/test_offline_notes.py::test_notes_offline_sync_on_network_back`
  (TC-NOTE-009) — red at "expect exactly the synced note": the server's notes stay `[]` for 30 s. Allure results under
  `automation/mobile/results/android/2026-10-01-offline-*` (local only).
- App log on reconnect (run `offline-note009-logs`, local only — the full log holds a token): "GlobalSyncCoordinator:
  connection restored — starting sync…", "SyncService: ops queue — nothing to sync", no notes request.

## Workaround

None for the timing; the note arrives with the submission.

## Related

- SRS §3.1.3.4.6 FR-NOT-10: "Offline note changes shall sync automatically when connectivity is restored."; FR-NOT-ADD-09.
- Checklist: `CHK-NOTE-045` — "Check that locally stored note changes are synced automatically when connectivity is restored."
- Test case: `TC-NOTE-009` ([../android/notes-test-cases.md](../android/notes-test-cases.md)).
- Tracker: not filed.
