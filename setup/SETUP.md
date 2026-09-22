# SETUP.md — how to deploy this template for a new project

This file is the **map** an AI agent (or a human) follows when configuring a fresh
clone of this template. The values themselves live in [project.yaml](project.yaml)
— fill that first (or let `/setup-project` ask you). This file tells you **where
each value goes** and **which integrations to wire up**.

> Entry point: run the **`/setup-project`** skill. It runs Discovery (§0), reads
> `project.yaml`, asks for anything still `<PLACEHOLDER>`, propagates values using
> the tables below, and verifies each integration. Any other agent (Cursor, Codex,
> Copilot) follows this file by hand: §0 → §1 → §2 → §3 → §4.

---

## 0. Discovery — the project profile (before any value is propagated)

Run [prompts/00-discovery.md](../prompts/00-discovery.md): ten questions, one batch,
answers written into `project.yaml → context:` and `tracker:`. The profile selects the
route through the template (routes table in that prompt) — recon-first for an existing
product, documents-first for greenfield, `qa/api/` chain for API-only, read-only tests
for a shared environment, no filing step when there is no tracker. `<unknown>` is allowed
and blocks only the steps that depend on it. Never guess an answer; never re-interview a
project whose profile is already filled.

**Minimum to run something today** (everything else can wait for the route that needs it):

| To run… | You need | Optional until later |
|---|---|---|
| web harness smoke (`npm run pw:smoke`) | `web.base_url` → `BASE_URL`; the login map curated from recon; `APP_USER_*` for the authenticated projects | Figma, Sheets, tracker, second role |
| API smoke (`uv run pytest -m smoke`) | `api.base_url` → `API_BASE_URL`, a token or credentials | schemas, security module, Sheets |
| mobile smoke | a build in `automation/mobile/builds/`, `PLATFORM`, app ids, Appium running (`doctor.sh`) | Figma, Sheets, device matrix |
| the first checklist (prompt 02) | one module's sources in `docs/` + its code in `feature-codes.md` | Sheets (publishing is a later step) |

## 1. Value propagation map (manifest key → consumer files)

| `project.yaml` key | Consumer file(s) | What to change |
|---|---|---|
| `template_version` | — | Version of the template this clone was made from; see §6 before pulling updates |
| `context.*` | `CLAUDE.md` (Project Overview: product state, sources of truth + precedence, scope, first module, data policy), `docs/environments.md` (Product, Roles, Test data), `qa/{web,mobile,api}/README.md` (first module row) | Propagate the profile; a `<unknown>` stays visible as `<unknown>` |
| `tracker.*` | read live by `prompts/08-file-bug.md` (no propagation) | — |
| `project.name` | `CLAUDE.md` (Project Overview) | Replace `<PROJECT_NAME>` |
| `project.name`, `project.repo_name`, `project.description` | `package.json` | `name`, `description` |
| `project.name` | `_bmad/core/config.yaml`, `_bmad/tea/config.yaml`, `_bmad/config.toml` | `project_name` (all three — `<PROJECT_NAME>` placeholder) |
| *(your name)* | `_bmad/core/config.yaml`, `_bmad/tea/config.yaml`, `_bmad/config.user.toml` | `user_name` (all three — `<USER_NAME>` placeholder) |
| `web.base_url` | `automation/web/.env` (+ GitHub repository variable `WEB_BASE_URL`) | `BASE_URL` — required; the config throws without it |
| `web.base_url` | `CLAUDE.md` (Project Overview), `docs/environments.md` | Web Base URL line; environments table |
| `web.figma.*` | `docs/designs/web/figma-sources.md` | File section: name, fileKey, URL, main page node. Then extend the screen map as you analyze screens. |
| `mobile.kind` | `automation/mobile/.env` | `APP_KIND=flutter` if flutter (`FLUTTER_DRIVER=native` by default, `integration` only for debug builds) |
| `mobile.android.*` | `automation/mobile/.env` | `ANDROID_APP_PACKAGE`, `ANDROID_APP_ACTIVITY` (+ `ANDROID_APP_PATH` once you have a build) |
| `mobile.ios.bundle_id` | `automation/mobile/.env` | `IOS_BUNDLE_ID` (+ `IOS_APP_PATH`) |
| `mobile.figma.*` | `docs/designs/mobile/figma-sources.md` | Same as web figma-sources |
| `api.base_url`, `api.env_label` | `automation/api/.env`, `docs/environments.md` | `API_BASE_URL`, `API_ENV`; environments table |
| `sheets.web.*` | `automation/tools/.env` | `WEB_SHEET_ID`, `WEB_WORKSHEET`, `WEB_ID_COL`, `WEB_OBSOLETE_COL` |
| `sheets.mobile.*` | `automation/tools/.env` | `MOBILE_SHEET_ID`, `MOBILE_WORKSHEET`, `MOBILE_ID_COL`, `MOBILE_OBSOLETE_COL` |
| *(feature list)* | `qa/shared/feature-codes.md` | Seed one row per feature (`slug | code | platform`) before the first sync — codes are the Sheets contract |

`.env` files are created by copying the matching `.env.example` in the same
directory (`automation/web/`, `automation/api/`, `automation/mobile/`, `automation/tools/`).
They are gitignored — never commit them.

## 2. Platform toggles

If `platforms.<stack>` is `false` in the manifest:

- **Skip** that stack's `.env` and config steps entirely.
- Optionally delete its CI workflow from `.github/workflows/`
  (`web-tests.yml` / `api-tests.yml` / `mobile-*-tests.yml`) — they are
  path-filtered, so leaving them is harmless but noisy.
- Leave the folder structure in place (it costs nothing and keeps the
  template's conventions intact).

## 2b. Optional modules (`modules.*`)

Each `modules.<name>` toggle in the manifest gates an optional QA capability. When
a module is `false`, `/setup-project` **skips its config and verify entirely** and
offers to delete its scaffold folder from the clone. When `true`, do the "wire"
column and run the "verify" column.

| Module | Scaffold (delete if disabled) | Wire (if enabled) | Verify |
|---|---|---|---|
| `load_testing` | `automation/load/` | `brew install k6`; set the SLA header + real endpoints in `runs.md` / `scenarios/` | `LOAD_ENV=staging BASE_URL=<url> k6 run automation/load/scenarios/smoke.js` |
| `visual_regression` | `automation/web/playwright/visual/` | pin capture env in `BASELINES.md`; add `*.visual.spec.ts` | `npx playwright test automation/web/playwright/visual/` (first run creates baselines — review + log them) |
| `security` | `automation/api/tests/security/`, `qa/shared/checklists/checklist-owasp-top10.md` | set `USER_A_TOKEN`, `USER_B_TOKEN`, `IDOR_RESOURCES`, `IDOR_RESOURCE_IDS` in `automation/api/.env` | `cd automation/api && uv run pytest -m security` (IDOR tests skip-loud until configured — a skip is `blocked`, not a pass) |
| `exploratory` | `qa/_templates/exploratory-session.md` | — (discipline only) | copy the template per session into `qa/{web,mobile}/<NN-module>/exploratory/<date>-<charter>.md` |
| `compatibility` | uses existing `qa/shared/device-matrix/` | fill the tiered matrix (P0/P1/P2/OUT) | matrix reviewed + owner-signed |
| `localization` | none yet (planned) | — | — |

Modules are independent of `platforms.*` but a module may assume a stack: e.g.
`security` and `load_testing` need `platforms.api`; `visual_regression` needs
`platforms.web`. If a module is on but its stack is off, flag it in the report.

## 3. Integrations checklist

### Figma MCP (design analysis)
- Project-local server `figma` is configured in [.mcp.json](../.mcp.json);
  it reads `FIGMA_PERSONAL_ACCESS_TOKEN` from the shell environment.
- Get a PAT: figma.com → Settings → Security → Personal access tokens
  (read scope for the design files is enough).
- Record the design files in `docs/designs/{web,mobile}/figma-sources.md` —
  agents read `fileKey` + `node-id` from there and never need fresh links.
- **Verify:** call `mcp__figma__get_figma_data` with the fileKey from the
  manifest; it should return the document tree.

### Playwright MCP + Mobile MCP (AI-driven exploration)
- Both are project-local servers in [.mcp.json](../.mcp.json): `playwright`
  (`@playwright/mcp`) for web, `mobile` (`@mobilenext/mobile-mcp`) for iOS
  simulators / Android emulators / real devices via the accessibility tree.
- Mobile MCP needs a booted simulator or emulator (`xcrun simctl boot …` /
  `emulator -avd …`) and the same Xcode / Android SDK that `doctor.sh` checks.
- **Verify (all three servers at once, read-only, no device needed):**
  ```bash
  python3 setup/check_mcp.py            # or: python3 setup/check_mcp.py mobile
  ```
  It starts each server exactly as an agent would, sends `initialize` + `tools/list`
  and prints one row per server. A server that starts and then dies on a broken
  dependency looks healthy to every other check and fails only here.
  Then, with a device: Playwright — `browser_snapshot` of `BASE_URL`; Mobile —
  `mobile_list_available_devices` and see the booted simulator/emulator.
- **`mobile` MCP is also a row in the mobile doctor:** `bash automation/mobile/scripts/doctor.sh --with-mcp`
  (opt-in — a cold npx cache downloads the package). It is WARN at worst: the server is a
  discovery channel, never the gate.
- **Troubleshooting `npx`-based servers** (`playwright`, `mobile`). Symptom: the agent
  reports the server as failed/`CONNECTION_CLOSED`, and running the command by hand prints
  `Error: Cannot find module …` / `MODULE_NOT_FOUND`. Cause: a partially-extracted package
  in the shared npx cache — not your config, not a missing SDK. Fix:
  ```bash
  rm -rf ~/.npm/_npx          # cache only; every package is re-downloaded on demand
  python3 setup/check_mcp.py  # re-verify
  ```
- These servers are for exploratory sessions (`qa/_templates/exploratory-session.md`)
  and for reading real screens while authoring screen maps. They never replace
  the Playwright / Appium suites as the gate.

### Google Sheets (checklist publishing)
- The ONLY live-sheet writer is
  [automation/tools/sync_checklist_to_sheets.py](../automation/tools/sync_checklist_to_sheets.py)
  (see CLAUDE.md "single writer" rule). `--reset` wipes statuses — owner-only.
- Auth: Google Cloud service account with Sheets API enabled. Put its JSON key
  at `automation/tools/.secrets/credentials.json` (gitignored). Share each
  target spreadsheet with the service-account email as **Editor**.
- **Verify:** `cd automation/tools && uv sync && uv run python
  sync_checklist_to_sheets.py <any checklist .md> --target web --dry-run`
  → must print a plan and write nothing.

### Playwright (web E2E)
- `npm ci` at repo root, then `npx playwright install`; `cp automation/web/.env.example automation/web/.env` and set `BASE_URL`.
- **Verify:** `npm run pw:smoke` (harness-health smoke against `BASE_URL`; without `BASE_URL` it must fail loudly).

### API tests
- `cd automation/api && uv sync`, fill `.env`.
- **Verify:** `uv run pytest -m smoke` (example health test).

### Mobile (Appium — Android, iOS, Flutter)
- `bash automation/mobile/scripts/doctor.sh` — Xcode, Android SDK/emulator, Appium + drivers, Flutter (if `APP_KIND=flutter`), uv. Fix every MISSING item first.
- `cd automation/mobile && uv sync`, fill `.env` (`PLATFORM`, `APP_KIND`, ids), drop the build into
  `automation/mobile/builds/{android,ios,flutter}/`.
- Start server: `bash scripts/start_appium.sh`.
- **Verify:** `uv run pytest --platform=android -m smoke` (or `--platform=ios`).

## 4. Post-setup hygiene (what /setup-project also does)

- Reset the BMAD configs → `project_name`, `user_name` (see §1 — three files each).
  Only the **TEA** module is installed; there is no `_bmad/bmm/`.
- Confirm `examples/` content (sample SRS / checklists from a past project,
  if present) is understood to be **reference only** — new artifacts go into
  `docs/` and `qa/` per the platform rules in CLAUDE.md.
- Fill `docs/environments.md`; hand `docs/requirements/shared/testability-contract.md` to the dev team;
  point the team at `docs/README.md` for where source material goes.
- Run through CLAUDE.md "When Starting a New Project" and confirm every step
  is done; update `docs/platform-specs/supported-devices.md` and
  `qa/shared/device-matrix/device-matrix.md` with the real support policy.
- Leave `setup/project.yaml` filled-in and committed — it documents the
  project's wiring for every future agent session.

## 5. What must NEVER be auto-run

- `sync_checklist_to_sheets.py --reset` — wipes the sheet data zone including
  statuses. Owner decision, dry-run first, never from a skill or CI.
- `examples/checklist-gen/**` — scaffold-only generator kept as an example;
  requires an explicitly configured `SPREADSHEET_ID` and an explicit user request.
- `examples/**` in general is reference-only content from a past project — see
  [examples/README.md](../examples/README.md). Never treat it as current
  requirements.

## 6. Pulling template updates into a clone

Every product is a separate clone, so a fix in the template does not reach a project by
itself. The clone records `template_version` in `project.yaml`; the template tags its
releases (`vX.Y.Z`) and keeps a `CHANGELOG.md` at the root.

```bash
git remote add template https://github.com/zeroG10/qa-template-for-AI-automation-testing.git
git fetch template --tags
git log --oneline v<current>..v<latest> -- automation/ prompts/ qa/_templates/ .github/ setup/ CLAUDE.md
```

Then either `git merge template/main` (clean clones with few local edits) or cherry-pick
the commits you need. What is safe to take blindly: `automation/tools/`, `automation/*/`
harness code that your project has not curated (fixtures, config, conftest), `prompts/`,
`qa/_templates/`, `.github/`. What always needs a look: `CLAUDE.md` Project Overview,
`setup/project.yaml`, curated screen maps, `.env.example` keys you renamed. After the
merge: bump `template_version`, run the offline checks (`cd automation/tools && uv run
pytest`, `npx tsc --noEmit`, `ruff check` in api/mobile) and the stack smokes, and log
the update in `docs/notes/decisions.md`.
