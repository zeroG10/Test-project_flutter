# Prompt M01 — Analyze Mobile SRS and Design

## Purpose
Analyze source documentation through a **mobile-first lens**: extract platform-specific requirements (iOS / Android / Flutter), identify mobile constraints (permissions, gestures, offline, deep links), and surface gaps before writing mobile test artifacts.

## When to Use
- At the start of a new mobile feature
- After receiving updated mobile designs (iOS / Android screens)
- Before generating mobile checklists or test cases (always run this first)
- Before selecting Appium automation candidates

## Input Required
- `docs/srs/` — SRS
- `docs/requirements/mobile/` — mobile-specific requirements
- `docs/requirements/shared/` — cross-platform requirements that also apply
- `docs/designs/mobile/{ios,android,flutter}/` — Figma / mockups
- `docs/business-rules/`
- `docs/api/` — API endpoints the app consumes
- `docs/platform-specs/{ios,android}/` — HIG / Material rules already documented
- `docs/platform-specs/supported-devices.md` — what we must support

State any missing inputs explicitly and proceed with available ones.

---

## Design input from Figma (read first)

Use available mobile design through the project-local Figma MCP server below. Apply
`qa/shared/oracles/README.md` for owner overrides, default precedence by layer and the
route with only a running app + owner. Missing documents/design do not block independent
UI discovery; record observations separately from confirmed expectations.

1. Open the **mobile** design map [docs/designs/mobile/figma-sources.md](../../docs/designs/mobile/figma-sources.md)
   for the `fileKey` + `node-id` of the screen(s) relevant to the mobile SRS section.
   Use the mobile file's `fileKey` from that map — do **NOT** use the web map.
2. Read structure with `mcp__figma__get_figma_data` (`fileKey` + `nodeId`); capture the
   rendered screen with `mcp__figma__download_figma_images` (save to
   `docs/designs/mobile/screens/`, gitignored) when layout, labels, states, or gestures matter.
3. Validate the SRS against what the design actually shows — reconcile every screen,
   element, state, and gesture in the Design vs SRS comparison. Record conflicts as
   Open Questions only when the agreed precedence does not resolve them; cite decisions.
4. If a screen is not in the map or the file is unreadable, state it and proceed (do not
   invent design behavior). If a needed resource is missing, note exactly what and from where.

---

## Prompt

```
You are a Senior Mobile QA Engineer with 7+ years of experience testing iOS and Android apps (native and Flutter). Analyze the provided documentation and produce a mobile-focused QA analysis report.

Input documents:
[Paste content or attach files from docs/srs/, docs/requirements/mobile/, docs/designs/mobile/, docs/platform-specs/, docs/api/, docs/business-rules/]

Supported platforms / OS versions: [from docs/platform-specs/supported-devices.md]
Device matrix (target devices): [from qa/shared/device-matrix/device-matrix.md]

The analysis will feed into:
- mobile checklist generation (per platform)
- mobile test case generation (with gestures, platform-specific expectations)
- traceability matrix
- automation candidate selection for Appium + Python
- open questions for BA / Dev / Designer

Produce a report with these sections:

---

## 1. Feature Overview
- What the feature does, business value, in/out of scope.
- Which mobile platforms it ships on (iOS / Android / Flutter / all).
- Whether feature parity with web is required.

## 2. Platform-Specific Behaviors
For each supported platform, list expected differences:
- iOS: HIG conventions, system controls, swipe-back gesture, share sheet, Face ID/Touch ID, etc.
- Android: Material conventions, back button, predictive back (14+), intent handling, etc.
- Flutter (if applicable): rendering parity, Semantics labels available?

## 3. Mobile-Specific Constraints to Test
Explicitly cover:
- **Permissions** — what permissions the feature requests, when, what happens on denial.
- **Network** — offline behavior, slow network, switching Wi-Fi ↔ cellular.
- **Background / foreground transitions** — backgrounded mid-flow, killed by OS, resume.
- **Lifecycle** — first launch, cold/warm start, reinstall.
- **Deep links / Universal Links / App Links** — entry points into this feature.
- **Push notifications** — does this feature trigger or react to them?
- **Local storage** — Keychain / EncryptedSharedPreferences / Hive / Realm.
- **Orientation** — portrait/landscape, what should happen on rotation.
- **Accessibility** — VoiceOver / TalkBack labels required.
- **Localization** — strings, RTL support, date/number formats.

## 4. Device Matrix Coverage
- Minimum supported OS (per platform).
- Tier-P0 devices that MUST pass.
- Form factors at risk (small phones, tablets, foldables).
- Any device-specific risks (Samsung OneUI quirks, MIUI background restrictions, etc.).

## 5. Cross-Platform Risk Areas
Where iOS and Android may diverge in observable behavior:
- UI primitives (date picker, segmented control, share sheet)
- Notifications channels (Android) vs categories (iOS)
- File picker / camera / photo library access
- Biometric prompts

## 6. API / Backend Touchpoints
- Which endpoints the feature hits.
- Auth requirements (token refresh on resume?).
- Error responses the app must handle.

## 7. Test Data Requirements
Accounts, fixtures, app states needed.

## 8. Gaps and Open Questions
Anything ambiguous in the spec. Direct the questions to BA / iOS dev / Android dev / Designer / Backend separately.

## 9. Suggested Next Steps
- Which checklists to build (link to template).
- Which test cases are P0.
- Which scenarios are good Appium automation candidates vs which stay manual.

---

End the report with a one-paragraph executive summary suitable for sharing in Slack.
```

## Output Location
Save the analysis to `_bmad-output/test-artifacts/test-design/mobile/{feature-name}-analysis.md`.
