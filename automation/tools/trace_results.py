#!/usr/bin/env python3
"""Close the traceability loop: checklist [CHK-…] IDs <- automated run results.

This is layer 4 of the automation chain described in ``automation/README.md``::

    checklist [CHK-…]  ->  test cases  ->  screen map  ->  test code tagged with CHK IDs
                                                                |
    qa/{web,mobile}/<NN-module>/<module>-traceability.md  <-  trace_results.py  <-  run results

Test code carries the CHK IDs it proves in a machine-readable place
(Playwright ``tag: ['@CHK-AUTH-001']`` and/or the title; pytest
``@pytest.mark.chk("CHK-AUTH-001")`` + ``@allure.tag("CHK-AUTH-001")``).
This script reads the runner output, extracts the IDs with the canonical regex
``CHK-[A-Z]{2,5}-\\d{3,}`` (automation/README.md → IDs and tags; the same pattern
is enforced at collection time by automation/{api,mobile}/conftest.py) from titles,
tags and labels, and writes ONE markdown report with the automated verdict per
checklist item.

READ-ONLY by design
-------------------
* Reads checklist ``.md`` files and runner output (Playwright JSON reporter
  ``results.json``; pytest-allure ``*-result.json`` files). Never edits them.
* Writes exactly one markdown file (``--out``), or prints the table (``--dry-run``).
* NEVER touches Google Sheets. The only Sheets writer in this repo is
  ``sync_checklist_to_sheets.py``; automated verdicts stay in the report and are
  copied into the Sheet by a human, if at all.

Verdict rules (QA Doctrine, CLAUDE.md)
--------------------------------------
Per CHK ID, over ALL test results tagged with it:

* ``Passed``  — every tagged result passed (an objective assertion decided it).
* ``Failed``  — at least one tagged result failed / timed out / broke. Computed
  from the raw result statuses, so a Playwright ``test.fail()`` that fails as
  expected and a retry that eventually passed (flaky) both stay ``Failed``.
* ``Blocked`` — none failed but at least one was skipped, or did not execute.
  A skip is Blocked, never a pass.
* (empty)     — no tagged test exists: not run / needs a human. Never green.

``Not run`` in the summary is derived by subtraction
(``total - Passed - Failed - Blocked``), never by counting cells. A results
source that yields zero tests is reported loudly and makes the exit code
non-zero: an empty run is not a passing run. A results file that cannot be
parsed blocks the WHOLE run: a corrupt result could be the one failure, so no
verdict is produced at all (the report says why) and the exit code is non-zero.

Run context (the limits of every verdict)
-----------------------------------------
A Passed verdict is only as wide as the configuration that produced it. The
report therefore carries a "Run context" block: target, product build, harness
commit, browsers / platform / env label, run label. What the runner output does
not contain is passed on the command line (``--target``, ``--build``,
``--run-label``); anything still unknown is printed as *not recorded*, never
guessed. Anything not listed there (other browsers, devices, environments,
quarantined tests) carries no verdict from this run.

Usage
-----
    uv run python trace_results.py --platform web \\
        --checklist ../../qa/web/01-authentication/authentication-checklist.md \\
        --playwright-json ../web/playwright/test-results/results.json \\
        --out ../../qa/web/01-authentication/authentication-traceability.md

    uv run python trace_results.py --platform mobile \\
        --checklist ../../qa/mobile/01-authentication/authentication-checklist.md \\
        --allure-dir ../mobile/allure-results --dry-run

    uv run python trace_results.py --platform api \\
        --checklist ../../qa/shared/checklists/checklist-owasp-top10.md \\
        --allure-dir ../api/allure-results --out ../../qa/shared/checklists/owasp-top10-traceability.md

Exit codes: 0 = report produced; 1 = Blocked run — a results source contained
zero tests (report still produced, verdicts are all not-run / Blocked) or could
not be parsed (a Blocked report with no verdicts is written instead);
2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent  # automation/tools -> repo root

# Canonical CHK ID (automation/README.md → IDs and tags): 2–5 uppercase letters of
# feature code, then at least three digits. The SAME pattern is enforced at collection
# time by automation/api/conftest.py and automation/mobile/conftest.py and by
# sync_checklist_to_sheets.py — one contract, so an id that a runner accepts is never
# invisible here. As it appears in tags, titles and labels: "@CHK-AUTH-001",
# "CHK-AUTH-001 Check that…", "CHK-AUTH-1000" (4+ digits stay valid).
CHK_ID_PATTERN = r"CHK-[A-Z]{2,5}-\d{3,}"
CHK_ID_RE = re.compile(rf"\b{CHK_ID_PATTERN}\b")

# Checklist item line. Mirrors sync_checklist_to_sheets._NUM_LINE_RE
# ("1. [CHK-AUTH-001] text"; duplicated here so this script does not import
# gspread) and additionally accepts the "- [ ] [CHK-SEC-001] text" bullet form
# used by shared checklists (qa/shared/checklists/).
CHK_LINE_RE = re.compile(
    rf"^(?:\d+\.|[-*]\s*\[[ xX]\]|[-*])\s*\[({CHK_ID_PATTERN})\]\s*(.*)$"
)

NOT_RECORDED = "*not recorded*"

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

CHECK_TEXT_WIDTH = 80

PLAYWRIGHT_FAILED = {"failed", "timedOut", "interrupted"}
ALLURE_STATUS = {
    "passed": "passed",
    "failed": "failed",
    "broken": "failed",
    "skipped": "skipped",
    "unknown": "skipped",  # no verdict recorded -> Blocked, never green
}

VERDICT_PASSED = "Passed"
VERDICT_FAILED = "Failed"
VERDICT_BLOCKED = "Blocked"
VERDICT_NOT_RUN = ""


def log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}", file=sys.stderr)


class ResultsError(Exception):
    """A results source cannot be trusted (unparseable file). The whole run is
    Blocked: a corrupt result could be the one failure, so no verdict is produced."""


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CheckItem:
    chk_id: str
    text: str
    section: str
    source: Path


@dataclass(frozen=True)
class TestResult:
    test_id: str  # "auth.spec.ts:12 [chromium]" | "tests.smoke.test_login#test_ok"
    source: str  # "playwright" | "allure"
    status: str  # "passed" | "failed" | "skipped"
    detail: str = ""  # first line of the error / skip reason
    chk_ids: tuple[str, ...] = ()


@dataclass
class TraceRow:
    item: CheckItem
    results: list[TestResult] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return verdict_for(self.results)


@dataclass
class RunContext:
    """The limits of every verdict in the report: what configuration produced it."""

    target: str = ""  # base URL / host the product was exercised on
    build: str = ""  # product build / commit / version under test
    run_label: str = ""  # what was run: filter, tag, suite ("smoke, chromium")
    harness_commit: str = ""  # commit of THIS repo (the harness), auto-detected
    projects: tuple[str, ...] = ()  # Playwright project names seen in results
    env_labels: tuple[str, ...] = ()  # allure `env` labels seen in results
    base_urls: tuple[str, ...] = ()  # allure `base_url` labels seen in results


@dataclass
class Summary:
    total: int
    automated: int
    passed: int
    failed: int
    blocked: int

    @property
    def not_run(self) -> int:
        # Derived by subtraction, never by counting cells (CLAUDE.md, status vocabulary).
        return self.total - (self.passed + self.failed + self.blocked)

    def line(self) -> str:
        return (
            f"Summary: total={self.total} automated={self.automated} "
            f"Passed={self.passed} Failed={self.failed} Blocked={self.blocked} "
            f"Not run={self.not_run}"
        )


def verdict_for(results: list[TestResult]) -> str:
    if not results:
        return VERDICT_NOT_RUN
    statuses = {r.status for r in results}
    if "failed" in statuses:
        return VERDICT_FAILED
    if "skipped" in statuses:
        return VERDICT_BLOCKED
    return VERDICT_PASSED


# --------------------------------------------------------------------------- #
# Checklist parsing
# --------------------------------------------------------------------------- #


def parse_checklist(path: Path) -> list[CheckItem]:
    items: list[CheckItem] = []
    section = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        m = CHK_LINE_RE.match(line)
        if not m:
            continue
        text = m.group(2).strip()
        items.append(
            CheckItem(chk_id=m.group(1), text=text, section=section, source=path)
        )
    return items


def parse_checklists(paths: list[Path]) -> list[CheckItem]:
    items: list[CheckItem] = []
    seen: dict[str, Path] = {}
    for p in paths:
        found = parse_checklist(p)
        if not found:
            log("WARN", f"No [CHK-…] items found in {p}")
        for it in found:
            if it.chk_id in seen:
                log(
                    "WARN",
                    f"Duplicate {it.chk_id}: {seen[it.chk_id]} and {p}; keeping first.",
                )
                continue
            seen[it.chk_id] = p
            items.append(it)
    return items


# --------------------------------------------------------------------------- #
# Result loaders
# --------------------------------------------------------------------------- #


def _first_line(text: str | None) -> str:
    if not text:
        return ""
    text = ANSI_RE.sub("", str(text))
    for ln in text.splitlines():
        ln = ln.strip()
        if ln:
            return ln
    return ""


def extract_chk_ids(*pools: str) -> tuple[str, ...]:
    found: set[str] = set()
    for pool in pools:
        found.update(CHK_ID_RE.findall(pool or ""))
    return tuple(sorted(found))


def _playwright_test_status(test: dict) -> tuple[str, str]:
    """(status, detail) for one Playwright test entry (one spec x one project)."""
    results = test.get("results") or []
    statuses = [r.get("status") for r in results]
    for r in results:
        if r.get("status") in PLAYWRIGHT_FAILED:
            err = r.get("error") or {}
            msg = err.get("message") or ""
            if not msg:
                errors = r.get("errors") or []
                msg = (errors[0].get("message") if errors else "") or ""
            return "failed", _first_line(msg) or r.get("status", "failed")
    if not results:
        return "skipped", "no results recorded (test did not execute)"
    if all(s == "skipped" for s in statuses):
        notes = [
            f"{a.get('type')}"
            + (f": {a.get('description')}" if a.get("description") else "")
            for a in (test.get("annotations") or [])
            if a.get("type") in {"skip", "fixme"}
        ]
        return "skipped", "; ".join(notes) or "skipped"
    if any(s == "passed" for s in statuses):
        return "passed", ""
    # Unrecognised statuses only -> no objective verdict -> Blocked.
    return "skipped", f"unrecognised result status(es): {', '.join(map(str, statuses))}"


def load_playwright_results(path: Path) -> list[TestResult]:
    """Playwright ``--reporter=json`` output. CHK IDs come from spec.tags (with or
    without the leading '@'), the spec title and every ancestor suite title —
    Playwright inherits describe-level tags exactly the same way."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResultsError(
            f"Unreadable Playwright results {path}: {exc}. A corrupt results file could "
            "hide a failure — the run is Blocked, no verdict is produced."
        ) from exc
    if not isinstance(data, dict):
        raise ResultsError(
            f"Playwright results {path} is not a JSON object — the run is Blocked, "
            "no verdict is produced."
        )
    out: list[TestResult] = []

    def walk(suite: dict, titles: list[str]) -> None:
        titles = titles + [str(suite.get("title") or "")]
        for spec in suite.get("specs") or []:
            tags = [str(t) for t in (spec.get("tags") or [])]
            ids = extract_chk_ids(*titles, str(spec.get("title") or ""), *tags)
            file = spec.get("file") or suite.get("file") or ""
            line = spec.get("line")
            base_id = (
                f"{file}:{line}"
                if file and line
                else (file or str(spec.get("title") or ""))
            )
            for test in spec.get("tests") or []:
                project = test.get("projectName") or ""
                test_id = f"{base_id} [{project}]" if project else base_id
                status, detail = _playwright_test_status(test)
                out.append(TestResult(test_id, "playwright", status, detail, ids))
        for child in suite.get("suites") or []:
            walk(child, titles)

    for suite in data.get("suites") or []:
        walk(suite, [])
    return out


def load_allure_results(directory: Path) -> list[TestResult]:
    """pytest + allure-pytest ``allure-results/*-result.json``. CHK IDs come from
    ``labels`` named ``tag`` (``@allure.tag`` and pytest markers such as
    ``@pytest.mark.chk("CHK-…")``, which allure-pytest also records as a tag),
    ``fullName`` and ``name``. Point this at a results dir from ONE clean run:
    every result file counts, so stale files from earlier runs would be mixed in."""
    out: list[TestResult] = []
    for f in sorted(directory.glob("*-result.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            # Never "skip and continue": the unreadable file may be the one failed test
            # tagged with a CHK id whose sibling passed — the row would turn Passed.
            raise ResultsError(
                f"Unreadable allure result {f}: {exc}. A corrupt result file could "
                "hide a failure — the run is Blocked, no verdict is produced."
            ) from exc
        if not isinstance(d, dict):
            raise ResultsError(
                f"Allure result {f} is not a JSON object — the run is Blocked, "
                "no verdict is produced."
            )
        name = str(d.get("name") or "")
        full_name = str(d.get("fullName") or "")
        tag_values = [
            str(lbl.get("value") or "")
            for lbl in (d.get("labels") or [])
            if lbl.get("name") == "tag"
        ]
        ids = extract_chk_ids(name, full_name, *tag_values)
        test_id = full_name or name or f.name
        if full_name and name and name not in full_name:
            test_id = f"{full_name} ({name})"  # parametrised: keep the param id
        raw_status = str(d.get("status") or "unknown")
        status = ALLURE_STATUS.get(raw_status, "skipped")
        detail = _first_line((d.get("statusDetails") or {}).get("message"))
        if status == "skipped" and not detail:
            detail = "skipped" if raw_status == "skipped" else f"status {raw_status!r}"
        if status == "passed":
            detail = ""
        out.append(TestResult(test_id, "allure", status, detail, ids))
    return out


def allure_run_labels(directory: Path) -> dict[str, set[str]]:
    """Distinct values of the run-level labels the pytest stacks attach to every
    result (``env``, ``base_url`` — see automation/api/conftest.py)."""
    found: dict[str, set[str]] = {"env": set(), "base_url": set()}
    for f in sorted(directory.glob("*-result.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue  # load_allure_results already raised for this file
        if not isinstance(d, dict):
            continue
        for lbl in d.get("labels") or []:
            name = lbl.get("name")
            if name in found and lbl.get("value"):
                found[name].add(str(lbl["value"]))
    return found


def harness_commit(repo_root: Path = REPO_ROOT) -> str:
    """Short commit of THIS repository (the harness, not the product). Empty when
    not a git checkout or git is unavailable — printed as not recorded, never guessed."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if out.returncode != 0:
        return ""
    commit = out.stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    if dirty.returncode == 0 and dirty.stdout.strip():
        commit += " (uncommitted changes)"
    return commit


def build_run_context(
    sources: list[tuple[str, Path, list[TestResult]]],
    target: str = "",
    build: str = "",
    run_label: str = "",
    commit: str | None = None,
) -> RunContext:
    projects: set[str] = set()
    envs: set[str] = set()
    base_urls: set[str] = set()
    for kind, p, results in sources:
        if kind == "playwright":
            for r in results:
                m = re.search(r"\[([^\[\]]+)\]$", r.test_id)
                if m:
                    projects.add(m.group(1))
        elif kind == "allure" and p.is_dir():
            labels = allure_run_labels(p)
            envs.update(labels["env"])
            base_urls.update(labels["base_url"])
    return RunContext(
        target=target.strip(),
        build=build.strip(),
        run_label=run_label.strip(),
        harness_commit=harness_commit() if commit is None else commit,
        projects=tuple(sorted(projects)),
        env_labels=tuple(sorted(envs)),
        base_urls=tuple(sorted(base_urls)),
    )


def render_run_context(ctx: RunContext) -> list[str]:
    def rec(value: str) -> str:
        return f"`{value}`" if value else NOT_RECORDED

    target = ctx.target or ", ".join(ctx.base_urls)
    lines = [
        "## Run context — the limits of every verdict below",
        "",
        f"- Target: {rec(target)}"
        + ("" if target else " — pass `--target <base url>`"),
        f"- Product build / version: {rec(ctx.build)}"
        + ("" if ctx.build else " — pass `--build <version or commit>`"),
        f"- Harness commit (this repo): {rec(ctx.harness_commit)}",
    ]
    if ctx.projects:
        lines.append(f"- Browser projects (Playwright): `{'`, `'.join(ctx.projects)}`")
    if ctx.env_labels:
        lines.append(f"- Environment label (pytest): `{'`, `'.join(ctx.env_labels)}`")
    lines.append(
        f"- Run label (suite / filter): {rec(ctx.run_label)}"
        + ("" if ctx.run_label else " — pass `--run-label \"smoke, chromium\"`")
    )
    lines.append(
        "- Not covered by this run: every browser, device, environment, role and quarantined "
        "test not listed above. A Passed here says nothing about them."
    )
    lines.append("")
    return lines


# --------------------------------------------------------------------------- #
# Tracing
# --------------------------------------------------------------------------- #


def build_rows(
    items: list[CheckItem], results: list[TestResult]
) -> tuple[list[TraceRow], dict[str, list[TestResult]]]:
    """Attach tagged results to checklist rows. Returns (rows, orphans) where
    orphans = CHK IDs referenced by tests but missing from every checklist."""
    by_id: dict[str, list[TestResult]] = {}
    for r in results:
        for cid in r.chk_ids:
            by_id.setdefault(cid, []).append(r)
    known = {it.chk_id for it in items}
    rows = [TraceRow(item=it, results=by_id.get(it.chk_id, [])) for it in items]
    orphans = {cid: rs for cid, rs in by_id.items() if cid not in known}
    return rows, orphans


def summarize(rows: list[TraceRow]) -> Summary:
    verdicts = [r.verdict for r in rows]
    return Summary(
        total=len(rows),
        automated=sum(1 for r in rows if r.results),
        passed=verdicts.count(VERDICT_PASSED),
        failed=verdicts.count(VERDICT_FAILED),
        blocked=verdicts.count(VERDICT_BLOCKED),
    )


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def _cell(text: str) -> str:
    return (
        ANSI_RE.sub("", text)
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("|", "\\|")
        .strip()
    )


def _truncate(text: str, width: int = CHECK_TEXT_WIDTH) -> str:
    text = text.strip()
    return text if len(text) <= width else text[: width - 1].rstrip() + "…"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _tests_cell(results: list[TestResult]) -> str:
    if not results:
        return "0"
    ids = "; ".join(f"`{_cell(r.test_id)}`" for r in results)
    return f"{len(results)} — {ids}"


def _evidence_cell(results: list[TestResult]) -> str:
    if not results:
        return "no tagged test — not run (manual / exploratory), never green"
    parts = []
    for r in results:
        piece = f"{r.source}: {r.status}"
        if r.detail:
            piece += f" — {_truncate(r.detail, 160)}"
        parts.append(_cell(piece))
    return "<br>".join(parts)


def _count_by_status(results: list[TestResult]) -> str:
    c = {"passed": 0, "failed": 0, "skipped": 0}
    for r in results:
        c[r.status] = c.get(r.status, 0) + 1
    return f"{len(results)} tests ({c['passed']} passed, {c['failed']} failed, {c['skipped']} skipped)"


def render_report(
    platform: str,
    checklists: list[Path],
    items: list[CheckItem],
    sources: list[tuple[str, Path, list[TestResult]]],
    rows: list[TraceRow],
    orphans: dict[str, list[TestResult]],
    summary: Summary,
    now: datetime | None = None,
    context: RunContext | None = None,
) -> str:
    now = now or datetime.now(UTC)
    lines: list[str] = []
    lines.append(f"# Automated traceability — {platform}")
    lines.append("")
    lines.append(
        f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')} by `automation/tools/trace_results.py` "
        "(read-only: nothing written to Sheets or checklists)."
    )
    lines.append("")
    lines.append(f"- Platform: **{platform}**")
    per_file: dict[Path, int] = {}
    for it in items:
        per_file[it.source] = per_file.get(it.source, 0) + 1
    for p in checklists:
        lines.append(f"- Checklist: `{_rel(p)}` — {per_file.get(p, 0)} items")
    for kind, p, results in sources:
        lines.append(f"- Results ({kind}): `{_rel(p)}` — {_count_by_status(results)}")
    empty = [p for _, p, results in sources if not results]
    if empty:
        lines.append("")
        lines.append(
            "> **BLOCKED — empty run.** Zero tests were found in: "
            + ", ".join(f"`{_rel(p)}`" for p in empty)
            + ". An empty run is not a passing run; nothing below is green because of it."
        )
    lines.append("")
    if context is not None:
        lines.extend(render_run_context(context))
    lines.append(
        "> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; "
        "**Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, "
        "never a pass); empty = no tagged test → not run, never green. Manual and exploratory "
        "verdicts live in the checklist Sheet, not here."
    )
    lines.append("")
    lines.append("| CHK ID | Check | Tests | Automated verdict | Evidence |")
    lines.append("|---|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row.item.chk_id} | {_cell(_truncate(row.item.text))} | "
            f"{_tests_cell(row.results)} | {row.verdict} | {_evidence_cell(row.results)} |"
        )
    lines.append("")
    lines.append(
        f"**Summary:** total {summary.total} · automated {summary.automated} · "
        f"Passed {summary.passed} · Failed {summary.failed} · Blocked {summary.blocked} · "
        f"Not run {summary.not_run} (= total − Passed − Failed − Blocked)"
    )
    if orphans:
        lines.append("")
        lines.append("## Tagged tests with no checklist item")
        lines.append("")
        lines.append(
            "These CHK IDs appear in test tags but in none of the checklists above — "
            "a stale tag, a typo, or a missing `--checklist`. They count for nothing until resolved."
        )
        lines.append("")
        lines.append("| CHK ID | Tests | Statuses |")
        lines.append("|---|---|---|")
        for cid in sorted(orphans):
            rs = orphans[cid]
            statuses = ", ".join(f"{r.status}" for r in rs)
            lines.append(f"| {cid} | {_tests_cell(rs)} | {_cell(statuses)} |")
    lines.append("")
    return "\n".join(lines)


def render_blocked_report(
    platform: str,
    checklists: list[Path],
    reason: str,
    now: datetime | None = None,
) -> str:
    """Report written when a results source cannot be parsed: no verdicts at all,
    so a stale earlier report cannot survive as a green one."""
    now = now or datetime.now(UTC)
    lines = [
        f"# Automated traceability — {platform}",
        "",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')} by `automation/tools/trace_results.py` "
        "(read-only: nothing written to Sheets or checklists).",
        "",
        f"- Platform: **{platform}**",
    ]
    for p in checklists:
        lines.append(f"- Checklist: `{_rel(p)}`")
    lines += [
        "",
        f"> **BLOCKED — results unreadable.** {reason}",
        ">",
        "> No verdict is produced for any item: a corrupt result file could be the one failed "
        "test, and a report built without it could show Passed. Re-run the suite from a clean "
        "results directory and trace again. Every checklist item counts as not run.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trace_results.py",
        description="Layer-4 traceability closure: checklist CHK IDs <- automated run results. "
        "Read-only; never writes to Google Sheets.",
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=("web", "mobile", "api"),
        help="Stack the results come from (header label; picks nothing else).",
    )
    parser.add_argument(
        "--checklist",
        action="append",
        required=True,
        metavar="MD",
        help="Checklist .md with [CHK-…] items. Repeatable.",
    )
    parser.add_argument(
        "--playwright-json",
        metavar="RESULTS_JSON",
        help="Playwright JSON reporter output (web).",
    )
    parser.add_argument(
        "--allure-dir",
        metavar="ALLURE_RESULTS",
        help="pytest allure-results directory with *-result.json (mobile / api).",
    )
    parser.add_argument(
        "--out",
        metavar="MD",
        help="Report path, e.g. qa/web/<NN-module>/<module>-traceability.md. "
        "Required unless --dry-run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the report to stdout only; write nothing.",
    )
    ctx = parser.add_argument_group(
        "run context",
        "The limits of every verdict. What the runner output does not contain is "
        "given here; anything omitted is printed as 'not recorded', never guessed.",
    )
    ctx.add_argument(
        "--target",
        default="",
        metavar="URL",
        help="Base URL / host the product was exercised on.",
    )
    ctx.add_argument(
        "--build",
        default="",
        metavar="VERSION",
        help="Product build, version or commit under test.",
    )
    ctx.add_argument(
        "--run-label",
        default="",
        metavar="TEXT",
        help='What was run, e.g. "smoke, chromium+firefox" or "-m smoke --platform=android".',
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.playwright_json and not args.allure_dir:
        parser.error(
            "give at least one results source: --playwright-json and/or --allure-dir"
        )
    if not args.out and not args.dry_run:
        parser.error("--out <md> is required unless --dry-run")

    checklists = [Path(p) for p in args.checklist]
    for p in checklists:
        if not p.is_file():
            parser.error(f"checklist not found: {p}")

    sources: list[tuple[str, Path, list[TestResult]]] = []
    try:
        if args.playwright_json:
            pw = Path(args.playwright_json)
            if not pw.is_file():
                parser.error(f"Playwright results not found: {pw}")
            sources.append(("playwright", pw, load_playwright_results(pw)))
        if args.allure_dir:
            ad = Path(args.allure_dir)
            if not ad.is_dir():
                parser.error(f"allure-results dir not found: {ad}")
            sources.append(("allure", ad, load_allure_results(ad)))
    except ResultsError as exc:
        log("ERROR", str(exc))
        blocked = render_blocked_report(args.platform, checklists, str(exc))
        if args.dry_run:
            print(blocked)
        else:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(blocked, encoding="utf-8")
            log("INFO", f"Wrote BLOCKED report {out} (no verdicts)")
        print("Summary: BLOCKED — results unreadable, no verdicts produced")
        return 1

    items = parse_checklists(checklists)
    results = [r for _, _, rs in sources for r in rs]
    rows, orphans = build_rows(items, results)
    summary = summarize(rows)

    empty_sources = [p for _, p, rs in sources if not rs]
    for p in empty_sources:
        log(
            "WARN",
            f"Zero tests found in {p} — empty run, treated as Blocked, never green.",
        )
    for cid in sorted(orphans):
        log("WARN", f"{cid} is tagged in tests but exists in no checklist given.")

    context = build_run_context(
        sources, target=args.target, build=args.build, run_label=args.run_label
    )
    report = render_report(
        args.platform, checklists, items, sources, rows, orphans, summary, context=context
    )

    if args.dry_run:
        print(report)
    else:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        log("INFO", f"Wrote {out}")

    print(summary.line())
    return 1 if empty_sources else 0


if __name__ == "__main__":
    sys.exit(main())
