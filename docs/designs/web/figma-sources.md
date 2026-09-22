# Figma Sources — Web

Reference for AI agents and QA: which Figma file backs this project's web design,
and how each screen maps to its SRS section. Agents do **not** need a fresh link each
time — just the `fileKey` + the `node-id` of the screen to analyze.

## File

- **Name:** `<Figma file name>`
- **Platform:** Web (`<desktop browser / responsive>`)
- **fileKey:** `<FIGMA_FILE_KEY>`  (from `setup/project.yaml → web.figma.file_key`)
- **URL:** `https://www.figma.com/design/<FIGMA_FILE_KEY>/<slug>`
- **Main page (canvas):** `<page name>` — node `<0:1>`
- **Other pages:** `<Thumbnail, Sandbox, … — not design sources>`
- **Access:** verified `YYYY-MM-DD` with the PAT in `FIGMA_PERSONAL_ACCESS_TOKEN`

## How agents read it

Read via the project-local Figma MCP server `figma` (PAT-based, see `.mcp.json`):
- Structure / content: `mcp__figma__get_figma_data` with `fileKey` + `nodeId`.
- Images / screenshots: `mcp__figma__download_figma_images` (exports land in `docs/designs/web/screens/`, gitignored).

Design wins over SRS on conflict (CLAUDE.md doctrine rule 2); a genuine SRS↔design
disagreement goes to the module's `*-questions.md`, never silently resolved.

## Screen map (page `<page name>`, node `<0:1>`)

One row per top-level screen frame. Fill it with `get_figma_data` on the main page at depth 1;
re-run when the design is restructured.

| Screen | node-id | Size (px) | QA module | SRS |
|---|---|---|---|---|
| `<Login>` | `<31:19824>` | | `qa/web/<NN-module>/` | `docs/srs/<project>/<N. Module>/<file>.md` |
| | | | | |
