# docs/ — project knowledge intake (what goes where)

Everything the AI reads to analyze, plan and test lives here. Drop files into the
matching folder; if you do not know where something belongs, put it in `00-intake/`
and the agent will triage it and log the move in `00-intake/intake-log.md`.

| Folder | Put here | Read by |
|---|---|---|
| `00-intake/` | anything unsorted: zips, exports, screenshots, PDFs, chat dumps | triage step (agent sorts into the folders below) |
| `srs/` | product specification: SRS, PRD, user stories, acceptance criteria (shared across platforms) | prompt 01, checklist + test-case generation |
| `requirements/shared/`, `requirements/web/`, `requirements/mobile/` | platform-agnostic vs platform-specific requirements, NFRs, `testability-contract.md` | prompt 01, screen-map authoring |
| `business-rules/` | domain rules, calculations, state machines, role matrices | prompt 01, invariants (`qa/shared/oracles/invariants.md`) |
| `api/` | OpenAPI / Swagger / Postman, auth flow notes, sample payloads | `automation/api/` contract tests, data seeding |
| `designs/web/`, `designs/mobile/` | `figma-sources.md` (fileKey + node map). Exported screens go to `screens/` (gitignored, regenerated via Figma MCP) | checklist generation (design wins over SRS) |
| `notes/` | BA / client / developer / QA notes, meeting minutes, decisions, known issues | prompt 01 (context), open questions |
| `environments.md` | environments, base URLs, roles, where test accounts live (pointers only, no secrets) | every automation stack, `/setup-project` |
| `platform-specs/` | supported devices / OS policy, store constraints (mobile only) | device matrix, mobile checklists |

Rules:
- **No secrets in docs/.** Tokens, passwords and keys go to the stack `.env` files (gitignored). `environments.md` only says *which* account to use, not its password.
- **Binary sources are welcome** (PDF, DOCX, PNG). The agent extracts what it needs; keep the original.
- **One product per clone.** Web, iOS, Android and Flutter clients of the same product share `srs/`, `api/`, `business-rules/`; platform-only material goes to the `web/` / `mobile/` subfolders.
- Mobile builds (`.apk`, `.ipa`, `.app`) are NOT docs — they go to `automation/mobile/builds/{android,ios,flutter}/` (gitignored).
- Reference material from past projects lives in `examples/`, never here.
