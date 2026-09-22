# Automation chain — conventions (read before writing any test artifact)

One template, three stacks, one document model. Platform differences live ONLY in
the last two layers (screen maps + drivers). Everything above them is shared.

```
SRS / Figma / notes  ──►  checklist  ──►  test cases  ──►  screen map  ──►  test code  ──►  run results
docs/**                   qa/*/<module>/   qa/*/<module>/   automation/*/screens  automation/*/tests   qa/*/<module>/
                          …-checklist.md   …-test-cases.md  alias → locator       tagged with CHK IDs  …-traceability.md
                          [CHK-…] IDs      TC-… IDs                                                    closes the loop
```

QA artifacts live per module: `qa/{web,mobile}/<NN-module>/<module>-<artifact>.md`
(`NN` = order in the SRS, `<module>` = the slug registered in `qa/shared/feature-codes.md`,
e.g. `qa/web/01-authentication/authentication-checklist.md`).

## Layers

| # | Layer | Where | Who writes it | Platform-specific? |
|---|---|---|---|---|
| 0 | Checklist, every check has a stable `[CHK-<FEATURE>-<NNN>]` | `qa/{web,mobile}/<NN-module>/<module>-checklist.md` | prompt 02 / `qa-checklist` | no (mobile has extra sections) |
| 1 | Structured test case, ONLY for automation candidates + high-risk manual | `qa/{web,mobile}/<NN-module>/<module>-test-cases.md` | prompt 03 (structured format, see `qa/_templates/test-case-format.md`) | no — steps use element **aliases** |
| 2 | Screen map: alias → locator per platform | `automation/web/playwright/screens/`, `automation/mobile/screens/` | human + AI from testability contract | **yes** |
| 3 | Test code | `automation/web/playwright/tests/`, `automation/mobile/tests/` | prompt 07 from TC + screen map, then reviewed | **yes** |
| 4 | Traceability closure from run results | `automation/tools/trace_results.py` → `qa/{web,mobile}/<NN-module>/<module>-traceability.md` | script | no |

Which checklist items become test cases is decided by risk (prompt 06: business impact,
repeatability, stability, isolation, maintenance cost) — not by a quota. In practice that
lands around 10–20 % for a UI module and can be far higher for a stable API; the number is a
sanity check, never a target. UI is the default priority for selected user-visible
validation, permission and business flows. API can prepare data and check backend effects
inside those UI tests; standalone checks live in `automation/api/` when in scope. A
project may choose a different focus explicitly; API coverage does not silently replace UI.

## IDs and tags (the contract between layers)

- Checklist item: `[CHK-AUTH-001]`. Feature code = 2–5 uppercase letters from the slug
  (`authentication → AUTH`). A project keeps its codes in `qa/shared/feature-codes.md`.
- **Canonical id regex, one contract everywhere: `CHK-[A-Z]{2,5}-\d{3,}`.** Enforced at
  collection time by `automation/api/conftest.py` and `automation/mobile/conftest.py`
  (a malformed id fails the run), by `sync_checklist_to_sheets.py` when parsing a checklist,
  and by `trace_results.py` when reading run output. An id that one layer accepts and another
  ignores would be a silently "not run" check — that is why the pattern is pinned here.
  Numbers are zero-padded to three digits and may grow beyond 999 (`CHK-AUTH-1000`).
- Test case: `TC-AUTH-001`, lists its source CHK IDs. One TC may cover several CHK IDs.
- Test code carries the CHK IDs it proves, in a machine-readable place:
  - Playwright: `test('CHK-AUTH-001 Check that …', { tag: ['@CHK-AUTH-001', '@smoke'] }, …)`
  - pytest (mobile/api): `@pytest.mark.chk("CHK-AUTH-001")` + `@allure.tag("CHK-AUTH-001")`
- `trace_results.py` reads the run output, extracts CHK IDs from tags, and writes the
  automated verdict per CHK ID. A CHK ID with no tagged test is **not run**, never green.

## Screen map format

Aliases are `screen.element`, lower-kebab, stable across platforms. The map is the ONLY
place a locator lives; page objects and generated tests resolve aliases through it.

Web — `automation/web/playwright/screens/<module>/<screen>.map.ts`:
```ts
export const login = {
  id: 'login', route: '/login',
  elements: {
    email:  { testId: 'login-email' },
    submit: { role: 'button', name: 'Sign in' },
    error:  { testId: 'login-error', state: 'failed-sign-in' },   // exists only after that state
  },
} as const satisfies ScreenMap;
```
`state` marks an element that is not on the screen at first paint. Every curated map is
registered in `screens/index.ts`, and `npm run pw:map-health` (project `map-health`) opens
each registered screen and proves that every observed alias resolves to exactly one element —
the first thing to run after the app's markup changes.
Mobile — `automation/mobile/screens/<screen>_map.py`:
```python
LOGIN = Screen(
    id="login",
    elements={
        "email":  El(android=("id", "com.example.app:id/login_email"), ios=("accessibility id", "login-email")),
        "submit": El(android=("accessibility id", "login-submit"),     ios=("accessibility id", "login-submit")),
    },
)
```
Flutter apps expose `Semantics(identifier: …)` as `resource-id` (Android) and
`accessibilityIdentifier` (iOS) since Flutter 3.19, so the SAME map format and the
native drivers (UiAutomator2 / XCUITest) work on release builds. The Flutter
integration driver is an opt-in fallback for debug builds only.

Locator priority (web and mobile): role/label → test-id / accessibility id → text.
Never structural CSS or XPath. Missing ids are a testability defect → `docs/requirements/shared/testability-contract.md`.

## Test-case step vocabulary

Steps are `action | target alias | data | expected`. Actions (platform-neutral):
`open`, `click` (tap on mobile), `fill`, `select`, `swipe`, `scroll-to`, `back`, `wait-for`,
`expect-visible`, `expect-hidden`, `expect-text`, `expect-enabled`, `expect-disabled`, `expect-url`.
Data placeholders come from fixtures: `{{user.email}}`, `{{order.id}}`. Never literal secrets.

**API test cases use a second vocabulary**, because a step is a request and not a screen
action: `as`, `request`, `store`, `wait-for`, `expect-status`, `expect-schema`,
`expect-field`, `expect-header`, `expect-count`. The target of a request row is the
operation exactly as `docs/api/openapi.json` writes it (`METHOD /path`, `operationId`); an
operation missing from the spec is a contract gap, never a guessed endpoint — the same
discipline that makes a missing alias a testability defect.

Full format, both vocabularies and an example: `qa/_templates/test-case-format.md`.

## Determinism rules (also enforced by `.github/GATES.md`)

- No `sleep`; web-first assertions / explicit waits only. `retries: 0` in CI.
- **Quarantine instead of retry.** A flaky or defect-blocked test is tagged `@quarantine`
  (Playwright) / `@pytest.mark.quarantine` (pytest) with a `BUG-<CODE>-NNN` id in the reason
  and a row in the quarantine register of `.github/GATES.md`; the gate command excludes the
  tag. It keeps running outside the gate. No register row = the test votes.
- Auth by state (API login, `storageState`, deep link), UI login only in the one smoke test that proves it.
- **Every test owns its data.** A test creates what it needs (prefer a documented API when available — web:
  `fixtures/test-fixtures.ts` `apiContext` + `seed*` fixtures; pytest: a fixture with a
  `finally`), tags it with a unique marker (`utils/data.ts` `unique()`), never depends on
  data another test or a previous run left behind, and removes it when it ends — even on
  failure. Shared-environment etiquette (what may be created or deleted, concurrent users)
  is recorded in `docs/environments.md` → *Test data and seeding* before the first seeding
  fixture is written; a target where data may not be touched means read-only tests only.
  Without an API, a scoped UI fixture may prepare/clean up test-owned records using
  observed screen maps and agreed expectations. Check the cleanup outcome, retain the
  record identifier for recovery, and never delete unrelated/shared records. An explicit
  failed cleanup is a harness failure; process termination may still require recovery.
- Every generated test must run red at least once against a broken expectation before it is trusted
  (GATES rule 6). Generated code is reviewed with `/bmad-testarch-test-review` before merge.
- A skip is `Blocked`, never a pass; zero tests collected is red. In CI a skip inside a
  pytest run is red too (`conftest.py` strict-skip; `QA_STRICT_SKIPS=1` locally).
- Every traceability report states its **run context** (target, build, harness commit,
  browsers / platform, run label — `trace_results.py --target/--build/--run-label`). A
  Passed verdict is only as wide as that configuration; what is not listed was not tested.
