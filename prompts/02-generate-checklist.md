# 02 — Generate QA Checklist

## When to Use
- After completing `01-analyze-srs-and-design.md`
- For smoke testing and regression passes
- When full test cases are not yet written but testing must begin

## Input Required
- Output from Prompt 01: `qa/{web|mobile|api}/<NN-module>/<module>-analysis.md`
- Or directly: SRS, requirements, designs, business rules, API notes, acceptance criteria

---

## Project overrides (read first)

These rules override the prompt body below for this project:

1. **No automation markers on checklist items.** Candidate selection is a separate step: `prompts/06-select-automation-candidates.md`.
2. **Use available sources for the selected platform.** For UI, read the relevant
   web/mobile Figma map when design is available; pull structure and images via the
   project-local Figma MCP. For API, use the API contract and confirmed business rules;
   no Figma is needed. Apply `qa/shared/oracles/README.md` (recorded owner overrides,
   then defaults by layer). With only a running product, record observations and owner
   confirmations or an explicitly adopted baseline; unconfirmed expectations are Open
   Questions. Missing design blocks only checks that need that design.
3. **Every checklist item MUST start with a stable ID** in the format `[CHK-<FEATURE>-<NNN>]`:
   - `<FEATURE>` is the feature code for the slug. Codes live in [qa/shared/feature-codes.md](../qa/shared/feature-codes.md) — look the slug up there and **create the row if it is missing** (2–5 uppercase letters, unique per platform, never reused or renamed). Fallback when no row exists yet: first 4 letters of the slug, uppercase (then register it).
   - `<NNN>` is a zero-padded 3-digit sequence number, monotonically increasing across the whole file (NOT restarted per section).
   - **When regenerating an existing checklist**: read the prior file first and PRESERVE existing IDs. Only assign new IDs to genuinely new checks, using numbers higher than the current max.
   - Format: `1. [CHK-AUTH-001] Check that ...`
   - IDs are the contract for syncing into Google Sheets via `automation/tools/sync_checklist_to_sheets.py`. Changing or reusing an ID will break status tracking.

## Prompt

```
## Role

You are a Senior QA Engineer.

Your task is to generate a clear, complete, and practical manual QA checklist based on the provided SRS, design, QA analysis, acceptance criteria, user stories, API notes, business rules, previous QA comments, and known issues.

## Goal

Create a checklist that can be copied into Google Sheets and used for manual testing.

The checklist must cover all meaningful and testable behaviors from the input, including only areas that are relevant or directly supported by the provided materials:
- positive scenarios
- negative scenarios
- validation rules
- permissions per user role
- UI behavior
- status behavior
- API/backend-related behavior
- notifications and alerts
- sorting, filtering, pagination
- empty states
- loading states
- error states
- edge cases
- regression risks
- cross-browser behavior
- security basics

Do not force checklist sections for areas that are not applicable to the feature.

## Input

[Paste content from qa/{web|mobile|api}/<NN-module>/<module>-analysis.md or source docs]

Use all available project materials:
- SRS
- design screenshots
- QA analysis
- acceptance criteria
- user stories
- API notes
- business rules
- previous QA comments
- known issues
- feature-specific context

If source materials conflict, do not choose one silently. Add the conflict to "Open Questions" and generate only checks that are supported by consistent input.

If behavior is unclear, missing, or not testable based on the provided input, add it to "Open Questions" instead of inventing a checklist item.

If the feature consists of multiple components (e.g., list page + detail page + modal), treat each component as a named sub-context within the relevant sections. Do not create a separate checklist per component — keep everything in one unified checklist, but reference the component name in each item where needed.

## Output Location

Save the result into the feature's module folder (`<NN-module>` = module folder, `NN` = order in the SRS, `<module>` = the feature slug registered in `qa/shared/feature-codes.md`):

`qa/{web|mobile|api}/<NN-module>/<module>-checklist.md`

- Web → `qa/web/<NN-module>/<module>-checklist.md` (e.g. `qa/web/01-authentication/authentication-checklist.md`)
- Mobile → `qa/mobile/<NN-module>/<module>-checklist.md` (state the sub-target — ios / android / flutter / cross-platform — in the checklist's Platform metadata, not in the path)
- API → `qa/api/<NN-module>/<module>-checklist.md` (items are operations, roles and rules from `docs/api/openapi.json` + the SRS; the oracle of an item is the operation or an invariant, never a screen)
- Cross-cutting a11y / security / performance / i18n → `qa/shared/checklists/[feature-name]-checklist.md`

Never write directly under `qa/web/`, `qa/mobile/` or `qa/api/` without a module folder. If the feature name is not provided, suggest a clear file name based on the analyzed functionality.

## Checklist Style Rules

Follow these rules strictly:

1. Write all checklist items in English.
2. Use a numbered list.
3. Restart numbering from 1 in each section.
4. Every checklist item must start with: `Check that`
5. Each checklist item must be one sentence only.
6. Each checklist item must be clear and independently testable.
7. Use simple professional QA language.
8. Use the logic: What to verify → UI location or API operation → sourced expected result. Apply only sections relevant to the selected platform.
9. Avoid unnecessary long wording.
10. Avoid duplicate checks.
11. Avoid vague phrases like "works correctly", "displays properly", "handles correctly", or "functions as expected".
12. Do not combine several independent checks into one item.
13. Do not invent requirements not present in the input.
14. Do not use tables — they break Google Sheets import.
15. Each checklist item must be on a separate line.
16. Format must be easy to copy into Google Sheets.
17. Generate all meaningful and non-duplicated checklist items needed to cover the testable behavior from the input.
18. Enumerate all user roles from the input and cover permission checks for each role separately.
19. Within action-based sections (Positive Flow, Negative Flow, API and Backend Error Handling), order checklist items according to the user journey: access → page load → data entry → action → result → persistence → error handling. In structural sections (UI Layout, Validation, Security), order by visual or logical grouping instead.
20. If a check applies only under a specific condition, put the condition at the end of the sentence using `if`.
21. Keep section headings plain.
22. Do not use the word "SECTION".
23. Do not add introductory text before the checklist.
24. Do not add closing summaries after the checklist.
25. Do not create test steps here.
26. Do not create full test cases here.

## Security Rules

For Security, include only basic checks that are directly relevant to:
- access control
- authorization
- role restrictions
- sensitive data visibility
- session behavior
- input handling
- file access
- API permissions

Do not add generic security checks unless they are relevant to the provided input.

## Regression Rules

Regression Checks must focus only on existing related functionality that may be impacted by this feature.

Do not duplicate checks already listed in other sections.

Regression checks should verify that previously existing behavior still works after the new or changed functionality is introduced.

## Open Questions Rules

Use "Open Questions" for:
- missing requirements
- unclear behavior
- conflicts between SRS and design
- missing validation rules
- missing role permissions
- missing API behavior
- unclear error handling
- unclear empty/loading states
- unclear notification behavior
- unclear status transitions

Each Open Question must clearly mention:
- the unclear area
- the conflicting or missing detail
- why it affects testing

Do not create checklist items based on assumptions from Open Questions.

## Section Boundary Rules

- Mobile Responsiveness: layout, element visibility, and touch interaction on mobile screen sizes (320px–767px). Do not include browser-specific behavior here.
- Cross-browser: behavior differences across Chrome, Firefox, and Safari on desktop. Do not duplicate mobile checks here.
- If a check is relevant to both mobile and cross-browser, place it under Mobile Responsiveness and do not repeat it in Cross-browser.

## Coverage Summary Rules

Count only checklist items, not Open Questions.

Use the following categories:
- functional: checks related to user actions, flows, business rules, and feature behavior
- UI: checks related to layout, visible elements, labels, controls, responsive behavior, and cross-browser behavior
- validation: checks related to required fields, formats, limits, invalid data, and validation messages
- permissions: checks related to roles, access, authorization, and visibility restrictions
- edge cases: checks related to empty states, loading states, error states, backend failures, boundary cases, and unusual but valid scenarios

## Checklist Item Examples

Good examples:

1. Check that the Create button is visible on the Orders page for a user with the Admin role.
2. Check that the Order title field displays a required field error below the input if the user submits the Order form without entering a title.
3. Check that the selected customer data is prefilled in all editable fields of the Order form after the user picks a customer from the Customer dropdown.
4. Check that the Save button keeps the order in Draft status when the user saves a valid unsubmitted order.
5. Check that a descriptive error message is shown and no form data is lost when the Save request returns a 500 error.
6. Check that a user with the Viewer role cannot see the Create button on the Orders page.
7. Check that a success toast message appears at the top right of the screen after the profile is saved successfully on the Profile editor.
8. Check that the order list is sorted by creation date descending by default on the Orders page.
9. Check that the Delete confirmation modal remains open and displays a descriptive error message if the Delete request fails due to a server error.
10. Check that the Save button remains disabled on the Profile editor if all required fields are empty.

Bad examples:

1. Check that everything works correctly.
2. Check validation.
3. Check UI.
4. Check that user can create, edit, delete, save, submit, and export an order.
5. Verify screen.
6. Check that permissions work.
7. Check that error handling works correctly.
8. Check that the page looks good.
9. Check that the system handles all edge cases.
10. Check that the feature is secure.

## Output Format

Use this exact structure.

Omit a section only if it is truly not applicable to the feature or not supported by the input.

# QA Checklist: [Feature Name]

## Access and Permissions

1. Check that ...

## Navigation

1. Check that ...

## UI Layout

1. Check that ...

## Fields and Controls

1. Check that ...

## Positive Flow

1. Check that ...
2. Check that ... if ...

## Validation

1. Check that ...

## Negative Flow

1. Check that ... if ...

## Status Behavior

1. Check that ...

## Notifications and Alerts

1. Check that ...

## Sorting, Filtering, and Pagination

1. Check that ...

## Data Saving and Persistence

1. Check that ...

## API and Backend Error Handling

1. Check that ... if ...

## Empty States

1. Check that ...

## Loading States

1. Check that ...

## Mobile Responsiveness

1. Check that ...

## Cross-browser

1. Check that ...

## Security

1. Check that ...

## Regression Checks

1. Check that ...

## Open Questions

- [Unclear area — conflicting or missing detail — why it affects testing]

**Coverage summary:** functional: X / UI: X / validation: X / permissions: X / edge cases: X
```
