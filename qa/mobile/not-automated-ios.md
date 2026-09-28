# Checks without an automated test — iOS, and why

> The 183 checklist checks that have no automated test after the final iOS run (step 6c, 2026-09-28).
> Every reason comes from the module's automation plan, its test cases or an owner decision, and the Source
> column names which. Nothing here is a verdict: these checks stay **not run** in the traceability matrix.
> The summary page (`automation/tools/build_summary.py`) reads this file. A check with no automated test and no row
> here is shown as "reason missing". Ranges like `CHK-AUTH-081…-086` include both ends.

## Kinds

| Kind | Title | What it means |
|---|---|---|
| android-stage | Offline — waits for the Android stage | A test cannot switch the iOS simulator's network off; the Android emulator's can, so these run in step 7 |
| owner-manual | Kept manual by the owner | The owner ruled these stay manual checks; most were run by hand on iOS, a real device or production (the reason says which) |
| deferred | Deferred — can be automated later | Right as worded and automatable; left out of the first pass by scope (Auth was a narrow pilot) |
| person | A person's check | A judgement no assertion can make, or something the accessibility tree does not show: design, motion, an icon, a 0.3-second banner |
| by-design | The app works differently — accepted | The checklist describes a control or a flow the app does not have; the owner accepted the app's behaviour |
| simulator | Beyond the simulator or outside the app | Needs hardware the simulator lacks (camera, a failed location fix) or the system's own screens (share sheet, other apps) |
| cannot-cause | Failures a test cannot cause | A save, upload or navigation failure needs the app's storage or network broken mid-action |
| not-observable | Not observable from the app on DEV | The outcome happens where neither the app nor the DEV API shows it: e-mail to a facilitator, a server schedule, a hard-coded DEV code |
| unclear | Requirement unclear or a placeholder | The item names no checkable outcome ("if allowed by business logic") |
| load | Load on DEV excluded | Load and performance are not run against the shared DEV server (decision 2026-09-23) |
| covered | Covered by another check | Proved by a neighbouring check |

## Checks

| Checks | Kind | Why | Source |
|---|---|---|---|
| CHK-SPL-004 | by-design | The logo is animated in the app and in Figma, not static | D-SPL-1 (owner, 2026-09-23) |
| CHK-SPL-006 | person | The status bar is drawn by iOS outside the app's tree — a visual check | 01 plan |
| CHK-SPL-010 | not-observable | Loading configuration and metadata shows nothing on screen; no oracle | 01 plan |
| CHK-SPL-013 | person | "Without visible delays or artifacts" is subjective | 01 plan |
| CHK-SPL-014 | person | Manual by the owner's decision; the debug build starts in about 9 s, reported as information only | owner, 2026-09-24 |
| CHK-SPL-015 | android-stage | Slow start-up needs network throttling; the iOS simulator has none | 01 plan |
| CHK-AUTH-006 | person | Layout across screen sizes and orientations — visual; tablets out of scope | 02 plan |
| CHK-AUTH-011, -012 | deferred | Rapid double taps on Sign up / Login — deferred in the narrow Auth pilot | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-013, -014 | person | "Without visual glitches or delays" is subjective; the navigation itself is proved by TC-AUTH-002 | 02 plan |
| CHK-AUTH-015 | cannot-cause | A failed navigation cannot be induced without changing the app | 02 plan |
| CHK-AUTH-025 | person | Layout across screen sizes and orientations — visual | 02 plan |
| CHK-AUTH-036…-040 | deferred | Country selector, its search, prefix and per-country phone format — deferred in the Auth pilot | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-042 | deferred | Numeric keyboard on the phone field — deferred in the Auth pilot | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-048 | deferred | One notification channel at a time — the radio state was not yet seen in the tree | 02 plan |
| CHK-AUTH-051, -052 | deferred | The channel stays selected; the channel is sent in the request (read back through the API) — deferred in the Auth pilot | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-054, -057 | deferred | The SMS Terms close icon has no label (a testability defect) — deferred | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-058 | deferred | The SMS consent checkbox after returning from Terms — deferred in the Auth pilot | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-059 | unclear | "Can be deselected if allowed by business logic" — no rule to check against | 02 plan |
| CHK-AUTH-065 | deferred | Registration with the SMS channel — SMS goes to fictional 555-01xx numbers only; deferred | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-067 | deferred | Rapid taps on Continue must not create two users (count through the API) — deferred | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-070 | android-stage | A registration failure on network loss — no network control on the iOS simulator | 02 plan |
| CHK-AUTH-076 | deferred | Four OTP boxes are drawn; the tree holds one hidden field — deferred | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-079 | deferred | "Request a new code" after the countdown needs a 60-second wait — deferred | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-081…-086 | deferred | OTP focus movement, digits only, at most four, paste, numeric keyboard — deferred in the Auth pilot | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-087 | covered | The app submits after the fourth digit; there is no Verify tap — proved by CHK-AUTH-088 | D-5, 02 plan |
| CHK-AUTH-092 | not-observable | Duplicate Verify taps cannot happen with auto-submit | 02 plan |
| CHK-AUTH-093 | not-observable | The OTP is hard-coded on DEV, so invalidating the previous code cannot be seen | 02 plan |
| CHK-AUTH-094, -095 | deferred | A new code and the restarted countdown — needs the countdown wait; delivery not observable on DEV | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-098…-100 | android-stage | Slow network and connectivity failures during OTP — no network control on the iOS simulator | 02 plan |
| CHK-AUTH-101 | deferred | The two-minute OTP lockout needs a dedicated account run serially — deferred | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-102 | unclear | OTP state after reopening "according to business logic" — expected behaviour not defined | 02 plan |
| CHK-AUTH-112 | by-design | The app shows no "Format is incorrect." message | D-12 (owner, 2026-09-23) |
| CHK-AUTH-113 | person | Validation styling (colour, border) — a visual judgement | 02 plan |
| CHK-AUTH-120 | deferred | Rapid taps on Continue at login — deferred in the Auth pilot | 02 plan (owner, 2026-09-23) |
| CHK-AUTH-124 | android-stage | A login failure on network loss — no network control on the iOS simulator | 02 plan |
| CHK-ORDL-014 | by-design | There are no New / In Progress / Completed filter buttons, in the app or in Figma | D-ORDL-1 (accepted) |
| CHK-ORDL-021 | by-design | There is no "Unsubmitted" label on the card | D-ORDL-5 (accepted) |
| CHK-ORDL-023 | person | Badges readable across screen sizes — visual, one phone configuration by decision | 03 plan |
| CHK-ORDL-025 | deferred | A single navigation per tap on a card — deferred, as the rapid-tap items in Auth | 03 plan |
| CHK-ORDL-030 | owner-manual | Jobs assigned through an SMS or e-mail link — verified by the owner on production; on DEV without COPS the link attaches nothing | owner, 2026-09-24 |
| CHK-ORDL-031…-035 | android-stage | Cached list offline, the offline state, load errors, retry, recovery — no network control on the iOS simulator | 03 plan |
| CHK-ORDL-041 | by-design | No month and year above the week, in the app or in Figma | D-ORDL-6 (accepted) |
| CHK-ORDL-045, -046 | deferred | The selected day and the days with jobs are shown by colour and an 8-px dot — a pixel oracle is possible later | 03 plan |
| CHK-ORDL-059 | deferred | Rapid taps on a card — deferred | 03 plan |
| CHK-ORDL-064, -065 | android-stage | The calendar offline — Android stage | 03 plan |
| CHK-ORDL-066 | person | No flicker when switching weeks — subjective | 03 plan |
| CHK-ORDL-067 | load | Many jobs in the calendar — load on DEV excluded | decision 2026-09-23 |
| CHK-ORDD-006 | person | The "Updated" banner lives about 0.3 s on the details — seen by eye, too short for a test | 04 test cases (after recon 5) |
| CHK-ORDD-009 | person | Dividers between sections — visual (Figma) | 04 plan |
| CHK-ORDD-023, -025, -026, -029 | by-design | The app has no own "Enable Location Services" prompt: it shows the system prompt, and Cancel ends the check-in | D-ORDD-9 (accepted) |
| CHK-ORDD-036…-042 | simulator | Manual location entry appears only when no location fix comes in 15 s; the simulator always reports a location. Verified by the owner on a real device | 05 test cases |
| CHK-ORDD-043 | by-design | A refused permission cancels the check-in until the setting changes | D-ORDD-9 (accepted) |
| CHK-ORDD-048…-050 | owner-manual | Details offline, check-in offline, slow network — verified by the owner on iOS, works | Q-ORDD-4 (owner, 2026-09-24) |
| CHK-ORDD-064, -065 | deferred | Scrolling a multi-page document, zoom — gestures plus pixel comparison, after the first pass | 04 plan |
| CHK-ORDD-069 | simulator | Saving a document goes through the system share sheet, outside the app | D-ORDD-6 |
| CHK-ORDD-070 | by-design | No success toast: the system share sheet saves | D-ORDD-6 (accepted 2026-09-24) |
| CHK-ORDD-071 | simulator | PDF opens in the app (TC-ORDD-007); DOC and XLS are handed to another app, and the simulator has none | D-ORDD-5 (accepted) |
| CHK-ORDD-072 | unclear | A placeholder item; the app says "Could not open document" | 04 plan |
| CHK-ORDD-077, -078 | deferred | Pinch-to-zoom and panning a photo — gestures, after the first pass | 04 plan |
| CHK-ORDD-081…-085 | owner-manual | Downloaded files offline, failures to load attachments, retry — verified by the owner on iOS, works | Q-ORDD-4 (owner, 2026-09-24) |
| CHK-ORDD-086 | person | No flicker between Documents and Photos — subjective | 04 plan |
| CHK-ORDD-088 | load | Many attachments — load on DEV excluded | decision 2026-09-23 |
| CHK-ORDD-089 | owner-manual | Attachment caching offline — verified by the owner on iOS | Q-ORDD-4 (owner, 2026-09-24) |
| CHK-CHIO-013, -019 | simulator | Check-in / check-out flagged Manual without GPS — manual entry is unreachable on the simulator; verified by the owner on a real device | 05 test cases |
| CHK-CHIO-015, -021 | not-observable | The e-mail to the Project Facilitator after check-in / check-out is not visible to the app | Q-CHIO-2 |
| CHK-CHIO-024…-026 | simulator | Manual check-in allowed and flagged — unreachable on the simulator; verified by the owner on a real device | 05 test cases, D-CHIO-5 |
| CHK-CHIO-027…-032 | owner-manual | Check-in / check-out errors on network or server faults and retry — kept manual | Q-CHIO-3 (owner, 2026-09-24) |
| CHK-CHIO-033, -034 | not-observable | `GET /job/{id}` does not return the user id of the record, so "the correct User ID" cannot be proved | 05 test cases |
| CHK-CHIO-038 | owner-manual | Responsive during slow GPS or network — kept manual | Q-CHIO-3 (owner, 2026-09-24) |
| CHK-ORDP-009 | by-design | There is no completion indicator on a deliverable | D-ORDP-1 (accepted) |
| CHK-ORDP-029…-037 | owner-manual | Submit disabled offline, the offline message, local progress, "Connection restored" — verified by the owner on iOS | Q-ORDP-2 (owner, 2026-09-24) |
| CHK-ORDP-040 | owner-manual | Stored deliverables retried when back online — verified by the owner on iOS | Q-ORDP-2 (owner, 2026-09-24) |
| CHK-DLV-003 | person | The checkmark icon is not in the accessibility tree; it is seen on the screenshot | D-DLV-6 |
| CHK-DLV-023…-026 | android-stage | Submission offline, the offline message, local storage, submission when back online | Q-DLV-1 |
| CHK-SRV-018 | by-design | There is no completion mark on the Survey deliverable | D-SRV-8 = D-ORDP-1 |
| CHK-SRV-023…-027 | android-stage | The survey offline and its sync — no network control on the iOS simulator | 08 plan §7.5 |
| CHK-SRV-028…-032 | owner-manual | Local save errors and failed photo uploads cannot be caused from a test; verified by the owner by hand on iOS | Q-SRV-3 |
| CHK-PHR-010 | simulator | The simulator has no camera; the owner checked the camera by hand | Q-PHR-2 (owner, 2026-09-25) |
| CHK-PHR-016…-024 | person | Crop and markup: the editor's canvas, palette and buttons are not in the accessibility tree (TD-PHOTO-001); a test only opens the editor. The owner checked them by hand | Q-PHR-3 (owner, 2026-09-25) |
| CHK-PHR-045…-050 | android-stage | Photos offline, local storage, upload and deletion when back online | Q-PHR-4 (owner, 2026-09-25) |
| CHK-PHR-051…-054 | cannot-cause | Upload, edit and save failures and retry — skipped with a comment | Q-PHR-4 (owner, 2026-09-25) |
| CHK-NOTE-041 | by-design | There is no "required notes" setting | Q-NOTE-2, D-NOTE-3 |
| CHK-NOTE-043…-047 | android-stage | Notes offline, local storage and sync when back online | Q-NOTE-1 (owner, 2026-09-25) |
| CHK-NOTE-048…-052 | cannot-cause | Save and delete failures and retry — skipped with a comment | Q-NOTE-1 (owner, 2026-09-25) |
| CHK-NOTIF-010 | person | The icon by notification type is not in the accessibility tree; it is seen on the screenshot | Q-NOTIF-4 |
| CHK-NOTIF-017, -018 | not-observable | "Job starts today" comes from a server schedule at 8 AM; a test cannot trigger it | Q-NOTIF-1 |
| CHK-NOTIF-029, -030 | android-stage | Cached notifications offline | Q-NOTIF-2 |
| CHK-PRF-015 | by-design | The email is not editable on Edit profile | D-PRF-1 |
| CHK-PRF-030 | android-stage | Log out offline | Q-PRF-4 |
