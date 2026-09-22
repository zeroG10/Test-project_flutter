# Prompt 03 — Generate Test Cases (structured)

## Purpose

Turn **selected** checklist items into structured test cases — layer 1 of the automation
chain ([automation/README.md](../automation/README.md)). A test case written here is
executable by a human as-is and is the exact input `prompts/07-generate-automation-from-test-cases.md`
turns into Playwright / pytest code without re-interpreting anything.

Two step models, one format: **UI TCs (web, mobile) are alias-based** — a step targets a
`screen.element` alias. **API TCs are request-based** — a step targets an operation
(`METHOD /path`) taken verbatim from `docs/api/openapi.json`. Both are defined in
[qa/_templates/test-case-format.md](../qa/_templates/test-case-format.md); pick the model
from the platform before writing the first step.

Default scope (Mode A): ONLY the CHK IDs selected by `prompts/06-select-automation-candidates.md`
(automation candidates) plus the high-risk checks prompt 06 flagged as manual-with-script.
Everything else stays a checklist item. A full manual suite (every checklist item → a TC)
is Mode B and is produced only when the user explicitly asks for it.

## When to Use

- After `02-generate-checklist.md` and `06-select-automation-candidates.md` exist for the feature
- Before `07-generate-automation-from-test-cases.md` (test cases are the spec for the code)
- When a high-risk manual check needs an exact reproducible script
- Mode B only: when the user explicitly requests a complete manual test-case suite

## Input Required

- Checklist: `qa/{web|mobile|api}/<NN-module>/<module>-checklist.md` (`<NN-module>` = module folder in SRS order, `<module>` = the feature slug from `qa/shared/feature-codes.md`, e.g. `qa/web/01-authentication/authentication-checklist.md`)
- Selection: `_bmad-output/test-artifacts/test-design/{web|mobile|api}/[feature-name]-automation-plan.md` → section "Selected CHK IDs" (prompt 06 output)
- Analysis: `qa/{web|mobile|api}/<NN-module>/<module>-analysis.md` (prompt 01)
- Format, vocabulary, example: [qa/_templates/test-case-format.md](../qa/_templates/test-case-format.md); template `qa/_templates/test-cases-{web|mobile|api}.md`
- Feature code: [qa/shared/feature-codes.md](../qa/shared/feature-codes.md)
- Oracles: recorded owner-confirmed expectations / accepted regression baseline / SRS / user-story acceptance criteria / design map (`docs/designs/{web,mobile}/figma-sources.md`) / the contract in `docs/api/openapi.json` (the oracle for every API TC) / [qa/shared/oracles/invariants.md](../qa/shared/oracles/invariants.md)
- Fixture names only (`{{user.email}}`, `{{order.id}}`): `automation/web/playwright/fixtures/`, `automation/mobile/fixtures/`, `automation/api/fixtures/`, `docs/environments.md` (pointers, no secrets)
- Optional: existing test-case file for the feature (to preserve IDs), known issues, `qa/{web|mobile|api}/<NN-module>/<module>-questions.md`

If the prompt 06 selection is missing, STOP and say so — do not guess which items are candidates. (Exception: the user explicitly asks for Mode B.)

---

## Project overrides (read first)

These rules win over anything in the prompt bodies below:

1. **Mode A is the default.** Structured TCs, only for selected CHK IDs (+ flagged high-risk manual). Mode B (full manual suite, legacy table format) only on explicit request, saved to a separate `-manual-suite.md` file.
2. **Every TC lists its Source CHK IDs and names its Oracle.** A TC missing either is not finished. `human` oracle ⇒ `Automation: manual`.
3. **UI: aliases, never locators.** Steps reference `screen.element` aliases (rules in `qa/_templates/test-case-format.md`). Do not write test ids, CSS, XPath or resource-ids into a TC; use only elements evidenced by available SRS/design or recorded UI observations; never invent an element. An alias that is not yet in the screen map is fine — list it in "Aliases used" as `MISSING`; that is the work order for the screen map / testability contract, not something to solve here.
3b. **API: operations, never guessed endpoints.** Steps reference `METHOD /path` exactly as `docs/api/openapi.json` writes it, with the `operationId` in parentheses; fields, status codes and schemas come from the same spec. Never invent a path, a field name, a status code or an error shape. An operation the spec does not contain is a **contract gap**: list it in "Operations used" as `MISSING` and add it to the module's `<module>-questions.md` — it is a question for the product owner, not something to solve here. Every API TC fills the `Roles` row, and permission cases switch identity with `as`.
4. **IDs are stable.** `TC-<FEATURE>-<NNN>` with the feature code from `feature-codes.md`, monotonic across the file; on regeneration read the existing file and preserve every existing ID.
5. **Platform-scoped output.** Web → `qa/web/<NN-module>/<module>-test-cases.md`; mobile → `qa/mobile/<NN-module>/<module>-test-cases.md`; API → `qa/api/<NN-module>/<module>-test-cases.md`. A feature on several platforms gets one file per platform (web and mobile share the steps, mobile adds device/app-state rows; the API file is request-based and shares nothing but the IDs). Always inside the module folder, next to the checklist it comes from — never directly under `qa/web/`, `qa/mobile/` or `qa/api/`.
6. **Owner overrides take precedence within their recorded scope** (qa/shared/oracles/README.md). Otherwise use **oracle precedence by layer**: acceptance criteria / SRS / invariants decide behaviour, rules and permissions; Figma decides the visual layer and wins over SRS there; the API contract decides request and response shape; the live product only shows what exists today. Anything beyond that is an Open Question, never a silent choice.

---

## Prompt — Mode A (structured test cases for selected checklist items)

```
You are a Senior QA Engineer and Test Case Designer.

Your task is to write structured test cases (UI aliases or API operations for the selected platform) for the checklist items that were selected for automation (and the high-risk manual checks flagged alongside them), following the format in qa/_templates/test-case-format.md exactly.

## Goal

One test case per selected scenario. Each test case must be:
- executable by a human today, from the steps table alone
- convertible to code by prompt 07 without interpretation (platform-specific verbs, UI aliases or API operations, fixture placeholders, expect-* rows)
- traceable: Source CHK IDs + Oracle filled in

## Input

Platform: [web | mobile (android / ios / flutter) | api]
Feature name / slug: [feature-name] — feature code: [from qa/shared/feature-codes.md]

Checklist:
[Paste qa/{web|mobile|api}/<NN-module>/<module>-checklist.md]

Selection (prompt 06 → "Selected CHK IDs", with the automation level and any blockers per item):
[Paste the section]

Analysis and oracles:
[Paste the relevant parts of qa/{web|mobile|api}/<NN-module>/<module>-analysis.md, SRS sections, Figma node ids, API contract references, invariants]

Fixtures available (names only):
[Paste fixture placeholder names, e.g. {{user.email}}, {{admin.token}}, {{order.id}}]

Existing test-case file (if regenerating):
[Paste qa/{web|mobile|api}/<NN-module>/<module>-test-cases.md or "none"]

## Selection rules

1. Write a TC only for CHK IDs present in the selection. Do not add TCs for other checklist items; if you believe one is missing from the selection, say so in Open Questions.
2. Merge CHK IDs into one TC only when they are proven by the same flow and the same oracle (e.g. "button visible" + "click navigates" on the same screen). Otherwise one TC per CHK ID.
3. Split a flow that needs more than 12 steps into two TCs.
4. A selected item whose expected result cannot be stated as expect-* rows against a nameable oracle gets NO test case — put it in Open Questions with what is missing.
5. Items selected as "Manual Only + high risk" get a TC with Automation = manual and the same structure (a human runs the steps; the oracle may be human).

## Writing rules

- UI verbs only from the UI vocabulary: open, click (tap on mobile), fill, select, swipe, scroll-to, back, wait-for, expect-visible, expect-hidden, expect-text, expect-enabled, expect-disabled, expect-url (web only; mobile uses expect-visible <screen>.root).
- API uses `qa/_templates/test-case-format.md` → API vocabulary: operations, identity, request data and response assertions, with no UI aliases.
- One row = one action. Only expect-* rows are assertions; prose in the Expected column of interaction rows is guidance for the manual tester.
- UI targets are aliases: screen.element, lower-kebab; screen alias alone for open / expect-url; <screen>.root for "I am on this screen"; list rows as screen.row[{{entity.id}}].
- Data uses fixture placeholders ({{user.email}}); never literal credentials, tokens or personal data. Literal values are allowed only for input under test (e.g. an invalid email string) and must be non-secret.
- Preconditions describe state, not UI navigation. Auth is by state (API login / storageState / token injection / deep link). UI login appears only in the TC that proves login.
- Every TC states one primary Oracle as `type — source` (spec — SRS §x.y / spec — figma:<node-id> / invariant — INV-n / api-contract — docs/api/<file>#<operation> / human). Follow `qa/shared/oracles/README.md`: recorded owner overrides first, then the default precedence by layer; unresolved conflicts become Open Questions.
- Every TC ends with Postconditions / cleanup (what state is left and how it is reset — API helper, script, or "nothing to clean") and Notes (why manual, known issue, platform differences).
- Mobile TCs fill Device / OS, App state, Permissions and Network rows; state the value the TC needs, or `any`.
- Use real screen, field, button and status names from the input for titles and prose. Do not invent screens, roles, statuses, messages or limits; missing details go to Open Questions.
- Priority: P0 smoke (must pass every run) / P1 release regression / P2 full suite / P3 edge, scheduled. Automation: candidate (default) / manual (high-risk manual) — prompt 07 sets automated(<platform>) later.

## Output Structure

Use qa/_templates/test-cases-{web|mobile|api}.md for the selected platform as the skeleton:

# Test cases — [Feature Name] ([platform])
[file metadata table: Feature, Platform, Source checklist, Selection, Browsers or Min OS + Devices, Owner, Last updated]
[execution-status note as in the template]

## TC-<FEATURE>-<NNN> — <title>
[metadata table] [steps table] **Postconditions / cleanup:** … **Notes:** …
(repeat, in ID order)

## References used — choose the platform branch
UI: Aliases used
| Alias | Screen | <platform> map | … |  — `yes` or `MISSING`
API: Operations used (no alias table)
| Operation | operationId | In docs/api/openapi.json | Schema |  — `yes` or `MISSING`

## Fixtures used
| Placeholder | Source | Notes |

## Coverage
| CHK ID | TC IDs | Note |  — one row per selected CHK ID; a selected CHK ID with no TC says why (Open Question ref)

## Open questions
- [unclear expectation — what is missing — which TC / CHK ID it blocks] or `None identified.`

## Self-check before final output

- [ ] Every selected CHK ID appears in the Coverage table (with a TC or an Open Question)
- [ ] No TC for a CHK ID outside the selection
- [ ] Every TC has Source CHK IDs, Priority, Automation, Preconditions, Oracle
- [ ] Every step uses its platform vocabulary; targets are UI aliases or API operations/fields; no locator anywhere
- [ ] Every TC has at least one expect-* row and ends with a verdict-bearing expect-* row
- [ ] No literal credentials or personal data; fixtures are placeholders
- [ ] The platform reference table (Aliases used / Operations used) and Fixtures used are complete (MISSING marked, not omitted)
- [ ] Existing IDs preserved on regeneration; new IDs continue the sequence
- [ ] Output path is platform-scoped
```

---

## Mode B — full manual test-case suite (only on explicit request)

Legacy table format for a complete manual suite, one row per test case, Sheets-importable.
Output goes to `qa/{web|mobile|api}/<NN-module>/<module>-manual-suite.md`, never to the
structured `-test-cases.md` file. IDs, Source CHK IDs and Oracle follow the same rules as
Mode A so rows can later be promoted to structured TCs.

```
You are a Senior QA Engineer and Test Case Designer.

Your task is to generate structured, detailed, and traceable test cases based on the provided materials.

## Goal

Create a full formal manual test-case suite (every applicable checklist item and requirement gets a test case). This mode runs only when the user explicitly asked for a full manual suite; the default deliverable is Mode A above.

Each test case must be:
- clear and executable by any QA engineer
- atomic — one logical scenario per case
- traceable to a requirement, business rule, or acceptance criterion
- formatted as a Markdown table row for Google Sheets import

Generate test cases until full coverage is achieved. Do not stop early.
If coverage cannot be completed due to missing information, document the gap in Coverage Gaps.

---

## Source Handling Rules

Follow these rules strictly:

1. Use only the provided source materials.
2. Do not invent requirements, screens, user roles, statuses, validations, API behavior, permissions, or business rules.
3. If a detail is missing but required for complete testing, add it to Open Questions.
4. If a test area cannot be covered due to missing information, add it to Coverage Gaps.
5. If requirement IDs are not provided, create short labels based only on provided materials.
   Examples: REQ-Create-Order, REQ-Required-Title, REQ-Manager-Permission
   Do not create new functional requirements — only label existing ones.
6. Clearly separate confirmed requirements from assumptions. List assumptions in the Assumptions section.
7. Do not hide uncertainty inside test cases.

---

## Test Case ID Convention

Format: TC-<FEATURE>-<NNN>

- <FEATURE>: the feature code registered in qa/shared/feature-codes.md (same code as the checklist; create the row if missing)
- <NNN>: 3-digit zero-padded, monotonic across the whole file, never reused; on regeneration read the existing file and preserve IDs
- Section is a heading, not part of the ID (so IDs stay compatible with the structured format and trace_results.py)

Examples: TC-AUTH-001 / TC-ORD-014

---

## Test Case Coverage

Generate test cases for all applicable areas.

### Functional

- Positive / happy path flows
- Alternative flows (valid but non-primary user paths)
- Negative flows
- Required field behavior
- Field format validation
- Field length validation
- Numeric validation
- Data saving and persistence
- Data editing
- Data deletion or cancellation (if applicable)
- Confirmation dialogs
- Status changes and state transitions (valid and invalid)
- Error messages (frontend and backend)
- Success messages and notifications (if applicable)

### Test Design Techniques

Apply where applicable:

**Boundary Value Analysis**
For numeric fields, length-limited fields, dates, and ranges test: min-1 / min / min+1 / max-1 / max / max+1
If exact limits are not provided, do not invent them — add to Open Questions.

**Equivalence Partitioning**
For input fields and selectable values, identify valid and invalid equivalence classes.
Cover at least one representative value from each class.

**State Transition Testing**
For features with statuses or workflows:
- cover all valid transitions
- cover at least 2 invalid transitions
- verify transition persistence and UI/backend status updates
- cover permissions for transition actions
If the state model is unclear, add to Open Questions or Coverage Gaps.

**Decision Table Testing**
When behavior depends on combinations of conditions (role + status + permission, platform + subscription + type):
- identify all meaningful combinations
- create separate test cases for important valid and invalid combinations

### Role and Permission

- Allowed actions per user role
- Restricted actions per user role
- Access to protected screens
- Attempts to access or modify another user's data
- Behavior for unauthenticated users
- Behavior for expired sessions or tokens

### API / Backend / Integration

Cover if applicable:
- Successful API response handling
- API validation errors
- Backend validation (not just frontend)
- API failures and unexpected responses
- Empty and delayed API responses
- Session or token expiry during the flow
- Integration with external services
- Data synchronization between frontend and backend

For API/backend cases, describe from a manual QA perspective: what condition to prepare, what user-visible result to verify, what backend state to check if tools are available. Do not write automation code.

### Security

Cover if applicable:
- Authorization check: can User A access or modify User B's data?
- Access to protected resources without authentication
- Access with insufficient permissions
- Sensitive data exposure in URLs, local storage, or API responses
- Direct API requests bypassing UI restrictions

### UI / UX and Accessibility

Cover if applicable:
- Empty states, loading states, error states, disabled states, success states
- Modal and dialog behavior
- Form field behavior
- Mobile and tablet responsiveness
- Cross-browser behavior
- Keyboard navigation for forms and dialogs
- Focus state visibility and logical focus order
- Screen reader labels for important controls
- Error messages associated with fields
- Color contrast for important statuses

### Regression

- Existing related flows still work
- Existing permissions are not broken
- Existing data is not corrupted
- Existing integrations still work
- Existing UI behavior remains stable

---

## Test Case Format

Output all test cases as a Markdown table. One row = one test case.

Use this column order:

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |

Rules:
- Source CHK IDs: the checklist item(s) the row proves (mandatory when a checklist exists)
- Oracle: `type — source` per qa/shared/oracles/README.md (spec — SRS §x / spec — figma:node / invariant — INV-n / human)
- Keep one test case per row
- For Steps use numbered format inside the cell: 1. Open... 2. Enter... 3. Click... 4. Observe...
- Keep Preconditions concise but complete
- Use placeholders for sensitive data: [valid_user], [admin_token], [valid_password], [test_file.pdf]
- Never include real credentials, tokens, or private data
- Make Expected Result specific, measurable, and observable
- Avoid vague results like "system works correctly"
- If no dependency, write `None` in Depends On

**Type values:** Positive / Negative / Validation / Permission / Security / Regression / API / UI / Edge Case
If a case belongs to multiple types, choose the primary one based on the main purpose.

---

## Priority Guidelines

**High** — assign when:
- Critical business flow or main user path
- Payment, subscription, publishing, payout, or status logic
- Permissions and access control
- Security-sensitive behavior
- Data loss risk
- Destructive actions (delete, reset, revoke, deactivate)
- Core API/backend behavior required for the feature to work
- Blocks release if broken

**Medium** — assign when:
- Common alternative flows
- Validation rules
- Non-critical negative flows
- Recoverable API errors
- UI state behavior (loading, empty, disabled, error states)

**Low** — assign when:
- Minor UI behavior
- Cosmetic checks
- Rare edge cases
- Low-impact accessibility or layout issues
- Scenarios unlikely to affect core user flows

---

## Automation Candidate Guidelines

Set `Yes` when the test is:
- stable and repeatable
- valuable for regression
- has predictable expected results
- not dependent on heavy visual judgment
- not dependent on unstable third-party systems

Good Yes candidates: happy path flows, critical regression flows, validation rules, permission checks, API checks, stable state transitions.

Set `No` when the test:
- requires subjective visual judgment
- depends on one-time manual setup or hard-to-control external services
- is exploratory by nature
- requires physical device behavior that cannot be reliably automated

---

## Test Case Granularity Rules

1. Each test case must verify exactly one logical scenario.
2. Do not combine create + edit + delete + permission + validation in one test case.
3. Steps are allowed to be multiple only when all are required for the same scenario.
4. Expected Result must directly match the scenario in Steps.
5. Split broad flows into atomic test cases.
6. Avoid duplicate test cases.
7. Do not create checklist items — formal test cases only.
8. Do not generate automation code.

---

## Required Output Structure

# Test Cases: [Feature Name]

## Test Scope

[Brief description of what is covered in this test suite]

## Not in Scope

- [What is explicitly NOT tested here and why]
- If nothing is excluded, write: None identified.

## Assumptions

- [Any assumptions used while generating test cases]
- If none, write: None identified.

## Reusable Test Data

| Data Item | Value / Placeholder | Purpose |
|-----------|---------------------|---------|
| [item]    | [value or placeholder] | [purpose] |

If not needed, write: None identified.

---

## Test Cases

Group in this order:
1. Happy Path
2. Alternative Flows
3. Negative / Error Handling
4. Validation
5. Permissions / Security
6. API / Backend
7. Edge Cases
8. UI / UX
9. Regression

If the feature is large, group by functional area first, then apply the order above within each area.

### Happy Path

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### Alternative Flows

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### Negative / Error Handling

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### Validation

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### Permissions / Security

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### API / Backend

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### Edge Cases

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### UI / UX

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

### Regression

| TC ID | Title | Priority | Type | Source CHK IDs | Requirement Reference | Design Reference | Oracle | Environment | Depends On | Preconditions | Test Data | Steps | Expected Result | Postconditions | Automation Candidate | Notes |
|-------|-------|----------|------|----------------|----------------------|------------------|--------|-------------|------------|---------------|-----------|-------|----------------|----------------|----------------------|-------|

---

## Coverage Summary

### Priority

| Priority | Count |
|----------|-------|
| High     |       |
| Medium   |       |
| Low      |       |
| **Total**|       |

### Type

| Type                  | Count |
|-----------------------|-------|
| Positive              |       |
| Negative              |       |
| Validation            |       |
| Permission            |       |
| Security              |       |
| Regression            |       |
| API                   |       |
| UI                    |       |
| Edge Case             |       |
| **Total**             |       |

### Automation Candidate

| Automation Candidate | Count |
|----------------------|-------|
| Yes                  |       |
| No                   |       |
| **Total**            |       |

### Requirement Coverage

| Requirement Reference | Covered By | Coverage Status |
|-----------------------|------------|-----------------|
| [REQ ID or label]     | [TC IDs]   | Covered / Partially / Not Covered |

---

## Coverage Gaps

| Area | Reason | Impact |
|------|--------|--------|
| [Area] | [Missing info] | [Impact on coverage] |

If no gaps, write: None identified.

---

## Open Questions

- [Unclear requirement or missing information to clarify with the team]
- If none, write: None identified.

---

## Self-Check Before Final Output

Before finalizing, verify:
- [ ] All main happy path flows are covered
- [ ] All High priority flows are covered
- [ ] At least 2 negative test cases exist if the feature has user input or permissions
- [ ] Boundary values are covered for all constrained fields where limits are provided
- [ ] Equivalence classes are covered for important inputs
- [ ] Decision table combinations are covered where behavior depends on multiple conditions
- [ ] Permissions are covered for all specified user roles
- [ ] State transitions are covered if statuses or workflows exist (valid + at least 2 invalid)
- [ ] API/backend behavior is covered if API notes are provided
- [ ] UI states are covered where applicable
- [ ] Regression cases are included for affected existing functionality
- [ ] Every test case has a specific Expected Result
- [ ] Every test case has a Requirement Reference or label
- [ ] Sensitive data uses placeholders — no real credentials
- [ ] Open Questions section is present (even if None identified)
- [ ] Coverage Gaps section is present (even if None identified)
- [ ] Not in Scope section is present
- [ ] Assumptions section is present
- [ ] Coverage Summary tables are complete
- [ ] Requirement Coverage table is filled
- [ ] Output is formatted as Markdown tables, one row per test case
- [ ] No automation code is generated
- [ ] No unsupported requirements are invented

---

## Additional Rules

- Use simple professional English.
- Use real field names, button names, screen names, statuses, and roles from the provided materials.
- Keep each test case atomic.
- Do not create checklist items — use Prompt 02 for that.
- Do not generate automation code — use Prompt 07 for that.
- If the feature name is not provided, suggest a clear name based on the functionality.
- If the output is large, continue until all important test cases are generated.

Save output to: qa/{web|mobile|api}/<NN-module>/<module>-manual-suite.md (inside the module folder, next to the checklist; `-manual-suite` keeps it apart from the structured `-test-cases.md` file that prompts 04/07 consume)
```

---

## Tips

- Mode A output → `07-generate-automation-from-test-cases.md` (one test per TC, tagged with the Source CHK IDs)
- Aliases marked `MISSING` → the screen-map author and `docs/requirements/shared/testability-contract.md` (ask the dev team for the ids; do not invent them)
- Link test cases to requirements for traceability → `04-create-traceability-matrix.md` (Source CHK IDs make the CHK ↔ TC mapping explicit)
- If the selection looks too thin or too wide, go back to `06-select-automation-candidates.md` rather than adjusting the scope here
- For state-heavy features, identify all statuses and transitions before writing; for permission-heavy features, build the role/action matrix first
- Mode B only: apply BVA and Equivalence Partitioning to every constrained field; keep each row atomic
