---
name: qa-checklist
description: Generate a manual QA checklist for a feature (web, mobile OR api), with this template's conventions baked in (platform routing, stable CHK- IDs, no [AUTO] markers, available design, scoped owner overrides and source precedence). Use when the user says "generate a checklist", "QA checklist for [feature]", or "create a checklist for [feature] (web/mobile/api)".
---

# QA Checklist Generator

Thin wrapper around the project's checklist prompts. The prompt is the **authoring spec**
(sections, style rules, examples, output format) — read it and follow it. This skill only
governs *which platform/prompt/folder*, *which inputs*, *which IDs*, and *which overrides win*.
Do NOT duplicate the prompt body here.

## Step 1 — Identify the platform (never default to web)

Decide the target using [CLAUDE.md → Platform decision rules](../../../CLAUDE.md):

- "browser", "page", "URL", "responsive", desktop Figma → **web**
- "app", "device", "iOS", "Android", "Flutter", "tap", "swipe", "push" → **mobile**
  (then resolve the sub-target: `ios`, `android`, `flutter`, or `cross-platform`)
- "endpoint", "API", "REST", "status code", "schema", OpenAPI → **api**
  (use the web prompt; sources are `docs/api/openapi.json` + SRS instead of Figma, output
  goes to `qa/api/<NN-module>/`, and every item names an operation or an invariant as its
  oracle — never a screen element)
- Cross-cutting only (a11y, security, perf, i18n), no platform → **shared** (use web prompt)

If ambiguous (e.g. "checklist for login"), **ask**: web, mobile or API? Do not guess.
**One run = one platform = one file.** To cover several platforms, run the skill once each.

## Step 2 — Pick the right prompt + inputs for that platform

### If WEB (or shared)
- **Prompt (authoring spec):** [prompts/02-generate-checklist.md](../../../prompts/02-generate-checklist.md)
- **Primary input:** `qa/web/<NN-module>/<module>-analysis.md` if it exists
  (`<NN-module>` = module folder, `NN` = order in the SRS, `<module>` = the feature slug
  registered in `qa/shared/feature-codes.md`, e.g. `qa/web/01-authentication/`).
- **Else source docs:** `docs/srs/`, `docs/requirements/{web,shared}/`,
  `docs/business-rules/`, `docs/api/`, acceptance criteria.
- **Design map:** [docs/designs/web/figma-sources.md](../../../docs/designs/web/figma-sources.md)

### If API

- **Prompt:** `prompts/02-generate-checklist.md`, API branch.
- **Inputs:** `qa/api/<NN-module>/<module>-analysis.md`, `docs/api/openapi.json`,
  confirmed business rules / owner notes. Skip Step 3's Figma instructions.

### If MOBILE
- **Prompt (authoring spec):** [prompts/mobile/02-generate-mobile-checklist.md](../../../prompts/mobile/02-generate-mobile-checklist.md)
- **Primary input:** `_bmad-output/test-artifacts/test-design/mobile/<feature>-analysis.md`
  (the M01 output); fall back to `qa/mobile/<NN-module>/<module>-analysis.md` if present.
- **Else source docs:** `docs/srs/mobile/`, `docs/requirements/{mobile,shared}/`,
  `docs/business-rules/`, `docs/api/`.
- **Mobile-only extra inputs (required):** `docs/platform-specs/{ios,android}/` and
  `qa/shared/device-matrix/device-matrix.md` — feed lifecycle, permissions, and device-class checks.
- **Design map:** [docs/designs/mobile/figma-sources.md](../../../docs/designs/mobile/figma-sources.md)
  (do NOT use the web map)

Resolve the **feature name** from the user's prompt; if missing, infer from the inputs and
confirm the slug before writing.

## Step 3 — Read the applicable sources

API uses the contract and confirmed business rules, with no design step. UI uses available
design below. With only a running product + owner, follow the observation/confirmation
route in `qa/shared/oracles/README.md`; missing Figma does not block independent checks.

When design is available, use the **platform-correct** design map from Step 2 to find the `fileKey` + `node-id` for the
feature's screen(s), via the **project-local `figma` MCP server** (its own PAT — NOT the
shared claude.ai Figma connector):

- `mcp__figma__get_figma_data` → structure
- `mcp__figma__download_figma_images` → rendered screen
  (mobile: save under `docs/designs/mobile/screens/`)

Generate checks from the available sources, including recorded owner confirmations.
When SRS and design both exist, cover them together, including visual elements absent
from the SRS. Apply the source policy below; never turn an unconfirmed observation into
an expected result. If a design resource is missing, note exactly what and from where in Open Questions.

## Step 4 — Apply project overrides (these win over the prompt body)

1. **No `[AUTO]` markers** on any item and no "AUTO candidates" line in the Coverage summary.
   Automation selection is a separate step (`prompts/06`), generation is `prompts/07`.
2. **Stable IDs on every item** — format `[CHK-<FEATURE>-<NNN>]`:
   - `<FEATURE>` = the feature code registered for the slug in
     [qa/shared/feature-codes.md](../../../qa/shared/feature-codes.md) — create the
     row if missing (2–5 uppercase letters, unique per platform, never reused/renamed).
     Fallback when no row exists yet: first 4 letters uppercase, then register it.
   - `<NNN>` = zero-padded 3-digit, monotonic across the **whole file** (not per section).
   - Item format: `1. [CHK-AUTH-001] Check that ...`
   - **Regeneration:** read the existing file first and PRESERVE existing IDs; new IDs only
     for new checks, numbered above the current max. IDs are the contract for
     `automation/tools/sync_checklist_to_sheets.py` — never change or reuse one.
3. **Apply the source policy in `qa/shared/oracles/README.md`.** Recorded owner overrides
   take precedence within their scope, otherwise use defaults by layer. Cite the resolution;
   unresolved expectations go to Open Questions.

## Step 5 — Write into the module folder

Naming `<module>-checklist.md` inside `qa/<platform>/<NN-module>/` (e.g.
`qa/web/01-authentication/authentication-checklist.md`). `NN` = order in the SRS; `<module>` = the slug
row in `qa/shared/feature-codes.md`. Create the module folder if it does not exist yet; the
path is load-bearing (the sync script derives `--target` from the platform folder and the
feature code from the file stem):

- web → `qa/web/<NN-module>/<module>-checklist.md`
- api → `qa/api/<NN-module>/<module>-checklist.md` (operations, no screen maps)
- shared (cross-cutting a11y / security / perf / i18n) → `qa/shared/checklists/<feature>-checklist.md`
- mobile → `qa/mobile/<NN-module>/<module>-checklist.md`
  (the sub-target resolved in Step 1 goes into the checklist's Platform metadata, not the path)

Follow the chosen prompt for section structure and the Coverage summary line, with the
override edits above.

## Step 6 — Report

State the file path written, item count, and any Open Questions. Suggest `prompts/06`
(automation candidates) or `/qa-test-cases` as the next step if relevant.
