# Prompt 04 — Create Traceability Matrix

## Purpose

Map requirements to design elements, checklist items, and test cases to ensure full coverage.

This prompt helps identify:
- untested requirements
- partially covered requirements
- design/SRS mismatches
- unclear or contradictory requirements
- automation gaps
- redundant tests
- release risks caused by missing or weak coverage

## When to Use

- After test cases are generated (`03-generate-test-cases.md`)
- After checklist is created (`02-generate-checklist.md`)
- Before release to verify that no important requirements are untested
- During audits or client reporting
- After any requirement change — re-run to update coverage
- Before selecting candidates for automation (`06-select-automation-candidates.md`)

## Input Required

- Source requirements from `docs/srs/` or `docs/requirements/`
- Acceptance criteria and business rules from `docs/business-rules/`
- Design screenshots or references from `docs/designs/`
- API/backend notes from `docs/api/`, if available
- QA analysis notes from `qa/{web|mobile|api}/<NN-module>/<module>-analysis.md` (`<NN-module>` = module folder in SRS order, `<module>` = the feature slug from `qa/shared/feature-codes.md`, e.g. `qa/web/01-authentication/`)
- Generated checklist from `qa/{web|mobile|api}/<NN-module>/<module>-checklist.md`
- Structured test cases from `qa/{web|mobile|api}/<NN-module>/<module>-test-cases.md` (their `Source CHK IDs` row is the explicit CHK ↔ TC mapping — use it instead of guessing); a Mode B `-manual-suite.md` file if one exists
- Automated run results, if any: the report `automation/tools/trace_results.py` writes with `--out` (by convention `qa/{web|mobile|api}/<NN-module>/<module>-traceability.md` — CHK IDs with a tagged test that ran)
- Known issues and bug reports from `qa/{web|mobile|api}/<NN-module>/bugs/`, if any
- Open questions from `qa/{web|mobile|api}/<NN-module>/<module>-questions.md` (and product-level ones in `qa/shared/questions/`)

> If any input is not available, proceed with what is provided and note each absence
> in the Open Questions section of the output.

---

## Prompt

```text
You are a Senior QA Engineer and Test Analyst.

Your task is to create a practical traceability matrix that links requirements, design elements,
checklist items, test cases, automation status, and known issues.

## Goal

Create a clear QA traceability matrix to show real test coverage and identify gaps.

The matrix must help answer:
- Which requirements are covered?
- Which requirements are partially covered?
- Which requirements are not covered?
- Which design elements are covered?
- Which checklist items map to which requirements?
- Which test cases cover which requirements?
- Which tests are automated vs manual?
- Where are the coverage gaps?
- Where are the automation gaps?
- Which requirements are blocked by known issues?
- Which items need clarification?
- Which areas create release risk?

## Input

Use the available materials:
[Paste content from: SRS, requirements, acceptance criteria, business rules, API notes,
design references, QA analysis, checklist, test cases, known issues, open questions]

If any input is missing, note the absence in the Open Questions section
and proceed with what is available.

## Requirement ID Rules

If requirement IDs exist in the SRS or requirements documentation, use them.

If the project works from user stories, the acceptance criterion is the requirement row:
`Req ID` = `<story id>/AC-<n>` (e.g. `US-12/AC-3`), `Source` = `Acceptance Criteria`, and the
criterion is quoted verbatim in the Requirement column. A story with no acceptance
criteria is one `❓ Needs Clarification` row, never a set of invented criteria. The same
`<story id>/AC-<n>` is what bug reports cite (prompt 08) and what the checklist item names
as its oracle — one id from story to bug.

If requirement IDs do not exist anywhere, create IDs using this format:

REQ-[FeatureCode]-001

Example:

REQ-ORDER-001

For compound requirements with multiple acceptance criteria, create one row per acceptance criterion,
not one row per large requirement.

For atomic requirements, one row per requirement is sufficient.

Do not invent new requirements.
Only extract requirements, acceptance criteria, business rules, API/backend rules, or design-only items
from the provided materials.

## Design-Only Item Rules

Include design-only items only if they affect testing.

Examples of design-only items that should be included:
- navigation behavior
- visible states
- validation messages
- disabled/enabled states
- required UI elements
- empty states
- error states
- confirmation modals
- user decision points
- data displayed to the user

Do not include purely decorative items unless they affect usability, accessibility, or acceptance criteria.

For design-only items that are not present in SRS or requirements, create IDs using this format:

DESIGN-[FeatureCode]-001

Example:

DESIGN-ORDER-001

Mark Source as `Design`.

If a design-only item conflicts with SRS, include it in the matrix and also list it
in the Design and SRS Gaps section.

## Checklist Item ID Rules

If checklist items have IDs, use them.

If checklist items do not have IDs, assign IDs using this format:

CHK-[FeatureCode]-001

Example:

CHK-ORDER-001

Do not create new checklist items in the matrix.
If a checklist item is missing, add the gap to Notes and Action Items.

## Test Case ID Rules

Use existing test case IDs if available.

If test case IDs do not exist, suggest IDs using this format:

TC-[FeatureCode]-001

Example:

TC-ORDER-001

Do not create new test cases here.
Only reference existing test cases or suggest missing test cases in Notes and Action Items.

## Source Values

Use one of the following values in the Source column:

- SRS
- Requirements
- Acceptance Criteria
- Business Rules
- API/Backend
- Design
- QA Analysis
- Known Issue
- Open Question

If a row is based on more than one source, separate values with a comma.

Example:

SRS, Design

## Requirement Type Values

Use one of the following values in the Requirement Type column:

- Functional
- UI/UX
- Validation
- Permission
- API/Backend
- Notification
- Error Handling
- Data
- Status/Workflow
- Integration
- Non-functional
- Design-only

Choose the most specific type.
If more than one type applies, use the dominant one and explain the secondary impact in Notes.

## Priority Rules

Assign a priority level to each requirement row.

Use the priority from source documentation if available.

If priority is not specified, assign based on impact:

- Critical — core user flows, data integrity, security, payments, access control, irreversible actions
- High — main feature functionality, important user flows, major validation or status behavior
- Medium — secondary features, frequent edge cases, non-blocking but important scenarios
- Low — cosmetic issues, minor UI behavior, low-frequency edge cases

Always fill in the Priority column. Never leave Priority blank.

## Design Reference Rules

Use the screen name, page name, frame name, or file name from the design file.

Format examples:
- Screen-Login
- Screen-Order-Form
- Frame-Checkout-Step1
- Modal-Delete-Confirmation
- design-01.png
- Figma: Order Form / Line Item Settings

If using Figma, use the frame name visible in the Figma layers panel.

If no design exists for this requirement, write `—`.

If a requirement should have a design but the design is missing, write `—` and add a note:

Design reference missing.

## Backend/API Rules

Include backend/API rules when they affect:
- visible behavior
- validation
- permissions
- status transitions
- data persistence
- calculations
- integrations
- notifications
- error handling
- user-visible results

If an API/backend rule is not directly visible to the user but affects system behavior,
include it in the matrix and mark Requirement Type as `API/Backend`, `Data`,
`Status/Workflow`, or `Integration`.

## Coverage Status Values

Use only these values in the Coverage Status column:

- ✅ Covered — the requirement has valid checklist coverage and valid test case coverage
- ⚠️ Partially Covered — the requirement has only checklist coverage, weak test case coverage,
  incomplete coverage of conditions/expected results, or has a test case but no checklist item
- ❌ Not Covered — the requirement has no checklist item and no test case
- 🔴 Blocked — testing is blocked by missing data, missing environment, unavailable integration,
  unresolved defect, or another blocker
- ❓ Needs Clarification — the requirement is unclear, incomplete, contradictory, or not testable as written
- — Not Applicable — the requirement is explicitly out of scope for this cycle, platform, role, or release;
  must include the reason in Notes

## Test Type Values

Use only these values in the Test Type column:

- Manual — covered by manual test case only
- Auto — covered by automated test only
- Manual+Auto — covered by both manual and automated tests
- Planned — manual test exists and automation is planned but not implemented yet
- — — no test case exists

Important:
`Planned` means automation is planned for an existing manual test case.
A row with `Planned` can still be marked as `✅ Covered` if the requirement has valid checklist
coverage and valid manual test case coverage.

Do not mark a requirement as `⚠️ Partially Covered` only because automation is not implemented.
Coverage Status is about requirement coverage.
Test Type is about execution and automation type.

## Evidence Rules

Map checklist items and test cases to requirements only when there is clear evidence from:
- checklist item title or text
- test case title
- test case preconditions
- test case steps
- expected results
- explicit requirement references
- acceptance criteria references

A requirement can be marked as `✅ Covered` only if the mapped checklist item and/or test case
explicitly validates:
- the expected behavior
- the relevant condition
- the expected result

Do not mark a requirement as covered based only on a loosely related test case.

If the relationship is reasonable but not fully explicit, add this note:

Assumed mapping — needs QA review.

If a test case touches a requirement indirectly but does not validate its expected result,
do not count it as full coverage.

## Over-Mapping Prevention

Do not map one generic checklist item or test case to many requirements unless it explicitly
validates each of them.

Avoid using broad test cases such as:
- Verify the screen works correctly
- Verify user can complete the flow
- Verify data is displayed correctly

as full coverage for multiple specific requirements.

If a broad test case partially covers a requirement, mark the row as `⚠️ Partially Covered`
and explain what is missing in Notes.

Do not overstate coverage. The matrix must show real coverage, not optimistic assumed coverage.

## Known Issues Rules

If a requirement is covered by tests but currently affected by a known bug, keep the Coverage Status
based on test coverage and add the bug ID in the Known Issue / Bug ID column.

If a known issue blocks validation of the requirement, mark the row as `🔴 Blocked`.

If a known issue shows that a requirement is failing but tests exist, do not mark the requirement
as `❌ Not Covered`. Instead, mark it according to test coverage and mention the bug in Notes.

Examples:
- Covered by TC-001 but currently failing due to BUG-123
- Blocked by unavailable API endpoint
- Blocked by missing test data
- Known issue affects expected status update

## Traceability Rules

1. Do not invent requirements.
2. Do not invent checklist items.
3. Do not invent test cases.
4. Map each requirement to at least one checklist item or test case if clear evidence exists.
5. If a requirement has no checklist item and no test case — mark as ❌ Not Covered.
6. If a requirement has a checklist item but no test case — mark as ⚠️ Partially Covered.
7. If a requirement has a test case but no checklist item — mark as ⚠️ Partially Covered and note that checklist coverage is missing.
8. If a requirement has a checklist item and a valid test case — mark as ✅ Covered.
9. If a requirement is unclear — mark as ❓ Needs Clarification.
10. If testing is blocked by missing data, environment, integration, or known issue — mark as 🔴 Blocked.
11. If a requirement is out of scope for this cycle — mark as — Not Applicable and add the reason in Notes.
12. Add notes for gaps, conflicts, assumptions, weak coverage, or missing evidence.
13. Include design-only items if they affect testing.
14. Include SRS-only items if they are missing in design.
15. Include backend/API rules if they affect visible or system behavior.
16. Assign Priority to every row.
17. Assign Source to every row.
18. Assign Requirement Type to every row.
19. Do not create automation scripts.
20. Do not create new test cases here — add suggestions to Notes or Action Items only.

## Output Format

---
Feature: [Feature Name]
Requirements Version: [v1.0 or source version if available]
Matrix Version: [v1.0]
Created: [Date]
Last Updated: [Date]
Author: [QA Engineer Name]
---

# Traceability Matrix: [Feature Name]

## Matrix

Sort rows by Priority (Critical first, then High, Medium, Low),
then within each priority group by Coverage Status (❌ Not Covered first, then ⚠️, then 🔴, then ❓, then ✅).

| Req ID | Source | Requirement Type | Priority | Requirement / Business Rule | Design Reference | Checklist Item ID | Test Case ID | Test Type | Coverage Status | Known Issue / Bug ID | Notes |
|--------|--------|------------------|----------|-----------------------------|------------------|-------------------|--------------|-----------|-----------------|----------------------|-------|
| REQ-001 | SRS | Functional | High | [Description] | Screen-Login | CHK-001 | TC-001, TC-002 | Manual+Auto | ✅ Covered | — | |
| US-12/AC-3 | Acceptance Criteria | Validation | High | "[criterion quoted verbatim]" | Screen-Login | CHK-002 | — | — | ⚠️ Partially Covered | — | Missing test case |
| REQ-003 | Business Rules | Permission | Critical | [Description] | — | — | — | — | ❌ Not Covered | — | Not covered by checklist or test cases |
| REQ-004 | SRS, Design | UI/UX | Medium | [Description] | Screen-Order-Form | CHK-003 | TC-003 | Manual | ❓ Needs Clarification | — | Acceptance criteria unclear |
| REQ-005 | API/Backend | Status/Workflow | High | [Description] | — | CHK-004 | TC-004 | Planned | ✅ Covered | — | Manual test exists; automation planned |
| DESIGN-001 | Design | Design-only | Medium | [Description] | Modal-Delete-Confirmation | — | — | — | ⚠️ Partially Covered | — | Design-only behavior needs test case |
| REQ-006 | SRS | Functional | Low | [Description] | — | — | — | — | — Not Applicable | — | Out of scope for v1.0 |
| REQ-007 | SRS | Integration | Critical | [Description] | Screen-Payment | CHK-008 | TC-008 | Manual | 🔴 Blocked | BUG-123 | Payment provider sandbox unavailable |

## Coverage Summary

- Total Requirements: X
- In-Scope Requirements: X
- ✅ Covered: X (X% of in-scope)
- ⚠️ Partially Covered: X (X% of in-scope)
- ❌ Not Covered: X (X% of in-scope)
- 🔴 Blocked: X (X% of in-scope)
- ❓ Needs Clarification: X (X% of in-scope)
- — Not Applicable: X (excluded from in-scope percentage)

> Percentages calculated against in-scope requirements only:
> % = count / (Total Requirements - Not Applicable) × 100

## Coverage by Requirement Type

| Requirement Type | Total | Covered | Partially Covered | Not Covered | Blocked | Needs Clarification |
|------------------|-------|---------|-------------------|-------------|---------|---------------------|
| Functional | X | X | X | X | X | X |
| UI/UX | X | X | X | X | X | X |
| Validation | X | X | X | X | X | X |
| Permission | X | X | X | X | X | X |
| API/Backend | X | X | X | X | X | X |
| Error Handling | X | X | X | X | X | X |
| Status/Workflow | X | X | X | X | X | X |
| Integration | X | X | X | X | X | X |

Only include rows for requirement types that are present in the matrix.

## Automation Coverage

- 🤖 Automated (Auto + Manual+Auto): X (X% of in-scope requirements)
- 📊 Automated among covered only: X (X% of covered requirements)
- ✋ Manual only: X
- 📋 Planned for automation: X
- ⬜ Not automated and not planned: X

Count `Auto` and `Manual+Auto` as automated.
Count `Planned` separately. Do not count `Planned` as automated.

## Coverage Gaps

List uncovered or partially covered areas, sorted by priority:

- [Priority] [REQ-ID]: [Description] — [What is missing]

Focus especially on Critical and High priority requirements.

## Automation Gaps

List important requirements or test cases that are manual only or planned but not automated:

- [Priority] [REQ-ID] / [TC-ID]: [Description] — [Suggested automation type: UI / API / E2E]

Prioritize automation suggestions for:
- high-risk flows
- regression-critical flows
- repetitive scenarios
- API/backend validation
- status transitions
- permission checks
- data persistence
- payment/subscription flows

## Design and SRS Gaps

List mismatches between design and SRS:

- [Item]: [SRS says X, but design shows Y]
- [Item]: [Design contains behavior not described in SRS]
- [Item]: [SRS contains requirement missing in design]

## Known Issues Impact

List known issues that affect requirement coverage or release confidence:

| Bug ID | Related Req ID | Impact | Status / Notes |
|--------|----------------|--------|----------------|
| BUG-001 | REQ-001 | Blocks validation of [behavior] | [Status or note] |
| BUG-002 | REQ-005 | Requirement is covered but currently failing | [Status or note] |

If known issues were not included in the input, write:

No known issues were provided.

If known issues were provided but none affect the requirements in this matrix, write:

No known issues identified for this feature.

## Open Questions

List questions that must be clarified before full coverage can be confirmed.
Include missing inputs here.

- [Question or missing input]

Examples:
- SRS was not provided.
- Design file was not provided.
- Test cases are missing for [area].
- Requirement [REQ-ID] is unclear.
- Expected behavior for [scenario] is not defined.

## Action Items

| Priority | Action | Owner | Due Date |
|----------|--------|-------|----------|
| High | Create test case for [REQ-ID] | QA | — |
| High | Clarify requirement [REQ-ID] with BA/PO | QA + PO | — |
| Medium | Add checklist item for [REQ-ID] | QA | — |
| Medium | Automate [TC-ID] | Automation Engineer | — |
| Low | Review redundant test [TC-ID] | QA | — |

Action items must be based on actual gaps found in the matrix.
Replace all template rows with actual items from your analysis.
Do not keep placeholder rows. Do not add generic action items.

## Redundant Tests

List test cases not linked to any requirement.
Do not remove without team review — may indicate undocumented business rules.

- [TC-ID]: [Title] — [Suggested action: link to REQ-XXX, mark as exploratory, update, or remove after review]

If there are no redundant tests, write:

No redundant tests were identified.

## Release Risk Summary

Summarize release risk based on uncovered, partially covered, blocked, and unclear Critical/High requirements.

Risk levels:
- Low Risk — all Critical/High requirements are covered and no major blockers exist
- Medium Risk — some Medium/Low gaps exist, but Critical/High coverage is acceptable
- High Risk — one or more Critical/High requirements are not covered, partially covered, or unclear
- Blocked — one or more Critical/High requirements cannot be validated due to blockers

Format:

Release Risk: [Low Risk / Medium Risk / High Risk / Blocked]

Reason:
- [Reason 1]
- [Reason 2]

Recommendation:
- [Proceed / Proceed with limitations / Do not release until blockers are resolved / Clarify requirements before sign-off]

## Save Output To

- `qa/{web|mobile|api}/<NN-module>/<module>-rtm.md` (reviewed, human-owned requirements↔checks↔tests matrix; automated verdicts live next to it in `<module>-traceability.md`, which `automation/tools/trace_results.py` regenerates on every run — never edit that one by hand)
- `_bmad-output/test-artifacts/traceability/{web|mobile}/[feature-name]-traceability-matrix.md` (AI draft)

Platform-scoped: web → `qa/web/<NN-module>/`, mobile → `qa/mobile/<NN-module>/`. A feature on both platforms gets one matrix per platform.

If the feature name is not provided, suggest a clear file name based on the analyzed functionality.

## Additional Rules

- Keep the matrix practical and readable.
- Use short but clear descriptions.
- Do not create new requirements, checklist items, or test cases.
- Do not create automation scripts.
- Do not over-map generic tests to specific requirements.
- Focus only on traceability, coverage visibility, gaps, and release risk.
- Always fill in Source, Requirement Type, Priority, and Coverage Status.
- If information is missing, be explicit about the missing input.
- If a mapping is assumed, mark it: Assumed mapping — needs QA review.
- If evidence is weak, mark the row as ⚠️ Partially Covered.
```

---

## Tips

- Use BMAD skill `/bmad-testarch-trace` for more detailed traceability workflows
- ❌ Not Covered + Critical/High priority → add the check to the checklist first, then (if it is an automation candidate) a structured TC in `qa/{web|mobile|api}/<NN-module>/<module>-test-cases.md`
- ⚠️ Partially Covered → route through `06-select-automation-candidates.md` → `03` → `07` (web: `automation/web/playwright/tests/`, mobile: `automation/mobile/tests/`)
- 🤖 Automation Coverage low → run `/bmad-testarch-automate` to expand coverage
- 🔴 Blocked → resolve known issues before release sign-off
- Release Risk: High or Blocked → do not sign off without team review
- Share the matrix with stakeholders before sign-off or release
- Redundant tests with no requirement → review before removing, may indicate undocumented rules
- Re-run this prompt after any requirement change or after new test cases are added
- For large features (50+ requirements) — split the matrix by module or sub-feature; one matrix per logical area is more readable than one giant table
