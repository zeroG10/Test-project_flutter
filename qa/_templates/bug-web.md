# BUG-<CODE>-NNN — [Short title]

> `<CODE>` = the module's feature code from [qa/shared/feature-codes.md](../shared/feature-codes.md),
> `NNN` = zero-padded, unique within the module, never reused. File location and name:
> `qa/web/<NN-module>/bugs/BUG-<CODE>-NNN.md` (e.g. `qa/web/01-authentication/bugs/BUG-AUTH-001.md`).
>
> **Evidence lives next to it**, one folder per bug: `bugs/evidence/BUG-<CODE>-NNN/` with at
> least a screenshot of the defect and a raw capture of the request/response and console.
> Evidence is committed — the client report is built from it. Playwright traces stay
> gitignored; name the command that reproduces the run instead.

> **Process:** whether it is a defect at all, the severity walk, the wording and the filing
> go are governed by [prompts/08-file-bug.md](../../prompts/08-file-bug.md). This file is the
> format only. Filing to a tracker is owner-confirmed (doctrine rule 5).

## Summary

One sentence describing the problem.

> **Wording by layer.** Frontend bugs are written from the USER's perspective: steps are
> the UI journey, actual/expected is what the user sees. Backend/API bugs are written from
> the API's perspective: exact `METHOD /endpoint` calls, actual/expected are response
> fields (e.g. `coverUrl = null`). Same defect, two languages — write for the dev who
> will fix it.

## Layer

- [ ] Frontend (UI) — user-perspective wording
- [ ] Backend / API — request/response wording
- [ ] Unclear (state the evidence for each side)

## Severity / Priority

Walk the tree top-down, first match wins — and record which branch fired:

1. Data loss/corruption, security breach (auth bypass, IDOR, PII leak), money charged
   wrongly, or app unusable for all users? → **S1 (blocker)**
2. Core feature broken for a significant user group with NO workaround, or a paid
   feature not delivering what was paid for? → **S2 (major)**
3. Feature broken but a workaround exists, or non-core feature broken, or noticeable
   quality degradation at scale? → **S3 (minor)**
4. Cosmetic, minor UX friction, rare edge case with an easy workaround? → **S4 (cosmetic)**

- **Severity:** S1 / S2 / S3 / S4 — **branch fired:** #
- **Priority:** P0 / P1 / P2 / P3 — a business decision made by the owner. QA (or an AI
  agent) may propose one, explicitly marked as a proposal. Severity is objective;
  priority is not. The two never merge.

## Environment

| Field | Value |
|---|---|
| URL | https://staging.example.com/... |
| Environment | dev / staging / prod |
| Build / commit | `<git sha>` or release tag |
| Browser | Chrome 124.0.6367.91 |
| OS | macOS 14.4 / Windows 11 / Ubuntu 22.04 |
| Viewport / device | Desktop 1440×900 / iPhone 15 Safari (390×844) |
| User role | guest / authenticated / admin |
| Feature flags | flag-name=on |

## Steps to reproduce

1.
2.
3.

## Actual result

What actually happens — short prose, evidence link appended after ` // `.

## Expected result

What should happen, derived from the quoted source (AC / rule / contract) and
phrased as the rule, not as this single case. Quote the source in Related.

## Frequency

- [ ] Always
- [ ] Intermittent — **measured rate mandatory** (e.g. "3/10 attempts"), never "sometimes"
- [ ] One-time

> Could not reproduce after a stated number of attempts → record it as an observation in
> the exploratory session log or the module's `<module>-traceability.md` run notes, not as a bug.

## Evidence

- Screenshot: ![screenshot](path/to/screenshot.png)
- Video / GIF: [link]
- Console errors:
```
<paste relevant console output>
```
- Network failures (status codes, request/response):
```
<paste relevant network log>
```
- Playwright trace (if from automation): `automation/web/playwright/test-results/...`

## Workaround

If any.

## Related

- Story / acceptance criterion: `<story id> / AC-<n>` (docs/srs/…), quoted verbatim
- Requirement / business rule: [docs/requirements/... or docs/business-rules/...]
- Known gap (if this defect was predicted): `<question id>` in `../<module>-questions.md`
- Test case: `TC-<CODE>-NNN` in `../<module>-test-cases.md`; checklist item `CHK-<CODE>-NNN` in `../<module>-checklist.md`
- Invariant violated: INV-N ([qa/shared/oracles/invariants.md](../shared/oracles/invariants.md)) — if none fits, that is a missing invariant: add it
- Linear / Jira: PROJ-123

## Status

`Open` / `Known issue (accepted)` / `Fixed — awaiting verification` / `Closed`. State who decided
and when.

> **A known, accepted defect must not block the suite.** Mark its test `test.fail()` with the bug
> id in the reason: the check still runs and still proves the defect, the run stays green, and
> Playwright reports an *unexpected pass* the day the app is fixed — the signal to remove the
> marker and close this file. Never edit the expectation itself (doctrine rules 1 and 4);
> `trace_results.py` keeps counting the tagged checklist items as **Failed**, so coverage stays
> honest.

> **When this bug is verified fixed:** re-verify with the ORIGINAL repro steps on the
> fixed build, then (1) add/confirm the invariant it violated in
> [invariants.md](../shared/oracles/invariants.md), and (2) create a regression test case /
> spec that traces back to this BUG ID. A fixed bug with no regression check will return.
