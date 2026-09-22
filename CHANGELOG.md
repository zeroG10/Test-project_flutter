# Changelog — template versions

Clones record the version they were made from in `setup/project.yaml → template_version`;
`setup/SETUP.md` §6 describes how to pull an update into a clone.

## Unreleased

- Source policy supports scoped owner overrides and a running-product + owner route:
  observations, confirmed expectations and explicitly adopted regression baselines.
- Preserve UI priority while supporting standalone API and API-assisted UI tests;
  align the API branch inside the checklist, test-case and automation prompts.
- Check cleanup responses, retain the API context through web fixture teardown and
  report failed cleanup; API examples use unique records and checked deletion.
- Redact helper diagnostics (nested secret fields, URL query values, cookies/tokens);
  configurable extra fields, unchanged response data for assertions, offline helper tests.
- Run the offline self-tests in gate G-5: they existed but nothing executed them. The
  `lint.yml` workflow now runs the API redaction helpers (`unittest`, no target needed),
  the `automation/tools` suite (Sheets sync + traceability closure, its own job) and the
  web reporting/cleanup helpers (`npm run test:helpers`). All three are runnable locally
  with no credentials, and each was proven to turn the gate red before being trusted
  (GATES.md rule 6). A test nothing runs is not coverage (doctrine rule 3).

## 1.1.0 — 2026-09-22

Mechanism defects fixed (things the doctrine promised and the code did not do):

- Web CI (`G-1`) passes `APP_USER_*` secrets to the `setup` project, runs the public
  projects, no longer runs `webkit` (outside the gate per `playwright.config.ts`); README,
  GATES register and workflow now agree.
- `trace_results.py`: an unreadable Playwright / Allure result file blocks the whole run
  (Blocked report, no verdicts, exit 1) instead of being skipped with a warning.
- pytest stacks (`api`, `mobile`): a skipped test in CI turns the exit code red
  (strict-skip); the API stack validates `@pytest.mark.chk` ids at collection like mobile.
- One canonical CHK id regex (`CHK-[A-Z]{2,5}-\d{3,}`) in trace_results, the Sheets sync
  and both conftests.
- API target fail-closed: `API_BASE_URL` empty or placeholder stops the session.

Added:

- Discovery (`prompts/00-discovery.md`; Step 0 of `/setup-project`): project profile in
  `project.yaml → context:` / `tracker:` selects the route; "minimum to run today" table.
- Bug filing process (`prompts/08-file-bug.md`) governing every bug; templates aligned
  (Actual before Expected, story/AC and gap references).
- Quarantine: `@quarantine` tag / marker, excluded from every gate command, register in
  `.github/GATES.md`.
- Run context block in traceability reports (`--target`, `--build`, `--run-label`, harness
  commit, browsers / env labels).
- Data ownership: `apiContext` + `seed` fixtures and `utils/api.ts` scaffold in the web
  harness; rule in `automation/README.md` → Determinism.
- `qa/api/` module index; `template_version` + update procedure (SETUP.md §6).
- Oracle precedence by layer (AC / SRS decide behaviour and permissions, Figma the visual
  layer, live product only what exists); story acceptance criteria as RTM rows.
- Risk-based automation selection in prompt 06 (percentage is a sanity check only).
- `CLAUDE.md` shortened to the operating manual; definition of done per workflow step.
- `examples/` anonymised (fictional product, placeholder Figma keys).

## 1.1.1 — 2026-09-22

Finishes the API branch of the chain, which 1.1.0 routed but left half-specified:

- `qa/_templates/test-cases-api.md`: request-based test cases with an *Operations used*
  table (the API analogue of *Aliases used* — a `MISSING` operation is a contract gap).
- `test-case-format.md`: second step vocabulary for API (`as`, `request`, `store`,
  `wait-for`, `expect-status`, `expect-schema`, `expect-field`, `expect-header`,
  `expect-count`), `api` in the Where table, Platforms and Automation values.
- Prompt 03: API mode — operations instead of aliases, never a guessed path, field or
  status code; `Roles` row mandatory; output to `qa/api/<NN-module>/`.
- Prompt 07: operation-resolution gate (stops on a missing operation or schema), API verb
  mapping, run command, and a pytest + httpx output skeleton including a permission/IDOR
  variant and a data-owning fixture with `finally` cleanup.
- Prompt 02, prompt 06 and the `/qa-checklist` skill route the `api` platform.

## 1.0.0 — 2026-08-05

Initial universal template: web (Playwright), mobile (Appium), API (httpx + pytest),
tools (Sheets sync, import, traceability), prompts 01–07, BMAD TEA, MCP servers, CI gates.
