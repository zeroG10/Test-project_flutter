# qa/mobile — module index

One folder per module: `qa/mobile/<NN-module>/<module>-<artifact>.md` ([qa/README.md](../README.md)).
`NN` follows the mobile SRS order; the slug and its code are registered in
`qa/shared/feature-codes.md` **before** the first artifact is written. Web and mobile
checklists of the same feature share the code (they sync to separate Sheets).

Stage legend: intake → analysed → checklist → candidates → test cases → automated → traced.

| # | Module | Code | SRS | Figma node | Platforms | Stage | Notes |
|---|---|---|---|---|---|---|---|
| 01 | `<module>` | `<CODE>` | `docs/srs/mobile/<N. Module>/<file>.md` | `<node-id>` | android · ios | intake | |

Platform column: which OS the module is verified on (`android`, `ios`, or both). A Flutter app
is still `android · ios` — Flutter is an app kind (`APP_KIND=flutter`), not a platform.

## Coverage model per module (default — override in `docs/notes/decisions.md`)

1. **Reachability** — every screen opens; navigation, back, deep links.
2. **CRUD / core flows** — for each entity or flow the module owns.
3. **Lists** — search, filters, sorting, pull-to-refresh, pagination / infinite scroll.
4. **Validation** — required fields, formats, limits, error copy, keyboard types.
5. **Permissions and states** — roles; OS permissions (camera, location, notifications); offline; background/foreground; interruptions.
6. **Edge cases** — selectively, where the risk is real; device matrix tiers in `qa/shared/device-matrix/`.

Per module the chain is: screen recon (mobile MCP / Appium inspector) ↔ checklist alignment →
candidates (prompt 06) → test cases (`prompts/mobile/03`) → screen maps
(`automation/mobile/screens/<screen>_map.py`) → specs (prompt 07) → run → `trace_results.py`.

Defects go to `<NN-module>/bugs/BUG-<CODE>-NNN.md` (template `qa/_templates/bug-mobile.md`) with
evidence in `bugs/evidence/BUG-<CODE>-NNN/`.
