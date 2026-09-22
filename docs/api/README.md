# docs/api — API contract of the product under test

| File | Source | Fetched |
|---|---|---|
| `openapi.json` | `<https://api.example.com/swagger-json>` (or a Postman collection export) | `YYYY-MM-DD` |

Drop the product's OpenAPI / Postman file here. Refresh it by re-downloading from the source
URL and committing the diff — never edit it by hand.

## What it is used for

1. **API tests** (`automation/api/`, only when `platforms.api: true` in `setup/project.yaml`) —
   smoke, contract and security suites; response schemas in `automation/api/schemas/`.
2. **Login-by-API and test-data seeding for UI tests** — web and mobile suites get a token and
   create/remove the data they need without driving the UI, even when API tests themselves are
   out of scope. Every endpoint, payload field and response field used this way is taken from
   this spec, never guessed. Where it lives: `automation/web/playwright/utils/api.ts`
   (`loginByApi()` is a scaffold that stays Blocked until written from this spec) and the
   `apiContext` / `seed` fixtures in `automation/web/playwright/fixtures/test-fixtures.ts`.
   Cited example from a past product: `examples/automation/web/utils/api.ts`.

Record the scope decision (API tests in or out) in `docs/notes/decisions.md` and
`setup/project.yaml → platforms.api`.
