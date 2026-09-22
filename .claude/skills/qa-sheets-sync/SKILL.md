---
name: qa-sheets-sync
description: Publish a QA checklist markdown file into its Google Sheet via automation/tools/sync_checklist_to_sheets.py — always dry-run first, show the plan, push only after the user confirms. Use when the user says "sync the checklist to sheets", "push <checklist> to the sheet", or "import checklist to Google Sheets".
---

# QA Checklist → Google Sheets Sync

Thin, safety-gated wrapper around [automation/tools/sync_checklist_to_sheets.py](../../../automation/tools/sync_checklist_to_sheets.py).
The script is idempotent and **never touches** status columns (Chrome/Firefox/Edge/…) or
reviewer comments — it only writes col A (Task), B (Check text), and the hidden ID/Obsolete
columns. This skill exists to make the push **deliberate**: resolve the target, preflight the
config, dry-run, show the plan, and only then write to the shared team sheet.

> This writes to an outward-facing, shared resource. NEVER push without a dry-run and explicit
> user confirmation. Generation (`/qa-checklist`) and publishing (this skill) are separate on
> purpose — the checklist should be reviewed (Open Questions, design↔SRS conflicts) before it
> reaches the team's tracking sheet.

## Step 1 — Resolve the file and the target

1. The user names a checklist `.md` (e.g. `qa/web/01-authentication/authentication-checklist.md`
   — checklists live per module as `qa/{web,mobile}/<NN-module>/<module>-checklist.md`).
   If not given, ask which file.
2. Derive `--target` from the path — **do not default silently** (the script applies the
   same rule when `--target` is omitted, and errors out if the path names neither platform):
   - path under `qa/web/<NN-module>/` or `qa/shared/` → `--target web`
   - path under `qa/mobile/<NN-module>/` → `--target mobile`
   - If the path doesn't make the target obvious, ask web or mobile.
   (Web and mobile live in separate sheets with different ID/Obsolete columns — wrong target
   writes to the wrong sheet.)

## Step 2 — Preflight the config (fail clearly, don't half-run)

Confirm these exist before invoking the script; if any is missing, stop and tell the user
exactly what to set up (point them at `automation/tools/README.md`):

- `automation/tools/.env` with the target's vars
  (`WEB_SHEET_ID` + `WEB_WORKSHEET`/`WEB_ID_COL`/`WEB_OBSOLETE_COL`, or the `MOBILE_*` set).
- `automation/tools/.secrets/credentials.json` (service-account JSON), and the target Sheet
  shared with that service-account email as Editor.

## Step 3 — Dry-run first (ALWAYS)

Run the script with `--dry-run` from the tool directory so `.env`/credentials resolve:

```bash
( cd automation/tools && uv run python sync_checklist_to_sheets.py --target <web|mobile> --dry-run ../../<path-to-md> )
```

Read the output and summarize the plan for the user, in particular:
- new rows to append, check-text updates, and rows to be flagged **Obsolete** (removed checks);
- any **warning** (section renamed/moved, duplicate IDs in the sheet);
- any **hard error** — a duplicate ID in the `.md` aborts the sync; fix the `.md` first
  (the ID is the contract; never reuse one) and re-run the dry-run.

## Step 4 — Confirm, then push

Only after the user explicitly approves the dry-run plan, run the real sync (drop `--dry-run`):

```bash
( cd automation/tools && uv run python sync_checklist_to_sheets.py --target <web|mobile> ../../<path-to-md> )
```

Do **not** pass `--reset` unless the user explicitly asks to rebuild the data zone — it is
destructive to the existing layout.

## Step 5 — Report

State what changed (rows appended / updated / marked obsolete), the target sheet/worksheet,
and surface any warnings the run emitted. Remind the user that hidden columns (ID/Obsolete)
are sync bookkeeping and must not be edited or unhidden manually.

## Notes

- The script derives the feature code from the file stem (`authentication-checklist.md` →
  slug `authentication`) via the registry `qa/shared/feature-codes.md`. If the checklist
  already carries `[CHK-…]` IDs (it should, when produced by `/qa-checklist`), the sync just
  reads them — code derivation only matters for items lacking an ID. Keep the registry in
  step with `prompts/02` and `qa-checklist` so newly auto-assigned IDs stay consistent.
