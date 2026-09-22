# Figma Sources — Mobile (Flutter, cross-platform)

Reference for AI agents and QA: which Figma file backs the mobile app design, and
how each screen maps to its SRS section. With this file, agents do **not** need a
fresh link each time — just the `fileKey` + the `node-id` of the screen to analyze.

This is **separate** from the web design map ([../web/figma-sources.md](../web/figma-sources.md))
to avoid web/mobile confusion. Mobile checklists sync to their own Google Sheet
via `--target mobile`.

## File

- **Name:** Acme Field Services: Mobile app (Design)
- **Platform:** Mobile — single cross-platform **Flutter** app (one design file)
- **fileKey:** `EXAMPLEmobileFileKey00`
- **URL:** https://www.figma.com/design/EXAMPLEmobileFileKey00/Acme-Field-Services--Mobile-app--Design-
- **Main page (canvas):** `Design` — node `2:3`
- **Theme section (default / light):** `Light` — node `1005:75183`
- **Other pages:** `Thumbnail` (`0:1`), `Sandbox` (`2:5`)

## How agents read it

Read via the project-local Figma MCP server `figma` (PAT-based, see `.mcp.json`):
- Structure / content: `mcp__figma__get_figma_data` with `fileKey` + `nodeId`.
- Images / screenshots: `mcp__figma__download_figma_images` → save under
  `docs/designs/mobile/screens/` (gitignored).

To focus on one screen, pass its `node-id` from the table below. A `node-id` is only
needed to scope quickly — agents can also traverse the whole file from `fileKey` alone.

## Screen map (section `Light`, node `1005:75183`)

| Screen | node-id | SRS section |
|---|---|---|
| Splash & Wellcome | `3:418` | [docs/srs/mobile/01-mobile_splash+authentication.md](../../srs/mobile/01-mobile_splash+authentication.md) |
| Splash animation | `700:18853` | [docs/srs/mobile/01-mobile_splash+authentication.md](../../srs/mobile/01-mobile_splash+authentication.md) |
| Registration | `7:496` | [docs/srs/mobile/01-mobile_splash+authentication.md](../../srs/mobile/01-mobile_splash+authentication.md) |
| Registration_Updated | `1518:10344` | [docs/srs/mobile/01-mobile_splash+authentication.md](../../srs/mobile/01-mobile_splash+authentication.md) |
| Log in | `398:7044` | [docs/srs/mobile/01-mobile_splash+authentication.md](../../srs/mobile/01-mobile_splash+authentication.md) |
| Log in_Updated | `1554:12365` | [docs/srs/mobile/01-mobile_splash+authentication.md](../../srs/mobile/01-mobile_splash+authentication.md) |
| Notifications | `355:15971` | _TBD — no SRS yet_ |
| Jobs | `332:10880` | _TBD — no SRS yet_ |
| Profile | `1049:25660` | _TBD — no SRS yet_ |

> "_Updated" sections are revised versions of Registration / Log in — confirm with
> the team which variant is the current build before writing checks against it.
> A Dark-theme section may also exist; this map tracks the Light (default) theme.
> Update the SRS column as new SRS sections land in `docs/srs/mobile/`.
> Re-run `get_figma_data` on `1005:75183` (depth 1) to refresh node-ids if the design is restructured.
