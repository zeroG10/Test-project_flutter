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
| `<authentication>` | `<AUTH>` | `<web \| mobile \| api \| shared>` | `<SRS section — one line>` — replace this row with the first real feature |
