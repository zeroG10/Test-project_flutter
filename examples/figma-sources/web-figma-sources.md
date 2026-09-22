# Figma Sources — Web (Admin panel)

Reference for AI agents and QA: which Figma file backs this project's web design,
and how each screen maps to its SRS section. With this file, agents do **not** need a
fresh link each time — just the `fileKey` + the `node-id` of the screen to analyze.

## File

- **Name:** Acme Field Services: Admin panel
- **Platform:** Web (admin panel, desktop browser)
- **fileKey:** `EXAMPLEwebFileKey00000`
- **URL:** https://www.figma.com/design/EXAMPLEwebFileKey00000/Acme-Field-Services--Admin-panel
- **Main page (canvas):** `Admin panel` — node `0:1`
- **Other pages:** `Thumbnail` (`1:18049`), `Sandbox` (`47:13424`)

## How agents read it

Read via the project-local Figma MCP server `figma` (PAT-based, see `.mcp.json`):
- Structure / content: `mcp__figma__get_figma_data` with `fileKey` + `nodeId`.
- Images / screenshots: `mcp__figma__download_figma_images`.

To focus on one screen, pass its `node-id` from the table below. A `node-id` is only
needed to scope quickly — agents can also traverse the whole file from `fileKey` alone.

## Screen map (page `Admin panel`, node `0:1`)

| Screen | node-id | Size (px) | SRS section |
|---|---|---|---|
| Login | `31:19824` | 3006×7889 | [docs/srs/01-authentication.md](../../srs/01-authentication.md) |
| Forgot password | `31:19987` | 2946×7889 | [docs/srs/01-authentication.md](../../srs/01-authentication.md) |
| Set password | `31:20046` | 3664×7889 | [docs/srs/01-authentication.md](../../srs/01-authentication.md) |
| Managers | `4:14561` | 9040×7041 | [docs/srs/02-managers.md](../../srs/02-managers.md) |
| Field Technicians | `114:18590` | 9040×5405 | [docs/srs/03-field-technicians.md](../../srs/03-field-technicians.md) |
| Survey | `15:26995` | 18557×9652 | _TBD — no SRS yet_ |
| Template | `33:43351` | 9040×5818 | _TBD — no SRS yet_ |
| Responses | `55:15922` | 10183×5562 | _TBD — no SRS yet_ |
| Photo tags | `129:22990` | 9040×3983 | _TBD — no SRS yet_ |
| Email templates | `541:35563` | 16983×2856 | _TBD — no SRS yet_ |

> Update the SRS column as new SRS sections land in `docs/srs/`.
> Re-run `get_figma_data` on `0:1` (depth 1) to refresh node-ids if the design is restructured.
