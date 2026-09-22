# Test cases — [Feature name] (web)

> One file per feature: `qa/web/<NN-module>/<module>-test-cases.md`, next to the checklist
> (e.g. `qa/web/01-authentication/authentication-test-cases.md`). Format, step vocabulary,
> alias and oracle rules: [test-case-format.md](test-case-format.md). TCs exist only for automation
> candidates (prompt 06 selection) and high-risk manual checks. Feature code from
> [qa/shared/feature-codes.md](../shared/feature-codes.md).

| Field | Value |
|---|---|
| Feature | |
| Platform | web |
| Source checklist | `qa/web/<NN-module>/<module>-checklist.md` |
| Selection | `_bmad-output/test-artifacts/test-design/web/<feature>-automation-plan.md` |
| Browsers | Chrome / Firefox / Safari — see [supported-devices.md](../../docs/platform-specs/supported-devices.md) |
| Owner | @username |
| Last updated | YYYY-MM-DD |

Execution statuses when running these TCs: **Passed / Failed / Skipped / Blocked / (empty)**
(CLAUDE.md "Checklist status vocabulary"). Blocked and Skipped need a comment; nothing is
upgraded to Passed because the round ended. Record results in the team Sheet (manual) or
`<module>-traceability.md` (automated, via `trace_results.py`), not here.

---

## TC-<FEATURE>-001 — [Action-oriented title: what is proven]

| Field | Value |
|---|---|
| ID | TC-<FEATURE>-001 |
| Title | [same as heading] |
| Source CHK IDs | CHK-<FEATURE>-NNN, CHK-<FEATURE>-NNN |
| Platforms | web |
| Priority | P0 / P1 / P2 / P3 |
| Automation | candidate / automated(web) / manual |
| Preconditions | `{{user.email}}` exists and is active with role `<role>`; auth by state (`storageState`), logged in as `{{user.email}}`; `{{order.id}}` exists in status `Draft` |
| Oracle | `spec — SRS §x.y` / `spec — figma:<node-id>` / `invariant — INV-n` / `human` — see [qa/shared/oracles/README.md](../shared/oracles/README.md) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | <screen> | — | screen shown |
| 2 | expect-visible | <screen>.root | — | visible |
| 3 | fill | <screen>.<field> | {{fixture.value}} | — |
| 4 | click | <screen>.<button> | — | — |
| 5 | wait-for | <screen>.<spinner> | — | hidden |
| 6 | expect-text | <screen>.<element> | — | exact text or {{fixture}} |
| 7 | expect-url | <next-screen> | — | /route |

**Postconditions / cleanup:** [what state is left; what to delete/reset and through which API helper — or "nothing to clean"]
**Notes:** [cross-browser scope, a11y note, known issue BUG-<FEATURE>-NNN (in `bugs/`), why manual if `manual`]

---

## Aliases used

| Alias | Screen | web map |
|---|---|---|
| <screen>.root | <screen> | yes / MISSING |
| <screen>.<field> | <screen> | yes / MISSING |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{user.email}} | `automation/web/playwright/fixtures/` (planned) | role `<role>`, read-only account |

## Open questions

- [Unclear expectation — what is missing — which TC it blocks] or `None identified.`
