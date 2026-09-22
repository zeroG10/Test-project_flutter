# examples/ — filled-in artifacts from a past project (REFERENCE ONLY, anonymised)

Everything here was produced for a past project and is kept **only** as a living example of
what a filled-in artifact looks like at each layer of the chain. It is **anonymised**: the
product is called "Acme Field Services", URLs are `*.example.com`, Figma keys are
`EXAMPLE…` placeholders. Its roles (Root / Manager / Technician), entities (orders,
surveys) and endpoints belong to THAT product — none of it exists in yours.

| Folder | Shows how to fill |
|---|---|
| `srs/` | `docs/srs/` — SRS docs (web + `mobile/`) |
| `checklists/web/`, `checklists/mobile/` | `qa/{web,mobile}/<NN-module>/<module>-checklist.md` — checklists with stable `[CHK-…]` IDs |
| `figma-sources/` | `docs/designs/{web,mobile}/figma-sources.md` — Figma design maps |
| `automation/web/` | the Playwright layers for one web module (authentication): `screens/*.map.ts` curated from a recon draft (observed vs placeholder aliases, oracle per alias), `pages/*.page.ts` (behaviour only, no selectors), `tests/*.public.spec.ts` (`@CHK-…` tags, named oracles, `test.fail()` for an accepted defect), `utils/api.ts` (login-by-API + seeding derived strictly from an OpenAPI spec) |
| `checklist-gen/` | one-off Sheets scaffold generator ported from a colleague's kit (the Python sync in `automation/tools/` is the only live-sheet writer) |

Rules for AI agents:

- **Never treat this content as current project requirements.** Real artifacts live in
  `docs/` and `qa/` and start empty in a fresh clone.
- **Never let a name from here leak into a new artifact.** A role, entity, endpoint, route
  or error text that appears only in `examples/` and not in the product's own `docs/` is a
  fabrication. When in doubt, cite the `docs/` source or write `<…>` and ask.
- **`automation/web/` here is not compiled or run** (excluded from `tsconfig.json`). Copy the
  pattern, not the files: the template's own harness expects
  `automation/web/playwright/screens/<module>/*.map.ts` etc. with the ids of *your* product.
- **Never run `checklist-gen/`** without an explicit user request and an explicitly configured
  `SPREADSHEET_ID` — it does a full sheet rebuild.
- When generating a new artifact, you may read the matching example here for format/tone, but
  the authoritative format spec is always the prompt template in `prompts/` and
  `qa/_templates/`.
- This folder may be deleted entirely once the team no longer needs the examples.
