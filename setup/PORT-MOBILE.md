# PORT-MOBILE.md — moving a project's mobile improvements back into the template

A project made from this template ends up holding two kinds of files: **the template** (the method and the
tooling, the same in every project) and **the project** (what was learned about one product). Improvements made
while working on a project belong to the template and should flow back to the clean template; the project's own
content never should. This file is the list that tells them apart for the **mobile** stack (Appium + pytest; native
or Flutter apps on iOS and Android).

Rule of thumb: everything project-specific lives in `setup/project.yaml` values, `docs/`, `qa/mobile/<NN-module>/`,
`qa/mobile/{ios,android}/`, the app's screens, pages, tests and data fixtures under `automation/mobile/`, the hook
`automation/mobile/helpers/account_names.py`, `reports/mobile/` and every `.env`. Everything else is template.

A product name, a module name, a date, a run, a test-case id or an environment quirk in a comment is caught only by
reading the diff (section 5).

The mobile stack's names: skills `/qa-mobile-*`, tools `automation/tools/mobile_*` (on top of the shared `brand.py`
and `paths.py`), `report.mobile:` in `setup/project.yaml`, reports in `reports/mobile/`.

## 1. Template — copy as is

| Path | What |
|---|---|
| `automation/tools/mobile_*.py`, `mobile_export_pdf.mjs`, `ocr/ocr_lines.swift`, `tests/test_mobile_*.py` | the mobile test completion reports: a platform's internal site, the combined one, the client's, all six at once (`--share`: the copy people get, with the privacy check), a run against the baseline, PDFs — see `automation/tools/README.md` *Mobile reports* |
| `automation/tools/import_checklist_from_csv.py` | a checklist from a CSV export of the team's sheet (the Sheets importer's rules) |
| `automation/mobile/scripts/{run.sh,qa.sh,qa.py,run_context.py,start_appium.sh}` | one named run per platform with its refusals; one command for a platform or both side by side; an Appium server per platform |
| `automation/mobile/scripts/recon/{dump_screen.py,app_logs.py,compare_android.py,redact_dumps.py}` | recon: a screen's tree without restarting the app, a Flutter app's own log, iOS ↔ Android locator comparison, redaction of dumps before a commit |
| `automation/mobile/helpers/{waits.py,device.py,evidence.py,reporting.py,pixels.py}`, `helpers/android/` | explicit waits, device helpers, checkpoints and screen video, the run's Allure environment, pixel oracles; adb: network on / off, time, permissions, media, links |
| `automation/mobile/fixtures/network.py` | offline / slow network for a test, restored in `finally` |
| `automation/mobile/pages/base_page.py` | the page base: gestures per platform, typing that survives the Android IME, reading lists that Flutter renders only on screen |
| `automation/mobile/screens/android/{__init__.py,system_dialogs_map.py,dialer_map.py}` | Android system UI: permission dialogs, the ANR dialog, the dialer |
| `automation/mobile/unit_tests/{android_dumps.py,test_ios_locator_guard.py,test_parallel_runs.py}` | the offline evaluator of Android locators on recon trees; the guard that locks a proven platform's locators; the parallel-run settings and the launcher |
| `automation/mobile/{LESSONS.md,SECOND-PLATFORM.md,PARALLEL-RUNS.md}` | what cost time on a mobile product; adding the second platform; running both at once (`PARALLEL-RUNS.md` §6 is the project's — keep the heading, empty the values) |
| `.claude/skills/qa-mobile-{run,regress,triage,report}/` | the four mobile skills |
| `docs/notes/mobile-qa-skills.md`, `mobile-qa-skills.en.md` | the owner's guide to the skills (Ukrainian, English) |
| `qa/shared/device-matrix/README.md` | list only the devices the runs use — the reports read the P0 rows |
| `setup/PORT-MOBILE.md` | this file |

## 2. Template, but carries the project's words — copy, then adapt

| Path | What to adapt |
|---|---|
| `automation/mobile/conftest.py` | template (prove-red, a session per module on Android and its revival, the ANR guard, `chk_skipped_on`, the platform's account and Appium server); **project**: the `pytest_plugins` list — keep only the template's fixture modules (`fixtures.network`) |
| `automation/mobile/config/{settings.py,capabilities.py}`, `.env.example` | template; the defaults (device names, OS versions) are examples |
| `automation/mobile/helpers/app.py` | app control (cold start, clear data, permissions, location, media, theme) is template; the app's own preference keys and its first-screen text are the project's |
| `automation/mobile/fixtures/{app_state.py,test_data.py}` | the pattern is template (state per test through fixtures; generated users in reserved ranges with a marker the cleanup refuses to go without); the sign-in flow, the fields and the API calls are the project's |
| `automation/mobile/unit_tests/{test_harness.py,test_screen_maps.py,test_android_maps.py}` | the checks are template; the maps, modules and dumps they list are the project's |
| `automation/mobile/README.md` | the sections from *Session model* to *Offline self-test* are template; the folder tree and the examples name the project's modules |
| `automation/mobile/scripts/build_shims/` | a build shim for a Flutter app whose plugin needs the client's credentials — an example, adapt to the plugin |
| `automation/tools/README.md` | the *Mobile reports* section and the table row are template |
| `reports/mobile/README.md` | the structure and the rebuild commands are template; the runs, dates and links are the project's |
| `setup/project.yaml` | **the structure** of `report.mobile:` and `mobile.parallel:` is template; every value is the project's |

## 3. Project — never copy

| Path | Why |
|---|---|
| `docs/` except the files in sections 1–2 | what the product's team gave, and the project's journal |
| `qa/mobile/<NN-module>/`, `qa/mobile/{ios,android}/`, `qa/mobile/README.md`, `qa/shared/{feature-codes.md,questions/,recon-*,app-code-audit.md,oracles/invariants.md}`, `qa/shared/device-matrix/device-matrix.md`, `docs/platform-specs/supported-devices.md`, `docs/requirements/shared/testability-contract.md` §5 (the project's log) | the product's checklists, test cases, traceability, bugs, recon, questions, devices and testability defects |
| `automation/mobile/{tests,pages,screens}/` except the files in sections 1–2 | the app's screens and flows |
| `automation/mobile/fixtures/` except `network.py`, `helpers/account_names.py`, the product's API helper, `scripts/recon/recon_*.py`, `unit_tests/` files that test the app's pages and data, `unit_tests/ios_locators.snapshot.json` | built on the app's API, data and screens |
| `reports/mobile/{ios,android,all}/`, `reports/mobile/{internal,client}.html` | the product's deliverables |
| `automation/mobile/{.env,results/,reports/,builds/}`, `automation/tools/.secrets/`, `_bmad-output/` | secrets and outputs; gitignored |

No worked examples of the app's code go into the template: the next project reads the earlier project's repository
when it needs one.

## 4. Reference only — the owner decides per clone

`examples/`, `_bmad-output/` — never copied by default; the owner decides.

## 5. How to port

1. In the template, make a branch.
2. Copy section 1 paths from the project (`rsync -a --relative <paths> <template>/`), then section 2 paths and adapt
   them. Files shared with the rest of the template (`CLAUDE.md`, `setup/SETUP.md`, `setup/project.yaml`,
   `.gitignore`, `automation/tools/{README.md,pyproject.toml}`) get the mobile lines added — nothing else in them
   changes; never copy a project's file over them. Section 3 is never copied.
3. `git diff` in the template: every changed file is read before it is committed — a module name, a date, a run or a
   test-case id in a comment is a leak.
4. In the template, all green (no device, no target, no credentials):
   `cd automation/tools && uv sync && uv run ruff check mobile_*.py import_checklist_from_csv.py tests/test_mobile_*.py
   && uv run ruff format --check mobile_*.py import_checklist_from_csv.py tests/test_mobile_*.py &&
   uv run pytest tests/test_mobile_*.py` ·
   `cd automation/mobile && uv sync && uv run ruff check . && uv run ruff format --check . &&
   uv run python -m unittest discover -s unit_tests` ·
   `uv run pytest --platform=ios --collect-only -q` and `--platform=android` ·
   `scripts/qa.sh both all --dry-run` (with the placeholders it says why the platforms cannot run side by side).
5. With `setup/project.yaml` at its placeholders: the mobile client report renders "Draft — not for sending", and
   `mobile_reports.py` without a run ends `Blocked`, never with an empty report.
6. `CHANGELOG.md`: the mobile entries under the new version; tag it.
