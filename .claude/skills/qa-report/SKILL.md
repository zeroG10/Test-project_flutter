---
name: qa-report
description: Make a finished regression run the basis of the final reports — update the traceability, rebuild the six test completion reports (iOS / Android / both × internal / client) and the PDFs, run the privacy check — and update the published pages only when the owner says so. Use when the user says "онови звіти", "збери звіти з останнього прогону", "rebuild the reports", "зроби PDF", "опублікуй звіти".
---

# QA report — from a regression run to the reports people get

Wrapper around [trace_results.py](../../../automation/tools/trace_results.py),
[build_reports.py](../../../automation/tools/build_reports.py) and
[export_pdf.mjs](../../../automation/tools/export_pdf.mjs). What the reports are and where they
live: [reports/README.md](../../../reports/README.md). Nothing here runs against an
environment. Answer in the owner's language.

## Step 1 — Which runs

- Per platform, the run to report: the owner names it, or propose the latest
  `automation/mobile/results/<platform>/*regress*` and **ask**. One platform may keep its
  current run (`setup/project.yaml → report.slices.<platform>.run`).
- The run must be a **whole regression**: compare its test count with the current baseline
  (`compare_runs.py --platform <p> <run>` — no MISSING). A module run, a dirty run
  (`RUN_INFO.txt: dirty: yes`) or an interrupted one is never a report's basis → stop.
- NEW RED / NEW BLOCKED without a triage → say so and offer `/qa-triage` first; a report with an
  unexplained failure gets the verdict "Failed", and the owner should know before it is built.

## Step 2 — Point the reports at the runs

Edit `setup/project.yaml → report.slices.<platform>`: `run:` = the new run; the previous `run`
and its history go to `history:` (oldest first) only if they are still comparable full runs;
rewrite `history_note` to say what the listed runs are.

## Step 3 — Traceability of record

```bash
cd automation/tools && uv run python trace_results.py --platform mobile \
  $(for c in ../../qa/mobile/*/*-checklist.md; do printf -- '--checklist %s ' "$c"; done) \
  --allure-dir ../mobile/results/<platform>/<run> \
  --target "<device · OS · DEV API>" --build "<version (build), source, debug|release>" \
  --run-label "<what ran, harness commit, date>" \
  --out ../../qa/mobile/<platform>/final-traceability.md
```

Target, build and run label: from the run's `environment.properties` and `RUN_INFO.txt` — never
from memory. A check without a test and without a row in `qa/mobile/<platform>/not-automated.md`
is reported by the builder as "reason missing": add the reason (ask the owner if it is a decision).

## Step 4 — Build, check, PDF

```bash
cd automation/tools
uv run python build_reports.py            # the full local copy (gitignored)
uv run python build_reports.py --share    # reports/ — must end: "… 0 · … 0 · videos: 0"
node export_pdf.mjs                       # six PDFs, named by the date of the run
uv run pytest -q                          # the generators' self-test
```

The privacy check not at zero → **stop**; nothing leaves the machine until it is.

## Step 5 — Show the owner

Per slice: verdict, checks passed / held red / blocked / not automated, open defects, what
changed against the previous reports. Open the local pages
(`reports/internal.html`, `reports/client.html`). The client report is approved by the owner
before it is sent.

## Step 6 — Only on the owner's word

- **Publish**: update the SAME pages (`setup/project.yaml → report.slices.*.internal_url` /
  `client_url`): Artifact publish with `url`, `file_path` =
  `automation/mobile/reports/publish/{internal,client}-page.html`, `root` = the absolute path of
  `reports/`, `files` = the files that changed (≤ 255 per call; files left out are kept).
- **Commit** on «коміть», **push** on «пуш» — never on your own.

## Rules

- A verdict is never edited by hand: a wrong number is fixed in the records or the generator.
- Reports state their run context; a platform without a fresh run keeps its date, and the
  combined report says so.
