# Prompt 07 — Generate Automation from Test Cases

## Purpose

Turn a structured test-case file (layer 1) into test code (layer 3) for the platform's stack,
resolving UI aliases through screen maps (layer 2), or API operations through the contract. One test per TC, tagged with
the CHK IDs it proves, so `automation/tools/trace_results.py` can close the loop. Nothing here
interprets requirements: the TC is the spec, the map is the only source of locators.

Read [automation/README.md](../automation/README.md) first (IDs and tags, screen-map format,
determinism rules) and [.github/GATES.md](../.github/GATES.md) (rules 2, 3, 6).

## When to Use

- After `03-generate-test-cases.md` produced `qa/{web|mobile|api}/<NN-module>/<module>-test-cases.md`
- After the screen map(s) for the screens in that file exist (or to find out exactly which aliases are still missing)
- When expanding the suite for a feature that already has TCs (re-run; existing tests are updated, not duplicated)

## Input Required

- Test cases: `qa/{web|mobile|api}/<NN-module>/<module>-test-cases.md` (`<NN-module>` = module folder in SRS order, `<module>` = the feature slug from `qa/shared/feature-codes.md`; Mode A structured format — a `-manual-suite.md` file is NOT an input)
- Screen maps for every screen the TCs touch (UI platforms only — an API TC has no screens):
  - web: `automation/web/playwright/screens/<screen>.map.ts`
  - mobile: `automation/mobile/screens/<screen>_map.py`
  - api: `docs/api/openapi.json` instead — the contract every operation, field and status code
    in the TC is resolved against, plus `automation/api/schemas/` for `expect-schema` rows
- Fixtures: `automation/web/playwright/fixtures/` or `automation/mobile/fixtures/test_data.py`; env pointers in `docs/environments.md`; secrets only via `.env`
- Existing tests for the feature (to update in place): `automation/web/playwright/tests/<feature>/` or `automation/mobile/tests/{android|ios|shared}/test_<feature>.py`
- Harness you build on (read, do not bypass):
  - web: `automation/web/playwright/screens/resolve.ts` (`locate(page, el)`), `screens/README.md`, `fixtures/test-fixtures.ts` (project `test` object + auth-by-state pattern), `pages/*.page.ts`, `playwright.config.ts` (`retries: 0`, `forbidOnly`, JSON reporter → `playwright/test-results/results.json`), `automation/web/README.md`
  - mobile: `automation/mobile/screens/` (`Screen`, `El`, `resolve`, `locator_for`), `pages/base_page.py` (`tap`, `type`, `visible`, `wait_gone`, `expect_text`, `assert_open`), `helpers/waits.py`, `conftest.py` (`--platform`, `driver` + `platform` fixtures, `chk` id validation), `pyproject.toml` markers (`chk` is registered), `automation/mobile/README.md`
  - api: `automation/api/clients/base_client.py` (`ApiClient` — `get/post/put/patch/delete`, Allure-logged), `conftest.py` (`api` fixture, fail-closed target, `chk` id validation, CI strict-skip), `helpers/schema_validator.py` (`validate_schema`), `helpers/retry.py`, `schemas/`, `pyproject.toml` markers, `automation/api/README.md`

---

## Project overrides (read first)

1. **UI aliases resolve through the map; API operations through the contract (Step 1).** Before writing any code, resolve every alias in the TC file against the platform map(s). If ANY alias is missing, output the "Missing aliases" list (alias · screen · TC IDs · platform) and STOP. A missing alias is a testability / screen-map gap, handled through `docs/requirements/shared/testability-contract.md` — never by inventing a locator, guessing a test id, or falling back to text/CSS/XPath in the test.
2. **Never edit an expectation to make a test pass.** If a generated test fails on the app's behaviour, the result is a bug report written per `prompts/08-file-bug.md` (three gates, severity walk, format from `qa/_templates/bug-{web,mobile}.md`, filed under `qa/{web|mobile|api}/<NN-module>/bugs/`) with the TC and CHK IDs, and the test stays red. If the failure is a harness problem (wrong locator in the map, fixture, timing), fix the harness. If the TC's expectation itself is wrong (the oracle was misread), say so and send it back to prompt 03 — do not silently rewrite it (doctrine rules 1 and 4).
3. **No sleeps.** Web-first assertions / explicit waits on map elements only; `wait-for` rows become `expect(...).toBeHidden()` / WebDriverWait, never `sleep`. `retries: 0`.
4. **Auth by state.** Preconditions like "logged in as {{user.email}}" become `storageState` / API login / token injection / deep link — never a UI login sequence, except in the TC that proves login itself.
5. **One test per TC**, title = `<CHK-ID(s)> <TC title>`, tags = every Source CHK ID plus the priority tag (`@smoke` for P0, `@regression` for P1/P2, `@edge` for P3), per automation/README.md. Tests must be independent and parallel-safe; cleanup from the TC's Postconditions row goes into `afterEach` / a fixture, never into the next test.
6. **Run it, report the real result.** Run the generated tests against the environment named in `docs/environments.md` (dev/staging only — GATES rule 4). Report exactly what ran: passed / failed / blocked (env down, missing build, zero tests collected = red). An empty run is not a passing run.
7. **Prove red once (GATES rule 6).** For every new test, break one expectation deliberately (wrong expected text, wrong route), confirm the test fails, restore it, confirm it passes. Record the proof in the report. A test that cannot fail is not a test.
8. **Then hand to review.** Finish by invoking `/bmad-testarch-test-review` on the new files; flip `Automation` in the TC file to `automated(<platform>)` only after the review and a green run.
9. **Harness prerequisites are harness work.** A missing page object for a screen (mobile: a thin `BasePage` subclass with `screen = <MAP>`; web: a `*.page.ts` over `locate()`), a missing data fixture, or the `storageState` setup project are added in the stack, never inline in a test — and listed under "Harness changes" in the report. Never weaken a gate to get green (no `continue-on-error`, no `|| true`, no `test.only`, no `retries`).

---

## Prompt

```
You are a Senior Automation Engineer. Generate test code from the structured test cases below, using screen maps for UI aliases or the API contract for API operations. Follow the chosen platform branch only; the test case supplies the expected behaviour.

Platform: [web | android | ios | flutter | api]
Stack: [web: Playwright + TypeScript → automation/web/playwright/tests/<feature>/<feature>.spec.ts | mobile: Appium + Python + pytest → automation/mobile/tests/{android|ios|shared}/test_<feature>.py | api: httpx + Python + pytest → automation/api/tests/{smoke|contract|security}/test_<feature>.py]
Feature: [feature-name] — feature code: [CODE]
Environment: [dev | staging, from docs/environments.md]

Test cases:
[Paste qa/{web|mobile|api}/<NN-module>/<module>-test-cases.md]

Platform inputs:
[UI: screen maps for the used screens. API: relevant docs/api/openapi.json operations and automation/api/schemas/ files; no screen maps.]

Fixtures available:
[Paste fixture names and the helper that provides auth by state]

Existing tests for this feature (if any):
[Paste, or "none"]

## Step 1 — Resolve UI aliases or API operations

Apply only the matching branch below. API-only tests do not resolve screen maps.

**UI:** List every alias in every TC (steps + <screen>.root + open targets). Resolve each against the map for this platform.

Output:

### Alias resolution
| Alias | Screen | Map entry | Locator kind (role / testId / accessibility id / resource-id) | TC IDs |

### Missing aliases
| Alias | Screen | TC IDs | Platform | Needed id per testability contract |

If the Missing aliases table has any row: STOP here. Do not generate code for any TC that uses a missing alias. Report which TCs are blocked and which could be generated (only if the user asks to proceed with the resolvable subset).

**API TCs resolve operations instead of aliases.** List every `METHOD /path` the TCs use and resolve each against `docs/api/openapi.json`; list every `expect-schema` row against `automation/api/schemas/`.

### Operation resolution
| Operation | operationId | In spec | Request schema | Response schema | TC IDs |

### Missing operations / schemas
| Operation or schema | TC IDs | Why missing (not in spec / schema not written yet) | Owner |

Same gate, same reason: an operation the spec does not contain is a contract gap for the product owner, and a missing schema is harness work. STOP rather than guess a path, a field name or a status code — a guessed endpoint produces a test that proves nothing and can even mutate real data.

## Step 2 — Map each step to code

Verb → code (web: `locate(page, <screen>.elements.<alias>)` gives the Locator; mobile: a `BasePage` subclass per screen, alias strings):
- open <screen>            → page.goto(<screen>.route) / deep link or navigation helper of the page object
- click <alias>            → locate(...).click() / page.tap("<alias>")
- fill <alias> <data>      → locate(...).fill(data) / page.type("<alias>", data) (+ page.hide_keyboard() before the next tap)
- select <alias> <data>    → locate(...).selectOption(data) / picker helper on the page object
- swipe <alias> <dir>      → (mobile) helpers/gestures.py on page.find("<alias>")
- scroll-to <alias>        → locate(...).scrollIntoViewIfNeeded() / gestures scroll helper
- back                     → page.goBack() / driver.back()
- wait-for <alias> hidden  → expect(locate(...)).toBeHidden() / page.wait_gone("<alias>")
- expect-visible <alias>   → expect(locate(...)).toBeVisible() / page.visible("<alias>") — for <screen>.root: page.assert_open() (the map's anchor must be `root`)
- expect-hidden <alias>    → expect(locate(...)).toBeHidden() / page.wait_gone("<alias>")
- expect-enabled/-disabled → expect(locate(...)).toBeEnabled() / .toBeDisabled() / assert page.find("<alias>").is_enabled() is True/False
- expect-text <alias> <expected> → expect(locate(...)).toHaveText(expected) (toContainText when the TC says "contains:") / page.expect_text("<alias>", expected) (contains-semantics — use `page.text("<alias>") == expected` for exact)
- expect-url <screen>      → expect(page).toHaveURL(<screen>.route) (web only; mobile TCs use expect-visible <screen>.root)

API verbs (pytest + httpx; `api` fixture = `ApiClient`, one response object per request row):
- as <role>                     → select a fixture-owned client carrying that role's token (`ApiClient(token=...)`); `token=""` explicitly selects anonymous access instead of the default token. Missing required role credentials are Blocked, never anonymous fallback. Keep clients open until dependent cleanup completes.
- request METHOD /path <data>   → `response = client.request("<METHOD>", "<path>", ...)`, using the client selected by the latest `as` row. Interpolate path parameters; query parameters use `params=`, JSON body uses `json=`, form data uses `data=`, uploads use `files=` only when specified by the contract. Do not send query values as a JSON body. With no data, omit those arguments.
- store <field> {{name}}        → bind the value from the parsed body into a local variable used by later steps
- wait-for METHOD /path <cond>  → a state-polling helper with a deadline and interval, created as harness work only when needed; `helpers/retry.py` retries transport failures and is not a state poll
- expect-status <code>          → `expect_status(response, <code>, "METHOD /path")` from `helpers.reporting`; diagnostics are redacted, the response used by assertions is unchanged
- expect-schema <file>          → `validate_schema(response.json(), load_schema("<file>"))`
- expect-field <path> <value>   → assert on the parsed body at that path (`absent` → assert the key is not present; `type: x` → assert the type)
- expect-header <name> <value>  → `assert response.headers["<name>"] == <value>` (or `in` for `contains:`)
- expect-count <path> <n>       → assert the length of the resolved collection (e.g. `len(body["items"])`); resolve nested field/index segments explicitly, never treat the whole dotted path as a literal key or use `eval`

Data placeholders ({{user.email}}) come from fixtures; never inline a literal credential. Only expect-* rows become assertions. Preconditions become fixtures / beforeEach (auth by state, seeded data via API helpers); Postconditions become afterEach cleanup (API: a fixture whose teardown runs in `finally`, so a failed step still removes what the test created).

## Step 3 — Emit the files

One test per TC, in TC-ID order, following the skeleton for the stack (below). Title and tags carry the Source CHK IDs. Group tests of one feature in one file (web: one spec per feature; mobile: shared/ for cross-platform TCs, android/ or ios/ for platform-only TCs; api: `tests/smoke/` for P0 round-trips, `tests/contract/` for schema-focused TCs, `tests/security/` for permission and IDOR TCs). Update existing tests for the same TC ID in place; never create a second test for the same TC.

## Step 4 — Run and prove

1. Run the new tests only — web, from the repo root: `npm run pw:test -- --grep @CHK-<CODE> --project=chromium` (JSON results land in `automation/web/playwright/test-results/results.json`); mobile, from `automation/mobile/`: `uv run pytest --platform=<android|ios> tests/<shared|android|ios>/test_<feature>.py` (Appium server running; a missing build or dead server is reported as Blocked by the driver fixture); api, from `automation/api/`: `uv run pytest tests/<smoke|contract|security>/test_<feature>.py` (an unset `API_BASE_URL` stops the session as Blocked before any request).
2. Report per TC: Passed / Failed / Blocked, with the reason for anything not green. Zero tests collected is a failed run.
3. Prove red once per new test: break one expectation, run, confirm red, restore, run, confirm green. Record "red proven" per TC.
4. A failure caused by the app → draft a bug report per prompts/08-file-bug.md (qa/{web|mobile|api}/<NN-module>/bugs/) with TC + CHK IDs, leave the test red; filing to a tracker waits for the owner's go. A failure caused by the harness → fix the harness. A wrong expectation → send the TC back to prompt 03; do not edit the assertion to pass.

## Step 5 — Report

### Generated
| TC ID | CHK IDs | File | Test title | Run result | Red proven |

### Blocked / not generated
| TC ID | Reason (missing alias / fixture / env) | Owner |

### Harness changes
- [resolver helper added / marker registered / fixture added — file paths]

### Next
- `/bmad-testarch-test-review` on the generated files; then flip `Automation` in the TC file to automated(<platform>).
```

---

## Output skeleton — Playwright (web)

`automation/web/playwright/tests/<feature>/<feature>.spec.ts`

```ts
import { test, expect } from '../../fixtures/test-fixtures'; // project test object — never '@playwright/test' directly
import { login } from '../../screens/login.map';             // alias → locator: the ONLY place a locator lives
import { dashboard } from '../../screens/dashboard.map';
import { locate } from '../../screens/resolve';              // locate(page, el) → Locator (role/label → testId → text)

// {{user.email}} / {{user.password}} come from automation/web/.env. Fail closed — never test.skip().
const user = { email: process.env.APP_USER_EMAIL ?? '', password: process.env.APP_USER_PASSWORD ?? '' };

test.describe('AUTH — login', () => {
  test.beforeAll(() => {
    if (!user.email || !user.password) throw new Error('APP_USER_EMAIL / APP_USER_PASSWORD not set — Blocked');
  });
  // TC-AUTH-001 proves login itself, so it starts logged out. Every other TC keeps the
  // storageState from the auth setup project (fixtures/test-fixtures.ts) — no UI login.
  test.use({ storageState: { cookies: [], origins: [] } });

  test(
    'CHK-AUTH-003 CHK-AUTH-004 Sign in with valid credentials lands on the dashboard', // TC-AUTH-001
    { tag: ['@CHK-AUTH-003', '@CHK-AUTH-004', '@smoke'] },
    async ({ page }) => {
      await page.goto(login.route);                                                 // open login
      await expect(locate(page, login.elements.root)).toBeVisible();                // expect-visible login.root
      await locate(page, login.elements.email).fill(user.email);                    // fill login.email {{user.email}}
      await locate(page, login.elements.password).fill(user.password);              // fill login.password {{user.password}}
      await locate(page, login.elements.submit).click();                            // click login.submit
      await expect(locate(page, login.elements.spinner)).toBeHidden();              // wait-for login.spinner hidden
      await expect(locate(page, dashboard.elements.root)).toBeVisible();            // expect-visible dashboard.root
      await expect(locate(page, dashboard.elements['user-menu'])).toHaveText(user.email); // expect-text dashboard.user-menu
      await expect(page).toHaveURL(new RegExp(`${dashboard.route}$`));              // expect-url dashboard
    },
  );
});
```

Rules baked in: no `waitForTimeout`; no inline selectors (an alias absent from the map is a
`tsc` error, which is the intended failure); `test.only` forbidden (CI `forbidOnly`);
`retries: 0`; cleanup from the TC's Postconditions row in `afterEach`.

## Output skeleton — pytest + Appium (mobile)

`automation/mobile/tests/shared/test_<feature>.py`

```python
import allure
import pytest

from fixtures.test_data import SAMPLE_USER      # {{user.email}} / {{user.password}}; secrets stay in .env
from pages.dashboard_page import DashboardPage  # thin BasePage subclass: screen = DASHBOARD (harness work if missing)
from pages.login_page import LoginPage          # behaviour only; every locator lives in screens/login_map.py


@pytest.mark.shared
@pytest.mark.smoke
@pytest.mark.chk("CHK-AUTH-003", "CHK-AUTH-004")   # validated at collection; exported for trace_results.py
@allure.tag("CHK-AUTH-003", "CHK-AUTH-004")
@allure.title("CHK-AUTH-003 CHK-AUTH-004 Sign in with valid credentials lands on the dashboard")  # TC-AUTH-001
def test_login_valid_credentials(driver, platform):
    login = LoginPage(driver, platform)
    dashboard = DashboardPage(driver, platform)

    # open login — the driver fixture starts the app fresh (logged out); no UI logout dance
    login.assert_open()                                          # expect-visible login.root (map anchor = "root")
    login.type("email", SAMPLE_USER["email"])                    # fill login.email {{user.email}}
    login.type("password", SAMPLE_USER["password"])              # fill login.password {{user.password}}
    login.hide_keyboard()
    login.tap("submit")                                          # click login.submit (tap)
    login.wait_gone("spinner")                                   # wait-for login.spinner hidden — explicit wait, no sleep
    dashboard.assert_open()                                      # expect-visible dashboard.root (mobile form of expect-url)
    dashboard.expect_text("user-menu", SAMPLE_USER["email"])     # expect-text dashboard.user-menu
```

Rules baked in: no `time.sleep` (every `BasePage` action is an explicit `WebDriverWait`); an
unknown alias raises `LookupError` at resolution — the intended failure; a skipped, deselected
or uncollected test is Blocked, never Passed (pytest exit 5 is red); cleanup from Postconditions
in a fixture; `@pytest.mark.android` / `ios` only for TCs whose Platforms row is a single OS.

---

## Output skeleton — pytest + httpx (API)

`automation/api/tests/smoke/test_<feature>.py` (contract-focused TCs → `tests/contract/`,
permission / IDOR TCs → `tests/security/`)

```python
import json
from pathlib import Path
from uuid import uuid4

import allure
import pytest

from helpers.reporting import expect_status
from helpers.schema_validator import validate_schema

SCHEMAS = Path(__file__).resolve().parents[2] / "schemas"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


@pytest.fixture
def order(api):
    """Preconditions + Postconditions of the TC: the test owns its data.

    Every operation and field below is taken from docs/api/openapi.json — cite the
    operationId in a comment. The teardown runs in `finally`, so a failed step still
    removes what was created (automation/README.md → Determinism).
    """
    # POST /orders — operationId createOrder, body OrderDraftDto
    marker = f"qa-order-{uuid4().hex}"
    response = api.post("/orders", json={"name": marker})
    expect_status(response, 201, f"POST /orders [test-data:{marker}]")
    created = response.json()
    assert isinstance(created, dict) and created.get("id"), f"Missing created id; recover {marker}"
    # Register cleanup as soon as the created id is known, before further assertions.
    # If creation has an unexpected response with no usable id, record the unique marker
    # for recovery; never claim that cleanup succeeded.
    try:
        yield created
    finally:
        # DELETE /orders/{id} — operationId deleteOrder
        deleted = api.delete(f"/orders/{created['id']}")
        expect_status(deleted, 204, f"DELETE /orders/{created['id']}")  # contract status
        # A failed delete is reported; never remove other tests' records as a fallback.


@pytest.mark.smoke
@pytest.mark.chk("CHK-ORD-010", "CHK-ORD-011")     # validated at collection; read by trace_results.py
@allure.tag("CHK-ORD-010", "CHK-ORD-011")
@allure.title("CHK-ORD-010 CHK-ORD-011 A created order is readable with status Draft")  # TC-ORD-001
def test_created_order_is_readable(api, order):
    # request GET /orders/{id} — operationId getOrder
    response = api.get(f"/orders/{order['id']}")

    expect_status(response, 200, "GET /orders/{id}")        # expect-status 200
    body = response.json()
    validate_schema(body, load_schema("order.schema.json"))  # expect-schema order.schema.json
    assert body["status"] == "Draft"                         # expect-field status Draft
    assert "secret" not in body                              # expect-field secret absent
```

Permission / IDOR TCs (`as` rows) take a second client instead of the shared `api` fixture:

```python
@pytest.mark.security
@pytest.mark.chk("CHK-ORD-030")
@allure.tag("CHK-ORD-030")
@allure.title("CHK-ORD-030 Another user cannot read someone else's order")  # TC-ORD-005
def test_other_user_cannot_read_order(api, order, api_as_other_user):
    # as other-user → request GET /orders/{id} (operationId getOrder)
    response = api_as_other_user.get(f"/orders/{order['id']}")
    # The contract says 404, not 403 (it hides existence) — cite the spec; guessing
    # between the two is a common false Fail.
    expect_status(response, 404, "GET /orders/{id}")
```

Rules baked in: no `time.sleep` (a `wait-for` row uses a bounded state-polling helper);
an unset `API_BASE_URL` stops the session as Blocked before any request; a skipped test is
red in CI (strict-skip); a malformed `chk` id fails collection; every endpoint and field is
cited to `docs/api/openapi.json`, never guessed; the test removes the data it created.

---

## Tips

- "Missing aliases" is the normal first output on a new feature — send the table to the dev team via the testability contract, fill the map, re-run this prompt.
- UI is the default priority: preserve selected user-visible validation, permission and business flows. API may prepare data or verify backend effects in the same UI test. Standalone API coverage lives in `automation/api/` when in scope; it does not replace the selected UI checks. With no API access, use independent UI checks and documented UI fixtures rather than inventing endpoints.
- After the review, close the loop from `automation/tools/`: `uv run python trace_results.py --platform web --checklist ../../qa/web/<NN-module>/<module>-checklist.md --playwright-json ../web/playwright/test-results/results.json --target "$BASE_URL" --run-label "<what ran>" --out ../../qa/web/<NN-module>/<module>-traceability.md` (mobile: `--platform mobile --allure-dir ../mobile/allure-results`; api: `--platform api --allure-dir ../api/allure-results`). The report is the automated verdict per CHK ID plus the run context that bounds it; it never writes to Sheets.
