# Prompt 01 — Analyze SRS and Design

## Purpose
Analyze source documentation to extract testable requirements, identify gaps, compare SRS with design, and build a shared QA understanding before writing any test artifacts.

## When to Use
- At the start of a new feature or project
- After receiving updated SRS, requirements, or Figma designs
- Before generating checklists or test cases (always run this first)
- Before reviewing test coverage or selecting automation candidates

## Input Required
Place relevant files in `docs/` before running:
- `docs/srs/` — Software Requirements Specification
- `docs/requirements/` — Functional & non-functional requirements
- `docs/designs/` — Figma screenshots or exported design files
- `docs/business-rules/` — Business logic and rules
- `docs/api/` — API documentation, Swagger, Postman collection, or endpoint descriptions
- `docs/notes/` — BA, client, developer, or QA notes, meeting minutes, decisions, known issues (if available)
- `docs/environments.md` — environments, base URLs, roles and where test accounts live (pointers only; feeds section 5 Preconditions and section 13)
- `docs/00-intake/` — unsorted material not yet triaged; read it, use what is relevant, and log where each item should move in `docs/00-intake/intake-log.md` (see `docs/README.md`)

If a document type is missing, state it explicitly and proceed with available inputs.

---

## Design input from Figma (read first)

Read available design for UI analysis using the project-local Figma MCP server below.
API-only work needs no design. When no design/documents exist, use the live-product +
owner route in `qa/shared/oracles/README.md`: record observations, obtain scoped expected
behaviour from the owner, and continue independent checks without Figma.

1. Open the design map [docs/designs/web/figma-sources.md](../docs/designs/web/figma-sources.md)
   (mobile: `docs/designs/mobile/`) to get the `fileKey` and the `node-id` of the screen(s)
   relevant to the SRS section being analyzed.
2. Read structure and content with `mcp__figma__get_figma_data` (`fileKey` + `nodeId`).
3. Capture the rendered screen with `mcp__figma__download_figma_images` when visual layout,
   exact labels, states, or element placement matter.
4. Validate the SRS section **against what the design actually shows**. Every UI element,
   field, control, state, label, and flow seen in the design must be reflected in section 8
   (UI Elements) and reconciled in section 15 (Design vs SRS Comparison).

Rules:
- Apply `qa/shared/oracles/README.md`: recorded owner overrides, then default precedence
  by layer. Record the resolution; raise unresolved conflicts as Open Questions.
- If the relevant screen is not in the design map or the file is unreadable, state it
  explicitly and proceed with available inputs (do not invent design behavior).
- If a needed resource is missing, note exactly what and from where it should come.

---

## Prompt

```
You are a Senior QA Engineer and Test Analyst. Analyze the provided documentation and produce a structured QA analysis report.

Input documents:
[Paste content or attach files from docs/srs/, docs/requirements/{shared,web,mobile}/, docs/designs/, docs/business-rules/, docs/api/, docs/notes/, docs/environments.md, docs/00-intake/]

The analysis will serve as the source for:
- checklist generation
- test case generation
- traceability matrix
- coverage review
- automation candidate selection
- open questions for BA / Dev / Designer

Produce a report with the following sections:

---

## 1. Feature Overview
Describe what the feature does in simple QA-oriented language.
Include:
- What problem it solves and its business value
- What is in scope and what is explicitly out of scope
- How this feature connects to other modules or features in the system
- Affected user roles and platforms (if specified)

If scope is not clear, mark as "Not specified" and add a question to Open Questions.

---

## 2. Source Documents Reviewed
List all documents, designs, API references, screenshots, or notes used for this analysis.

| Source ID | Source Name | Type | Version / Date | Notes |
|-----------|-------------|------|----------------|-------|

Type may be: SRS / Requirement / Figma / API / Business Rule / QA Note / Client Note / Developer Note

If version or date is not available, mark as "Not specified".

---

## 3. Testable Requirements Inventory
Extract all testable requirements from the provided documentation.

| Req ID | Requirement | Type | Priority | Source | Notes |
|--------|-------------|------|----------|--------|-------|

Requirement Type may be: Functional / UI / Validation / Business Rule / Permission / API / Data / Non-functional / Compatibility / Integration

Priority: High / Medium / Low / Not specified

Rules:
- Include only requirements supported by provided sources
- Do not invent requirements
- If a requirement is implied but not directly stated, mark Notes as "Assumption" and add it to section 16

---

## 4. User Roles and Permissions
Identify all user roles involved in the feature.

| Role | Allowed Actions | Restricted Actions | UI / Behavior Differences | Source |
|------|-----------------|--------------------|---------------------------|--------|

If roles or permissions are not specified, mark as "Not specified" and add a question to Open Questions.

---

## 5. Preconditions
List all required preconditions before testing can start.

| Precondition | Area | Required Value / State | Source | Notes |
|--------------|------|------------------------|--------|-------|

Include:
- user authentication state
- required user role
- required test data
- backend/API dependencies
- feature flags
- environment requirements
- required app state and object status

If a precondition is not specified but appears necessary, mark as "Assumption".

---

## 6. Main User Flows
Describe each positive user flow using this format:

**Flow name:**
**Actor:**
**Preconditions:**
**Steps:**
1. ...
2. ...
3. ...
**Expected result:**
**Source:**

Keep each flow clear and independently testable.
Do not add test data unless provided in the source.
If a flow is partially unclear, describe the known part and add the unclear part to Open Questions.

---

## 7. Alternative and Negative Flows
Identify alternative paths and negative scenarios using the same format as section 6:

**Flow name:**
**Actor:**
**Preconditions:**
**Steps:**
1. ...
2. ...
3. ...
**Expected result:**
**Source:**

Cover at minimum, if applicable:
- validation errors
- empty states
- disabled states
- permission restrictions
- failed API responses
- network errors
- expired or invalid data
- incorrect input
- duplicate or missing required data
- interrupted or cancelled actions
- edge cases

Do not invent error messages. If not provided, mark as "Not specified".

---

## 8. UI Elements and Screen States
List visible UI elements grouped by screen or page.

**Screen / Page name:**

| Element Type | Element Name | Description / Behavior | State | Source |
|--------------|--------------|------------------------|-------|--------|

Include: fields, buttons, links, tabs, filters, labels, icons, status indicators, popups, confirmation dialogs, error messages, success messages, loading states, empty states, disabled states.

If an element exists in design but not in SRS, or vice versa — mark it for section 15 (Design vs SRS Comparison).
Do not describe decorative elements unless they affect testing.

---

## 9. Validation Rules
Extract all field-level and action-level validation rules.

| Field / Action | Rule | Valid Input Example | Invalid Input Example | Expected Message | Source |
|----------------|------|--------------------|-----------------------|------------------|--------|

If examples are not provided in the source, mark as "Not specified".
Do not invent error messages. If not specified, mark as "Not specified".

---

## 10. Business Rules
Extract business logic rules only. Do not repeat field validation from section 9.

| Rule ID | Rule Description | Trigger | Expected Behavior | Source | Notes |
|---------|------------------|---------|-------------------|--------|-------|

Business rules may include:
- status transitions and allowed state changes
- date and time restrictions
- permission-based behavior
- object uniqueness and publishing rules
- assignment, cancellation, synchronization rules
- pricing or subscription logic
- data visibility rules

Flag any contradictions or edge cases found.

---

## 11. State Model and Transitions
If the feature includes object statuses, lifecycle states, publication states, subscription states, or similar — document them here.

| Object | Current State | Trigger / Action | Next State | Allowed? | Expected Behavior | Source | Notes |
|--------|---------------|------------------|------------|----------|-------------------|--------|-------|

Examples: Draft → Published / Active → Inactive / Pending → Verified / Active → Cancelled

If states are not specified, mark as "Not specified".
If transitions are implied but not documented, add them to section 16 (Assumptions) and Open Questions.

---

## 12. Non-Functional Requirements
Document non-functional constraints.

| Category | Requirement | Source | Notes |
|----------|-------------|--------|-------|

Categories: Performance / Security / Authentication / Authorization / Data protection / Accessibility / Usability / Reliability / Error recovery / Logging / Localization / Time zone handling

Do not invent NFRs. If missing but important for testing, mark as "Not specified" and add to Open Questions.

---

## 13. Test Environment and Compatibility
Specify the required test environment and compatibility scope.

| Area | Requirement / Scope | Source | Notes |
|------|---------------------|--------|-------|

Include: browsers and versions / operating systems / devices and screen sizes / desktop, tablet, mobile / app versions / API versions / feature flags / third-party services

If not specified, mark as "Not specified" and flag in Open Questions.

---

## 14. Data and API Dependencies
Identify backend, API, data, and integration dependencies.

| Endpoint / Service | Method | Trigger | Expected Response / Result | Source | Notes |
|--------------------|--------|---------|----------------------------|--------|-------|

Also document:
- required, created, updated, deleted entities
- data persistence expectations
- external services and integrations
- synchronization behavior
- possible backend validation
- permissions enforced by backend

If API details are not available, mark as "Not specified" and add to Open Questions.

---

## 15. Design vs SRS Comparison
Compare the SRS and design.

| Area | SRS Behavior | Design Behavior | Status | QA Note | Source |
|------|--------------|-----------------|--------|---------|--------|

Status: Match / Gap / Conflict / Not clear / Design only / SRS only

Do not assume design or SRS is correct by default. Add unresolved conflicts to Open Questions.

---

## 16. Assumptions
List all conclusions based on implied but not directly documented behavior.

| Assumption ID | Assumption | Reason | Impact | Needs Confirmation From |
|---------------|------------|--------|--------|--------------------------|

Impact: Blocks testing / Blocks test design / Affects coverage / Needs confirmation / Low impact

Do not mix assumptions with confirmed requirements. Add high-impact assumptions to Open Questions.

---

## 17. Risks
Identify QA risks with priority and impact.

| Risk | Area | Priority | Impact | Notes |
|------|------|----------|--------|-------|

Priority: High / Medium / Low

Risk areas: functional / integration / data consistency / permissions / mobile compatibility / browser compatibility / API/backend / UX / regression / security / performance / unclear requirements / third-party dependencies

---

## 18. Open Questions
List all unclear, missing, or conflicting information.

| Gap ID | Question | Area | Impact | Needs Answer From |
|--------|----------|------|--------|-------------------|

Impact: Blocks testing / Blocks test design / Affects coverage / Needs clarification
Needs Answer From: BA / Dev / Designer / Product Owner / Client / QA Lead

Make each question specific and actionable. Use format: GAP-01, GAP-02, GAP-03.

---

## 19. Suggested Test Areas
Group future testing into clear test areas.

| Test Area | Type | Automation Potential | Priority | Notes |
|-----------|------|----------------------|----------|-------|

Type: Functional / UI / Validation / Permission / API / Integration / Compatibility / Regression / Non-functional
Automation Potential: Auto / Manual / Both / Not recommended
Priority: High / Medium / Low

Examples: UI layout and responsiveness / field validation / positive flows / negative flows / permissions / status transitions / API error handling / mobile and cross-browser / regression / data synchronization

Do not generate checklist items or test cases in this section.

---

## Output Location

Save the main analysis into the feature's module folder (web → `qa/web/`, mobile → `qa/mobile/`; a feature shipping on both gets one file per platform). `<NN-module>` is the module folder (`NN` = order in the SRS, `<module>` = the feature slug registered in `qa/shared/feature-codes.md`), e.g. `qa/web/01-authentication/authentication-analysis.md`:
qa/{web|mobile}/<NN-module>/<module>-analysis.md

Also create related follow-up files if applicable:
- qa/{web|mobile}/<NN-module>/<module>-questions.md — from section 18 (module-level open questions; a question that spans modules goes to `qa/shared/questions/`)
- qa/shared/risks/[feature-name]-risks.md — from section 17 (product-level risk register, no platform split)
- qa/{web|mobile}/<NN-module>/<module>-traceability.md — from section 3 (the requirements inventory seeds the matrix; prompt 04 completes it in the same file)

If the feature name is not provided, suggest a clear file name based on the analyzed functionality.

---

## Rules
- Do not invent requirements, error messages, API endpoints, user roles, or permissions
- Do not invent compatibility scope or NFRs
- If information is missing, mark it as "Not specified"
- If behavior is unclear, add it to Open Questions
- If design and SRS conflict, clearly mark the conflict
- If a conclusion is based on assumption, add it to section 16
- Keep confirmed facts, assumptions, risks, and questions clearly separated
- Include source references in all tables where possible
- If source is unclear, mark as "Not traceable"
- Use simple and professional QA language
- Prefer tables for structured information
- Do not generate test cases, checklist items, or automation scripts
- Focus only on analysis
```

---

## Tips
- Run this before any other prompt in the workflow
- Section 18 (Open Questions) → save to `qa/{web|mobile}/<NN-module>/<module>-questions.md` (cross-module questions: `qa/shared/questions/`)
- Section 17 (Risks) + Section 19 Automation Potential → feed into `06-select-automation-candidates.md`
- Section 19 (Suggested Test Areas) → feed into `02-generate-checklist.md`
- Section 3 (Requirements Inventory) → feed into traceability matrix prompt
