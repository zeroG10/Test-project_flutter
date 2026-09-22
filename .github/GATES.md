# GATES.md — CI quality-gate register

The source of truth for what actually gates a merge. A gate that isn't in this register
doesn't exist; a workflow job with no register row is a finding. Rules follow the
"QA Doctrine" section of [CLAUDE.md](../CLAUDE.md).

## Rules

1. **Required check = the `verdict` job, never an individual test job.** GitHub counts a
   SKIPPED job as a passing required check; every workflow therefore ends in a `verdict`
   job with `if: always()` that converts "didn't run" into red. In branch protection,
   require only `verdict` from each workflow.
2. **Blocked is never green.** Zero tests collected (pytest exit 5), Playwright
   "no tests found", a stray `test.only` (`forbidOnly` in CI), a crashed driver, a
   missing build, a missing credential (web preflight) — all red, never silently skipped.
   **A skip inside a CI run is red too:** the pytest stacks (`api`, `mobile`) count every
   skipped test and turn the exit code non-zero when `CI` is set (`conftest.py`,
   strict-skip; locally the same with `QA_STRICT_SKIPS=1`). A skip is a Blocked check that
   still owes a verdict — it never votes green.
3. **No gate weakening.** `continue-on-error`, `allow_failure`, `|| true` on a gate step,
   retries above 0, and `--update-snapshots` in CI are forbidden. A flake is a defect in
   the suite — fix it, or **quarantine** it (the only sanctioned way to take a test out of
   a gate): tag it `@quarantine` (Playwright) / `@pytest.mark.quarantine` (pytest) with a
   `BUG-<CODE>-NNN` id in the reason, add a row to the quarantine register below, and let
   the gate command exclude the tag (`--grep-invert @quarantine`, `-m "... and not
   quarantine"`). A quarantined test still runs locally and in non-gate runs, so the day
   it is fixed is visible; `trace_results.py` keeps counting its CHK ids as Blocked while
   it is excluded. No register row = not quarantined = the test votes.
4. **Fail-closed environments.** CI runs only against dev/staging. The api workflow
   refuses any other value before a single test runs. Production is not an input option.
5. **A gate is only a gate if it's stable.** Every new gate starts as `soaking` (runs and
   reports, but is NOT in branch protection). Promotion to `required` is an owner
   decision, logged below. A flaky required gate teaches the team to click "merge
   anyway" — after which the real red goes through too.
6. **Prove a gate can fail before trusting it.** When promoting, break something on
   purpose (delete a marker, point `--grep` at nothing) and confirm the verdict goes
   red. A gate that cannot fail is not a gate.

## Gate register

| Gate | Workflow | Covers | Explicitly does NOT cover | Trigger | Status |
|---|---|---|---|---|---|
| G-1 | `web-tests.yml` → `verdict` | Playwright E2E: `chromium` + `firefox` (signed in via `setup`, needs `APP_USER_*` secrets) and `chromium-public` + `firefox-public`; `@quarantine` excluded | `webkit` (outside the gate until the SRS names Safari — then add it here and to the workflow), `map-health`, visual baselines, a11y, performance | PR/push on `automation/web/**` | soaking |
| G-2 | `api-tests.yml` → `verdict` | pytest `-m "smoke and not quarantine"` against dev/staging; any skip = red | contract suite (`-m contract`), security (`-m security`), load | PR/push on `automation/api/**` | soaking |
| G-3 | `mobile-android-tests.yml` → `verdict` | Appium smoke on emulator (API 34) | real devices, upgrade/migration | PR/push on `automation/mobile/**` | **blocked** — APK source not wired (deliberate `exit 1` in Download step) |
| G-4 | `mobile-ios-tests.yml` → `verdict` | Appium smoke on iOS simulator | real devices, offline toggling | PR/push on `automation/mobile/**` | **blocked** — .app source not wired (deliberate `exit 1` in Download step) |
| G-5 | `lint.yml` → `verdict` | ruff (mobile+api) + tsc (web) + the offline self-tests that need no target: `automation/api/unit_tests` (reporting / redaction), `automation/tools` (Sheets sync + traceability closure), `automation/web/unit-tests` (reporting / cleanup helpers) | product behaviour (that is G-1…G-4), test quality, spec lint | every PR/push | soaking |

Statuses: `soaking` → runs and reports, not required · `required` → in branch protection ·
`blocked` → cannot produce a verdict yet (reason mandatory) · `retired` → removed, reason logged.

## Quarantine register

A test may be excluded from a gate only while it has a row here. Every row names the bug
that explains it and the owner who will bring it back. Review the register at every
promotion decision; a row older than two sprints is a finding.

| Since | Test (file / title or nodeid) | Gate | Bug | Why (flaky / blocked by defect) | Owner | Exit condition |
|---|---|---|---|---|---|---|
| | | | | | | |

## Decision log

| Date | Gate | Decision | By | Note |
|---|---|---|---|---|
| 2026-08-05 | all | Register created; all gates start as `soaking`. G-3/G-4 marked `blocked` until build sources are wired (see workflow TODOs). | — | Promotion to `required` needs an owner decision + a proven-red test (rule 6). |
| 2026-09-22 | G-5 | The offline self-tests now run in the gate: they existed but no command or workflow executed them, so a helper that leaked a secret or a traceability rule that stopped working would have gone unnoticed. A test nothing runs is not coverage (doctrine rule 3). | — | `npm run test:helpers`, `uv run python -m unittest discover -s unit_tests`, `cd automation/tools && uv run pytest` — all runnable locally too. |
| 2026-09-22 | G-1, G-2, G-3, G-4 | G-1 now runs the public projects and passes `APP_USER_*` secrets to `setup`; `webkit` removed from the CI command to match `playwright.config.ts` (outside the gate). Strict-skip in CI for the pytest stacks; `@quarantine` tag/marker + register added to every gate command. | — | Rule 6 still owed: prove each gate red once after the first real target is wired. |
