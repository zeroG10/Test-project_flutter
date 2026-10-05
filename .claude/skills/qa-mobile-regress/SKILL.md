---
name: qa-mobile-regress
description: MOBILE (iOS / Android app, native or Flutter) — run the whole mobile regression on iOS, Android or both side by side, compare every test with the last final run and say exactly what changed. Use when the user says "регрес iOS", "регрес Android", "мобільний регрес на обох", "full regression on android", "нічний прогін апки". Web regression is /qa-run.
---

# QA regress — the whole regression, compared with the last final run

> **Scope.** The mobile stack only (`automation/mobile/`), for any app kind — native or Flutter: the platform is the
> OS (`ios` / `android`), `APP_KIND` lives in `.env`. The web stack has its own skills (`/qa-run`, `/qa-report`);
> platform-neutral ones (`/qa-bug`, `/qa-handoff`, where the template provides them) serve both.

Wrapper around [scripts/qa.sh](../../../automation/mobile/scripts/qa.sh) `… all` and
[mobile_compare_runs.py](../../../automation/tools/mobile_compare_runs.py). The baseline is the run the final
reports describe (`setup/project.yaml → report.mobile.slices.<platform>.run`). Answer in the owner's
language. Invoking this skill is the owner's go for this regression only.

## Step 1 — Scope and time

- **Platform**: `ios` | `android` | `both` (side by side). Not said → ask.
- Tell the owner the time before starting: iOS ≈ 1.5 h, Android ≈ 2 h 45 min, both side by side
  ≈ the longer one. The Mac must stay on the charger with the lid open.
- `cd automation/mobile && scripts/qa.sh <platform> all --dry-run` — show the plan.

## Step 2 — Preflight (all must hold)

- A committed tree (`git status --short` shows no tracked change). Dirty → stop and say so; a
  regression is never run with `ALLOW_DIRTY=1` — it could not be a report's basis.
- No other run going on these platforms (`results/.run.<platform>.lock`).
- For `both`: the dry run says "side by side". If parallel was never proven on this project
  (PARALLEL-RUNS.md §4/§6 status), say that this run is also its proof.

## Step 3 — Run

```bash
cd automation/mobile && EVIDENCE_VIDEO=auto scripts/qa.sh <platform> all --name regress-<N>
```

`EVIDENCE_VIDEO=auto`: a regression may become a report's basis, so failed and end-to-end tests
keep their video. Run in the background; report progress only when asked or when it ends.
The owner may ask for several runs in a row (repeatability): run them one after another, names
`regress-<N>a`, `…b`, `…c`, and compare each.

## Step 4 — Compare with the baseline (per platform)

```bash
cd automation/tools && uv run python mobile_compare_runs.py --platform <platform> \
  ../mobile/results/<platform>/<date>-regress-<N>
```

Exit 0 → the run repeats the baseline: say so with the numbers. Exit 1 → list NEW RED,
NEW BLOCKED, still-red-without-a-defect and MISSING tests, each with its reason line.

## Step 5 — Tell the owner, then stop

1. Numbers per platform: tests passed / failed / blocked, and how that differs from the baseline.
2. What needs triage (`/qa-mobile-triage`), what looks fixed ("fixed?" — a defect to re-check and close).
3. Ask: make this run the basis of the reports (`/qa-mobile-report`)? Shut the devices down?

## Rules

- **No re-runs until green.** One exception, announced: after a `both` run, a module whose
  verdict differs from the baseline may be run ONCE alone on that platform (`/qa-mobile-run`) to tell
  load from a real failure — both results are reported, neither is dropped.
- Blocked is never green; an empty or interrupted run is `Blocked`, not a result.
- This skill changes nothing in the repository: no traceability, no reports, no bugs, no commit.
