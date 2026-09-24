# Automation plan — Survey (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/08-survey/survey-checklist.md`
> (40 items, `CHK-SRV-001…040`, imported 2026-09-24) **plus 17 proposed items `CHK-SRV-041…057`** (logic, CR-2, empty
> survey, Number, "Other" — the checklist has none; owner's plan §7.5, Q-SRV-5). Date: 2026-09-24. Owner: mykola.zhuchenko.
> **Status: draft — waits for the owner (Q-SRV-1…5 in [survey-questions.md](survey-questions.md), logic tables in
> [survey-logic-tables.md](survey-logic-tables.md)).**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| Feature code | `SRV` |
| Scope decision (proposed) | the survey screen on an In progress job: every field type, validation, auto-save, logic (decision tables), CR-2 repeatable sections, photos, what reaches the server; offline → Android stage; the submission of deliverables → module 07 |
| Oracle model | accepted production baseline; SRS §3.1.3.4.2 (FR-SUR-01…15); PRD Repeatable Survey Sections (CR-2); the **logic tables approved by the owner** (not a second logic engine in the tests); the saved survey on the server (`GET /job/{id}` → `surveyResponse`) |

## Step 0–2 — Input, readiness, approach

**Input: Medium.**
- Known: SRS, PRD, the app code (read-only), and the definitions of the 10 chosen surveys (`survey-definitions/`).
- Unknown: the screen tree of the survey form (field types, the date / time pickers, the photo editor and metadata
  pages, the repeatable-section cards, the delete dialog), and the shape of `surveyResponse` on the server. Recon 8 settles
  these (Q-SRV-4).

**Readiness: Ready with conditions** (Q-SRV-1…5, recon 8).

**Approach:**
- One job per test, created **directly In progress** through `POST /job` with the survey under test. The timer is not
  asserted here, so no check-in is needed.
- The survey is filled through the UI, and every visible / hidden question is compared with a row of the logic tables.
- After Save, the stored response is read back through `GET /job/{id}`.
- Photos come from the simulator gallery (`simctl addmedia`).

## Step 3–4 — Candidate matrix

### Imported items (40)

| CHK ID | Scenario (short) | Level | Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|
| CHK-SRV-001 | required questions marked | E2E UI | Good Candidate | P2 | TC-SRV-004 | D-SRV-1: no marker, every question required — asserts the app (no marker, error after touch); Q-SRV-1 may turn it into a bug |
| CHK-SRV-002, -003 | inline error appears / disappears | E2E UI | Good Candidate | P1 | TC-SRV-004 | "This field is required" after a touched field is emptied (D-SRV-2) |
| CHK-SRV-004 | cannot complete until all required answered | E2E UI | Good Candidate | P0 | TC-SRV-001, -004 | Save disabled |
| CHK-SRV-005 | Yes/No single choice | E2E UI | Good Candidate | P1 | TC-SRV-002 | |
| CHK-SRV-006 | radio single choice | E2E UI | Good Candidate | P1 | TC-SRV-002 | |
| CHK-SRV-007 | checkbox multiple choice | E2E UI | Good Candidate | P1 | TC-SRV-002 | |
| CHK-SRV-008, -009 | text ≤ 500, the 501st refused | E2E UI | Good Candidate | P1 | TC-SRV-003 | 500 / 501 boundary; counter "N characters remaining" |
| CHK-SRV-010, -011 | auto-save as you type / on back | E2E UI | Good Candidate | P0 | TC-SRV-005 | back without Save → reopen |
| CHK-SRV-012 | auto-save on background | E2E UI | Good Candidate | P1 | TC-SRV-005 | |
| CHK-SRV-013 | restored on reopen | E2E UI | Good Candidate | P0 | TC-SRV-005 | |
| CHK-SRV-014 | persists across app restart | E2E UI | Good Candidate | P0 | TC-SRV-005 | terminate + launch |
| CHK-SRV-015 | Save enabled only when valid | E2E UI | Good Candidate | P0 | TC-SRV-001, -004 | |
| CHK-SRV-016 | Save persists and marks completed | E2E UI + API | Good Candidate | P0 | TC-SRV-001 | "Survey saved"; answers shown on reopen; server copy (D-SRV-7) |
| CHK-SRV-017 | Save returns to the In progress screen | E2E UI | Good Candidate | P0 | TC-SRV-001 | |
| CHK-SRV-018 | Survey row marked completed | — | Skipped (D-SRV-8 = D-ORDP-1) | – | — | no indicator exists |
| CHK-SRV-019, -020 | attach photos, thumbnails shown | E2E UI | Good Candidate | P1 | TC-SRV-014 | gallery only on the simulator; thumbnails likely pixels (as TD-ORDD-002) — recon 8 |
| CHK-SRV-021 | photos compressed | E2E UI + API | Good Candidate | P2 | TC-SRV-014 | a 4032×3024 photo in → the stored file's longest side ≤ 1920 px (app policy) |
| CHK-SRV-022 | photos stay after leaving and returning | E2E UI | Good Candidate | P1 | TC-SRV-014 | |
| CHK-SRV-023 | photos after restart while offline | Manual (Android stage) | Needs Device | P3 | — | offline — no network control on the iOS simulator (plan §7.5) |
| CHK-SRV-024…027 | offline fill / edit / photos / sync | Manual (Android stage) | Needs Device | P2 | — | as above (FR-SUR-12/13) |
| CHK-SRV-028…030 | local save fails: message, data kept, retry | Manual | Not Recommended (automation) | P3 | — | cannot make local storage fail from a test (Q-SRV-3) |
| CHK-SRV-031, -032 | photo upload fails: notice, kept, retried | Manual (Android stage) | Needs Device | P3 | — | needs the network cut mid-upload (Q-SRV-3) |
| CHK-SRV-033…035 | read-only after deliverables submitted | E2E UI + API setup | Good Candidate | P1 | TC-SRV-016 | the survey does not open at all (D-SRV-9, recon 7) |
| CHK-SRV-036 | saved with the job and the template | API (after UI) | Good Candidate | P1 | TC-SRV-001 | `surveyResponse` on the job; template id — recon 8 |
| CHK-SRV-037 | each answer under its question id | API (after UI) | Good Candidate | P0 | TC-SRV-001, -002, -009 | |
| CHK-SRV-038 | photo references in the payload | API (after UI) | Good Candidate | P1 | TC-SRV-014 | file ids under the photo question |
| CHK-SRV-039 | last-modified updated after each change | API (after UI) | Good Candidate | P3 | TC-SRV-005 | if the server keeps it (recon 8); else Blocked with the reason |
| CHK-SRV-040 | completion status stored after Save | API (after UI) | Good Candidate | P1 | TC-SRV-001 | shape — recon 8 |

### Proposed items (17, Q-SRV-5) — logic, CR-2, edge cases

| CHK ID | Check that … | Level | Priority | TC | Source |
|---|---|---|---|---|---|
| CHK-SRV-041 | each answer shows exactly the questions its logic rule leaves visible (the logic tables) | E2E UI | P0 | TC-SRV-006, -007, -008 | template rules; plan §7.5 |
| CHK-SRV-042 | changing an answer after a branch shows the new branch and hides the old one | E2E UI | P0 | TC-SRV-006, -007 | plan §7.5 ("A → B") |
| CHK-SRV-043 | a rule that leads to another section hides the sections in between | E2E UI | P1 | TC-SRV-007 | T8 |
| CHK-SRV-044 | an "end survey" answer hides every later question and lets the survey be saved | E2E UI + API | P0 | TC-SRV-008 | End Survey |
| CHK-SRV-045 | hidden questions are not saved | API (after UI) | P1 | TC-SRV-008 | logic rule 7 |
| CHK-SRV-046 | a repeatable section shows its first entry, named after the section, with "Repeat section" | E2E UI | P0 | TC-SRV-010 | PRD story 3; D-SRV-10/11 |
| CHK-SRV-047 | "Repeat section" adds an entry with the same questions, named "<section> 2", "<section> 3"…; names cannot be edited | E2E UI | P0 | TC-SRV-010 | PRD stories 2–3 |
| CHK-SRV-048 | each entry keeps its own answers; editing an entry creates no duplicate | E2E UI + API | P0 | TC-SRV-010 | PRD story 4 |
| CHK-SRV-049 | deleting an entry with data asks for confirmation; Cancel keeps it; Delete removes it and renumbers the rest; the first entry cannot be deleted | E2E UI | P0 | TC-SRV-011 | PRD story 5; D-SRV-11/12 |
| CHK-SRV-050 | a deleted entry is not saved | API (after UI) | P1 | TC-SRV-011 | PRD story 5 |
| CHK-SRV-051 | an incomplete entry keeps Save disabled; its card shows "not complete" | E2E UI | P0 | TC-SRV-012 | PRD §14.2; D-SRV-13 |
| CHK-SRV-052 | logic inside an entry applies to that entry only; a rule leading out of the section continues the survey at its target | E2E UI | P1 | TC-SRV-013 | logic rule 6 |
| CHK-SRV-053 | photos added inside an entry stay linked to that entry in the saved survey | E2E UI + API | P1 | TC-SRV-014 | PRD §9.3 |
| CHK-SRV-054 | the saved survey keeps every entry, in order, with its name and answers | API (after UI) | P0 | TC-SRV-009, -010 | PRD §9.3; D-SRV-14 |
| CHK-SRV-055 | entries (added, edited, deleted) survive leaving the survey and an app restart | E2E UI | P1 | TC-SRV-010, -011 | PRD story 6 (draft) |
| CHK-SRV-056 | a survey with no questions opens and can be saved | E2E UI | P2 | TC-SRV-015 | owner's plan §7.5 |
| CHK-SRV-057 | an "Other" option asks for its own text, and that text is required | E2E UI | P2 | TC-SRV-002 | template `answers[].options.enabled` (code: custom option) |

## Step 5b — Selected (draft)

**Selected: 29 of the 40 imported items + all 17 proposed items, in 16 TCs.** The rest:
- 10 are manual or waiting for the Android stage (offline, save / upload failures);
- 1 is skipped (D-SRV-8).

| TC | Survey | Covers |
|---|---|---|
| TC-SRV-001 | Short Survey | happy path: Save disabled → answer both → Save → "Survey saved" → the job → server copy |
| TC-SRV-002 | Mo3 All Question Types | every field type: Yes/No, radio, checkboxes + "Other", text, date, time; server values per type |
| TC-SRV-003 | Short Survey | text 500 / 501 |
| TC-SRV-004 | Short Survey | no marker; "This field is required" after touch → gone when filled; Save disabled while empty |
| TC-SRV-005 | Mo3 | auto-save: back without Save, background, restart → answers restored |
| TC-SRV-006 | Mo5 Radio Logic | table MO5-0…5 |
| TC-SRV-007 | T8 Branching | table T8-1…3 (a whole section disappears / returns) |
| TC-SRV-008 | End Survey | END-1, END-3, END-8; Save with only Q1; hidden not saved |
| TC-SRV-009 | Fiber Site Survey | realistic end-to-end: 2 rooms, Number, FIB-2 / FIB-3; server structure |
| TC-SRV-010 | Repeatable Single without logic | CR-2: first entry, Repeat → 2, 3; edit without duplicate; restart; server |
| TC-SRV-011 | Repeatable Single without logic | CR-2: delete — empty (no dialog), with data (Cancel / Delete), renumbering, first not deletable; server |
| TC-SRV-012 | Repeatable Single without logic | CR-2: an incomplete entry blocks Save |
| TC-SRV-013 | Repeatable TWO with logic | TWO-1 / TWO-8 per entry; TWO-12 lands in S2; TWO-9 end |
| TC-SRV-014 | Photo Upload Test Survey | photos: several, thumbnails, stay after leaving; per-room photos in entry 2 → server under entry 2; compression ≤ 1920 px |
| TC-SRV-015 | stringsdf (0 questions) | opens, Save works |
| TC-SRV-016 | Short Survey on a Submitted job | the survey does not open (read-only) |

## Step 7–8 — API support, selectors

- **API:**
  - `POST /job` (in_progress, `surveyId`) and `DELETE /job/{id}`;
  - `GET /job/{id}` → `surveyResponse` (the stored answers; shape from recon 8);
  - `GET /survey/{id}` read once for the tables (done).
  - Nothing is written to surveys.
- **Selectors:** unknown until recon 8. Expected defects:
  - repeatable-card delete / collapse icons without names (the app puts `ValueKey`s only on the section cards — invisible
    to XCUITest; app code audit);
  - photo thumbnails not in the tree (as TD-ORDD-002);
  - the photo editor's toolbar unnamed (TD-PHOTO-001).

## Step 9 — Test data

- **Per run:** ~16 jobs (one per TC), `QA-AUTO-*`, In progress, each with its survey. They are deleted in `finally`.
- **Photos:** 3 photos in the simulator gallery (once per simulator), one of them 4032×3024. Survey photos are uploaded to
  DEV storage and may stay after the jobs are deleted (accepted in module 04).
- **Surveys:** 10 published DEV surveys, used read-only. If a survey is edited on DEV, the tables and the tests must follow.

## Step 12 — Execution order

TC-SRV-001 (smoke) → 002…005 → logic 006…009 → CR-2 010…013 → photos 014 → 015 → 016. Serial, as every module.

## Step 15 — Risks

- **The DEV surveys are shared.** Somebody may edit them; the test then fails for the right reason. The snapshot in
  `survey-definitions/` shows what changed.
- **Pickers.** The date and time pickers are Material dialogs; their tree is not known yet (recon 8).
- **Photo flow.** Gallery → editor → metadata page — three screens, two of them with known unnamed controls.
- **Duplicate question titles.** Titles repeat across entries and sections. Questions are found inside the card of their
  entry / section.
- **Upload timing.** The upload to the server is queued. The server copy is waited for, not assumed.

## Step 16 — Recommendation

Owner's word on Q-SRV-1…5 and the logic tables → recon 8 → test cases → maps / tests.
