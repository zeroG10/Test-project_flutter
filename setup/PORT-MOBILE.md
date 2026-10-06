# PORT-MOBILE.md — moving the template's mobile improvements into the clean template

The mobile twin of `setup/PORT.md` (the web port, which lives in the web project). A project made from the template
ends up holding two kinds of files: **the template** (the method and the tooling, the same in every project) and
**the project** (what was learned about one product). This file tells them apart for the **mobile** stack — written
in the first mobile project (a Flutter app on iOS and Android), for the port into the clean template.

Rule of thumb: everything project-specific lives in `setup/project.yaml` values, `docs/`, `qa/mobile/<NN-module>/`,
`automation/mobile/{tests,pages,screens}/` (this app's screens and flows), the app-specific fixtures and API helper,
`reports/` and every `.env`. Everything else is template.

## 0. Order and what this port relies on

1. **The web port goes into the template first** (owner, 2026-10-05). It brings `automation/tools/brand.py`,
   `paths.py`, `brand/triare-logo.svg` and the web skills `/qa-run`, `/qa-report`, `/qa-module`, `/qa-bug`,
   `/qa-handoff`. This repository holds **unchanged copies** of `brand.py`, `paths.py` and the logo, so the mobile
   tools run here; in the template they are the web's files — do not copy ours over them.
2. **Nothing mobile collides with the web** — the names were changed here before the port, and proven on real runs:

   | Kind | Web keeps | Mobile uses |
   |---|---|---|
   | Skills | `/qa-run`, `/qa-report`, `/qa-module`, `/qa-bug`, `/qa-handoff` | `/qa-mobile-run`, `/qa-mobile-regress`, `/qa-mobile-triage`, `/qa-mobile-report` |
   | Report tools | `summary_report.py`, `client_report.py`, `report_html.py`, `report_site.py`, `regression_run.py` | `mobile_summary.py`, `mobile_client_report.py`, `mobile_combined_report.py`, `mobile_report_data.py`, `mobile_reports.py`, `mobile_compare_runs.py`, `mobile_redact_screens.py`, `mobile_export_pdf.mjs` |
   | Brand | `brand.py` (shared: company, client, colours, logo) | `mobile_brand.py` — on top of `brand.py`: slices, two status colours, header pieces |
   | Manifest | `report:` (flat keys) | `report.mobile:` (`slices.{ios,android,all}`, `environment`, `out_of_scope`, `client_groups`, `client_blocked`) |
   | Deliverables | `reports/web/` | `reports/mobile/{ios,android,all}/`, `reports/mobile/{internal,client}.html`, `reports/mobile/README.md` |
   | Commands | `npm run qa:*`, `pw:*` | `automation/mobile/scripts/qa.sh`, `run.sh`; `uv run python mobile_*.py` |

   The mobile skills serve any app kind (native or Flutter — `APP_KIND` in `.env`). Skills for *authoring* native
   suites, if they come, take `qa-ios-*` / `qa-android-*`.
3. **`automation/tools/trace_results.py`: keep the template's version** (with `ResultsError`, the run context and
   the blocked report). The mobile tools need it; the web project's copy is older. This is the one place where the
   web sync can break the mobile reports.

## 1. Template — copy as is

| Path | What |
|---|---|
| `automation/tools/mobile_brand.py`, `mobile_combined_report.py`, `mobile_report_data.py`, `mobile_reports.py`, `mobile_client_report.py`, `mobile_compare_runs.py`, `mobile_redact_screens.py`, `mobile_export_pdf.mjs`, `ocr/ocr_lines.swift` | the mobile reports: a platform's internal site is `mobile_summary.py` (section 2), the combined one, the client's, all six at once (`--share`: the copy people get), a run against the baseline, the privacy check (macOS Vision), PDFs without packages |
| `automation/tools/import_checklist_from_csv.py` | a checklist from a CSV export of the team's sheet |
| `automation/tools/tests/test_mobile_summary.py` | the internal report's self-test (its fixtures build their own tiny project) |
| `automation/mobile/scripts/{run.sh,qa.sh,qa.py,run_context.py,start_appium.sh}` | one named run per platform with its rules; one command for a platform or both side by side; an Appium server per platform |
| `automation/mobile/scripts/recon/{dump_screen.py,app_logs.py,compare_android.py,redact_dumps.py}` | recon tools: a screen's tree, the app's own log (Flutter VM service), iOS ↔ Android tree comparison, redaction of dumps before a commit |
| `automation/mobile/helpers/{waits.py,device.py,evidence.py,reporting.py,pixels.py}`, `helpers/android/` | explicit waits, device helpers, named screenshots and video, the run's environment for Allure, pixel checks (a colour, a theme's brightness), adb: network on / off, time, permissions |
| `automation/mobile/fixtures/network.py` | offline / slow network for a test, restored after it |
| `automation/mobile/pages/base_page.py`, `screens/{__init__.py,README.md}` | the page base (gestures per platform, typing that survives the Android IME) and the screen-map mechanism with a column per platform |
| `automation/mobile/unit_tests/{android_dumps.py,test_ios_locator_guard.py}` | the offline evaluator of Android locators on recon trees; the guard that an iOS locator did not change while Android was added |
| `automation/mobile/PARALLEL-RUNS.md` §1–5 | the rule of parallel runs, the rules of use, setting it up in another project |
| `.claude/skills/qa-mobile-{run,regress,triage,report}/` | the four mobile skills |
| `docs/notes/mobile-qa-skills.md`, `mobile-qa-skills.en.md` | the owner's guide to the skills, in Ukrainian and English |
| `docs/requirements/shared/testability-contract.md` (the added section) | what the mobile build must expose to be testable |
| `qa/shared/device-matrix/README.md` | list only the devices the runs use — the reports read the P0 rows |

## 2. Template, but carries this project's words — copy, then adapt

| Path | What to adapt |
|---|---|
| `automation/tools/mobile_summary.py` | the "Scope of this run" and "How a verdict is decided" lines of the technical section name this product's environment and test data (`DEV`, `QA-AUTO-…`, a throwaway technician) — make them read from the manifest or neutral |
| `automation/tools/tests/test_mobile_reports.py` | asserts this product's names in `report.mobile.slices` — make it check "set and not a placeholder" |
| `automation/tools/mobile_redact_screens.py` | `account_names()` reads the name through this product's API helper (`FieldServicesApi.find_technicians_by_email`) — a hook the project implements |
| `automation/tools/pyproject.toml`, `uv.lock` | **union** with the web's: add `pillow`, `markdown-it-py` (the web brings `markdown`, `pyyaml`) |
| `automation/tools/README.md` | add the mobile rows and the `mobile_*` sections beside the web's; do not replace |
| `automation/mobile/config/settings.py`, `config/capabilities.py`, `.env.example` | the mechanism is template (an account and an Appium port per platform, `apply_platform()`, `run_tag`, `ANDROID_SERIAL`, emulator arguments); the comments describe this app's sign-in (phone or e-mail → OTP) |
| `automation/mobile/conftest.py` | template: `--prove-red`, a session per module on Android and its revival, the ANR guard, `chk_skipped_on`; project: the `pytest_plugins` list of this app's fixtures |
| `automation/mobile/helpers/app.py` | app control (cold start, permissions, location, theme, media) — a few names are this app's keys |
| `automation/mobile/fixtures/{app_state.py,test_data.py}` | the pattern is template (state per test through fixtures, generated users in reserved ranges, a marker the cleanup refuses to go without); the sign-in flow and the fields are this app's |
| `automation/mobile/unit_tests/{test_harness.py,test_screen_maps.py,test_android_maps.py,test_parallel_runs.py}` | the checks are template (harness helpers, map-health, the Android column, parallel settings); the module names and maps they list are this app's |
| `automation/mobile/README.md` | the sections on runs, evidence, prove-red, reports and parallel runs are template; the examples name this app's modules |
| `automation/mobile/PARALLEL-RUNS.md` §6 | this project's accounts, ports and findings (the DEV sign-in rate limit) — keep the heading, empty the values; move the finding into the lessons |
| `automation/mobile/scripts/build_shims/` | a build shim for a Flutter app with Firebase — a worked example of building the client's app without touching its repository |
| `reports/mobile/README.md` | the structure and the rebuild commands are template; the runs, links and dates are this project's |
| `setup/project.yaml` | **the structure** of `report.mobile:` and `mobile.parallel:` is template; every value is the project's |
| `qa/_templates/bug-mobile.md` | the device example line |

## 3. Shared files both stacks touch — merge by hand, add-only

The web port changes these too. Never copy ours over the template's: read the diff and add the mobile part beside
the web's.

| Path | What the mobile side adds |
|---|---|
| `CLAUDE.md` | the four `qa-mobile-*` rows in Skills; the `scripts/qa.sh`, `mobile_compare_runs.py`, `mobile_reports.py` lines in Commands |
| `setup/SETUP.md` | the pointer to `PARALLEL-RUNS.md` in the mobile setup; this file in the list of ports |
| `setup/project.yaml` | `report.mobile:` under the web's `report:`; `mobile.parallel:` |
| `.gitignore` | `automation/mobile/results/`, `automation/mobile/reports/` |
| `automation/tools/README.md`, `pyproject.toml` | see section 2 |
| `.github/workflows/mobile-android-tests.yml`, `mobile-ios-tests.yml` | this project's small fixes — compare with the web's edits of the same files |
| `automation/mobile/{README.md,conftest.py,pyproject.toml,screens/README.md,screens/__init__.py,scripts/doctor.sh}` | the web project edited these six mobile files as well (small generic fixes): three-way merge — template, web, mobile |
| `automation/tools/tests/test_brand.py` (the web's guard) | extend its tooling roots with `automation/tools/mobile_*`, `automation/mobile/scripts/`, `.claude/skills/qa-mobile-*`, and its names with `report.mobile.slices.*.{product,file_prefix}` |

## 4. Project — never copy

| Path | Why |
|---|---|
| `docs/` except the files in sections 1–2: `srs/`, `api/`, `designs/`, `environments.md`, `notes/{decisions,session-handoff,android-plan}.md`, `00-intake/` | what this product's team gave us, and our journal of it |
| `qa/mobile/<NN-module>/`, `qa/mobile/{ios,android}/`, `qa/mobile/README.md` (module index), `qa/shared/{feature-codes.md,questions/,recon-*.md,recon-dumps/,app-code-audit.md,oracles/invariants.md}`, `qa/shared/device-matrix/device-matrix.md`, `docs/platform-specs/supported-devices.md` | this product's checklists, test cases, traceability, bugs, recon, questions and devices |
| `automation/mobile/{tests,pages,screens}/` except the base and the map mechanism in section 1 | this app's screens and flows |
| `automation/mobile/fixtures/{jobs,details,check,progress,survey,notifications,profile}.py`, `fixtures/media/`, `helpers/{field_services_api.py,survey_response.py}`, `scripts/recon/recon_*.py`, `unit_tests/{test_android_pages.py,test_order_list_helpers.py,test_survey_helpers.py,ios_locators.snapshot.json}` | built on this app's API, data and screens |
| `reports/mobile/{ios,android,all}/`, `reports/mobile/{internal,client}.html` | this product's deliverables |
| `automation/mobile/{.env,results/,reports/,builds/}`, `automation/tools/.secrets/`, `_bmad-output/` | secrets and outputs; gitignored anyway |
| `app/`, `automation/mobile/results.xml`, `.claude/worktrees/`, `.playwright-mcp/` | leftovers of this project's work |

**No worked examples of this app's code go into the template** (owner, 2026-10-05): the next project reads this
repository when it needs one.

## 5. To write in the template during the port (the process, not files to copy)

| New file | From what |
|---|---|
| `automation/mobile/LESSONS.md` — what cost time on the first mobile product (the twin of `automation/web/LESSONS.md`) | `docs/notes/session-handoff.md`, `docs/notes/decisions.md`: typing on Android (set-text vs IME, the lost first key), the emulator's DNS and time zone, a sleeping Mac, a hung System UI, the banner over the first row, device time vs the machine's, a rate limit shared by everything behind one address, a phone on a cable beside the emulator |
| `automation/mobile/SECOND-PLATFORM.md` — adding a platform to a suite that already runs on the other | `docs/notes/android-plan.md`: recon of every screen → the differences as questions for the owner → the platform's column in the maps → the existing tests module by module → the platform-only tests → three identical final runs → the reports |

## 6. How to port

1. The web port is merged in the template. Make a branch there.
2. Copy section 1 paths from this repository (`rsync -a --relative <paths> <template>/`); copy and adapt section 2;
   merge section 3 by hand. Section 4 is never copied. Write section 5.
3. `git diff` in the template: every changed file is read before it is committed.
4. In the template, all green:
   `cd automation/tools && uv sync && uv run pytest` ·
   `cd automation/mobile && uv sync && uv run ruff check . && uv run python -m unittest discover -s unit_tests` ·
   `uv run pytest --platform=ios --collect-only -q` and `--platform=android` ·
   `scripts/qa.sh both all --dry-run` (with placeholders it must say why the platforms cannot run side by side,
   not crash) · the web's `npm run check`.
5. A dry "new project": clone the branch, leave `setup/project.yaml` at its placeholders — the mobile client
   report must show "Draft — not for sending", and `mobile_reports.py` without a run must end `Blocked`, never
   with an empty report.
6. `CHANGELOG.md`: the mobile entries under the new version; tag it.

How the names were before this port (for reading the journal of this project): `build_summary.py` →
`mobile_summary.py`, `build_reports.py` → `mobile_reports.py`, `mobile_report.py` → `mobile_combined_report.py`,
`report_data.py` → `mobile_report_data.py`; `client_report.py`, `compare_runs.py`, `redact_screens.py`,
`export_pdf.mjs` took the `mobile_` prefix; `/qa-run`, `/qa-regress`, `/qa-triage`, `/qa-report` → `/qa-mobile-*`;
`reports/{ios,android,mobile}/` → `reports/mobile/{ios,android,all}/`.
