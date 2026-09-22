# QA template for AI-driven automation testing

A reusable, self-describing QA repository: **one clone per product**, three test stacks,
one document model that goes from source docs to executable, traceable automation.
Built to be operated by an AI agent (Claude Code, Cursor, Codex, Copilot) with a human owner
who decides scope, publishes results and files bugs.

```
docs/**  ──►  <module>-checklist.md  ──►  <module>-test-cases.md  ──►  screen maps  ──►  tests  ──►  <module>-traceability.md
sources       [CHK-…] ids              TC-… (structured)         alias → locator     tagged @CHK-…    closed from run results
```

Everything above the screen map is platform-neutral; only screen maps and drivers differ per platform.

## What is inside

| Stack | Platform | Tooling | Lives in |
|---|---|---|---|
| Web | browser UI | Playwright + TypeScript; recon crawler + locator harvester; screen-map health check; API seeding fixtures | `automation/web/` |
| Mobile | Android · iOS · Flutter | Appium 2 + pytest + Allure (uv); native drivers, Flutter via `Semantics(identifier:)`, opt-in flutter-integration driver | `automation/mobile/` |
| API | REST | httpx + pytest + Allure (uv); smoke / contract / security suites | `automation/api/` |
| Tools | — | checklist → Google Sheets sync (only writer), Sheets → markdown import, run results → traceability with run context | `automation/tools/` |
| Load | — | k6 smoke → load → stress (optional module) | `automation/load/` |

Plus: `docs/` (intake of SRS / PRD / user stories, designs, API spec, environments), `qa/`
(one folder per module per platform — `web/`, `mobile/`, `api/`: analysis, checklist, test
cases, bugs, traceability), `prompts/` (00 Discovery, 01–08, + `mobile/01–03` — every
artifact is generated from one of them), `qa/_templates/`, `examples/` (anonymised
artifacts from a past project, reference only), `.claude/skills/` (project skills + BMAD
Test Architect module), `.mcp.json` (Figma, Playwright and mobile MCP servers),
`.github/workflows/` (path-filtered CI per stack with a `verdict` job, gate rules,
quarantine register in `.github/GATES.md`).

Pick the stacks per project in `setup/project.yaml → platforms.*`; the unused ones stay in
place as reference and cost nothing.

## Quick start (new project)

```bash
git clone https://github.com/zeroG10/qa-template-for-AI-automation-testing.git <my-product>-qa
cd <my-product>-qa
```

1. **Discovery first** — `/setup-project` runs it as Step 0; any other agent reads
   [prompts/00-discovery.md](prompts/00-discovery.md). Ten questions, one batch: does the
   product already run, which documents exist (design / SRS or PRD / user stories) and which
   wins, platforms, first module, auth and roles, test-data policy, environments, reporting,
   tracker, decision owner. Answers go to `setup/project.yaml → context:` / `tracker:` and
   select the route (recon-first, documents-first, API-only, read-only data, …).
2. **Fill `setup/project.yaml`** — product name, platforms (`web` / `mobile` / `api`), base
   URLs, Figma file keys, mobile ids, Sheets ids. Leave what you do not know as `<PLACEHOLDER>`.
3. **Run `/setup-project`** (Claude Code) — or follow [setup/SETUP.md](setup/SETUP.md) §0–§4
   by hand with any other agent. It propagates the values into every consumer file, wires
   the integrations and verifies each one, reporting Blocked for anything it could not confirm.
4. **Drop the product material into `docs/`** (`docs/README.md` says where; unsorted →
   `docs/00-intake/`). Hand `docs/requirements/shared/testability-contract.md` to the dev team.
5. **Install the stacks you enabled**, copy every `.env.example` to `.env` (gitignored):
   ```bash
   npm ci && npx playwright install                       # web
   cd automation/mobile && uv sync && bash scripts/doctor.sh   # mobile (Xcode / Android SDK / Appium / Flutter)
   cd automation/api && uv sync                           # api
   cd automation/tools && uv sync                         # tools
   ```
   A run without a target fails loudly by design (web `BASE_URL`, api `API_BASE_URL`).

### What you need to run something today

| To run… | Required | Can wait |
|---|---|---|
| Web harness smoke: `npm run pw:smoke`, then `npm run pw:map-health` | `BASE_URL`; `APP_USER_*` credentials; the login map curated from `npm run pw:recon` | Figma, Sheets, tracker, second role, the full checklist chain |
| API smoke: `uv run pytest -m smoke` | `API_BASE_URL` + token / credentials | schemas, security module, Sheets |
| Mobile smoke: `uv run pytest --platform=android -m smoke` | a build in `automation/mobile/builds/`, app ids, Appium running | Figma, Sheets, device matrix |
| First checklist: `/qa-checklist` or `prompts/02` | one module's sources in `docs/` + its code in `qa/shared/feature-codes.md` | Sheets (publishing is a later step) |

The full chain per module, once the smoke is honest: `/qa-checklist` → `/qa-sheets-sync`
(dry-run first) → `prompts/06` (candidates by risk) → `prompts/03` (test cases) → screen
maps → `prompts/07` (tests, red once) → `trace_results.py` (traceability with run context).
Without Claude Code skills: `prompts/02` for the checklist, the CLI in `automation/tools/`
for the sync.

## For AI agents — read this first

1. **`CLAUDE.md`** is the operating manual: the QA doctrine (when a result may be called
   *Passed*), the status vocabulary, platform decision rules, the artifact chain with its
   definition of done per step, commands. Claude Code loads it automatically; other agents
   must read it before the first action.
2. **Discovery before setup.** If `CLAUDE.md` → Project Overview still shows a `<…>`
   placeholder, run `prompts/00-discovery.md` first. Never guess a profile value.
3. **Never default to a platform.** Identify web / mobile / API from the request or ask.
4. **Generate artifacts only from the prompt templates** in `prompts/` (web, shared, API)
   and `prompts/mobile/` — never improvise the instruction. Bugs included (`prompts/08`).
5. **IDs are the contract.** `[CHK-<CODE>-NNN]` in checklists, `TC-<CODE>-NNN` in test cases,
   `@CHK-…` tags in test code; codes pinned in `qa/shared/feature-codes.md`; one regex
   (`CHK-[A-Z]{2,5}-\d{3,}`) enforced by every layer.
6. **Locators live only in screen maps.** A missing stable id is a testability defect, not a
   reason for CSS/XPath.
7. **Five doctrine rules, always on:** never fake a Pass · name the oracle · Blocked ≠ green ·
   fix the harness, never the expectation · escalate, don't decide.
8. **Nothing from `examples/` is your product.** Roles, entities, endpoints and routes there
   belong to an anonymised past project; cite `docs/` or write `<…>` and ask.

## Where to go deeper

| Topic | Read |
|---|---|
| Conventions of the whole chain (layers, ID/tag contract, screen-map format, step vocabulary, determinism, data ownership, quarantine) | `automation/README.md` |
| Web harness, projects, data fixtures, adding a module, recon | `automation/web/README.md`, `automation/web/playwright/screens/README.md`, `automation/web/playwright/scripts/README.md` |
| Mobile harness, Android / iOS / Flutter strategy, markers, builds | `automation/mobile/README.md`, `automation/mobile/screens/README.md`, `automation/mobile/builds/README.md` |
| API harness, markers, strict-skip, security module | `automation/api/README.md`, `automation/api/tests/security/README.md` |
| Sheets sync, import, traceability tools | `automation/tools/README.md` |
| Where source material goes | `docs/README.md`, `docs/00-intake/README.md`, `docs/api/README.md` |
| QA artifact layout per platform, templates, oracles, device matrix | `qa/README.md`, `qa/{web,mobile,api}/README.md`, `qa/_templates/`, `qa/shared/oracles/README.md`, `qa/shared/device-matrix/README.md` |
| Discovery questions and routes | `prompts/00-discovery.md` |
| Filing a bug (gates, severity, wording, owner-confirmed filing) | `prompts/08-file-bug.md` |
| Deploying the template, value propagation map, pulling template updates | `setup/SETUP.md` |
| Checking the MCP servers actually start | `python3 setup/check_mcp.py` (see `setup/SETUP.md` §3) |
| CI gates, quarantine register and required secrets | `.github/GATES.md`, `.github/workflows/README.md` |
| Watching runs and reading reports | `docs/notes/viewing-test-runs.md` |
| Reference artifacts from a past project (anonymised) | `examples/README.md` |
| What changed between template versions | `CHANGELOG.md` |
