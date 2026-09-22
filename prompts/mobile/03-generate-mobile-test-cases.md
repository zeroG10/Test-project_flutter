# Prompt M03 — Generate Mobile Test Cases (structured, alias-based)

## Purpose
Turn the **selected** mobile checklist items into structured, alias-based test cases — layer 1
of the automation chain ([automation/README.md](../../automation/README.md)) — with the mobile
rows (device / OS, app state, permissions, network) that Appium tests and manual device runs need.
Same format as the web prompt ([prompts/03-generate-test-cases.md](../03-generate-test-cases.md));
this file only adds the mobile specifics.

Default scope: ONLY the CHK IDs selected by `prompts/06-select-automation-candidates.md` plus
the high-risk checks flagged there as manual-with-script. A full manual suite is produced only
on explicit request (Mode B in the web prompt, saved as `-manual-suite.md`).

## When to Use
- After the mobile analysis (M01), the mobile checklist (M02) and the prompt 06 selection exist
- Before `prompts/07-generate-automation-from-test-cases.md` scaffolds Appium tests
- When a high-risk manual device check needs an exact reproducible script

## Input Required
- Checklist: `qa/mobile/<NN-module>/<module>-checklist.md` (`<NN-module>` = module folder in SRS order, `<module>` = the feature slug from `qa/shared/feature-codes.md`, e.g. `qa/mobile/01-authentication/authentication-checklist.md`)
- Selection: `_bmad-output/test-artifacts/test-design/mobile/{feature}-automation-plan.md` → "Selected CHK IDs"
- Analysis: `_bmad-output/test-artifacts/test-design/mobile/{feature}-analysis.md` (M01) or `qa/mobile/<NN-module>/<module>-analysis.md`
- Format + example: [qa/_templates/test-case-format.md](../../qa/_templates/test-case-format.md); template [qa/_templates/test-cases-mobile.md](../../qa/_templates/test-cases-mobile.md)
- Feature code: [qa/shared/feature-codes.md](../../qa/shared/feature-codes.md)
- Device matrix: `qa/shared/device-matrix/device-matrix.md`; supported OS: `docs/platform-specs/supported-devices.md`
- Oracles: SRS, **mobile** design map `docs/designs/mobile/figma-sources.md`, `docs/api/`, `qa/shared/oracles/invariants.md`
- Fixture names only: `automation/mobile/fixtures/test_data.py`, `docs/environments.md`

If the prompt 06 selection is missing, STOP and say so — do not guess candidates.

---

## Project overrides (read first)

1. **Structured format only** — the metadata table + `# | Action | Target (alias) | Data | Expected` steps table from `qa/_templates/test-case-format.md`. No free-form step tables, no locator hints in the TC.
2. **Aliases, never locators.** `screen.element`, platform-neutral. Do not write resource-ids, accessibility ids, XPath or `ByValueKey` into a TC. Aliases not yet in `automation/mobile/screens/` are listed as `MISSING` in "Aliases used" — that is the work order for the screen map and `docs/requirements/shared/testability-contract.md`.
3. **Source CHK IDs + Oracle on every TC.** `human` oracle ⇒ `Automation: manual`.
4. **IDs** `TC-<FEATURE>-<NNN>` from `feature-codes.md`, monotonic, preserved on regeneration. Mobile and web files for the same feature number independently (separate files, separate Sheets).
5. **Output** `qa/mobile/<NN-module>/<module>-test-cases.md` (one file per feature, inside the module folder next to the checklist; never directly under `qa/mobile/`).
6. Follow `qa/shared/oracles/README.md`: recorded owner overrides first, then the default precedence by layer; unresolved conflicts become Open Questions.

## Prompt

```
You are a Senior Mobile QA Engineer. Write structured, alias-based test cases for the selected checklist items of the feature below, following qa/_templates/test-case-format.md exactly and the mobile template qa/_templates/test-cases-mobile.md.

Inputs:
- Platform(s): [android / ios / flutter / cross-platform]  Min OS: [from supported-devices.md]  P0 devices: [from device matrix]
- Checklist: [paste qa/mobile/<NN-module>/<module>-checklist.md]
- Selection: [paste "Selected CHK IDs" from the prompt 06 automation plan, with automation level and blockers]
- Analysis / oracles: [paste relevant analysis sections, SRS §, Figma node ids from the MOBILE design map, API contract refs, invariants]
- Fixtures available (names only): [e.g. {{user.email}}, {{user.token}}, {{order.id}}]
- Existing file (if regenerating): [paste qa/mobile/<NN-module>/<module>-test-cases.md or "none"]

Selection rules: one TC per selected CHK ID (merge only when the same flow and the same oracle prove several); no TC for unselected items (say so in Open Questions if one looks missing); split flows longer than 12 steps; a selected item with no nameable oracle gets an Open Question, not a TC; "Manual Only + high risk" items get a TC with Automation = manual.

Writing rules:
- Verbs only from the vocabulary: open, click (= tap), fill, select, swipe (Data = up/down/left/right), scroll-to, back (system back / swipe-back), wait-for, expect-visible, expect-hidden, expect-text, expect-enabled, expect-disabled. expect-url does not exist on mobile — use expect-visible <screen>.root.
- One row = one action; only expect-* rows are assertions. Prose in Expected on interaction rows is for the manual tester (e.g. "keyboard type: email").
- Targets are aliases (screen.element, <screen>.root, screen.row[{{entity.id}}]); Data uses fixture placeholders; never literal credentials or personal data.
- Preconditions describe state; auth by state (API token injection / deep link). UI login only in the TC proving login.
- Fill the mobile rows on every TC: Device / OS (P0 device or `any`), App state (cold start / warm start / resumed from background / after OS kill; fresh install / upgraded), Permissions (per permission: not yet requested / granted / denied-once / denied-permanently), Network (online Wi-Fi / cellular / offline / throttled). Lifecycle, permission and offline scenarios are separate TCs — one condition per TC.
- Platform-specific expectations: only where iOS and Android observably differ; otherwise omit the line.
- Oracle as `type — source`; Follow `qa/shared/oracles/README.md`: recorded owner overrides first, then the default precedence by layer; unresolved conflicts become Open Questions.
- Postconditions / cleanup: permissions or app data to reset (scripts/reset_simulator.sh, adb pm clear), API cleanup, or "nothing to clean".
- Priority P0/P1/P2/P3; Automation candidate (default) / manual. Prompt 07 sets automated(android|ios|flutter) later.

Coverage expectations for the selected set (only if the selection contains such items — do not add unselected scenarios): happy path per platform, negative/validation, permission flow, lifecycle (background → foreground, kill → resume), offline/poor network, deep-link entry, a11y (VoiceOver/TalkBack labels reachable — oracle usually human ⇒ manual).

Output structure (from the template): file metadata table + execution-status note; one `## TC-<FEATURE>-<NNN> — title` section per TC in ID order; `## Aliases used` (alias · screen · android map · ios map, `yes`/`MISSING`); `## Fixtures used`; `## Coverage` (one row per selected CHK ID → TC IDs or Open Question ref); `## Open questions`.

Self-check: every selected CHK ID in Coverage; no TC outside the selection; every TC has Source CHK IDs, Priority, Automation, Device/OS, App state, Permissions, Network, Preconditions, Oracle; vocabulary verbs and aliases only; at least one expect-* row per TC, last row is the verdict; no secrets; Aliases/Fixtures tables complete; IDs preserved.
```

## Output Location
- `qa/mobile/<NN-module>/<module>-test-cases.md` — the file prompts 04 and 07 consume
- Mode B (explicit request only): `qa/mobile/<NN-module>/<module>-manual-suite.md`

## Notes for the QA reviewer
- `MISSING` aliases go to the dev team via the testability contract (ids), then into `automation/mobile/screens/` — never verified by hand-picking XPath in Appium Inspector into the TC.
- Confirm priority and the manual/candidate split with the team before prompt 07 runs.
