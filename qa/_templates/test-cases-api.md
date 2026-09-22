# Test cases — [Feature name] (API)

> One file per feature: `qa/api/<NN-module>/<module>-test-cases.md`, next to the checklist
> (e.g. `qa/api/01-authentication/authentication-test-cases.md`). Format, step vocabulary,
> operation and oracle rules: [test-case-format.md](test-case-format.md). TCs exist only for
> automation candidates (prompt 06 selection) and high-risk manual checks. Feature code from
> [qa/shared/feature-codes.md](../shared/feature-codes.md).
>
> **An API TC has no aliases and no screens.** A step is a request; the target is an
> operation (`METHOD /path`) taken verbatim from `docs/api/openapi.json`. An operation that
> is not in the spec is a contract gap for the module's `<module>-questions.md`, never a
> guessed endpoint.

| Field | Value |
|---|---|
| Feature | |
| Platform | api |
| Source checklist | `qa/api/<NN-module>/<module>-checklist.md` |
| Selection | `_bmad-output/test-artifacts/test-design/api/<feature>-automation-plan.md` |
| Contract | `docs/api/openapi.json` — `<tag or /resource>`, fetched `YYYY-MM-DD` |
| Environment | dev / staging (never production — `.github/GATES.md` rule 4) |
| Owner | @username |
| Last updated | YYYY-MM-DD |

Execution statuses when running these TCs: **Passed / Failed / Skipped / Blocked / (empty)**
(CLAUDE.md "Status vocabulary"). Blocked and Skipped need a comment; nothing is upgraded to
Passed because the round ended. Record results in `<module>-traceability.md` (automated, via
`trace_results.py --platform api`), not here.

---

## TC-<FEATURE>-001 — [Action-oriented title: what is proven]

| Field | Value |
|---|---|
| ID | TC-<FEATURE>-001 |
| Title | [same as heading] |
| Source CHK IDs | CHK-<FEATURE>-NNN, CHK-<FEATURE>-NNN |
| Platforms | api |
| Priority | P0 / P1 / P2 / P3 |
| Automation | candidate / automated(api) / manual |
| Roles | `<role>` — the identity the requests carry (`as` switches it mid-TC for permission checks) |
| Preconditions | `{{user.token}}` for role `<role>`; `{{order.id}}` exists in status `Draft` (seeded through `<METHOD /path>`, not through the UI) |
| Oracle | `spec — openapi:<operationId>` / `spec — SRS §x.y` / `invariant — INV-n` — see [qa/shared/oracles/README.md](../shared/oracles/README.md) |

| # | Action | Target (operation / field) | Data | Expected |
|---|---|---|---|---|
| 1 | as | `<role>` | — | requests below carry this identity |
| 2 | request | POST /orders (`createOrder`) | `{{order.draft}}` | — |
| 3 | expect-status | — | — | 201 |
| 4 | expect-schema | — | — | `order.schema.json` |
| 5 | store | `id` | `{{order.id}}` | — |
| 6 | request | GET /orders/{id} (`getOrder`) | `{{order.id}}` | — |
| 7 | expect-status | — | — | 200 |
| 8 | expect-field | `status` | — | `Draft` |
| 9 | expect-field | `createdBy` | — | `{{user.id}}` |

**Postconditions / cleanup:** `DELETE /orders/{id}` for `{{order.id}}` — every record this TC
creates, this TC removes, even when a step failed.
**Notes:** [rate limits, async delay and the bounded `wait-for` used, known issue
BUG-<FEATURE>-NNN (in `bugs/`), why manual if `manual`]

---

## Operations used

The analogue of "Aliases used" for UI: an operation missing from the spec is a **contract
gap** (question for the product owner), never an endpoint invented here. Prompt 07 stops on
a missing operation instead of guessing a path or a field.

| Operation | operationId | In `docs/api/openapi.json` | Schema |
|---|---|---|---|
| POST /orders | createOrder | yes / MISSING | `order.schema.json` / none yet |
| GET /orders/{id} | getOrder | yes / MISSING | `order.schema.json` / none yet |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{user.token}} | `automation/api/fixtures/` (planned) | role `<role>`; the value lives in `.env`, never here |
| {{order.draft}} | `automation/api/fixtures/` (planned) | request body built from the spec's schema, unique marker per run |
| {{order.id}} | captured by `store` in step 5 | removed in Postconditions |

## Open questions

- [Unclear expectation, undocumented status code, field not in the spec — which TC it blocks]
  or `None identified.`
