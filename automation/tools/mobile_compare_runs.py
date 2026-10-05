#!/usr/bin/env python3
"""A run against a baseline, test by test: what changed, and whether a red test is a known one.

    uv run python mobile_compare_runs.py --platform android ../mobile/results/android/<run>
    uv run python mobile_compare_runs.py --baseline <dir> <run>          # any two runs

The baseline is, by default, the run the final reports describe (`setup/project.yaml →
report.mobile.slices.<platform>.run`). Read-only. Verdict words as everywhere: Passed / Failed / Blocked. Each
red test of the new run gets one label, which is where triage starts — it is not a verdict on the app:

  known        a filed defect (or a draft the owner decided not to file) names this test: expected red
  NEW RED      it passed in the baseline, or is new, and no defect names it
  still red    red in the baseline too, no defect names it — still owed a triage
  NEW BLOCKED  it could not run now and did run in the baseline — owed, never green
  fixed?       it was red and is green now — a held defect may be fixed: confirm, then close the bug

Exit code: 0 — nothing new is red or blocked and no test went missing; 1 — there is something to triage.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mobile_brand as brand
import mobile_summary as bs


def load(directory: Path) -> dict[str, bs.TestRun]:
    if not directory.is_dir():
        raise SystemExit(f"Blocked: no run at {directory}")
    runs = bs.load_test_runs(directory)
    if not runs:
        raise SystemExit(f"Blocked: {directory} holds no test results — an empty run")
    return {r.key: r for r in runs}


def compare(baseline: dict[str, bs.TestRun], new: dict[str, bs.TestRun], bugs: list[bs.Bug]) -> dict[str, list]:
    out: dict[str, list] = {k: [] for k in ("known", "new_red", "still_red", "fixed", "missing", "added", "blocked")}
    for key, run in new.items():
        before = baseline.get(key)
        if before is None:
            out["added"].append(run)
        if run.status == "Passed":
            if before is not None and before.status == "Failed":
                out["fixed"].append((run, bs.bug_for(before, bugs)))
            continue
        if run.status == "Blocked":
            out["blocked"].append((run, before.status if before else "—"))
            continue
        bug = bs.bug_for(run, bugs)
        if bug:
            out["known"].append((run, bug))
        elif before is not None and before.status == "Failed":
            out["still_red"].append(run)
        else:
            out["new_red"].append((run, before.status if before else "new test"))
    out["missing"] = [run for key, run in baseline.items() if key not in new]
    return out


def name(run: bs.TestRun) -> str:
    return run.title if run.title.startswith("TC-") else f"{run.tc} {run.title}".strip()


def report(result: dict[str, list], baseline: Path, new: Path, n_base: int, n_new: int, partial: bool) -> str:
    lines = [f"baseline: {bs.rel_to_repo(baseline)} — {n_base} tests", f"run:      {bs.rel_to_repo(new)} — {n_new} tests"]
    lines.append("")
    if result["new_red"]:
        lines.append(f"NEW RED · {len(result['new_red'])} — triage these first (app, test or environment):")
        lines += [f"  {name(r)}  [was: {was}]\n      {r.detail[:200]}" for r, was in result["new_red"]]
    if result["still_red"]:
        lines.append(f"still red, no defect names it · {len(result['still_red'])}:")
        lines += [f"  {name(r)}" for r in result["still_red"]]
    new_blocked = [(r, was) for r, was in result["blocked"] if was != "Blocked"]
    old_blocked = [(r, was) for r, was in result["blocked"] if was == "Blocked"]
    if new_blocked:
        lines.append(f"NEW BLOCKED · {len(new_blocked)} — could not run now, did before; owed, never green:")
        lines += [f"  {name(r)}  [was: {was}]\n      {bs._reason(r.detail)[:200]}" for r, was in new_blocked]
    if old_blocked:
        lines.append(f"blocked as in the baseline · {len(old_blocked)}:")
        lines += [f"  {name(r)}\n      {bs._reason(r.detail)[:200]}" for r, _ in old_blocked]
    if result["fixed"]:
        lines.append(f"fixed? · {len(result['fixed'])} — was red, green now:")
        lines += [f"  {name(r)}" + (f"  [{b.bug_id} may be fixed — confirm]" if b else "") for r, b in result["fixed"]]
    if result["known"]:
        lines.append(f"known red · {len(result['known'])} — expected until the defect is fixed:")
        lines += [f"  {name(r)}  [{b.bug_id}{'' if b.filed else ', not filed — owner'}]" for r, b in result["known"]]
    if result["added"]:
        lines.append(f"not in the baseline · {len(result['added'])}: " + ", ".join(r.tc or r.title[:30] for r in result["added"]))
    if result["missing"] and not partial:
        lines.append(f"MISSING · {len(result['missing'])} — in the baseline, did not run now:")
        lines += [f"  {name(r)}" for r in result["missing"]]
    elif result["missing"]:
        lines.append(f"not part of this run: {len(result['missing'])} tests of the baseline (a partial run)")
    if not needs_triage(result, partial):
        lines.append("Nothing new is red or blocked" + ("" if partial else " and no test went missing") + ".")
    return "\n".join(lines)


def needs_triage(result: dict[str, list], partial: bool) -> bool:
    new_blocked = any(was != "Blocked" for _, was in result["blocked"])
    return bool(result["new_red"] or result["still_red"] or new_blocked or (result["missing"] and not partial))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=Path, help="allure results of the run to judge")
    parser.add_argument("--platform", choices=bs.PLATFORMS, help="baseline = the platform's final run")
    parser.add_argument("--baseline", type=Path, help="allure results to compare with")
    parser.add_argument("--partial", action="store_true", help="the run is a module, not the regression: tests it did not include are not 'missing'")
    args = parser.parse_args(argv)
    baseline = args.baseline or (brand.slice_(args.platform).run if args.platform else None)
    if baseline is None:
        parser.error("give --platform (baseline = its final run) or --baseline")
    base, new = load(baseline), load(args.run)
    result = compare(base, new, bs.load_bugs())
    print(report(result, baseline, args.run, len(base), len(new), args.partial))
    return 1 if needs_triage(result, args.partial) else 0


if __name__ == "__main__":
    sys.exit(main())
