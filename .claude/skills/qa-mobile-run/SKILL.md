---
name: qa-mobile-run
description: MOBILE (iOS / Android app, native or Flutter) — run a module, several modules or one test on iOS, Android or both at the same time through automation/mobile/scripts/qa.sh, then say what passed, what is new red and what is a known defect. Use when the user names a mobile platform or the app: "прожени auth на android", "запусти модуль 08 на обох платформах", "run the notes tests on ios", "перевір цей тест на емуляторі". Web suites use /qa-run; the whole mobile regression is /qa-mobile-regress.
---

# QA run — a module or a test, on one platform or both

> **Scope.** The mobile stack only (`automation/mobile/`), for any app kind — native or Flutter: the platform is the
> OS (`ios` / `android`), `APP_KIND` lives in `.env`. The web stack has its own skills (`/qa-run`, `/qa-report`);
> platform-neutral ones (`/qa-bug`, `/qa-handoff`, where the template provides them) serve both.

A thin wrapper around [automation/mobile/scripts/qa.sh](../../../automation/mobile/scripts/qa.sh)
(devices and Appium started for you; rules of parallel runs:
[PARALLEL-RUNS.md](../../../automation/mobile/PARALLEL-RUNS.md)) and
[automation/tools/mobile_compare_runs.py](../../../automation/tools/mobile_compare_runs.py). Answer in the
owner's language, in plain words. Invoking this skill is the owner's go for THIS run only.

## Step 1 — What and where (never guess the platform)

- **Platform**: `ios` | `android` | `both`. Not said → ask; do not default.
- **What**: a module by number / name (`02`, `auth`, `order-list`), several (`08,09`), or one
  test (`tests/shared/test_x.py::test_name`). "Everything" → use `/qa-mobile-regress` instead.
- Show the plan first — it starts nothing:
  `cd automation/mobile && scripts/qa.sh <platform> <what> --dry-run`
  With `both` it must say "side by side"; if it refuses, tell the owner why and offer `--sequential`.

## Step 2 — Preflight (stop instead of working around)

- `git status --short` — tracked changes present → **stop**: `run.sh` wants a committed tree, and
  commits are made only on the owner's word. Offer: the owner says «коміть», or agrees to a
  throwaway debug run (`ALLOW_DIRTY=1`, never traced, never a report's basis).
- A run of the same platform already going (`results/.run.<platform>.lock`) → say so, do not kill it.

## Step 3 — Run

```bash
cd automation/mobile && scripts/qa.sh <platform> <what> [--name <name>]
```

Run it in the background and wait for it; with `both`, each platform's live log is
`results/.logs/<date>-<name>-<platform>.log`. Do not start anything else on the devices meanwhile.

## Step 4 — Read the result against the baseline

For each platform that ran (a module is a partial run):

```bash
cd automation/tools && uv run python mobile_compare_runs.py --platform <platform> --partial \
  ../mobile/results/<platform>/<date>-<name>
```

Report to the owner, per platform: passed / failed / blocked; then **NEW RED**, **NEW BLOCKED**,
"fixed?" and the known red with their defect ids. Zero tests ran → `Blocked`, never "passed".

## Rules

- **Never re-run a red test until it is green.** New red or new blocked → offer `/qa-mobile-triage`.
- After a `both` run, a verdict that differs from the baseline is an environment finding until
  proven otherwise (PARALLEL-RUNS.md rule 5).
- This skill does not touch traceability, reports, bugs or the checklist. Offer `/qa-mobile-report` only
  after a full regression.
- Devices and Appium stay up after the run; ask whether to shut them down
  (`adb -s <emulator> emu kill`, `xcrun simctl shutdown "<device>"`, stop the Appium processes).
