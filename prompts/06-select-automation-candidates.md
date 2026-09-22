# Prompt 06 — Select Automation Candidates

## Purpose

Review the checklist (and any existing QA artifacts) and select the best candidates for automation. Classify each scenario, identify blockers, define required test data, and produce a realistic automation plan for the platform's stack — Playwright + TypeScript (web) or Appium + Python + pytest (mobile). The output's "Selected CHK IDs" section is the scope for `03-generate-test-cases.md`: only selected checklist items get structured test cases.

This prompt helps avoid over-automation and focuses on high-value, stable, maintainable scenarios.

---

## When to Use

- After the checklist exists (`02-generate-checklist.md`) and before structured test cases are written (`03-generate-test-cases.md` consumes the selection)
- After the coverage review (`05-review-coverage.md`), if one was done
- When planning a new automation sprint or deciding what to add to the regression suite
- Before implementing a Playwright (web) or Appium (mobile) suite
- When developers need a clear list of required test IDs and API support

---

## Input Required

### Required

- Checklist from `qa/{web|mobile|api}/<NN-module>/<module>-checklist.md` (`<NN-module>` = module folder in SRS order, `<module>` = the feature slug from `qa/shared/feature-codes.md`, e.g. `qa/web/01-authentication/authentication-checklist.md`) — the unit of selection is the `[CHK-…]` item
- Risk analysis from `qa/{web|mobile|api}/<NN-module>/<module>-analysis.md`
- Feature code from `qa/shared/feature-codes.md`

### Optional but Recommended

- Coverage review from `qa/{web|mobile|api}/<NN-module>/<module>-coverage-review.md` (prompt 05 writes exactly there)
- Existing structured test cases from `qa/{web|mobile|api}/<NN-module>/<module>-test-cases.md` (re-selection runs) or a Mode B `-manual-suite.md`
- Requirements traceability matrix from `qa/{web|mobile|api}/<NN-module>/<module>-rtm.md` (prompt 04); automated verdicts, if any, from `<module>-traceability.md` (trace_results.py)
- Testability contract `docs/requirements/shared/testability-contract.md` and existing screen maps (`automation/web/playwright/screens/`, `automation/mobile/screens/`) — tells you which selectors already exist
- SRS or functional requirements from `docs/srs/` or `docs/requirements/`
- Design screenshots from `docs/designs/`
- API documentation from `docs/api/`
- Business rules from `docs/business-rules/`
- Known issues, previous QA notes, or bug reports

---

## Prompt

```text
You are a Senior QA Automation Engineer and Manual QA Strategist.

Your task is to review the provided QA artifacts and select realistic automation candidates for the platform's stack.

Your output will be used by:
- QA engineers planning the first automation sprint
- developers adding stable test IDs (docs/requirements/shared/testability-contract.md)
- Prompt 03, which writes structured test cases ONLY for the CHK IDs you select
- Prompt 07, which generates test code from those test cases

Platform: [web | mobile (android / ios / flutter)]
Automation stack: [web: Playwright + TypeScript, tests in automation/web/playwright/tests/ | mobile: Appium + Python + pytest, tests in automation/mobile/tests/{android|ios|shared}/]
Base URL / app build: [from docs/environments.md]
Feature name: [feature-name] — feature code: [from qa/shared/feature-codes.md]

Input:
[Paste content from qa/{web|mobile|api}/<NN-module>/<module>-checklist.md — selection is per [CHK-…] item]
[Paste risk analysis from qa/{web|mobile|api}/<NN-module>/<module>-analysis.md]
[Paste additional materials if available: coverage review from qa/{web|mobile|api}/<NN-module>/<module>-coverage-review.md, existing test cases, SRS, designs, traceability matrix, API notes, known issues, testability contract / screen maps]

---

## Step 0: Input Quality Check

Before selecting automation candidates, assess whether the provided checklist and supporting materials are ready for automation planning.

Check whether the input contains:

- stable checklist IDs ([CHK-<FEATURE>-<NNN>] on every item)
- clear, single-assertion checklist items
- preconditions
- user roles
- test data requirements
- expected results
- environment assumptions
- dependencies on backend state
- dependencies on third-party services
- cleanup expectations
- known risks or open questions

Output:

### Input Quality Summary

- Overall input quality: High / Medium / Low
- Main gaps:
  - [Gap 1]
  - [Gap 2]
  - [Gap 3]

If important information is missing, continue with the available input but clearly mark assumptions and planning gaps.

Do not invent missing requirements, APIs, selectors, credentials, or test data.

---

## Step 1: Automation Readiness Rating

Assess overall readiness of this feature for automation.

Use one of these ratings:

- Ready for automation
- Partially ready for automation
- Not ready for automation yet

Briefly explain the rating in 2–3 sentences.

Consider:

- stability of requirements
- stability of UI
- availability of test data
- availability of stable selectors
- availability of API support
- environment readiness
- risk of flaky tests

---

## Step 2: Recommended Automation Approach

Choose the overall recommended approach before planning details:

- UI automation only
- API setup + UI validation
- API validation only
- Manual now, automate later
- Hybrid approach

Briefly justify the choice in 1–2 sentences.

Guidance:

- Prefer lower-level automation when possible.
- Preserve the owner's UI priority: API coverage does not replace selected user-visible checks. Offer API-assisted UI or standalone API coverage where useful; record a different testing priority only when the owner chooses it.
- Use UI automation for critical user flows, permissions, validations visible to users, and business-critical paths.
- Prefer documented API setup when available. Without API access, use scoped UI fixtures or read-only UI scenarios; block only scenarios whose own prerequisites are missing.
- Use API validation to verify backend state after UI actions.
- Keep subjective visual checks, exploratory testing, hardware-dependent scenarios, and unstable flows manual unless a reliable automation strategy exists.

---

## Step 3: Score Each Checklist Item

For each checklist item in scope (or each existing test case, when a structured TC file is provided), assign scores:

- ROI: High / Medium / Low
- Stability: High / Medium / Low
- Risk Coverage: High / Medium / Low

### ROI Guidance

High ROI:
- repetitive regression scenario
- business-critical flow
- time-consuming manual validation
- frequently executed in release cycles
- high chance of catching regressions

Medium ROI:
- useful regression scenario
- moderate manual effort
- important but not release-blocking

Low ROI:
- rarely executed
- very quick manual check
- low business impact
- high automation cost compared to value

### Stability Guidance

High Stability:
- predictable UI
- stable selectors available
- deterministic result
- reliable test data
- no dependency on external systems

Medium Stability:
- requires setup or cleanup
- depends on backend state
- has moderate async behavior
- needs stable test IDs before automation

Low Stability:
- depends on animations or transitions
- uses dynamic external content
- depends on third-party widgets or iframes
- depends on email or SMS verification
- depends on file uploads/downloads without stable test hooks
- depends on time-sensitive behavior
- requires subjective visual judgment
- requires hardware, GPS, camera, real payment, or real device-specific behavior

### Risk Coverage Guidance

High Risk:
- core business flow
- payment, subscription, publishing, permissions, authentication, or data integrity
- affects many users
- previously had defects
- release blocker if broken

Medium Risk:
- important secondary flow
- affects a specific role or configuration
- moderate business impact

Low Risk:
- cosmetic or low-impact behavior
- rarely used edge case
- minor validation

Use the scores as input for classification in Step 4. Do not make a binary Automate/Skip decision in this step.

---

## Step 4: Automation Candidate Matrix

Create a matrix for all checklist items in scope (one row per CHK ID; if a structured TC already covers it, put the TC ID in the same cell).

| CHK / TC ID | Scenario / Test Area | Automation Level | ROI | Stability | Risk Coverage | Automation Status | Priority | Suggested Tags | Reason | Blockers / Requirements |
|------|----------------------|------------------|-----|-----------|---------------|-------------------|----------|----------------|--------|--------------------------|

### Automation Level values

- E2E UI
- API
- API setup + UI assertion
- Component / UI-level
- Manual only
- Not applicable yet

### Priority levels

- P1 — smoke / business-critical, should pass in every CI run
- P2 — regression, should run before release
- P3 — edge case, should run in full suite or scheduled runs

### Automation Status values

- Good Candidate — stable, repetitive, business-critical, predictable data, suitable for regression
- Medium Candidate — useful but needs setup, partially stable, or dependent on backend state
- Manual Only — requires visual judgment, exploratory testing, subjective UX, real payments, hardware, or real device behavior
- Needs API Support — requires API to create data, reset state, trigger events, or verify backend
- Needs Stable Selectors — missing test IDs, unstable CSS, dynamic structure, or generated class names
- Needs Test Data Setup — requires specific users, roles, statuses, permissions, or preconfigured records
- Not Recommended Now — requirements unclear, UI unstable, feature changing, or maintenance cost too high

### Suggested Tags

- `@smoke` — must pass before any release
- `@regression` — full regression suite
- `@critical` — business-critical path
- `@flaky` — known instability, should run separately
- `@wip` — not ready, placeholder only
- `@api` — API-level validation
- `@e2e` — end-to-end UI scenario
- `@manual-only` — should remain manual

### Classification guidance

Use this logic when assigning Automation Status:

- Good Candidate: ROI = High or Medium, Stability = High, Risk Coverage = High or Medium
- Medium Candidate: ROI = High or Medium, Stability = Medium, or the test requires setup/support before automation
- Needs API Support: scenario is valuable but cannot be automated reliably without API setup, cleanup, state reset, or backend verification
- Needs Stable Selectors: scenario is valuable but current UI selectors are unstable or unavailable
- Manual Only: Stability = Low and scenario requires human judgment, hardware, real payment, real device behavior, exploratory testing, or subjective UX evaluation
- Not Recommended Now: ROI = Low and Stability = Low, or requirements/UI are unclear or changing

For Manual Only or Not Recommended Now, clearly explain why automation is not recommended now.

---

## Step 5: Best First Automation Candidates

List the best first scenarios to automate.

Include 3–10 scenarios depending on suite size and candidate quality.

Format:

1. [CHK / TC ID] [Scenario name] — [Reason]

Selection criteria:

- highest ROI
- high stability
- high or medium risk coverage
- suitable for smoke or core regression
- independent or easy to isolate
- can be implemented without major blockers

If fewer than 3 suitable candidates exist, list only the realistic candidates and explain why the number is limited.

---

## Step 5b: Selected CHK IDs (handoff to Prompt 03)

This section is the contract with `03-generate-test-cases.md`: it writes structured test cases ONLY for the rows below. Include every Good Candidate and Medium Candidate, plus Manual Only items whose Risk Coverage is High (they get a `manual` test case with an exact script). Everything else stays a checklist item.

| CHK ID | Automation Level | Priority | Automation Status | Blockers to clear before Prompt 07 | Note |
|--------|------------------|----------|-------------------|------------------------------------|------|

Rules:
- One row per CHK ID; no CHK ID outside the input checklist.
- `Manual Only` rows in this table must say `high-risk manual` in Note.
- **Selection is by risk, never by quota.** A row is here because of its ROI, Stability and
  Risk Coverage scores (Step 3): business impact, repeatability, stability of the surface,
  isolation (can the test own its data), maintenance cost. Do not add or drop rows to hit a
  number. As a sanity check only: a UI module usually lands around 10–20 % of its checklist,
  a stable API module can be far higher, a brand-new UI far lower — when the result is far
  from what the module's nature suggests, explain why in one sentence under the table.

---

## Step 6: Manual-Only Scenarios

List scenarios that should remain manual for now.

| CHK / TC ID | Scenario | Reason to Keep Manual | Revisit Later? |
|------|----------|-----------------------|----------------|

Common reasons:

- requires visual or subjective judgment
- requires exploratory testing
- requires real payment, real subscription, or production-only flow
- requires hardware, GPS, camera, biometric, or device-specific behavior
- depends on email/SMS without test hooks
- depends on third-party systems that are not stable in test environments
- automation cost is higher than value
- requirements are unclear or changing

Do not recommend destructive, payment, subscription, or production-only flows for regular CI automation unless a dedicated safe test environment and safe test accounts are available.

---

## Step 7: Scenarios Requiring API Support

List scenarios that need API support before automation.

| CHK / TC ID | Scenario | API Action Needed | Endpoint if Known | Priority | Notes |
|------|----------|-------------------|-------------------|----------|-------|

API action types:

- Create test user or record
- Reset status or state
- Delete created data after test
- Trigger notification or callback
- Verify backend state
- Prepare user roles or permissions
- Simulate external service response
- Mock email or SMS verification
- Prepare payment/subscription test state
- Clean up test data

Rules:

- Do not invent missing endpoints.
- If endpoint is unknown, write `Unknown — needs dev confirmation`.
- Clearly mark API support that blocks automation.

---

## Step 8: Scenarios Requiring Stable Selectors

List UI areas where stable selectors are needed.

Suggest test IDs using this format:

| CHK / TC ID | UI Element | Suggested testId | Reason |
|------|------------|------------------|--------|

Test ID naming convention (docs/requirements/shared/testability-contract.md — the same id on every platform):

- `<screen>-<element>`, readable kebab-case, feature-scoped.
- Do not base test IDs on visual position, styling, text, or generated classes.
- Every screen has `<screen>-root`; list rows carry the entity id (`<screen>-row-<id>`); every error / toast / empty state / spinner has an id.
- Also give the platform-neutral alias (`screen.element`) the test case will use — that is the handshake with the screen map.

Examples:

| CHK / TC ID | UI Element | Alias | Suggested testId | Reason |
|------|------------|-------|------------------|--------|
| CHK-ORD-003 | Save button | order-form.save | order-form-save | Needed for stable save action |
| CHK-ORD-003 | Title field | order-form.title | order-form-title | Needed for stable form input |
| CHK-ORD-005 | Submit button | order-form.submit | order-form-submit | Needed for stable submit action |
| CHK-ORD-006 | Status filter | orders.status-filter | orders-status-filter | Needed for reliable filtering |

Do not invent existing selectors. Only suggest new test IDs needed for reliable automation; check the existing screen maps first.

---

## Step 9: Required Test Data

List required test data per test case.

| CHK / TC ID | Data Type | Description | Source | Reusable? | Cleanup Needed? |
|------|-----------|-------------|--------|-----------|-----------------|

Source options:

- API fixture
- DB seed
- Manual setup
- Existing test account
- Generated at runtime
- Mocked service
- Unknown — needs clarification

Data categories to cover:

- user accounts and roles
- prepared records and statuses
- specific dates
- permissions
- feature configurations
- preconfigured backend state
- files or images for upload
- payment/subscription test data if applicable
- external service test data if applicable

Prefer generated runtime data or API fixtures when possible.

Avoid tests depending on fragile shared data unless there is no realistic alternative.

---

## Step 10: Authentication & Session Handling

Identify authentication requirements for automation.

Create a role matrix:

| Role | Required For CHK / TC IDs | Login Method | Test Account Needed | Notes |
|------|---------------------|--------------|---------------------|-------|

Login method options:

- `storageState` (web)
- API login / token injection into app storage (mobile) or deep link with a session
- custom auth fixture
- `beforeAll` / `beforeEach` UI login flow — only for the one test that proves login itself (determinism rule: auth by state everywhere else)
- manual only

Assess:

- which user roles are needed
- whether multi-role scenarios require session switching
- whether tests need separate browser contexts
- whether token expiry can affect execution
- whether session timeout creates flakiness
- whether accounts can be reused safely in parallel runs

Recommend the safest authentication strategy for the platform's stack (auth by state; UI login only in the login smoke test).

---

## Step 11: Test Isolation Assessment

For each Good Candidate or Medium Candidate, assess whether the test can run independently.

| CHK / TC ID | Independent? | Creates Data? | Cleanup Needed? | Parallel-Safe? | Shared-State Risk | Setup/Teardown Recommendation |
|------|--------------|---------------|-----------------|----------------|-------------------|-------------------------------|

Assess:

- Can the test run independently in any order?
- Does it create data that must be cleaned up after?
- Does it depend on state left by another test?
- Does it modify shared records?
- Could it fail when tests run in parallel?
- Does it require unique generated data?
- Does it need API cleanup after execution?

Recommended setup/teardown options:

- `beforeAll` suite setup
- `beforeEach` data setup
- `afterEach` cleanup
- `afterAll` cleanup
- API cleanup helper
- isolated test account per worker
- unique generated test data
- manual cleanup only

Every Good Candidate must have a defined isolation assessment.

---

## Step 12: Automation Plan

Create a practical implementation plan.

### Test Files to Create

Recommended structure — web:

automation/web/playwright/tests/
  [feature-name]/
    [feature-name].spec.ts              — P0/P1 smoke + core flows using @smoke @critical
    [feature-name]-regression.spec.ts   — P2 regression cases using @regression
    [feature-name]-edge.spec.ts         — P3 edge cases if needed

Recommended structure — mobile:

automation/mobile/tests/
  shared/test_[feature-name].py         — cross-platform flows (@pytest.mark.shared)
  android/test_[feature-name].py        — Android-only behaviour (@pytest.mark.android)
  ios/test_[feature-name].py            — iOS-only behaviour (@pytest.mark.ios)

Every test carries the CHK IDs it proves (Playwright `tag: ['@CHK-…']`; pytest `@pytest.mark.chk("CHK-…")` + `@allure.tag`) — see automation/README.md.

### Screen Maps and Page Objects

automation/web/playwright/screens/[screen].map.ts  — alias → locator (web)
automation/mobile/screens/[screen]_map.py           — alias → locator per platform (mobile)
automation/web/playwright/pages/[FeatureName]Page.ts / automation/mobile/pages/  — optional flow helpers on top of the map

List the screens whose maps must exist before Prompt 07 can run, and which aliases are already resolvable.

For each Page Object, briefly describe responsibility:

| Page Object | Responsibility |
|------------|----------------|
| [FeatureName]Page.ts | [Description] |

### Suggested Fixtures / Helpers

automation/web/playwright/fixtures/
automation/web/playwright/helpers/

Identify what should be implemented as:

| Type | Name | Responsibility |
|------|------|----------------|
| Fixture | [fixture-name] | [Purpose] |
| Helper | [helper-name] | [Purpose] |
| API Helper | [api-helper-name] | [Purpose] |
| Data Builder | [data-builder-name] | [Purpose] |

Guidance:

- Page Objects should contain UI interactions and locators.
- Fixtures should manage authentication, browser context, and reusable setup.
- API helpers should create, reset, verify, or delete backend data.
- Data builders should generate unique and reusable test data.

### Execution Order

List CHK / TC IDs in recommended implementation order:

1. [CHK / TC ID] [Title] — [Reason for priority]
2. [CHK / TC ID] [Title] — [Reason for priority]

Start with:

- smoke tests
- stable happy paths
- high-risk regression scenarios
- scenarios with available data and selectors
- scenarios that can run independently

### Estimated Effort

Estimate:

- Total test cases reviewed: X
- Good Candidates: X
- Medium Candidates: X
- Manual Only: X
- Not Recommended Now: X
- Total test cases recommended for first automation sprint: X
- Estimated development time: X hours
- Maintenance risk: Low / Medium / High

Use rough effort estimation:

- Simple UI validation: 1–2 hours
- Standard form flow with setup/cleanup: 3–5 hours
- API setup + UI validation: 4–6 hours
- Multi-role scenario: 5–8 hours
- Complex external dependency, file upload, notification, payment, or subscription flow: 8+ hours
- Scenario requiring missing test IDs or missing API support: do not include in active estimate until blocker is resolved

Maintenance risk guidance:

High maintenance risk if:

- many dynamic elements
- frequent UI changes
- complex data setup
- third-party dependencies
- unstable selectors
- time-dependent behavior
- no API cleanup
- parallel execution risks

Low maintenance risk if:

- stable UI
- predictable data
- simple flows
- reusable Page Objects
- API setup/cleanup available
- stable selectors available

---

## Step 13: Runtime Notes (Playwright / Appium)

Provide runtime behavior notes, not code.

Cover:

- stable locator strategy (resolved through the screen map, never inline in tests)
- recommended use of `data-testid` / `resource-id` / `accessibilityIdentifier` per the testability contract
- use of ARIA roles (web) / accessibility ids (mobile) where appropriate
- when visible text locators are acceptable
- `beforeAll` setup
- `beforeEach` setup
- `afterEach` teardown
- `afterAll` teardown
- browser/context strategy
- retries policy if relevant
- handling of async operations
- handling of loading states
- handling of network requests
- handling of test data uniqueness
- recommended tags for fast and full test runs

Locator strategy priority (automation/README.md):

1. ARIA role / accessible label
2. `data-testid` (web) / test id or accessibility id (mobile)
3. stable visible text
4. never structural CSS or XPath — a missing id is a testability defect, not a reason to use one

Do not recommend selectors based on:

- generated class names
- visual position
- CSS styling
- fragile DOM hierarchy
- dynamic text that changes frequently

Do not generate test code here — that is Prompt 07, after the structured test cases exist.

---

## Step 14: CI/CD Readiness

Assess whether automated tests can run in CI.

| Area | Status | Notes / Requirements |
|------|--------|----------------------|
| Headless execution | Ready / Not Ready / Partial | [Notes] |
| Environment variables | Ready / Not Ready / Partial | [Notes] |
| Credentials | Ready / Not Ready / Partial | [Notes] |
| Test data | Ready / Not Ready / Partial | [Notes] |
| API setup/cleanup | Ready / Not Ready / Partial | [Notes] |
| External services | Ready / Not Ready / Partial | [Notes] |
| Parallel execution | Ready / Not Ready / Partial | [Notes] |
| Runtime duration | Acceptable / Too long / Unknown | [Notes] |

Assess:

- Can tests run in headless mode without manual intervention?
- Are environment variables required?
- Are credentials required?
- Are API keys or service tokens required?
- Are there dependencies on external services?
- Is test data environment-specific?
- Are tests staging-only or production-only?
- Are there long-running tests that should be excluded from fast CI runs?
- Which tests are safe for CI?
- Which tests require special setup?

Recommend:

- tests safe for every PR run
- tests safe for nightly runs
- tests safe only before release
- tests that should not run in CI yet

---

## Step 15: Risks and Blockers

Categorize all identified risks and blockers.

### Technical Risks

Include risks such as:

- flaky behavior
- dynamic content
- timing issues
- animation dependencies
- unstable selectors
- iframe or third-party widget dependency
- file upload/download instability
- browser-specific behavior

### Data Risks

Include risks such as:

- missing fixtures
- production-only data
- shared test data
- data cleanup challenges
- test account conflicts
- environment-specific records
- inability to reset state

### Environment Risks

Include risks such as:

- no staging environment
- staging not matching production
- third-party service dependencies
- unstable test environment
- missing environment variables
- missing credentials
- unavailable API endpoints

### Process Blockers

Include blockers such as:

- missing test IDs
- unclear requirements
- changing requirements
- missing API endpoints for setup or cleanup
- no backend reset mechanism
- no ownership for test data
- no agreement on automation scope
- team capacity or knowledge gaps

Output format:

| Category | Risk / Blocker | Impact | Recommended Action | Owner |
|----------|----------------|--------|--------------------|-------|

Owner options:

- QA
- Automation QA
- Developer
- DevOps
- Product Owner
- Design
- Unknown

---

## Step 16: Final Recommendation

Provide a concise final recommendation.

Include:

- whether automation should start now
- what should be automated first
- what must be resolved before implementation
- what should remain manual
- recommended first sprint scope
- expected benefit of the first automation sprint

Format:

### Final Recommendation

[Clear summary in 3–6 sentences]

### First Sprint Scope

- [CHK / TC ID] [Scenario]
- [CHK / TC ID] [Scenario]
- [CHK / TC ID] [Scenario]

### Must Be Resolved Before Automation Starts

- [Blocker 1]
- [Blocker 2]
- [Blocker 3]

---

## Rules

- Do not automate everything.
- Prioritize high-value, stable, independent scenarios.
- Prefer lower-level automation when possible.
- Preserve the owner's UI priority: API coverage does not replace selected user-visible checks. Offer API-assisted UI or standalone API coverage where useful; record a different testing priority only when the owner chooses it.
- Do not recommend automation for unclear or unstable functionality.
- Do not generate automation code in this prompt.
- Do not invent missing APIs.
- Do not invent existing selectors.
- Do not invent credentials, test accounts, or test data.
- Clearly mark assumptions.
- Clearly mark what must be resolved before automation can start.
- Keep the plan realistic for a QA engineer building the suite incrementally.
- Every Good Candidate must have a defined tag, priority, and isolation assessment.
- Every Medium Candidate must have a clear blocker or condition before implementation.
- Every Manual Only scenario must have a reason why it should remain manual.
- Avoid production, payment, subscription, destructive, or real-user-data automation unless a dedicated safe test environment and safe test accounts are available.

Save output to (platform-scoped):

_bmad-output/test-artifacts/test-design/{web|mobile|api}/[feature-name]-automation-plan.md
```

---

## Tips
- Next: `03-generate-test-cases.md` (structured TCs for the Selected CHK IDs) → `07-generate-automation-from-test-cases.md` (code) → `/bmad-testarch-test-review`
- Use `/bmad-testarch-automate` to expand coverage after the initial suite is built
- Prioritize P1 test cases first — build the regression suite incrementally
- Unstable selectors → review BMAD TEA knowledge: `selector-resilience.md`
- API support gaps → align with the dev team before starting automation
- storageState for auth → see Playwright docs on authentication reuse across tests
