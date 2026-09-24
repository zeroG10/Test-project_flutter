# Test cases — Survey (mobile)

> Structured, alias-based test cases for the CHK IDs selected in [survey-automation-plan.md](survey-automation-plan.md).
> Format: [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: draft — written after recon 8 ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md)) and the
> owner's decisions (2026-09-24: Q-SRV-1…6 closed, every D-SRV accepted, logic tables approved); validation by the owner
> together with the first results.**

| Field | Value |
|---|---|
| Feature | The survey of an In progress job: every field type, validation, auto-save, Save and the server copy, skip logic, CR-2 repeatable sections, photos, an empty survey, read-only after submission |
| Source checklist | `qa/mobile/08-survey/survey-checklist.md` (CHK-SRV-001…057) |
| Devices / build | iPhone 17 · iOS 26.5 (simulator) · `[DEV] CT Mobile` 1.1.1 (178), `CLIENT_BUILD=true` · online · photos permission: the system picker (no prompt) |
| Owner | @mykola.zhuchenko · Last updated 2026-09-24 |

**Conventions**

- **One job per test**, created through `POST /job` directly In progress (`{{job.<survey>}}`, fixture `survey_job`) with
  the survey under test, and deleted after the test. `{{job.done}}` is created Submitted.
- **Visible questions** = the numbered question titles the form renders (`survey.titles`, TD-SRV-001). A logic check
  compares them with a row of [survey-logic-tables.md](survey-logic-tables.md) (the approved oracle).
- **Fields have no names** (TD-SRV-001). `survey.yes[n]` / `survey.no[n]` is the Yes / No of the n-th Yes/No question
  in form order; `survey.text[n]`, `survey.date[n]`, `survey.time[n]`, `survey.upload-photo[n]` work the same way. The
  question title is given in Data for the reader.
- **The photo flow** after `survey.upload-photo[n]`: `photo-picker.grid` (cell k by position) → `photo-editor.done` →
  `photo-metadata.description` → `photo-metadata.save`. Cell 0 is the newest gallery photo: the 4032×3024 test photo (fixture `gallery_photos`).
- **The server copy** = `GET /job/{id}` → `surveyResponse` (`items[]`; `value[].data`; photos in `files[]`), read after
  Save. It is waited for, because the upload is queued.
- **Dates** are stored as local midnight in UTC (15 Sep, UTC+3 → `…-09-14T21:00:00.000Z`): accepted, Q-SRV-6.

---

## TC-SRV-001 — Short Survey: Save stays disabled until every question is answered; Save stores the answers and returns to the job

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-004, -015, -016, -017, -036, -037, -040 |
| Priority | P0 · smoke |
| Preconditions | `{{job.short}}` In progress (Short Survey), details open |
| Oracle | spec — FR-SUR-04, FR-SUR-11; accepted baseline (D-SRV-7: Save also sends the survey, status `draft`) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Survey] | — | — |
| 2 | expect-text | survey.survey-name[Short Survey] | — | Short Survey |
| 3 | expect-text | survey.titles | — | Good? · Text? |
| 4 | expect-disabled | survey.save | — | — |
| 5 | click | survey.yes[1] | Good? | — |
| 6 | expect-disabled | survey.save | — | one question still empty |
| 7 | fill | survey.text[1] | Text? — `QA-AUTO short answer` | — |
| 8 | expect-enabled | survey.save | — | — |
| 9 | click | survey.save | — | "Survey saved" |
| 10 | expect-visible | job-details.header[{{job.short.titleLine}}] | — | back on the job |
| 11 | expect-text | api.surveyResponse | — | `jobId` = the job's; question ids = the template's; Good? → `true`, Text? → the text; `status` `draft` |

## TC-SRV-002 — Mo3: every field type takes its answer, and the server stores each value

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-005, -006, -007, -019, -020, -037, -038, -057 |
| Priority | P0 |
| Preconditions | `{{job.mo3}}` In progress (Mo3 All Question Types), details open; `gallery_photos` |
| Oracle | spec — FR-SUR-02, FR-SUR-08/09; recon 8 (the "Other" text is required at once) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Survey] | — | — |
| 2 | click | survey.no[1] | Was the job completed successfully? | — |
| 3 | click | survey.yes[1] | the same question | Yes selected, No not |
| 4 | click | survey.option[Completed] | What is the current job result? | — |
| 5 | click | survey.option[Partially completed] | the same question | only "Partially completed" selected |
| 6 | click | survey.checkbox[Cable installation] | Which tasks…? | on |
| 7 | click | survey.checkbox[Testing] | the same question | on (both) |
| 8 | click | survey.checkbox[ON!!!] | the "Other" option | its text field shows survey.required-error |
| 9 | fill | survey.text[1] | the "Other" text — `QA-AUTO other task` | the error is gone |
| 10 | fill | survey.text[2] | Add technician notes — `QA-AUTO notes` | — |
| 11 | click | survey.upload-photo[1] | cell 1, `QA-AUTO survey photo` — then the photo flow (conventions) | survey.thumbnail[QA-AUTO survey photo] |
| 12 | select | survey.date[1] | day 15 of the current month | `<Mon> 15, <yyyy>` |
| 13 | select | survey.time[1] | 09:45 (text input mode) | `09:45` |
| 14 | click | survey.save | — | "Survey saved" |
| 15 | expect-text | api.surveyResponse | — | toggle `true`; single `Partially completed`; multi `Cable installation`, `Testing`, `QA-AUTO other task`; text; date = local midnight of day 15; time `09:45`; the photo question: 1 file, note `QA-AUTO survey photo` |

## TC-SRV-003 — A text answer takes 500 characters; the 501st is refused

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-008, -009 |
| Priority | P1 |
| Preconditions | `{{job.short}}`, Survey open |
| Oracle | spec — FR-SUR-02 (max 500) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | fill | survey.text[1] | 501 characters | — |
| 2 | expect-text | survey.text[1] | — | exactly the first 500 characters |
| 3 | expect-text | survey.counter | — | No characters remaining |

## TC-SRV-004 — Validation: no required marker; "This field is required" after an emptied field, gone when filled

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-001, -002, -003, -004, -015 |
| Priority | P1 |
| Preconditions | `{{job.short}}`, Survey open |
| Oracle | accepted baseline — D-SRV-1/2 (every question required, no marker; owner Q-SRV-1) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | survey.titles | — | `Good?`, `Text?` — no marker (`*`, "required") |
| 2 | fill | survey.text[1] | `abc`, then clear it | — |
| 3 | expect-visible | survey.required-error | — | This field is required |
| 4 | fill | survey.text[1] | `QA-AUTO text` | — |
| 5 | expect-hidden | survey.required-error | — | — |
| 6 | expect-disabled | survey.save | — | Good? still unanswered |
| 7 | click | survey.yes[1] | Good? | — |
| 8 | expect-enabled | survey.save | — | — |

## TC-SRV-005 — Auto-save: answers survive back, background and a restart; a new Save updates the stored survey

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-010, -011, -012, -013, -014, -039 |
| Priority | P0 |
| Preconditions | `{{job.short}}`, Survey open |
| Oracle | spec — FR-SUR-06, -07, -11-1 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.yes[1] | Good? | — |
| 2 | fill | survey.text[1] | `QA-AUTO kept` | — |
| 3 | click | survey.back | — | the job's details (no Save) |
| 4 | click | job-details.deliverable[Survey] | — | Yes selected, text `QA-AUTO kept` |
| 5 | wait-for | app | 5 s in the background | the same answers |
| 6 | open | app | terminate + launch → the job → Survey | the same answers |
| 7 | click | survey.save | — | stored: `updatedAt` t1 |
| 8 | click | job-details.deliverable[Survey] | — | — |
| 9 | click | survey.no[1] | Good? | — |
| 10 | click | survey.save | — | — |
| 11 | expect-text | api.surveyResponse | — | Good? `false`; the same response id; `updatedAt` > t1 |

## TC-SRV-006 — Mo5: each answer shows exactly the questions of its logic-table row, also after changing it

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-041, -042 |
| Priority | P0 |
| Preconditions | `{{job.mo5}}`, Survey open |
| Oracle | the approved logic tables — rows MO5-0…MO5-5 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | survey.titles | — | MO5-0 |
| 2 | click | survey.option[Access issue] | — | titles = MO5-1 |
| 3 | click | survey.option[Equipment issue] | — | titles = MO5-2 |
| 4 | click | survey.option[Customer issue] | — | titles = MO5-3 |
| 5 | click | survey.option[No issue found] | — | titles = MO5-4 |
| 6 | click | survey.option[Access issue] | — | titles = MO5-5 (Q2, Q3 back) |

## TC-SRV-007 — T8: "No" hides the "Site Ready" section; "Yes" brings it back

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-041, -042, -043 |
| Priority | P1 |
| Preconditions | `{{job.t8}}`, Survey open |
| Oracle | the approved logic tables — T8-1…T8-3 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.no[1] | S1Q3 Was the site ready? | titles = T8-2 |
| 2 | expect-hidden | survey.section[S2 Site Ready Path] | — | — |
| 3 | click | survey.yes[1] | — | titles = T8-3 |
| 4 | expect-visible | survey.section[S2 Site Ready Path] | — | — |

## TC-SRV-008 — End Survey: an "end" answer hides everything after it, removes "Repeat section", and the survey saves with only what is visible

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-041, -042, -044, -045 |
| Priority | P0 |
| Preconditions | `{{job.end}}`, Survey open |
| Oracle | the approved logic tables — END-2, END-3, END-1; logic rule 7 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.no[1] | End Survey | titles = END-2 (all 15) |
| 2 | click | survey.yes[2] | Q1 Enter the work order ID (entry 1) | titles = End Survey · Q1 Enter the work order ID (END-3) |
| 3 | expect-hidden | survey.repeat | — | — |
| 4 | click | survey.yes[1] | End Survey | titles = End Survey (END-1) |
| 5 | expect-enabled | survey.save | — | — |
| 6 | click | survey.save | — | "Survey saved" |
| 7 | expect-text | api.surveyResponse | — | one item: End Survey → `true`; no section block |

## TC-SRV-009 — Fiber Site Survey end to end: a hidden section, two entries of a repeatable section, an "end" in the copy; editing adds no duplicate

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-037, -041, -044, -045, -048, -054 |
| Priority | P0 |
| Preconditions | `{{job.fiber}}`, Survey open |
| Oracle | the approved logic tables — FIB-2, FIB-3; accepted baseline D-SRV-14 (one block per entry) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.no[1] | Are there any rooms…? = No | titles = FIB-2 ("Room Information" gone) |
| 2 | fill | survey.text[1] | Additional comments — `QA-AUTO comments` | — |
| 3 | click | survey.yes[2] | entry 1: Was the job completed successfully? | — |
| 4 | select | survey.date[1] | entry 1: day 10 | — |
| 5 | click | survey.checkbox[Splicing] | entry 1 | — |
| 6 | click | survey.option[Completed as planned] | entry 1 | — |
| 7 | click | survey.repeat[1] | — | survey.entry-headers: `…tests`, `…tests 2`, `…(Copy)` |
| 8 | click | survey.no[3] | entry 2: Was the job completed successfully? | — |
| 9 | select | survey.date[1] | entry 2 (the first empty date): day 11 | — |
| 10 | click | survey.checkbox[Testing] | the 2nd (entry 2) | — |
| 11 | click | survey.option[Completed as planned] | the 2nd (entry 2) | — |
| 12 | click | survey.yes[4] | (Copy): Was the job completed successfully? | titles = FIB-3 |
| 13 | click | survey.save | — | "Survey saved" |
| 14 | expect-text | api.surveyResponse | — | Q1 `No`; comments; block `…tests` (true, day 10, Splicing, Completed as planned); block `…tests 2` (false, day 11, Testing); block `…(Copy)` with only `true`; no "Room Information" |
| 15 | click | job-details.deliverable[Survey] | — | — |
| 16 | click | survey.option[Partially completed] | the 1st (entry 1) | — |
| 17 | click | survey.save | — | — |
| 18 | expect-text | api.surveyResponse | — | the same blocks (no duplicate); entry 1 status `Partially completed` |

## TC-SRV-010 — CR-2: the first entry is named after the section; "Repeat section" adds numbered entries; each entry keeps its answers, also after a restart

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-046, -047, -048, -055 |
| Priority | P0 |
| Preconditions | `{{job.rep1}}` (Repeatable Single section without logic), Survey open |
| Oracle | accepted baseline — D-SRV-10/11 (first entry permanent, "<section>", "<section> 2") |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-text | survey.entry-headers[S1 Job Details…] | — | `S1 Job Details…` (1 entry) |
| 2 | expect-hidden | survey.delete-entry | — | the first entry cannot be deleted |
| 3 | click | survey.repeat[1] | — | — |
| 4 | click | survey.repeat[1] | on the last entry | headers `…`, `… 2`, `… 3`; 2 × survey.delete-entry |
| 5 | click | survey.yes[1] | entry 1: Q1 Enter the work order ID | — |
| 6 | click | survey.no[6] | entry 2: the same question | — |
| 7 | expect-visible | survey.yes[1] | — | selected |
| 8 | expect-visible | survey.no[6] | — | selected |
| 9 | expect-visible | survey.yes[11] | entry 3 | not selected (and no[11] not selected) |
| 10 | open | app | terminate + launch → the job → Survey | 3 entries, the same selections |

## TC-SRV-011 — CR-2: deleting an entry — no dialog when empty; with data: Cancel keeps it, Delete removes it and the rest renumber; a deleted entry is not saved

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-049, -050 |
| Priority | P0 |
| Preconditions | `{{job.fiber}}`, Survey open |
| Oracle | accepted baseline — D-SRV-12 (a dialog only for an entry with data) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.no[1] | Are there any rooms…? = No | titles = FIB-2 ("Room Information" gone) |
| 2 | fill | survey.text[1] | Additional comments — `QA-AUTO comments` | — |
| 3 | click | survey.yes[2] | entry 1: Was the job completed successfully? | — |
| 4 | select | survey.date[1] | entry 1: day 10 | — |
| 5 | click | survey.checkbox[Splicing] | entry 1 | — |
| 6 | click | survey.option[Completed as planned] | entry 1 | — |
| 7 | click | survey.repeat[1] | — | entry 2 |
| 8 | click | survey.repeat[1] | — | entry 3; headers `…`, `… 2`, `… 3` |
| 9 | click | survey.yes[3] | entry 2 | — |
| 10 | click | survey.no[4] | entry 3 | — |
| 11 | click | survey.delete-entry[1] | entry 2 (has data) | — |
| 12 | expect-text | survey-delete-dialog.message[Are you sure you want to delete this section? All data will be lost.] | — | title "Delete section" |
| 13 | click | survey-delete-dialog.cancel | — | 3 entries |
| 14 | click | survey.delete-entry[1] | entry 2 | — |
| 15 | click | survey-delete-dialog.delete | — | headers `…`, `… 2`; survey.no[3] selected (the old entry 3) |
| 16 | click | survey.repeat[1] | — | an empty entry 3 |
| 17 | click | survey.delete-entry[2] | the empty entry 3 | removed without a dialog |
| 18 | click | survey.delete-entry[1] | entry 2 (has data) | — |
| 19 | click | survey-delete-dialog.delete | — | 1 entry; no survey.delete-entry |
| 20 | click | survey.yes[3] | (Copy) = Yes → end | — |
| 21 | click | survey.save | — | "Survey saved" |
| 22 | expect-text | api.surveyResponse | — | exactly one "Fiber installation report…" block (+ the copy) |

## TC-SRV-012 — CR-2: an incomplete entry keeps Save disabled

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-051 |
| Priority | P0 |
| Preconditions | `{{job.fiber}}`, Survey open |
| Oracle | PRD §14.2 (an incomplete entry blocks the submission); D-SRV-13 accepted (no message) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.no[1] | Are there any rooms…? = No | titles = FIB-2 ("Room Information" gone) |
| 2 | fill | survey.text[1] | Additional comments — `QA-AUTO comments` | — |
| 3 | click | survey.yes[2] | entry 1: Was the job completed successfully? | — |
| 4 | select | survey.date[1] | entry 1: day 10 | — |
| 5 | click | survey.checkbox[Splicing] | entry 1 | — |
| 6 | click | survey.option[Completed as planned] | entry 1 | — |
| 7 | click | survey.repeat[1] | — | an empty entry 2 |
| 8 | click | survey.yes[4] | (Copy) = Yes → end | — |
| 9 | expect-disabled | survey.save | — | entry 2 is empty |
| 10 | click | survey.no[3] | entry 2: Was the job completed successfully? | — |
| 11 | select | survey.date[1] | entry 2 (the first empty date): day 11 | — |
| 12 | click | survey.checkbox[Testing] | the 2nd (entry 2) | — |
| 13 | click | survey.option[Completed as planned] | the 2nd (entry 2) | — |
| 14 | expect-enabled | survey.save | — | — |

## TC-SRV-013 — Repeatable TWO: logic applies per entry; a rule leads into the next section; backward rules as approved; "end" removes the rest

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-041, -052 |
| Priority | P1 |
| Preconditions | `{{job.two}}`, Survey open |
| Oracle | the approved logic tables — TWO-8, TWO-12, TWO-14, TWO-15, TWO-9 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | survey.no[5] | S1 entry 1: Good?  Redirect to S2 | "Problems?" gone; S2 starts with "S2 Q4 …" (TWO-12) |
| 2 | click | survey.no[10] | S2: S2 Finish? (backward) | nothing more hidden (TWO-14) |
| 3 | click | survey.no[9] | S2: S2 Good? if No than  Redirect to S1 Q1 (backward) | "S2 Finish?" gone; Question 1…7 and S3 stay (TWO-15) |
| 4 | click | survey.no[1] | S1 entry 1: Q1 Enter the work order ID | "Q2 text Select the visit date" gone from entry 1 |
| 5 | click | survey.repeat[1] | S1 | entry 2 of S1 shows "Q2 text Select the visit date" (TWO-8) |
| 6 | click | survey.no[4] | S1 entry 1: Bad? | end: S2, Question 1…7, S3 gone (TWO-9) |
| 7 | expect-hidden | survey.repeat | — | — |

## TC-SRV-014 — Photos: required, several per question, kept after leaving, compressed, and stored under their question / entry

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-019, -020, -021, -022, -038, -053 |
| Priority | P1 |
| Preconditions | `{{job.photo}}` (Photo Upload Test Survey), Survey open; `gallery_photos` |
| Oracle | spec — FR-SUR-08…10; app policy: longest side ≤ 1920 px; owner Q-SRV-1 (photos required) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | fill | survey.text[1] | Per-room photos: Room name — `QA-AUTO room` | — |
| 2 | fill | survey.text[2] | Additional comments — `QA-AUTO comments` | — |
| 3 | expect-disabled | survey.save | — | no photo yet (photos are required) |
| 4 | click | survey.upload-photo[1] | cell 0 (4032×3024), `QA-AUTO overview 1` — then the photo flow (conventions) | survey.thumbnail[QA-AUTO overview 1] |
| 5 | click | survey.upload-photo[1] | cell 1, `QA-AUTO overview 2` — then the photo flow (conventions) | 2 thumbnails in the question |
| 6 | click | survey.upload-photo[2] | cell 1, `QA-AUTO close-up` — then the photo flow (conventions) | — |
| 7 | click | survey.upload-photo[3] | cell 1, `QA-AUTO room photo` (the Per-room photos entry) — then the photo flow (conventions) | — |
| 8 | click | survey.back | — | the job's details |
| 9 | click | job-details.deliverable[Survey] | — | the 4 thumbnails are there |
| 10 | click | survey.save | — | "Survey saved" |
| 11 | expect-text | api.surveyResponse | — | Site overview photos: 2 files (their notes); Equipment close-up: 1; block "Per-room photos": Room photos 1 (`QA-AUTO room photo`) |
| 12 | expect-text | api.surveyResponse | the stored file of `QA-AUTO overview 1` | JPEG 1920×1440 — longest side ≤ 1920 px |

## TC-SRV-015 — A survey with no questions opens and saves

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-056 |
| Priority | P2 |
| Preconditions | `{{job.empty}}` (stringsdf, 0 questions), details open |
| Oracle | owner's plan §7.5 ("must work"); D-SRV-18 accepted (blank form) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Survey] | — | survey.header |
| 2 | expect-text | survey.titles | — | none |
| 3 | expect-enabled | survey.save | — | — |
| 4 | click | survey.save | — | "Survey saved"; the job's details |
| 5 | expect-text | api.surveyResponse | — | `items` empty |

## TC-SRV-016 — After the deliverables are submitted the survey cannot be opened or changed

| Field | Value |
|---|---|
| Source CHK IDs | CHK-SRV-033, -034, -035 |
| Priority | P1 |
| Preconditions | `{{job.done}}` Submitted (Short Survey), details open |
| Oracle | accepted baseline — D-SRV-9 (recon 7) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | job-details.deliverable[Survey] | — | — |
| 2 | expect-hidden | survey.header | 3 s | the details stay; nothing can be changed |

## Aliases used

| Alias | ios map |
|---|---|
| job-details.deliverable, .header | yes (module 06) |
| survey.header, .back, .survey-name, .titles, .save, .yes, .no, .option, .checkbox, .text, .counter, .required-error, .date, .time, .upload-photo, .thumbnail, .section, .entry-headers, .repeat, .delete-entry, .saved | yes — `screens/survey_map.py` (recon 8) |
| survey-date-picker.day, .ok · survey-time-picker.text-mode, .hour, .minute, .ok · survey-delete-dialog.title, .message, .cancel, .delete | yes — `screens/survey_map.py` |
| photo-picker.root, .grid · photo-editor.done · photo-metadata.description, .save | yes — `screens/survey_photo_map.py` |
| api.surveyResponse | not an element — `GET /job/{id}` |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-SRV-001…-004, -015 | TC-SRV-004 (+ -001) | D-SRV-1/2 accepted |
| CHK-SRV-005…-007, -057 | TC-SRV-002 | |
| CHK-SRV-008, -009 | TC-SRV-003 | |
| CHK-SRV-010…-014, -039 | TC-SRV-005 | |
| CHK-SRV-016, -017, -036, -040 | TC-SRV-001 | |
| CHK-SRV-037 | TC-SRV-001, -002, -009 | |
| CHK-SRV-019…-022, -038, -053 | TC-SRV-014 (+ -002) | |
| CHK-SRV-033…-035 | TC-SRV-016 | |
| CHK-SRV-041, -042 | TC-SRV-006, -007, -008, -013 | the approved logic tables |
| CHK-SRV-043 | TC-SRV-007 | |
| CHK-SRV-044, -045 | TC-SRV-008, -009 | |
| CHK-SRV-046, -047, -055 | TC-SRV-010 | |
| CHK-SRV-048, -054 | TC-SRV-009, -010 | |
| CHK-SRV-049, -050 | TC-SRV-011 | |
| CHK-SRV-051 | TC-SRV-012 | |
| CHK-SRV-052 | TC-SRV-013 | |
| CHK-SRV-056 | TC-SRV-015 | |

**Not here:**
- CHK-SRV-018 — skipped (D-SRV-8 = D-ORDP-1).
- CHK-SRV-023…-027 — offline, Android stage.
- CHK-SRV-028…-032 — skipped with a comment: the owner verified them manually on iOS (Q-SRV-3).
