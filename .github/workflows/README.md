# CI Workflows

Each stack has its own workflow. **Path filters** ensure a workflow runs only when its stack's files change — so editing a mobile test never triggers Playwright, and vice-versa.

## Workflows

| Workflow | Trigger paths | Runner | What it does |
|---|---|---|---|
| [web-tests.yml](web-tests.yml) | `automation/web/**`, root `package*.json` | `ubuntu-latest` | Installs Playwright + browsers, runs the gate projects (`chromium`, `firefox` signed in via `setup`; `chromium-public`, `firefox-public` for login/forgot-password/smoke) against `WEB_BASE_URL`, `@quarantine` excluded; `webkit` (outside the gate by default), `visual` (optional module) and `map-health` (harness check) are not run here |
| [api-tests.yml](api-tests.yml) | `automation/api/**` | `ubuntu-latest` | uv sync → pytest `-m "smoke and not quarantine"` against `API_BASE_URL` secret; any skip inside the run is red (CI strict-skip) |
| [mobile-android-tests.yml](mobile-android-tests.yml) | `automation/mobile/**` | `ubuntu-latest` + KVM emulator | Boots Android emulator, runs Appium pytest |
| [mobile-ios-tests.yml](mobile-ios-tests.yml) | `automation/mobile/**` | `macos-14` | Boots iOS simulator, runs Appium pytest |
| [lint.yml](lint.yml) | all PRs | `ubuntu-latest` | ruff (Python) + tsc (TypeScript) + the offline self-tests that need no target: API reporting/redaction helpers, the `automation/tools` suite (Sheets sync + traceability), the web reporting/cleanup helpers |

All workflows also support `workflow_dispatch` (manual trigger from the Actions tab).

## Quality gates

Every workflow ends in a **`verdict` job** — the only job branch protection should
require (GitHub counts a skipped job as a passing required check; `verdict` runs
always and turns "didn't run" into red). The gate register — what each gate covers,
its soaking/required status, and the promotion rules — lives in
[.github/GATES.md](../GATES.md).

## Required GitHub Secrets

Set these under **Repo → Settings → Secrets and variables → Actions**:

| Secret | Used by | Purpose |
|---|---|---|
| `APP_USER_EMAIL` / `APP_USER_PASSWORD` | web-tests | **Required.** Primary account; `tests/auth.setup.ts` signs in once and saves the storage state every authenticated project starts from. The preflight step fails the run when either is empty — Blocked, not green |
| `APP_MANAGER_EMAIL` / `APP_MANAGER_PASSWORD` | web-tests | Optional second, lower-privilege role for permission checks (`asManager()`). Set **both or neither** — half-set is a configuration error |
| `API_BASE_URL` | api-tests | API endpoint to test |
| `API_TOKEN` | api-tests | Auth token for API |

Rules that apply to every workflow (from `.github/GATES.md`):

- **No skip is green in CI.** The pytest stacks (`api`, `mobile`) turn any skipped test into
  a red exit code when `CI` is set (`conftest.py`, strict-skip). Playwright counts a skip as
  Blocked in `trace_results.py`. A skip is a Blocked check that still owes a verdict.
- **Quarantine, never retry.** A flaky or defect-blocked test is tagged `@quarantine`
  (Playwright) / `@pytest.mark.quarantine` (pytest) with a `BUG-<CODE>-NNN` id in the reason,
  listed in the quarantine register in `GATES.md`, and excluded from the gate command. It keeps
  running locally so the day it is fixed is visible.

## Required repository variables

Set these under **Repo → Settings → Secrets and variables → Actions → Variables**
(not secrets — a target URL is not sensitive and should be readable in logs):

| Variable | Used by | Purpose |
|---|---|---|
| `WEB_BASE_URL` | web-tests | Target URL for Playwright (`BASE_URL`). The preflight step fails the run if it is empty — a run without a target is Blocked, not green (GATES.md rule 2) |

For mobile, you'll likely need additional secrets when wiring up real build artifacts:
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` — if APKs/IPAs are in S3
- `FIREBASE_TOKEN` — if using Firebase App Distribution

## ⚠️ Before mobile workflows can pass

Both `mobile-android-tests.yml` and `mobile-ios-tests.yml` have a **TODO** step that downloads the build artifact (`.apk` / `.app`). It currently `exit 1`s by design — replace it with your real source:

```yaml
# Example: from another job in the same workflow run
- uses: actions/download-artifact@v4
  with:
    name: app-debug-apk
    path: automation/mobile/builds/android/

# Example: from S3
- run: aws s3 cp s3://artifacts/${{ github.sha }}/app-debug.apk builds/android/app-debug.apk
```

You also need to populate `automation/mobile/.env` (or set the same keys as env vars) so `ANDROID_APP_PACKAGE` / `ANDROID_APP_ACTIVITY` / `IOS_BUNDLE_ID` match the build you're testing.

## Cost note

- `ubuntu-latest` is the cheapest runner (free for public repos, billed for private).
- `macos-14` is **10× more expensive** per minute on private repos. Run iOS tests sparingly:
  - Consider scheduling iOS smoke nightly instead of on every PR.
  - Use path filters aggressively to avoid wasting macOS minutes on non-mobile PRs.

## How to test locally before pushing

Each workflow's commands map to local commands documented in:
- [automation/web/README.md](../../automation/web/README.md) — `npm run pw:test` (needs `BASE_URL`, see `.env.example`)
- [automation/api/README.md](../../automation/api/README.md) — `uv run pytest`
- [automation/mobile/README.md](../../automation/mobile/README.md) — `uv run pytest --platform=...`

The offline part of the lint gate runs anywhere, with no target and no credentials:

```bash
npm run test:helpers                                            # web reporting + cleanup helpers
cd automation/api   && uv run python -m unittest discover -s unit_tests   # redaction helpers
cd automation/tools && uv run pytest                            # Sheets sync + traceability
```
