# qa/api — module index

One folder per module: `qa/api/<NN-module>/<module>-<artifact>.md` ([qa/README.md](../README.md)),
the same layout as `qa/web/` and `qa/mobile/`. `NN` follows the order of the API surface
in `docs/api/openapi.json` (tags / resource groups) or the SRS; the slug and its code are
registered in `qa/shared/feature-codes.md` **before** the first artifact is written. When a
module exists for web or mobile too, reuse the same slug and code — one `CHK-<CODE>-NNN`
namespace per feature, so a permission rule checked through the API and through the UI
trace to the same feature.

Use this folder when the product has an API in scope (`platforms.api: true`): API-only
products, and products whose business rules, validation and permissions are proven here
rather than through the UI (automation/README.md: "validation logic, permissions and
business rules go to `automation/api/`"). An API that only serves login-by-API and seeding
for the UI suites needs no folder here.

Stage legend: intake → analysed → checklist → candidates → test cases → automated → traced.

| # | Module | Code | Contract (tag / paths) | Stage | Notes |
|---|---|---|---|---|---|
| 01 | `<module>` | `<CODE>` | `docs/api/openapi.json` → `<tag or /resource>` | intake | |

## The chain for an API module

Same documents, no screen maps:

```
docs/api/openapi.json + docs/srs/** + business rules
   → <module>-analysis.md       endpoints, roles, rules, gaps → <module>-questions.md
   → <module>-checklist.md      [CHK-<CODE>-NNN]; every item names its oracle: the
                                operation (method + path + response schema) or an invariant
   → prompt 06                  candidates by risk (most API checks are good candidates)
   → <module>-test-cases.md     TC-<CODE>-NNN; steps are requests, not aliases
                                (template: qa/_templates/test-cases-api.md; vocabulary:
                                 qa/_templates/test-case-format.md → "Step vocabulary — API")
   → automation/api/tests/<module>/test_<feature>.py
                                @pytest.mark.chk("CHK-<CODE>-NNN") + @allure.tag(...)
   → uv run pytest -m <tier>    then automation/tools/trace_results.py --platform api
   → <module>-traceability.md   generated per run (run context: env label, target)
```

Cross-cutting API checks (headers, CORS, IDOR matrix, OWASP) stay product-level in
`qa/shared/checklists/` and `automation/api/tests/security/`.

## Coverage model per module (default — override in `docs/notes/decisions.md`)

1. **Contract** — every in-scope operation responds with the documented status and a body
   that validates against its schema (`automation/api/schemas/`, `helpers/schema_validator`).
2. **Auth and permissions** — every operation × every role: allowed / forbidden as the
   rules say; IDOR for every `{id}` path (security module).
3. **Validation** — required fields, formats, limits, error shape and copy.
4. **Business rules** — state transitions, calculations, invariants
   (`qa/shared/oracles/invariants.md`).
5. **Data lifecycle** — create / read / update / delete round-trips; what the test creates,
   the test removes.

Defects go to `<NN-module>/bugs/BUG-<CODE>-NNN.md` with request/response captures in
`bugs/evidence/BUG-<CODE>-NNN/`; an accepted, unfixed defect is marked
`@pytest.mark.xfail(reason="BUG-<CODE>-NNN …", strict=True)` in its test so it reports
without blocking the suite and flips loudly the day it is fixed.
