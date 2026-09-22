# Web E2E — Playwright + TypeScript

Web layer of the automation chain described in [automation/README.md](../README.md).
Read that first: it defines the layers, the `[CHK-…]` tag contract and the screen-map
format this folder implements. Doctrine ("QA Doctrine" in [CLAUDE.md](../../CLAUDE.md))
applies to every run: no target → Blocked, an empty run is not a passing run.

Target: `BASE_URL` from `automation/web/.env` (dev/staging, never production) — see [docs/environments.md](../../docs/environments.md).

## Structure

```
automation/web/
├── playwright.config.ts          # fail-closed BASE_URL, retries 0, list+html+json reporters, projects below
├── .env.example                  # copy to .env (gitignored): BASE_URL, APP_USER_*, APP_MANAGER_*, API_BASE_URL, MAILBOX_*
├── README.md
└── playwright/
    ├── tests/
    │   ├── auth.setup.ts             # project `setup`: UI sign-in per role → .auth/<role>.json
    │   ├── smoke/app-loads.public.spec.ts   # harness health (@smoke), public — needs no credential
    │   └── <module>/                 # feature specs, generated from test cases (prompt 07), tagged @CHK-…
    │       ├── <screen>.public.spec.ts      # pages reachable without a session (login, forgot/set password)
    │       └── <screen>.spec.ts             # everything behind login — starts signed in as Root
    ├── screens/                  # screen maps: alias → locator (the ONLY place a locator lives)
    │   ├── README.md             # format + alias rules
    │   ├── resolve.ts            # locate() / resolveScreen() + ScreenMap / ElementSpec types
    │   ├── index.ts              # registry of curated maps (publicScreens / appScreens)
    │   ├── map-health.spec.ts    # project `map-health`: every observed alias resolves to exactly one element
    │   └── authentication/       # one folder per module, one file per screen
    │       └── login.map.ts      # scaffold (`<…>` placeholders) — the setup project signs in through it
    ├── pages/                    # page objects — behaviour only, locators via the map
    │   ├── actions.ts            # fillInput(): Ant Design inputs are readonly until focused
    │   └── authentication/login.page.ts   # scaffold page object behind the login map
    ├── fixtures/
    │   └── test-fixtures.ts      # `test` with page-object fixtures, apiContext + seed (data ownership), asManager(), state paths
    ├── utils/
    │   ├── api.ts                # apiBaseUrl(), newApiContext(), loginByApi() SCAFFOLD (Blocked until cited from openapi.json), expectStatus()
    │   ├── env.ts                # requireEnv(): a missing variable is Blocked and names itself
    │   ├── data.ts               # unique(), testEmail() (plus-addressed, TEST_MAILBOX_DOMAIN)
    │   └── mailbox.ts            # Mailbox interface + NotConfiguredMailbox (MAILBOX_PROVIDER=none)
    ├── scripts/                  # recon crawler + locator harvester → scripts/README.md
    ├── .auth/                    # storageState per role (gitignored, written by setup)
    ├── visual/                   # [module] visual regression — own README + BASELINES.md
    ├── playwright-report/        # html report (gitignored)
    └── test-results/             # traces, screenshots, results.json (gitignored)
```

Module-first: everything about one module sits in `screens/<module>/`, `pages/<module>/`,
`tests/<module>/`, mirroring `qa/web/<NN-module>/`.

## Projects (playwright.config.ts)

| Project | Runs | State | Depends on |
|---|---|---|---|
| `setup` | `**/*.setup.ts` — UI sign-in as Root (required) and Manager (optional) | writes `.auth/root.json`, `.auth/manager.json` | — |
| `chromium`, `firefox` | every spec except `*.public.spec.ts` | starts from `.auth/root.json` | `setup` |
| `chromium-public`, `firefox-public` | only `*.public.spec.ts` (login, forgot/set password, smoke) | none | — (runs before any credential exists) |
| `webkit` | like `chromium` — **outside the gate** by default; move it in if the product's SRS names Safari | `.auth/root.json` | `setup` |
| `map-health` | `playwright/screens/map-health.spec.ts` — every curated alias resolves to exactly one element (Chromium only) | `.auth/root.json`; public maps override it with a clean context | `setup` |
| `visual` | `playwright/visual/` — optional module, run explicitly | — | — |

Gate G-1 = `chromium` + `firefox` by default (Edge is Chromium; match the browsers the SRS names and
record the choice in `docs/notes/decisions.md`). CI needs the `APP_USER_*` secrets for the
authenticated projects; without them setup is red there (Blocked, loud).

## Prerequisites

- Node.js 20+ (CI pins 20), npm.
- Playwright browsers (`npx playwright install`, `--with-deps` on Linux).
- A reachable target environment — dev/staging only, never production.

## First run

```bash
npm ci                                   # from the repo root
npx playwright install
cp automation/web/.env.example automation/web/.env
$EDITOR automation/web/.env              # 1. BASE_URL (replace the whole <…> placeholder)
                                         # 2. APP_USER_EMAIL / APP_USER_PASSWORD (Root) — from the team, never from a commit
                                         # 3. optional: APP_MANAGER_*, TEST_MAILBOX_DOMAIN, MAILBOX_PROVIDER

npm run pw:smoke                                       # public smoke — works with BASE_URL alone
npm run pw:test -- --project=chromium-public           # every public spec
npm run pw:test -- --project=chromium                  # runs setup first, then the signed-in specs
npm run pw:test                                        # everything (setup, gate browsers, public, webkit)
```

What fails, and how, when something is missing:

| Missing | Result |
|---|---|
| `BASE_URL` | config throws `BASE_URL is not set — …` before any browser starts |
| `APP_USER_EMAIL` / `APP_USER_PASSWORD` | `setup` fails: `APP_USER_EMAIL is not set — Root account used for the authenticated projects. … Blocked, not green`; dependent projects do not run |
| `APP_MANAGER_*` (both empty) | setup logs `manager state NOT created …`; a spec that calls `asManager()` throws `Blocked: manager state missing — set APP_MANAGER_* and rerun setup` |
| `API_BASE_URL` | `utils/api.ts` throws at first use |
| `TEST_MAILBOX_DOMAIN` | `testEmail()` throws at first use |
| `MAILBOX_PROVIDER=none` (default) | `mailbox().waitForEmail()` throws `Blocked: mailbox not configured (see docs/notes/email-automation-setup.md)` |

Nothing skips. A skip is Blocked, not a pass.

`BASE_URL` resolution: an exported shell variable wins, then `automation/web/.env`; the
same applies to every other variable (dotenv never overrides the shell).

## Commands (run from the repo root)

| Command | What it does |
|---|---|
| `npm run pw:test` | All specs, all projects |
| `npm run pw:smoke` | Only `@smoke` — harness health, public, no credential needed |
| `npm run pw:map-health` | Screen-map health: opens every registered screen and reports each alias as ok / missing / ambiguous / hidden / conditional / placeholder (one markdown table per screen, attached to the report) |
| `npm run pw:test -- --project=chromium` | One gate browser (setup runs first) |
| `npm run pw:test -- --project=chromium-public` | Public pages only, no setup |
| `npm run pw:test -- --grep @CHK-AUTH` | Every test tagged with a CHK ID of that feature |
| `npm run pw:ui` / `npm run pw:debug` | Interactive UI mode / inspector |
| `BASE_URL=https://… npm run pw:codegen` | Recorder. `codegen` takes no config, so it reads `$BASE_URL` from the shell only (not from `.env`) |
| `npm run pw:report` | Open the last HTML report — the main way to look at a run; see [docs/notes/viewing-test-runs.md](../../docs/notes/viewing-test-runs.md) (guide, Ukrainian) |
| `npm run pw:recon -- --module <name>` | Recon crawl → draft screen maps, inventory, gaps ([scripts/README.md](playwright/scripts/README.md)) |
| `npx playwright test --config=automation/web/playwright.config.ts --project=visual` | Visual module, run explicitly (see `playwright/visual/README.md`) |

`retries: 0`, `forbidOnly` in CI, `--update-snapshots` banned in CI — see
[.github/GATES.md](../../.github/GATES.md).

## Tags

| Tag | Meaning |
|---|---|
| `@smoke` | Harness health / critical path. Proves the wiring, closes no checklist item. |
| `@CHK-<FEATURE>-<NNN>` | The checklist item(s) this test proves. One tag per CHK ID; several allowed. |

```ts
import { test, expect } from '../../fixtures/test-fixtures';

test('CHK-AUTH-018 Check that a failed sign-in shows the server error', { tag: ['@CHK-AUTH-018'] },
  async ({ loginPage }) => {
    await loginPage.open();
    await loginPage.signIn('nobody@example.invalid', 'not-the-password-12');
    await loginPage.expectError('Incorrect email or password');   // oracle named inside the helper
  });
```

A CHK ID with no tagged test is **not run** in traceability, never green. A test with a
skip inside is Blocked, not a pass — throw on a missing precondition instead of skipping.

## Auth by state

`tests/auth.setup.ts` signs in through the UI once per role (the only UI login outside the
login specs themselves) and saves the browser state; `chromium` / `firefox` / `webkit`
start from `.auth/root.json`. The success oracle shipped in the scaffold is the weakest
honest one — the URL leaves the login route and the login landmark is gone; replace it with
the landing page's own landmark once observed, citing the product's SRS section / Figma node
(`TODO(product)` in `auth.setup.ts`).

Roles ([docs/environments.md](../../docs/environments.md)):

- **Root** — `APP_USER_EMAIL` / `APP_USER_PASSWORD`, required; default state for every signed-in spec.
- **Manager** — `APP_MANAGER_EMAIL` / `APP_MANAGER_PASSWORD`, optional. In a spec:

```ts
import { test, expect, asManager } from '../../fixtures/test-fixtures';
asManager();   // whole file runs from .auth/manager.json, or throws "Blocked: manager state missing"
```

The `.auth/` folder is gitignored and regenerated per run. Credentials never appear in code.

## Screen-map workflow (layer 2 → 3)

1. Test case in `qa/web/<NN-module>/<module>-test-cases.md` names elements by alias: `login.email`, `login.submit`.
2. Recon (`npm run pw:recon`) harvests the real page into draft maps; curate them into
   `playwright/screens/<module>/<screen>.map.ts` — alias → `{ testId | role+name | label | text }`,
   named by purpose. Rules and format: [playwright/screens/README.md](playwright/screens/README.md);
   curation steps: [playwright/scripts/README.md](playwright/scripts/README.md).
   Unobserved elements stay `<…>` placeholders (they fail loudly). Missing stable ids →
   testability defect in `docs/requirements/shared/testability-contract.md`.
   Mark elements that exist only after an interaction with `state: '<name>'` (error alerts,
   revealed password) and register the map in `playwright/screens/index.ts`; then
   `npm run pw:map-health` proves every observed alias still resolves to exactly one element.
3. Page object in `playwright/pages/<module>/` exposes `el.<alias>` via `resolveScreen(page, map)`;
   it holds behaviour, never selectors. Only `expect*` helpers assert, and each names its oracle.
4. Expose the page object as a fixture in `playwright/fixtures/test-fixtures.ts`.
5. Write the spec (prompt 07 from TC + map) in `tests/<module>/`, `.public.spec.ts` if the page
   needs no session, tag it with the CHK IDs, make it run **red** once against a broken
   expectation (GATES rule 6), review with `/bmad-testarch-test-review`.

The template ships `screens/authentication/login.map.ts` as a scaffold (all `<…>`): the setup
project refuses to run until its sign-in aliases are curated, and `map-health` lists the
placeholders as Blocked. A fully curated module (maps, page objects, specs, API seeding) is in
`examples/automation/web/` — copy the pattern, not the files.

## Test data — every test owns its data

`fixtures/test-fixtures.ts` ships two data fixtures (pattern in the file header):

- **`apiContext`** — an `APIRequestContext` signed in as the primary role through
  `utils/api.ts` → `loginByApi()`. The scaffold throws `Blocked` until `loginByApi` is written
  from `docs/api/openapi.json` (cite the operation above the call); no token, no seeding.
- **`seed`** — `seed.track(cleanup, label, expectedStatus?)` registers the undo of every record the test
  created; the fixture runs the cleanups LIFO when the test ends, even on failure, and fails
  the test loudly (as a *harness* defect) if a cleanup fails — data left behind pollutes the
  next run. API cleanup callbacks must return the response; pass the documented status
  (e.g. 204) explicitly. Existing two-argument callbacks remain valid, but HTTP errors
  now fail cleanup. The API context stays open until cleanup finishes. For a UI-only
  fixture use `utils/cleanup.ts` → `cleanupRegistry()` in `try/finally`, with the page
  declared as a fixture dependency and assertions inside every UI cleanup callback.

Rules (automation/README.md → Determinism): the UI is what the test judges; prefer API
preparation when available, or a scoped UI fixture when API access is absent; every record carries a unique marker (`unique()`); no test
depends on data another test or a previous run left; a shared read-only environment
(`docs/environments.md` → *Test data and seeding*) means read-only tests and no seeding.

## Utils

- **`utils/api.ts`** — `apiBaseUrl()` (fail-closed), `newApiContext(token?)`, `loginByApi()`
  (scaffold, product-specific), `expectStatus(res, code, operation)` (throws with the
  operation and body — a seeding call that silently returns `undefined` would make the test
  judge data that does not exist). Every endpoint, field and status code comes from
  `docs/api/openapi.json` and nothing else. Cited example for one past product:
  `examples/automation/web/utils/api.ts` — copy the discipline, not the endpoints.
- **`utils/env.ts`** — `requireEnv(name, purpose)`: a missing variable throws naming itself.
- **`utils/data.ts`** — `unique(prefix)`, `testEmail()` = `qa+<unique>@<TEST_MAILBOX_DOMAIN>`.
- **`utils/mailbox.ts`** — interface for email-driven flows:
  `waitForEmail({ to, subjectMatches?, timeoutMs? }) → { subject, text, html, links }` and
  `extractLink(email, /reset-password|set-password/)`. Provider chosen by `MAILBOX_PROVIDER`
  (`none` default → every call Blocked; `mailosaur` / `mailslurp` / `imap` reserved, not implemented).
  Typical flow: seed the user via API → trigger the email → `mailbox().waitForEmail` →
  `extractLink` → open the link → assert the landing page by its own landmark.

## Run results → traceability (layer 4)

The `json` reporter writes `playwright/test-results/results.json` on every run.
`automation/tools/trace_results.py` reads it, extracts `@CHK-…` tags per test, and writes
the automated verdict per checklist item into `qa/web/<NN-module>/<module>-traceability.md`:

```bash
npm run pw:test
cd automation/tools && uv run python trace_results.py --platform web \
  --checklist ../../qa/web/<NN-module>/<module>-checklist.md \
  --playwright-json ../web/playwright/test-results/results.json \
  --target "$BASE_URL" --build "<product version or commit>" --run-label "pw:test, chromium+firefox" \
  --out ../../qa/web/<NN-module>/<module>-traceability.md
```

Only a test that ran and passed turns a CHK ID green; failed → Failed, skipped/not
collected → Blocked / not run. A `results.json` that cannot be parsed blocks the whole
report (no verdicts, exit 1). The report opens with a **Run context** block — target,
product build, harness commit, browser projects, run label — because a Passed is only as
wide as the configuration that produced it; pass `--target/--build/--run-label`, anything
omitted prints as *not recorded*. The HTML report is for humans; `results.json` is the
machine-readable oracle.

## Quarantine (the only way out of the gate)

A flaky or defect-blocked test gets `tag: ['@quarantine', '@CHK-…']` and a comment with the
`BUG-<CODE>-NNN` id, plus a row in the quarantine register of
[.github/GATES.md](../../.github/GATES.md). CI runs `--grep-invert @quarantine`; `npm run
pw:test` locally still runs it, so the day it passes again is visible. Never `retries`,
never `test.skip` to hide a flake (a skip is Blocked and still owed).

## Diagnostic data

`utils/reporting.ts` and `utils/api.ts` → `expectStatus()` redact sensitive fields before reporting.
Tokens, cookies, passwords and common secret fields are masked recursively; add product
fields through `QA_REDACT_FIELDS` (comma-separated names, including personal-data fields
where needed). Request URL query values and credentials are hidden. Unstructured bodies
are omitted; JSON is redacted before truncation. Assertions receive the original response.
Use these helpers instead of printing raw response bodies in assertion messages.
This does not sanitise arbitrary test prints, framework exception introspection, browser
traces, screenshots or videos; handle those artifacts according to the project data policy.

Offline helper checks (from the repository root, after `npm ci`; no browser, no target,
no report files). They run in CI as part of gate G-5 (`.github/workflows/lint.yml`), so a
helper that starts leaking a secret or a cleanup that stops checking its response turns the
gate red.

```bash
npm run test:helpers
```
