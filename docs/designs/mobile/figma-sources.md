# Figma Sources — Mobile

Reference for AI agents and QA: which Figma file backs the mobile app design, and
how each screen maps to its SRS section. With this file, agents do **not** need a
fresh link each time — just the `fileKey` + the `node-id` of the screen to analyze.

This is **separate** from the web design map ([../web/figma-sources.md](../web/figma-sources.md))
to avoid web/mobile confusion. Mobile checklists sync to their own Google Sheet
via `--target mobile`.

> Template note: fill the placeholders via `/setup-project` (values come from
> `setup/project.yaml → mobile.figma`). A filled-in example from a real project:
> [examples/figma-sources/mobile-figma-sources.md](../../../examples/figma-sources/mobile-figma-sources.md).

## File

- **Name:** <Figma file name>
- **Platform:** Mobile — <native iOS+Android | single cross-platform Flutter app>
- **fileKey:** `<FIGMA_FILE_KEY>`
- **URL:** https://www.figma.com/design/<FIGMA_FILE_KEY>/<file-name>
- **Main page (canvas):** `<page name>` — node `<0:1>`

## How agents read it

Read via the project-local Figma MCP server `figma` (PAT-based, see `.mcp.json`):
- Structure / content: `mcp__figma__get_figma_data` with `fileKey` + `nodeId`.
- Images / screenshots: `mcp__figma__download_figma_images`.

## Screen map

Extend this table as screens are analyzed (one row per screen):

| Screen | node-id | Size (px) | SRS section |
|---|---|---|---|
| | | | |
