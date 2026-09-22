# Environments and access — `<PROJECT_NAME>` (pointers only, NO secrets)

Filled by `/setup-project` from `setup/project.yaml` (`web.*`, `api.*`, `mobile.*` and the
Discovery profile `context.*` — prompts/00-discovery.md) and by hand after the kickoff.
Credentials live ONLY in the gitignored `.env` files (`automation/web/.env`,
`automation/mobile/.env`, `automation/api/.env`) — this file says *which variable*, never *the value*.

## Product

`<One paragraph: what the product is, which stacks exist (web SPA / mobile app / API), which
share a backend, who the user roles are.>`

## Environments

| Env | Web | Mobile build | API | Purpose | Data reset |
|---|---|---|---|---|---|
| dev | `<WEB_BASE_URL>` | `automation/mobile/builds/<platform>/<file>` (source: `<where builds come from>`) | `<API_BASE_URL>` (spec: `docs/api/openapi.json`) | **automation target** | `<scheduled reset / seed script / none — ask>` |
| staging | | | | | |
| prod | — | — | — | never tested by automation (`.github/GATES.md` rule 4) | — |

Reachability note: `<is the target reachable from GitHub-hosted runners without VPN? checked YYYY-MM-DD>`.

## Roles and test accounts

| Role | Env vars | Can | Cannot |
|---|---|---|---|
| `<primary / admin role>` | `APP_USER_EMAIL` / `APP_USER_PASSWORD` (web) · `APP_USER_*` (mobile) | | |
| `<second, lower-privilege role>` | `APP_MANAGER_EMAIL` / `APP_MANAGER_PASSWORD` — optional; both or neither | | |

> Record here any place where the UI names a role differently from the API — that is a
> product decision to test against, not a defect, once the team confirms it.

Login mechanics: `<email + password / OTP / SSO — which endpoint or screen, verified YYYY-MM-DD>`.
Account activation / password recovery: `<via email link? see docs/notes/email-automation-setup.md>`.

## Browsers, devices, viewport

- Web: `<browsers and versions from the SRS>`; gate projects in `automation/web/playwright.config.ts`.
- Mobile: `docs/platform-specs/supported-devices.md` (product policy) → `qa/shared/device-matrix/device-matrix.md` (what we test on).
- Viewport / responsive rules: `<min–max width, tablet, mobile web?>`.

## Known environment constraints (observed by automation)

`<Slow bundle, rate limiting, flaky endpoints, shared-DEV etiquette — with the date observed
and what the harness does about it (workers, timeouts). Retries stay 0 by policy.>`

## Test data and seeding

- Policy (`project.yaml → context.test_data.policy`): `<free | naming-rule | read-only-shared | unknown>`.
  `read-only-shared` = no seeding fixtures, read-only tests only, and the report says so.
- Endpoints usable for seeding/cleanup (from `docs/api/openapi.json`): `<list>`.
- Data rules: `<unique marker convention; what may be created/deleted; cleanup at test end
  (fixtures/test-fixtures.ts → seed); scheduled reset / seed script if any>`.

## Open questions (answers go to `qa/shared/questions/` or the module's `*-questions.md`)

- Can test data be freely created and deleted on the target env? Does anyone else use it concurrently?
- Is there a scheduled DB reset or seed script?
- Which test accounts exist per role, and who owns them?
