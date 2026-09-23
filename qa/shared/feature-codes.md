# Feature codes — registry for `[CHK-<FEATURE>-<NNN>]` / `TC-<FEATURE>-<NNN>` IDs

<!--
Rule (read before adding a row):
- A code is 2–5 UPPERCASE letters derived from the feature slug (authentication → AUTH).
- One slug -> exactly ONE code, on every platform. automation/tools/sync_checklist_to_sheets.py
  reads the first two columns of this table (slug, code) and fails loudly if a slug maps
  to two codes. Web and mobile checklists of the same feature therefore share the code
  (they sync to separate Google Sheets, so CHK-AUTH-001 web and mobile never collide);
  two DIFFERENT features never share a code on the same platform.
- The `platform` column is informational (web | mobile | api | shared); the parser ignores it.
- `slug` = the checklist filename stem without `-checklist` / `checklist-`
  (`authentication-checklist.md` -> `authentication`).
- NEVER reuse a retired code and NEVER rename one: the IDs are the contract between the
  markdown checklists, the Google Sheets sync (automation/tools/sync_checklist_to_sheets.py)
  and the automated-test tags that trace_results.py reads. Renaming a code orphans every
  status ever recorded against it.
- Register the code BEFORE generating a checklist. If the prompt had to fall back to
  "first 4 letters uppercase", add the row here in the same session.
-->

| slug | code | platform | notes |
|---|---|---|---|
| `splash` | `SPL` | mobile | Splash screen — 15 перевірок у чеклісті |
| `authentication` | `AUTH` | mobile | Welcome + Registration + Phone/email verification + Login — 126 перевірок у чеклісті |
| `order-list` | `ORDL` | mobile | Order list screen / List view — 68 перевірок у чеклісті |
| `order-details` | `ORDD` | mobile | Order details screen — 89 перевірок у чеклісті |
| `check-in-out` | `CHIO` | mobile | Check-In / Check-Out Flow + confirmation logic — 40 перевірок у чеклісті |
| `order-progress` | `ORDP` | mobile | Order details — In progress state — 42 перевірок у чеклісті |
| `submit-deliverables` | `DLV` | mobile | Submit Deliverables — 33 перевірок у чеклісті |
| `survey` | `SRV` | mobile | Survey screen — 40 перевірок у чеклісті |
| `photo-report` | `PHR` | mobile | Photo report screen — 54 перевірок у чеклісті |
| `notes` | `NOTE` | mobile | Notes screen — 52 перевірок у чеклісті |
| `notifications` | `NOTIF` | mobile | Notifications screen — 31 перевірок у чеклісті |
| `profile` | `PRF` | mobile | Profile screen — 35 перевірок у чеклісті |
