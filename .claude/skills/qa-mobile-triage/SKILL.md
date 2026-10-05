---
name: qa-mobile-triage
description: MOBILE — triage the red and blocked tests of a mobile run (iOS / Android): for each one decide with evidence whether it is the app (a bug), the test, the expectation or the environment, and prepare the fix, the bug draft or the question. Use when the user says "розбери що впало на android", "чому тест червоний на ios", "triage the mobile run", or after /qa-mobile-run or /qa-mobile-regress reported NEW RED / NEW BLOCKED.
---

# QA triage — why a test is red, with evidence

> **Scope.** The mobile stack only (`automation/mobile/`), for any app kind — native or Flutter: the platform is the
> OS (`ios` / `android`), `APP_KIND` lives in `.env`. The web stack has its own skills (`/qa-run`, `/qa-report`);
> platform-neutral ones (`/qa-bug`, `/qa-handoff`, where the template provides them) serve both.

Starts from [mobile_compare_runs.py](../../../automation/tools/mobile_compare_runs.py), ends with one decision
per test. Doctrine (CLAUDE.md): never fake a Pass, name the oracle, fix the harness — never the
expectation, escalate — don't decide. Answer in the owner's language, in plain words.

## Step 1 — The list

```bash
cd automation/tools && uv run python mobile_compare_runs.py --platform <platform> [--partial] \
  ../mobile/results/<platform>/<run>
```

Triage, in this order: **NEW RED**, **NEW BLOCKED**, "still red, no defect names it", **MISSING**,
then "fixed?". Known red (a defect names the test) needs nothing — it is expected.

## Step 2 — Evidence for each test (read, do not re-run)

From the run's Allure results (`*-result.json` of the test, its attachments): the failing step and
message, the failure screenshot (look at it), the screen video if kept, the API bodies attached.
Then the test's code and page objects, its test case (`qa/mobile/<NN-module>/…-test-cases.md`),
and the oracle that test case names (SRS / AC / Figma / invariant / owner's decision).
App logs hold a token: read them in the scratchpad only, never commit or quote them.

## Step 3 — Decide: one of five

| It is… | Signs | What follows |
|---|---|---|
| **the environment** | device / Appium / network / server error, a timing miss under load, the other platform's run going | `Blocked` with the reason; fix the cause or note it; the test is owed |
| **the test (harness)** | wrong locator, a wait too short, state left by another test, data collision | fix the harness — propose the change, make it on the owner's go |
| **a wrong expectation** | the oracle says otherwise than the test asserts | a test defect: correct the test case and the test to the oracle, cite it; no bug |
| **the app** | the app contradicts a named oracle, reproducibly | a bug **draft** per `prompts/08-file-bug.md` (three gates, severity walk, evidence) — through `/qa-bug` where the template provides it; filed only on the owner's word |
| **no oracle** | nobody wrote what should happen | a question in `<module>-questions.md`; the check stays not-run, never Passed |

Cannot tell the environment from the rest by reading? ONE diagnostic re-run of that single test,
alone on its platform, announced first (`/qa-mobile-run <platform> <node id>`): red twice → not the
environment; green → an environment / flakiness finding (say so; a flaky test is quarantined with
a bug id, never retried). Both results are reported. This is the only re-run allowed.

"fixed?" (was red under a defect, green now): confirm from the evidence that the defect's
behaviour is gone, then propose closing the bug to the owner — do not close it yourself.

## Step 4 — Report to the owner

One row per test: what happened (plain words) · the decision · the evidence (step, screenshot) ·
what you propose. Then the questions that only the owner can answer, as one block.

## Rules

- Never edit an expected value, a checklist status or a baseline to make a test green.
- Nothing is filed, fixed in the app's repo (read-only), committed or pushed without the owner's word.
- Personal data: redact the test accounts in anything committed.
