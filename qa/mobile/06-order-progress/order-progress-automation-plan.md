# Automation plan — Order progress / In progress (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/06-order-progress/order-progress-checklist.md`
> (42 items, `CHK-ORDP-001…042`, imported 2026-09-24). Date: 2026-09-24. Owner: mykola.zhuchenko.
> **Status: draft — waits for the owner (Q-ORDP-1…3 in [order-progress-questions.md](order-progress-questions.md)).**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| Feature code | `ORDP` |
| Scope decision (proposed) | the In progress screen itself; the submission flow → module 07 (Q-ORDP-1) |
| Oracle model | accepted production baseline; SRS §3.1.3.4; Figma `Job details_In progress` 2451:82704, `…_Scroll` 2451:83008, `…_Poor connection` 2451:82898; D-ORDD / D-CHIO accepted |

## Step 0–2 — Input, readiness, approach

**Input: Medium.** The In progress details were seen in recon 6c (status, timer, the three deliverable rows, the info
block). Unknown: the Survey / Photo report / Notes screens (their anchors — modules 08–10), the timer after the app is
backgrounded. **Readiness: Ready with conditions** (Q-ORDP-1…3). **Approach:** jobs created through `POST /job`
directly In progress (no check-in needed for the screen); every assertion through the UI; nothing is filled or submitted.

## Step 3–4 — Candidate matrix (42 items)

| CHK ID | Scenario (short) | Level | Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|
| CHK-ORDP-001 | "In progress" badge | E2E UI + API setup | Good Candidate | P0 | TC-ORDP-001 | recon 6c |
| CHK-ORDP-002 | timer HH:MM:SS, runs | E2E UI + API setup | Good Candidate | P1 | TC-ORDP-001 | two reads a few seconds apart; digits joined from the tree |
| CHK-ORDP-003 | timer continues after background | E2E UI + API setup | Good Candidate | P2 | TC-ORDP-002 | background the app 10 s (`AppControl.background`) |
| CHK-ORDP-004, -005 | three rows with icon and chevron | E2E UI + API setup | Good Candidate | P1 | TC-ORDP-001 | names from the tree; icons / chevrons are images (presence) |
| CHK-ORDP-006…008 | rows open Survey / Photo report / Notes | E2E UI + API setup | Good Candidate | P1 | TC-ORDP-003 | anchors from recon 7 |
| CHK-ORDP-009 | completion indicator | — | Skipped (D-ORDP-1) | – | — | placeholder item; the app has none |
| CHK-ORDP-010 | scope text multi-line | E2E UI + API setup | Good Candidate | P2 | TC-ORDP-001 | as TC-ORDD-001 |
| CHK-ORDP-011 | Location section | E2E UI + API setup | Good Candidate | P2 | TC-ORDP-001 | one address line (D-ORDP-2) |
| CHK-ORDP-012, -013 | On map shown / opens the location | E2E UI + API setup | Good Candidate | P3 | TC-ORDP-004 | in-app browser (D-ORDP-3), as TC-ORDD-003 |
| CHK-ORDP-014 | date & time | E2E UI + API setup | Good Candidate | P2 | TC-ORDP-001 | |
| CHK-ORDP-015 | PF name + phone | E2E UI + API setup | Good Candidate | P2 | TC-ORDP-001 | PF in the seed |
| CHK-ORDP-016 | PF phone → dialer | E2E UI + API setup | Needs Device | P3 | TC-ORDP-004 | iOS: Blocked — simulator limitation (as CHK-ORDD-017) |
| CHK-ORDP-017 | Attachments row opens Attachments | E2E UI + API setup | Good Candidate | P2 | TC-ORDP-004 | |
| CHK-ORDP-018 | primary action "Submit deliverables" | E2E UI + API setup | Good Candidate | P1 | TC-ORDP-001 | |
| CHK-ORDP-019…028 | submission flow | E2E UI + API | → module 07 | P1 | — | Q-ORDP-1 |
| CHK-ORDP-029…037, -040 | offline, "Connection restored" | Manual | Q-ORDP-2 | P3 | — | no network control on the iOS simulator |
| CHK-ORDP-038, -039, -041 | submission errors, retry, locked after submit | E2E UI + API | → module 07 | P2 | — | Q-ORDP-1 |
| CHK-ORDP-042 | the primary action matches the status after returning | E2E UI + API setup | Good Candidate | P2 | TC-ORDP-005 | In progress → Submit deliverables; Submitted → Check out, after back and reopen |

## Step 5b — Selected (draft)

**~18 of 42 → 5 TCs** (TC-ORDP-001…005); 13 → module 07; 10 → manual (Q-ORDP-2); 1 skipped. Final after recon 7.

## Step 9 — Test data

2 jobs per run: `progress` (In progress, with description and PF), `done` (Submitted) — `POST /job`, deleted in `finally`.
Nothing is filled, uploaded or submitted.

## Step 16 — Recommendation

Owner's word on Q-ORDP-1…3 → recon 7 → test cases → maps / tests.
