# qa/web — module index

One folder per module: `qa/web/<NN-module>/<module>-<artifact>.md` ([qa/README.md](../README.md)).
`NN` follows the SRS order; the slug and its code are registered in
`qa/shared/feature-codes.md` **before** the first artifact is written.

Stage legend: intake → analysed → checklist → candidates → test cases → automated → traced.

| # | Module | Code | SRS | Figma node | Stage | Notes |
|---|---|---|---|---|---|---|
| 01 | `<module>` | `<CODE>` | `docs/srs/<project>/<N. Module>/<file>.md` | `<node-id>` | intake | |

Cross-module behaviour (navigation, header, session expiry, role access) is checked inside the
module it belongs to; product-wide checklists (a11y, OWASP) live in `qa/shared/checklists/`.

## Coverage model per module (default — override in `docs/notes/decisions.md`)

Not every checklist item becomes a test. The default target per module:

1. **Reachability** — every screen of the module opens and its navigation works.
2. **CRUD** — create, read, update, delete for each entity the module owns.
3. **List behaviour** — search, filters, sorting, pagination.
4. **Validation** — required fields, formats, limits, error copy.
5. **Permissions** — per role, for every entity (`asManager()` in the fixtures for the second role).
6. **Edge cases** — selectively, where the risk is real.

Per module the chain is: recon inventory (`npm run pw:recon`) ↔ checklist alignment →
candidates (prompt 06) → test cases (prompt 03) → screen maps (registered in
`automation/web/playwright/screens/index.ts`) → specs (prompt 07) → run → `trace_results.py`.

Defects go to `<NN-module>/bugs/BUG-<CODE>-NNN.md` with evidence in `bugs/evidence/BUG-<CODE>-NNN/`;
an accepted, unfixed defect is marked `test.fail()` in its spec so it reports without blocking
the suite.
