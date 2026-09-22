# Test cases — structured format (layer 1 of the automation chain)

Read [automation/README.md](../../automation/README.md) first: checklist → **test case** →
screen map → test code → traceability. This file defines the test-case layer.

## Purpose — what gets a test case, and what does not

A test case (TC) exists ONLY for:

1. **Automation candidates** — checklist items selected by
   `prompts/06-select-automation-candidates.md`. Prompt 07 turns each TC into one test.
2. **High-risk manual checks** — items prompt 06 marked `Manual Only` but with High risk
   coverage (payments, destructive actions, permissions boundaries, data integrity), where a
   human needs an exact reproducible script, not a one-line check.

Everything else stays a checklist item (`qa/{web,mobile,api}/<NN-module>/<module>-checklist.md`) and is executed from the Sheet.
Selection is by risk (prompt 06), never by quota: a UI module usually lands around 10–20 %
of its checklist, a stable API module can be far higher. A full manual suite (every
checklist item → a TC) is produced only on explicit request (prompt 03, Mode B) and is
saved as a separate `<feature>-manual-suite.md` so it never mixes with this format.

## Where

| Platform | File (one per feature, TCs in ID order) | Template |
|---|---|---|
| web | `qa/web/<NN-module>/<module>-test-cases.md` | [test-cases-web.md](test-cases-web.md) |
| mobile | `qa/mobile/<NN-module>/<module>-test-cases.md` | [test-cases-mobile.md](test-cases-mobile.md) |
| api | `qa/api/<NN-module>/<module>-test-cases.md` | [test-cases-api.md](test-cases-api.md) |

`<NN-module>` is the module folder (`NN` = order in the SRS), `<module>` the slug registered in
[qa/shared/feature-codes.md](../shared/feature-codes.md); the file sits next to the checklist
it comes from (e.g. `qa/web/01-authentication/authentication-test-cases.md`).
A feature shipping on several platforms gets one file per platform. Web and mobile share the
steps (aliases are platform-neutral); the mobile file carries the extra device/app-state rows.
**API is the one exception to the alias model:** an API step is a request and its target is an
operation from `docs/api/openapi.json`, not a screen element — see *Step vocabulary — API*.

## The format

Every TC is a `##` section: a metadata table, a steps table, postconditions, notes.

```
## TC-<FEATURE>-<NNN> — <title>

| Field | Value |
|---|---|
| ID | TC-<FEATURE>-<NNN> |
| Title | <what is proven, one line, action-oriented> |
| Source CHK IDs | CHK-<FEATURE>-<NNN>[, …] — the checklist items this TC proves |
| Platforms | web \| android \| ios \| flutter \| api (comma-separated, all where the TC applies) |
| Priority | P0 \| P1 \| P2 \| P3 |
| Automation | candidate \| automated(web) \| automated(android) \| automated(ios) \| automated(flutter) \| automated(api) \| manual |
| Preconditions | state + fixture refs, e.g. `{{user.email}}` exists and is active; logged out |
| Oracle | `<type> — <source>` per qa/shared/oracles/README.md, e.g. `spec — SRS §4.2`, `spec — figma:12-345`, `invariant — INV-3` |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|

**Postconditions / cleanup:** …
**Notes:** …
```

Rules for the metadata:

- **ID** `TC-<FEATURE>-<NNN>`: `<FEATURE>` is the code from
  [qa/shared/feature-codes.md](../shared/feature-codes.md) (same code as the
  checklist it comes from); `<NNN>` is zero-padded, monotonic across the file, never
  reused. On regeneration read the existing file and preserve IDs.
- **Source CHK IDs** is mandatory. One TC may prove several CHK IDs; a CHK ID may be
  proven by several TCs. Test code is tagged with these CHK IDs, and
  `automation/tools/trace_results.py` closes the loop through them.
- **Priority**: P0 = smoke, must pass on every run · P1 = release regression · P2 = full
  suite / nightly · P3 = edge, scheduled.
- **Automation** starts as `candidate`; prompt 07 flips it to `automated(<platform>)` when
  the test exists and has run; `manual` is for the high-risk manual TCs (oracle = human, or
  hardware / payment / store behaviour).
- **Preconditions** describe state, never how to reach it by UI. Auth is by state
  (API login, `storageState`, deep link) — UI login appears only in the TC that proves login.
- **Oracle** names what decides the verdict (doctrine rule 2). No oracle → the TC is not
  ready. `human` as oracle ⇒ Automation must be `manual`.

## Step vocabulary (copied from automation/README.md — keep in sync)

Steps are `action | target alias | data | expected`. One row = one action. Actions
(platform-neutral): `open`, `click` (tap on mobile), `fill`, `select`, `swipe`,
`scroll-to`, `back`, `wait-for`, `expect-visible`, `expect-hidden`, `expect-text`,
`expect-enabled`, `expect-disabled`, `expect-url`.
Data placeholders come from fixtures: `{{user.email}}`, `{{order.id}}`. Never literal secrets.

How the columns are used per verb:

| Action | Target (alias) | Data | Expected |
|---|---|---|---|
| `open` | screen alias (`login`) — resolves to the route (web) or deep link / navigation (mobile) | — | short prose (what appears) |
| `click` / `fill` / `select` | element alias | value or `{{fixture}}` (`click`: —) | short prose or — |
| `swipe` | element / list alias | direction: `up` `down` `left` `right` | short prose or — |
| `scroll-to` | element alias (may be parametrised) | — | — |
| `back` | — | — | short prose (where you land) |
| `wait-for` | element alias | — | `visible` or `hidden` |
| `expect-visible` / `expect-hidden` / `expect-enabled` / `expect-disabled` | element alias | — | `visible` / `hidden` / `enabled` / `disabled` (restated) |
| `expect-text` | element alias | — | the exact text or `{{fixture}}` (substring allowed, say so: `contains: …`) |
| `expect-url` (web only; mobile: `expect-visible <screen>.root`) | screen alias | — | the route, for the human reader |

**Only `expect-*` rows produce assertions in generated code.** Prose in the Expected
column of interaction rows is guidance for the manual tester, not an oracle. Keep TCs at
3–12 steps; more than that is two scenarios.

## Step vocabulary — API (`qa/api/…`, template [test-cases-api.md](test-cases-api.md))

An API TC has no screens and no aliases. Steps are
`action | target operation or field | data | expected`; the target of a request row is the
operation **exactly as `docs/api/openapi.json` writes it** (`METHOD /path`, `operationId` in
parentheses). Actions:

| Action | Target | Data | Expected |
|---|---|---|---|
| `as` | role name (`admin`, `owner`, `other-user`) | — | prose: which identity the following requests carry. Changing identity mid-TC is how permission and IDOR cases are written |
| `request` | `METHOD /path` (`operationId`) | request body / query as `{{fixture}}`, path parameter as `{{entity.id}}`, or `—` | prose or `—` |
| `store` | response field path (`id`, `data.items[0].id`) | the placeholder it binds (`{{order.id}}`) | — |
| `wait-for` | `METHOD /path` polled | the condition (`status == Ready`) | `within <n>s` — a bounded poll, never a sleep |
| `expect-status` | — | — | the code (`200`, `403`) |
| `expect-schema` | — | — | schema file in `automation/api/schemas/` |
| `expect-field` | field path | — | value, `{{fixture}}`, `absent`, or `type: string` |
| `expect-header` | header name | — | value or `contains: …` |
| `expect-count` | collection path (`items`) | — | the number |

Rules that differ from UI TCs:

- **Never invent an operation, a field or a status code.** Anything not in the spec is a
  contract gap: list it in *Operations used* as `MISSING` and raise it in the module's
  `<module>-questions.md`. Prompt 07 stops rather than guess a path.
- **Identity is explicit.** Every TC names its `Roles`; a permission TC uses `as` to switch.
  A 403/404 expectation says which of the two the contract specifies — guessing between them
  is a common false Fail.
- **The TC owns its data.** Records created by `request` steps are removed in Postconditions
  through the documented delete operation, even when a step failed.
- Only `expect-*` rows become assertions, exactly as for UI.

## Alias rule (UI test cases; API uses *Operations used* instead)

- Aliases are `screen.element`, lower-kebab, stable across platforms: `login.email`,
  `order-form.save`, `orders.empty-state`. The screen alone (`login`) names the screen for
  `open` / `expect-url`; `<screen>.root` is the screen container (every screen has one —
  see the [testability contract](../../docs/requirements/shared/testability-contract.md)).
  In the mobile map, `root` is the screen's `anchor` (`Screen(anchor="root")`), so
  `expect-visible <screen>.root` becomes `assert_open()`; until the dev team ships the
  `<screen>-root` id, the map author may point `root` at another always-present element
  with a `note=` — that is a map decision, never a TC change.
- List items carry the entity id as a parameter: `orders.row[{{order.id}}]`.
- A TC never contains a locator, test id, XPath or CSS. The alias → locator mapping lives
  ONLY in the screen map (`automation/web/playwright/screens/`, `automation/mobile/screens/`).
- Every TC file ends with an **Aliases used** table (alias · screens · in map? per
  platform). An alias not yet in the map is normal at authoring time and is the work order
  for layer 2; prompt 07 STOPS on missing aliases instead of inventing locators.
- An API TC file ends with an **Operations used** table instead (operation · operationId ·
  in `docs/api/openapi.json`? · schema). The two tables play the same role: a `MISSING` row
  is a work order for someone else (dev team for an id, product owner for a contract), never
  something the TC author solves by guessing.

## Oracle rule

Each TC names one primary oracle in `type — source` form (the 8 types:
[qa/shared/oracles/README.md](../shared/oracles/README.md)). Apply the recorded owner
overrides, then default precedence by layer from that guide. A red run
first asks whether the expectation is wrong (test defect → fix the TC, no bug); an
app-caused red is a bug report, never a TC edit (doctrine rule 4).

## Execution status

TC runs use the execution vocabulary from CLAUDE.md — **Passed / Failed / Skipped /
Blocked / (empty)**. Blocked = could not run (stays owed); Skipped = deliberately will not
run; both need a comment; none is ever upgraded to Passed. Results are recorded in the
team Sheet (manual runs) and in `qa/{web,mobile,api}/<NN-module>/<module>-traceability.md`
(automated verdicts written by `trace_results.py`), never inside the TC file.

## Full example

```
## TC-AUTH-001 — Sign in with valid credentials lands on the dashboard

| Field | Value |
|---|---|
| ID | TC-AUTH-001 |
| Title | Sign in with valid credentials lands on the dashboard |
| Source CHK IDs | CHK-AUTH-003, CHK-AUTH-004 |
| Platforms | web, android, ios |
| Priority | P0 |
| Automation | candidate |
| Preconditions | `{{user.email}}` / `{{user.password}}` exist in fixtures, account active with role `user`; no session (fresh browser context / fresh install) |
| Oracle | spec — SRS §4.2 Login; spec — figma:12-345 (Dashboard header shows the signed-in user) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | login screen shown |
| 2 | expect-visible | login.root | — | visible |
| 3 | fill | login.email | {{user.email}} | — |
| 4 | fill | login.password | {{user.password}} | — |
| 5 | click | login.submit | — | request sent |
| 6 | wait-for | login.spinner | — | hidden |
| 7 | expect-visible | dashboard.root | — | visible |
| 8 | expect-text | dashboard.user-menu | — | {{user.email}} |
| 9 | expect-url | dashboard | — | /dashboard (web only) |

**Postconditions / cleanup:** session is active; nothing to clean — the fixture account is read-only and reusable.
**Notes:** UI login is allowed here because this TC proves login itself; every other TC gets auth by state.
```

```
## Aliases used

| Alias | Screen | web map | android map | ios map |
|---|---|---|---|---|
| login.root | login | yes | yes | yes |
| login.email | login | yes | yes | yes |
| login.password | login | yes | yes | yes |
| login.submit | login | yes | yes | yes |
| login.spinner | login | MISSING | MISSING | MISSING |
| dashboard.root | dashboard | yes | yes | yes |
| dashboard.user-menu | dashboard | yes | MISSING | MISSING |
```
