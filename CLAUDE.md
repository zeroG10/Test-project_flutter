# CLAUDE.md — QA Automation Template (Web + Mobile + API)

Operating manual for every AI agent working in this repository. Read it fully before the
first action. Details live behind the links; this file holds the rules and the map.

## Project Overview

Filled by `/setup-project` from `setup/project.yaml` (values + the Discovery profile
`context:`). **If any `<…>` placeholder is still here, run
[prompts/00-discovery.md](prompts/00-discovery.md) before anything else — never guess.**

- **Project:** `<PROJECT_NAME>` — `<one line: what the product is, which stacks it has, what shares a backend>`
- **Product state:** `<existing-reachable | existing-access-pending | greenfield>` → route: `<recon-first | documents-first | api-only>`
- **Sources of truth:** `<design / SRS-PRD / user stories + AC / API spec — and which wins on conflict inside this project>`
- **Web Base URL:** `<WEB_BASE_URL>` — `BASE_URL` in `automation/web/.env`
- **Mobile app:** `automation/mobile/.env` (`PLATFORM=android|ios`, `APP_KIND=native|flutter`, package / bundle id, builds in `automation/mobile/builds/`)
- **API:** `<API_BASE_URL>` — spec in `docs/api/openapi.json` (also serves login-by-API and seeding for the UI suites)
- **Test data policy:** `<free | naming-rule | read-only-shared>` (read-only → no seeding, read-only tests)
- **Scope now:** `<platforms and modules in scope; first module and why>` — `platforms.*` in `setup/project.yaml`; module indexes in `qa/{web,mobile,api}/README.md`
- **Environments, roles, tracker:** [docs/environments.md](docs/environments.md), `setup/project.yaml → tracker:`

> ⚠️ **Never default to web.** Identify the platform from the request or ask
> ([Platform decision rules](#platform-decision-rules-for-ai-agents)).

## The automation chain

```
docs/**  ──►  <module>-checklist.md  ──►  <module>-test-cases.md  ──►  automation/*/screens  ──►  automation/*/tests  ──►  <module>-traceability.md
sources       [CHK-…] ids         TC-… (structured)   alias → locator          tagged with CHK ids      closed from run results
```

Everything above the screen map is platform-neutral; only screen maps and drivers differ.
Full conventions — layers, ID/tag contract, screen-map format, step vocabulary, determinism,
data ownership, quarantine: [automation/README.md](automation/README.md).

## Where things live

| What | Where | Guide |
|---|---|---|
| Source material (SRS / PRD / user stories, designs, API spec, notes, environments) | `docs/` (unsorted → `docs/00-intake/`) | [docs/README.md](docs/README.md) |
| QA artifacts, one folder per module per platform: analysis, checklist, automation plan, test cases, questions, rtm, traceability, coverage review, `bugs/`, `exploratory/` | `qa/{web,mobile,api}/<NN-module>/<module>-<artifact>.md` | [qa/README.md](qa/README.md), `qa/<platform>/README.md` |
| Product-level QA: feature codes, cross-cutting checklists, oracles + invariants, device matrix, risks, questions | `qa/shared/` | [qa/shared/oracles/README.md](qa/shared/oracles/README.md) |
| Templates for every artifact | `qa/_templates/` | — |
| Web harness (Playwright + TS): screens, pages, fixtures, tests, visual | `automation/web/` | [automation/web/README.md](automation/web/README.md) |
| API harness (httpx + pytest): clients, schemas, tests/{smoke,contract,security} | `automation/api/` | [automation/api/README.md](automation/api/README.md) |
| Mobile harness (Appium + pytest): screens, pages, tests/{android,ios,flutter,shared}, builds | `automation/mobile/` | [automation/mobile/README.md](automation/mobile/README.md) |
| Tools: Sheets sync (only writer), Sheets import, traceability | `automation/tools/` | [automation/tools/README.md](automation/tools/README.md) |
| Prompt templates 00–08 (+ `mobile/01–03`) | `prompts/` | this file, *Prompt Templates* |
| BMAD TEA output (test-design, test-reviews, traceability) | `_bmad-output/test-artifacts/{web,mobile}/` | commit only after review |
| Manifest + propagation map + template updates | `setup/project.yaml`, [setup/SETUP.md](setup/SETUP.md) | `/setup-project` |
| CI workflows, gate register, quarantine register | `.github/workflows/`, [.github/GATES.md](.github/GATES.md) | [.github/workflows/README.md](.github/workflows/README.md) |
| Anonymised artifacts from a past project — REFERENCE ONLY | `examples/` | [examples/README.md](examples/README.md) |

Optional modules (`setup/project.yaml → modules.*`: load_testing, visual_regression, security,
exploratory, compatibility, localization) are described in [setup/SETUP.md](setup/SETUP.md) §2b.
Don't wire or run a module whose toggle is `false`.

## QA Doctrine — when a result may be called "Passed"

Five always-on rules for every artifact, run, report and agent. Everything else here is
*how*; this is *when you are allowed to say it works*.

1. **Never fake a Pass.** "Passed" only when something objective decided it — not "no error
   was thrown", not "it looked fine", not "exit 0". If you cannot point at *what* decided
   the pass, it is not a pass.
2. **Name the oracle.** Every verdict cites its source of truth: a story's acceptance
   criterion, an SRS / PRD section, a Figma node, an API contract in `docs/api/`, an
   invariant in `qa/shared/oracles/invariants.md`, or a human. Precedence by layer: **AC /
   SRS / invariants decide behaviour, rules and permissions; Figma decides the visual layer
   (and wins over SRS there); the live product decides only what exists today** — it is
   discovery, never proof of correctness (a visible delete button proves no permission).
   These are defaults: an explicit owner decision for a project/module takes precedence
   within its recorded scope (`context.precedence_note` + `docs/notes/decisions.md`).
   With only a running product, record observations and the owner's confirmed expectations
   or explicitly accepted regression baseline; see the oracle guide below. Conflicts not
   resolved by that policy block only the affected expectation until answered. No oracle → not-run /
   needs-human, never Passed. And do not fake a Fail either: when a check goes red, first ask
   whether the expectation is wrong — a wrong expectation is a test defect (fix the check,
   file no bug). The 8 oracle types: [qa/shared/oracles/README.md](qa/shared/oracles/README.md).
3. **Blocked ≠ green; an empty run is not a passing run.** Missing credential, unreachable
   environment, crashed driver, zero tests executed, a tag filter that matched nothing, a
   skipped test, an unreadable results file — all `Blocked`, never Passed, never silently
   dropped. Say what did not run and why. Silence is not coverage.
4. **Fix the harness, never the expectation.** The app under test (and any client repo) is
   read-only. Editing an expected value, a baseline, a checklist status, or retrying a flake
   until green is fabricating a Pass — by hand or by an automation loop. An app-caused
   failure is a bug report (`prompts/08-file-bug.md`), never a test edit. A flaky test is
   quarantined with a bug id, never retried.
5. **Escalate, don't decide.** Owner-only calls: publishing to a live team Sheet
   (`qa-sheets-sync` is dry-run-first), `--reset` on a sheet, filing bugs to a tracker,
   anything destructive or irreversible, spending money. Show the situation and the
   options, then wait. Proceeding because nobody answered is a failed run.

### Status vocabulary (execution axis)

**Passed / Failed / Skipped / Blocked / (empty)**. Three are non-verdicts, never interchangeable:

- **Blocked** = *could not run* (env down, missing build, unreached screen, missing
  credential, skip inside a run). Stays owed, re-attempted next round. Comment mandatory.
- **Skipped** = *deliberately will not run* (a scoping decision). Comment mandatory.
- **(empty)** = not-run / needs-human — nobody has produced a verdict yet.
- None is EVER upgraded to Passed because the round ended. **"Partial" is a computed
  roll-up, never a status.** `Not run = total − (Passed + Failed + Skipped + Blocked)`,
  derived by subtraction. Automated verdicts (`trace_results.py`) use the same words: Passed
  only if every tagged test passed, Blocked if any skipped, empty if no tagged test exists;
  every report states its **run context** (target, build, harness commit, browsers /
  platform, run label) — a Passed is only as wide as that configuration.

> Different axis, do not mix: coverage reviews (`prompts/05`) grade *area coverage* as
> `Good / Partial / Weak / Blocked`; that vocabulary never appears in a checklist status column.

## Key Conventions

- **Source docs → `docs/`**; QA artifacts → `qa/<platform>/<NN-module>/`; AI-generated BMAD
  artifacts → `_bmad-output/test-artifacts/` (commit after review). Tests: web
  `automation/web/playwright/tests/`, mobile `automation/mobile/tests/`, API `automation/api/tests/`.
- **IDs are the contract.** Checklist items `[CHK-<FEATURE>-<NNN>]`, test cases
  `TC-<FEATURE>-<NNN>`, bugs `BUG-<FEATURE>-<NNN>`; codes pinned in
  `qa/shared/feature-codes.md`. One regex everywhere — `CHK-[A-Z]{2,5}-\d{3,}` — enforced by
  both pytest conftests, the Sheets sync and `trace_results.py`. Tags: `@CHK-…` in
  Playwright, `@pytest.mark.chk("CHK-…")` + `@allure.tag` in pytest.
- **Test cases only for automation candidates** selected by risk in `prompts/06` (ROI,
  stability, risk coverage, isolation, maintenance cost — a percentage is a sanity check,
  never a target) plus high-risk manual flows; format
  [qa/_templates/test-case-format.md](qa/_templates/test-case-format.md). UI steps use
  element **aliases**, never locators; **API steps use operations** (`METHOD /path` +
  `operationId`) taken verbatim from `docs/api/openapi.json`, never a guessed endpoint,
  field or status code. No `[AUTO]` markers in checklists.
- **Screen maps are the only place a locator lives** (`automation/web/playwright/screens/`,
  `automation/mobile/screens/`). A missing stable id is a testability defect →
  [docs/requirements/shared/testability-contract.md](docs/requirements/shared/testability-contract.md).
- **Every test owns its data**: created through a documented API when available (`apiContext` + `seed` in
  web; a fixture with `finally` in pytest), or a scoped UI fixture when no API is available. Records are uniquely
  marked and removed at the end even on failure; never dependent on what another test or run left. Read-only shared target →
  read-only tests, said so in the report.
- **Bugs follow `prompts/08-file-bug.md`** (three gates, severity walk, format from
  `qa/_templates/bug-*.md`, filing owner-confirmed). No source covers the behaviour → a
  question, not a bug.
- **`examples/` is an anonymised past project.** A role, entity, endpoint or route that exists
  only there is a fabrication in yours; cite `docs/` or write `<…>` and ask.
- **Checklist → Google Sheets, single writer.** Markdown is the source of truth.
  `automation/tools/sync_checklist_to_sheets.py` is the ONLY writer (idempotent, never
  touches status/comment columns; `--reset` owner-only, dry-run first, never in automation).
  `trace_results.py` and `import_checklist_from_sheets.py` are read-only.

## Platform decision rules (for AI agents)

| Signal in the user's prompt | Platform |
|---|---|
| "browser", "page", "URL", "responsive", "Chrome/Firefox/Safari", desktop Figma | **Web** |
| "app", "device", "iOS", "Android", "Flutter", "screen", "tap", "swipe", "push", "permissions", "deep link", APK/IPA | **Mobile** |
| "endpoint", "API", "REST", "GraphQL", "POST/GET", "schema", "status code", OpenAPI | **API** |
| Ambiguous (e.g. "login flow") | **ASK**: web, mobile, or API? |

| Platform | Language / framework | Tests | QA artifacts |
|---|---|---|---|
| Web | TypeScript / Playwright | `automation/web/playwright/tests/<module>/` | `qa/web/<NN-module>/`, `_bmad-output/test-artifacts/*/web/` |
| Mobile | Python / Appium + pytest | `automation/mobile/tests/{android,ios,flutter,shared}/` | `qa/mobile/<NN-module>/`, `_bmad-output/test-artifacts/*/mobile/` |
| API | Python / httpx + pytest | `automation/api/tests/{smoke,contract,security}/` | `qa/api/<NN-module>/` (no screen maps; steps are requests) |

**UI is the default testing priority once the UI platform is identified.** Preserve the
user-visible checks selected by the owner. API may support setup/cleanup and backend
checks inside a UI flow; standalone API tests are a separate scope choice. Neither API
coverage nor missing API access replaces or blocks independent UI checks. Record a
different project priority in the existing scope/automation plan when the owner requests it.

Cross-platform features: separate test files per stack (never share TS and Python); API
contracts documented once in `docs/api/`.

## Commands

```bash
# Web (Playwright) — BASE_URL required, no fallback
npm ci && npx playwright install && cp automation/web/.env.example automation/web/.env
npm run pw:smoke | pw:map-health | pw:test | pw:ui | pw:debug | pw:report | pw:recon
# API (httpx + pytest) — API_BASE_URL required, no fallback; a skip in CI is red
cd automation/api && uv sync && cp .env.example .env && uv run pytest -m smoke   # -m security (module)
# Mobile (Appium + pytest) — --platform is the OS; Flutter is APP_KIND in .env
cd automation/mobile && uv sync && cp .env.example .env && bash scripts/doctor.sh
bash scripts/start_appium.sh   # terminal 1
uv run pytest --platform=android -m smoke   # or --platform=ios
# Mobile, one command — a platform or both side by side (automation/mobile/PARALLEL-RUNS.md); skills: docs/notes/qa-skills.en.md (uk: qa-skills.md)
scripts/qa.sh <ios|android|both> <all|module|path> [--name N] [--sequential] [--dry-run]
# Offline self-tests — no target, no credentials; part of gate G-5
npm run test:helpers                                                 # web reporting + cleanup helpers
cd automation/api && uv run python -m unittest discover -s unit_tests # redaction helpers (unittest: needs no API_BASE_URL)
# Tools
cd automation/tools && uv sync && uv run pytest                      # offline self-test (Sheets sync + traceability)
uv run python sync_checklist_to_sheets.py --target web <checklist.md> --dry-run
uv run python compare_runs.py --platform <ios|android> ../mobile/results/<platform>/<run>   # a run vs the last final run
uv run python build_reports.py [--share] && node export_pdf.mjs                           # the test completion reports
uv run python trace_results.py --platform web --checklist <checklist.md> \
  --playwright-json ../web/playwright/test-results/results.json \
  --target "$BASE_URL" --build "<version>" --run-label "pw:test, chromium+firefox" \
  --out ../../qa/web/<NN-module>/<module>-traceability.md
```

Tags / markers: `@smoke`, `@CHK-…`, `@quarantine` (Playwright); `smoke`, `regression`,
`contract`, `security`, `chk(id)`, `quarantine`, plus `android` / `ios` / `flutter` /
`shared` (mobile). Reports: Playwright HTML + `results.json`; `allure serve allure-results`.

## AI Workflow (end to end) — with the definition of done per step

A step is not started until the previous one's *done* condition holds. Platform note:
mobile uses `prompts/mobile/01–03` instead of 01–03; API skips step 7.

| # | Step | Done when |
|---|---|---|
| 0 | Discovery — `prompts/00-discovery.md` (Step 0 of `/setup-project`) | `project.yaml → context:` / `tracker:` filled or `<unknown>`; route named; Overview above has no `<…>` the profile could fill |
| 1 | Intake — material into `docs/` ([docs/README.md](docs/README.md)); feature codes in `qa/shared/feature-codes.md` | every module in scope has a code and at least one source file (or "live product only" recorded) |
| 2 | Analysis — `prompts/01` → `<module>-analysis.md`; existing product: recon of real screens first (`pw:recon` / mobile MCP) | gaps between product, SRS and design are entries in `<module>-questions.md`, none chosen silently |
| 3 | Checklist — `/qa-checklist` or `prompts/02` → `<module>-checklist.md` | every item has a stable CHK id and an oracle; a team Sheet, if any, imported once |
| 4 | Publish — `/qa-sheets-sync` (dry-run first, owner confirms) | dry-run plan shown; push only after the go; or "markdown only" per profile |
| 5 | Candidates — `prompts/06` → `_bmad-output/test-artifacts/test-design/<platform>/` and `<module>-automation-plan.md` | each selected CHK has ROI / stability / risk scores and its blockers listed |
| 6 | Test cases — `prompts/03` → `<module>-test-cases.md` | selected CHKs linked to structured TCs; UI aliases or API operations; oracle row filled |
| 7 | Screen maps — recon harvest + testability contract + Figma → `automation/*/screens/<module>/` | every alias the TCs use resolves (`pw:map-health` green) or is listed as a testability defect |
| 8 | Tests — `prompts/07` → run → prove red once → `/bmad-testarch-test-review` | every test ran, red proven, reviewed; app failures are bugs (`prompts/08`), harness failures fixed |
| 9 | Close the loop — `trace_results.py` → `<module>-traceability.md`; `prompts/04` → `<module>-rtm.md` | report has a run context; every Failed row has a bug or a question; orphans resolved |
| 10 | Exploratory — `qa/_templates/exploratory-session.md` → `<module>/exploratory/` | findings fed forward: bugs (`prompts/08`), invariants, questions |

Strategy and risk: `/bmad-tea` (Murat), `/bmad-testarch-test-design`, `/bmad-testarch-trace`.

## Prompt Templates (REQUIRED for QA artifact generation)

When generating any QA artifact (directly or via subagents), first read the matching prompt
and use it as the instruction. Do not improvise. When dispatching to a subagent, pass the
prompt content plus the input path and the target output path.

| Task | Web / shared / API | Mobile (instead of 01–03) |
|---|---|---|
| Discover the project (Step 0) | [prompts/00-discovery.md](prompts/00-discovery.md) | same |
| Analyze SRS + design | [prompts/01-analyze-srs-and-design.md](prompts/01-analyze-srs-and-design.md) | [prompts/mobile/01](prompts/mobile/01-analyze-mobile-srs-and-design.md) |
| Generate checklist | [prompts/02-generate-checklist.md](prompts/02-generate-checklist.md) | [prompts/mobile/02](prompts/mobile/02-generate-mobile-checklist.md) |
| Generate structured test cases | [prompts/03-generate-test-cases.md](prompts/03-generate-test-cases.md) | [prompts/mobile/03](prompts/mobile/03-generate-mobile-test-cases.md) |
| Create traceability matrix (RTM) | [prompts/04-create-traceability-matrix.md](prompts/04-create-traceability-matrix.md) | same |
| Review coverage | [prompts/05-review-coverage.md](prompts/05-review-coverage.md) | same |
| Select automation candidates (by risk) | [prompts/06-select-automation-candidates.md](prompts/06-select-automation-candidates.md) | same |
| Generate automation from test cases | [prompts/07-generate-automation-from-test-cases.md](prompts/07-generate-automation-from-test-cases.md) | same |
| File a bug | [prompts/08-file-bug.md](prompts/08-file-bug.md) | same |

## Skills

| Skill | Purpose |
|---|---|
| `/setup-project` | Discovery (Step 0) + deploy the template from `setup/project.yaml` per `setup/SETUP.md` |
| `/qa-checklist` | Platform-routed checklist with stable CHK ids and live Figma pull |
| `/qa-sheets-sync` | Publish a checklist to its Google Sheet, dry-run first |
| `/qa-run` | Mobile: run a module or a test on iOS, Android or both side by side (`scripts/qa.sh`), then what is new red vs the last final run |
| `/qa-regress` | Mobile: the whole regression on a platform or both; every test compared with the baseline (`compare_runs.py`) |
| `/qa-triage` | Why a test is red or blocked: environment / test / expectation / app / no oracle — with evidence; bug drafts per `prompts/08` |
| `/qa-report` | From a regression run to the final reports: traceability, six test completion reports, PDFs, privacy check; publish only on the owner's word |
| `/bmad-tea`, `/bmad-testarch-test-design`, `/bmad-testarch-automate`, `/bmad-testarch-atdd`, `/bmad-testarch-trace`, `/bmad-testarch-test-review` | BMAD TEA (only the TEA module is installed; `bmm` skills do not exist here by design). Test review is mandatory for generated tests |
| `/bmad-advanced-elicitation`, `/bmad-review-edge-case-hunter`, `/bmad-party-mode` | Deeper critique passes used by the `qa-*` skills |

## MCP servers (project-local, `.mcp.json`) — discovery only, never the gate

`figma` (design structure + screenshots; `FIGMA_PERSONAL_ACCESS_TOKEN` in the shell env),
`playwright` (AI-driven web exploration), `mobile` (`@mobilenext/mobile-mcp`: simulator /
emulator / device via the accessibility tree; needs Xcode / Android SDK + a booted device).
Verify without a device: `python3 setup/check_mcp.py [server]`. `npx` server failing with
`MODULE_NOT_FOUND` → `rm -rf ~/.npm/_npx` (setup/SETUP.md §3). Google Sheets is not an
MCP: only the Python sync script writes to Sheets.

## CI/CD

Path-filtered workflows per stack (`web-tests.yml`, `api-tests.yml`,
`mobile-android-tests.yml`, `mobile-ios-tests.yml`, `lint.yml`); every one ends in a
`verdict` job — the only required check. Rules, gate register, quarantine register and
promotion discipline: [.github/GATES.md](.github/GATES.md). Secrets and variables
(`WEB_BASE_URL`, `APP_USER_*`, `API_*`): [.github/workflows/README.md](.github/workflows/README.md).
`retries: 0`; a skip in CI is red; `@quarantine` is the only way out of a gate.

## When Starting a New Project

Run **`/setup-project`** (Discovery → manifest → propagation → integrations → verify). Then
fill [docs/environments.md](docs/environments.md), drop the material into `docs/`, hand
[the testability contract](docs/requirements/shared/testability-contract.md) to the dev
team, update `docs/platform-specs/supported-devices.md` and
`qa/shared/device-matrix/device-matrix.md` (mobile), run `bash automation/mobile/scripts/doctor.sh`
on the mobile machine, and start the workflow above at step 1. Pull template updates later
per [setup/SETUP.md](setup/SETUP.md) §6 (`template_version` in the manifest, `CHANGELOG.md`).
