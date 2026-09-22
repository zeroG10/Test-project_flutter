# checklist-gen — Vadym's rich-layout checklist generator (service-account variant)

Generates a QA checklist directly into a Google Sheet using **Vadym's v5 layout**
(page bands → sections → checks, 3 platform blocks with COUNTIF/SUM roll-ups,
conditional formatting, collapsible column/row groups, section-aware borders).

This is the **service-account** adaptation of a colleague's kit (the kit itself
was removed from the template on 2026-09-16; this folder is a frozen reference and a
deletion candidate). It reuses `automation/tools/.secrets/credentials.json`
and writes into an **existing** spreadsheet by ID (no OAuth, no 7-day token).

> ⚠️ This generator does a **full rebuild** of the target sheet's `Checklist` tab.
> Point it ONLY at a dedicated sheet — never at a live team sheet maintained by
> `automation/tools/sync_checklist_to_sheets.py`, or manually-entered statuses are lost.

## web/

- `checklist_generator.gs` — the `.gs` generator (Authentication, Variant A:
  1 screen = 1 page band). Content mirrors
  `examples/checklists/web/authentication-checklist.md` with CHK-AUTH IDs preserved in col B.
- `generate_via_api.mjs` — service-account adapter that executes the `.gs` via the
  Sheets REST API. Edit `SPREADSHEET_ID` / `GENERATOR_FN` at the top per run.

## Run

```sh
# one-time: install googleapis next to the adapter (no package.json here on purpose)
npm install --prefix examples/checklist-gen googleapis

# generate (writes into the configured SPREADSHEET_ID) — explicit user request only
node examples/checklist-gen/web/generate_via_api.mjs
```

Expected output: `Auth: service account …`, batch progress, `Done: 4 pages …`,
`STEP 5 test: PASSED`, and the sheet URL.

## Prerequisites

- The target Google Sheet must be shared with your service-account email
  (from `automation/tools/.secrets/credentials.json`, field `client_email`) as **Editor**.
- `googleapis` installed as above.
