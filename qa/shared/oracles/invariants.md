# Invariants registry — INV-N

Properties of the product that must ALWAYS hold. The cheapest strong oracle we have
(see [README.md](README.md)). One line per invariant; IDs are stable and never reused.

**Where invariants come from:**
- every **business rule** in `docs/business-rules/` implies one;
- every **fixed bug** implies one — when a bug is verified fixed, add the invariant it
  violated here and reference it from the bug report's Related section;
- schema/contract guarantees worth asserting outside the contract suite.

**Every invariant should be checked by something** — a Playwright/pytest assertion, a
contract test, or (worst case) a named manual check. An invariant nothing checks is a
wish; note the gap in `Checked by` rather than leaving it blank.

| ID | Invariant (must always hold) | Area | Origin | Checked by |
|---|---|---|---|---|
| INV-1 | *(example)* A user never sees another user's data in any list or detail response | security | business rule | `automation/api/tests/` (IDOR checks — planned) |
| | | | | |

> Formatting: `Origin` = business rule / BUG-WEB-NNN / BUG-MOB-NNN / schema.
> `Checked by` = path to the automated check, or `manual: <checklist/test-case ID>`,
> or `GAP — not checked yet`.
