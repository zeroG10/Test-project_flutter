#!/usr/bin/env python3
"""Summary page for the lead — one local HTML page over ONE clean mobile run.

Third reporting level (owner decision 2026-09-23), next to the Allure report (per module,
for engineers) and the traceability matrix (``trace_results.py``, per CHK id):

* top half for a PM — how much of the checklist this run verified, what failed, what could
  not run and why, run time against a manual estimate;
* bottom half for engineers — per-module and per-test tables, run context, key screens.

Verdicts per CHK id come from ``trace_results.py`` itself (same loader, same rules:
Passed only if every tagged result passed, Blocked if any was skipped, empty if no tagged
test exists), so the page and the traceability matrix can never disagree.

The page shows screenshots of the client's app: it is written locally only
(``automation/mobile/reports/`` is gitignored). Publishing it anywhere is an owner call.

    cd automation/tools
    uv run python build_summary.py \\
        --allure-dir ../mobile/allure-results \\
        --checklist ../../qa/mobile/02-authentication/authentication-checklist.md \\
        --run-label "pytest --platform=ios, Authentication" \\
        [--manual-minutes-per-check 3] [--out-dir ../mobile/reports/summary]
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import trace_results as tr

DEFAULT_OUT = tr.REPO_ROOT / "automation" / "mobile" / "reports" / "summary"
MARKER = ".generated-by-build_summary"  # only a folder carrying it is ever cleaned
CHECKPOINT_PREFIX = "· "  # checkpoint attachments are named "NN · name" (helpers/evidence.py)
STATUS = {"passed": "Passed", "failed": "Failed", "skipped": "Blocked"}


@dataclass
class TestRun:
    title: str
    status: str  # Passed | Failed | Blocked — trace_results mapping of the allure status
    detail: str
    module: str
    tc: str
    duration_s: float
    start_ms: int
    stop_ms: int
    checkpoints: list[tuple[str, Path]] = field(default_factory=list)
    failure_shots: list[Path] = field(default_factory=list)
    videos: list[Path] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Reading
# --------------------------------------------------------------------------- #


def _attachments(node: dict) -> list[dict]:
    """Attachments of a result and of all its (nested) steps, in order."""
    found = list(node.get("attachments") or [])
    for step in node.get("steps") or []:
        found.extend(_attachments(step))
    return found


def _fixture_attachments(allure_dir: Path) -> dict[str, list[dict]]:
    """Attachments made in fixtures (setup / teardown), by test uuid.

    allure-pytest files them under ``*-container.json`` (befores / afters), not under the
    test result — the per-test screen video is attached in a teardown (conftest.py).
    """
    by_test: dict[str, list[dict]] = {}
    for f in sorted(allure_dir.glob("*-container.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        parts = (d.get("befores") or []) + (d.get("afters") or [])
        found = [att for part in parts for att in _attachments(part)]
        for uuid in d.get("children") or []:
            by_test.setdefault(str(uuid), []).extend(found)
    return by_test


def load_test_runs(allure_dir: Path) -> list[TestRun]:
    runs: list[TestRun] = []
    from_fixtures = _fixture_attachments(allure_dir)
    for f in sorted(allure_dir.glob("*-result.json")):
        d = json.loads(f.read_text(encoding="utf-8"))  # tr.load_allure_results already vetted
        labels: dict[str, str] = {}
        for lbl in d.get("labels") or []:
            labels.setdefault(str(lbl.get("name")), str(lbl.get("value") or ""))
        raw = str(d.get("status") or "unknown")
        start, stop = int(d.get("start") or 0), int(d.get("stop") or 0)
        run = TestRun(
            title=str(d.get("name") or f.name),
            status=STATUS[tr.ALLURE_STATUS.get(raw, "skipped")],
            detail=tr._first_line((d.get("statusDetails") or {}).get("message")),
            module=labels.get("suite") or "Unmapped",
            tc=labels.get("feature", ""),
            duration_s=max(stop - start, 0) / 1000,
            start_ms=start,
            stop_ms=stop,
        )
        for att in _attachments(d) + from_fixtures.get(str(d.get("uuid")), []):
            source = allure_dir / str(att.get("source") or "")
            name = str(att.get("name") or "")
            if not source.is_file():
                continue
            if CHECKPOINT_PREFIX in name and name[:2].isdigit():
                run.checkpoints.append((name, source))
            elif name.startswith("screenshot-"):
                run.failure_shots.append(source)
            elif name.startswith("video"):
                run.videos.append(source)
        runs.append(run)
    runs.sort(key=lambda r: r.start_ms)
    return runs


def read_environment(allure_dir: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    props = allure_dir / "environment.properties"
    if props.exists():
        for line in props.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep:
                env[key.replace(".", " ")] = value
    return env


def module_of_checklist(path: Path) -> str:
    """``qa/mobile/02-authentication/…`` -> ``02 · Authentication``."""
    number, _, slug = path.parent.name.partition("-")
    if number.isdigit() and slug:
        return f"{number} · {slug.replace('-', ' ').capitalize()}"
    return path.stem


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

CSS = """
:root{--bg:#f7f7f5;--surface:#fff;--text:#1d1d1b;--muted:#5f5e5a;--line:#e3e2dc;
--pass:#1f7a4d;--pass-bg:#e3f3ea;--fail:#b3261e;--fail-bg:#fbe7e5;--block:#8a5a00;
--block-bg:#fdf1d8;--none:#5f5e5a;--none-bg:#eeede8;--accent:#2b59c3}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161615;
--surface:#1f1f1d;--text:#ecebe6;--muted:#a3a29b;--line:#34332f;--pass:#6fd19c;
--pass-bg:#173526;--fail:#ff9b91;--fail-bg:#3d1c19;--block:#f3c262;--block-bg:#3a2d10;
--none:#a3a29b;--none-bg:#2a2a27;--accent:#8fb0ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1100px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:40px 0 12px}
h3{font-size:15px;margin:20px 0 8px}.muted{color:var(--muted)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px}
.tile b{display:block;font-size:26px;line-height:1.2;font-variant-numeric:tabular-nums}
.box{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:4px 16px}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:13px;color:var(--muted);font-weight:600}tr:last-child td{border-bottom:0}
.wrap{overflow-x:auto}.pill{display:inline-block;padding:1px 8px;border-radius:999px;
font-size:13px;font-weight:600;white-space:nowrap}
.Passed{color:var(--pass);background:var(--pass-bg)}.Failed{color:var(--fail);background:var(--fail-bg)}
.Blocked{color:var(--block);background:var(--block-bg)}.NotRun{color:var(--none);background:var(--none-bg)}
.gallery{display:flex;flex-wrap:wrap;gap:12px}.gallery figure{margin:0;width:180px}
.gallery img{width:100%;border:1px solid var(--line);border-radius:8px}
figcaption{font-size:12px;color:var(--muted)}video{max-width:320px;border-radius:8px}
dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px;margin:12px 0}dt{color:var(--muted)}
dd{margin:0}code{font-size:13px}
"""


def _e(text: object) -> str:
    return html.escape(str(text))


def _pill(status: str) -> str:
    label = status or "Not run"
    return f'<span class="pill {label.replace(" ", "")}">{_e(label)}</span>'


def _count(n: int, noun: str) -> str:
    return "" if n == 0 else f"{n} {noun}{'' if n == 1 else 's'}"


def _minutes(seconds: float) -> str:
    return f"{seconds / 60:.1f} min" if seconds >= 60 else f"{seconds:.0f} s"


class AssetCopier:
    """Copies the attachments the page shows next to it; names stay unique and stable."""

    def __init__(self, out_dir: Path):
        self.dir = out_dir / "assets"
        if self.dir.exists() and (self.dir / MARKER).exists():
            shutil.rmtree(self.dir)  # our own previous output only
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / MARKER).write_text("generated by automation/tools/build_summary.py\n")

    def __call__(self, source: Path) -> str:
        shutil.copy2(source, self.dir / source.name)
        return f"assets/{source.name}"


def render(
    runs: list[TestRun],
    rows: list[tr.TraceRow],
    summary: tr.Summary,
    env: dict[str, str],
    run_label: str,
    manual_minutes: float | None,
    copy: AssetCopier,
    now: datetime,
) -> str:
    counts = {s: sum(1 for r in runs if r.status == s) for s in ("Passed", "Failed", "Blocked")}
    wall = (max(r.stop_ms for r in runs) - min(r.start_ms for r in runs)) / 1000 if runs else 0
    verified = summary.passed + summary.failed  # an objective verdict either way
    out: list[str] = []
    w = out.append
    w("<!doctype html><html lang='en'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w(f"<title>Regression Run Summary</title><style>{CSS}</style></head><body><main>")
    w("<h1>Regression run summary</h1>")
    w(
        f"<p class='muted'>{_e(env.get('App', 'App not recorded'))} · build "
        f"{_e(env.get('Build', 'not recorded'))} · {_e(env.get('Platform', ''))} "
        f"{_e(env.get('Device', ''))} · generated {now:%Y-%m-%d %H:%M} UTC</p>"
    )

    # --- for the PM ---------------------------------------------------------------------
    w("<h2>In short</h2><div class='tiles'>")
    w(
        f"<div class='tile'><b>{summary.passed} / {summary.total}</b>checklist items "
        f"verified as working in this run</div>"
    )
    w(
        f"<div class='tile'><b>{len(runs)}</b>automated tests: {counts['Passed']} passed, "
        f"{counts['Failed']} failed, {counts['Blocked']} blocked</div>"
    )
    w(f"<div class='tile'><b>{_minutes(wall)}</b>automated run time, one device</div>")
    if manual_minutes is not None:
        manual_h = verified * manual_minutes / 60
        w(
            f"<div class='tile'><b>≈ {manual_h:.1f} h</b>the same {verified} checks by hand "
            f"({manual_minutes:g} min per check, owner's estimate)</div>"
        )
    else:
        w(
            "<div class='tile'><b>—</b>manual-time comparison not recorded "
            "(pass <code>--manual-minutes-per-check</code>)</div>"
        )
    w("</div>")
    failed = [r for r in runs if r.status == "Failed"]
    blocked = [r for r in runs if r.status == "Blocked"]
    w("<h3>What needs attention</h3><div class='box'><ul>")
    if not failed and not blocked:
        w("<li>Nothing failed and nothing was blocked in this run.</li>")
    for r in failed:
        w(f"<li>{_pill('Failed')} {_e(r.title)} — <span class='muted'>{_e(r.detail)}</span></li>")
    for r in blocked:
        w(f"<li>{_pill('Blocked')} {_e(r.title)} — <span class='muted'>{_e(r.detail)}</span></li>")
    w("</ul></div>")
    w(
        "<p class='muted'>A failed test is checked against its expectation first; only then "
        "is it a product defect. Blocked means the test could not run (environment, build, "
        "test data) — it is never counted as passed. Checklist items without an automated "
        "test stay <em>not run</em>.</p>"
    )

    # --- for engineers ------------------------------------------------------------------
    w("<h2>Coverage by module</h2><div class='box wrap'><table><tr><th>Module</th>")
    w("<th>Checklist items</th><th>Automated</th><th>Passed</th><th>Failed</th>")
    w("<th>Blocked</th><th>Not run</th></tr>")
    by_module: dict[str, list[tr.TraceRow]] = {}
    for row in rows:
        by_module.setdefault(module_of_checklist(row.item.source), []).append(row)
    for module, module_rows in sorted(by_module.items()):
        s = tr.summarize(module_rows)
        w(
            f"<tr><td>{_e(module)}</td><td>{s.total}</td><td>{s.automated}</td>"
            f"<td>{s.passed}</td><td>{s.failed}</td><td>{s.blocked}</td><td>{s.not_run}</td></tr>"
        )
    w("</table></div>")

    w("<h2>Tests</h2><div class='box wrap'><table><tr><th>Test</th><th>Module</th>")
    w("<th>Result</th><th>Time</th><th>Evidence</th></tr>")
    for r in runs:
        parts = [
            _count(len(r.checkpoints), "key screen"),
            _count(len(r.failure_shots), "failure screenshot"),
            _count(len(r.videos), "video"),
        ]
        evidence = ", ".join(part for part in parts if part) or "—"
        detail = f"<br><span class='muted'>{_e(r.detail)}</span>" if r.detail else ""
        w(
            f"<tr><td>{_e(r.title)}{detail}</td><td>{_e(r.module)}</td><td>{_pill(r.status)}</td>"
            f"<td>{_minutes(r.duration_s)}</td><td>{_e(evidence)}</td></tr>"
        )
    w("</table></div>")

    shown = [r for r in runs if r.checkpoints or r.failure_shots or r.videos]
    if shown:
        w("<h2>Key screens</h2>")
    for r in shown:
        w(f"<h3>{_e(r.title)} {_pill(r.status)}</h3><div class='gallery'>")
        pictures = r.checkpoints + [("on failure", shot) for shot in r.failure_shots]
        for name, source in pictures:
            w(
                f"<figure><img loading='lazy' src='{_e(copy(source))}' alt='{_e(name)}'>"
                f"<figcaption>{_e(name)}</figcaption></figure>"
            )
        for video in r.videos:
            w(f"<video controls preload='none' src='{_e(copy(video))}'></video>")
        w("</div>")

    w("<h2>Run context</h2><div class='box'><dl>")
    for key, value in env.items():
        w(f"<dt>{_e(key)}</dt><dd>{_e(value)}</dd>")
    w(f"<dt>Run label</dt><dd>{_e(run_label or tr.NOT_RECORDED.strip('*'))}</dd></dl></div>")
    w(
        "<p class='muted'>Every verdict is limited to this configuration. Per-item verdicts: "
        "the traceability matrix (<code>trace_results.py</code>); step-by-step detail: the "
        "Allure report (<code>allure serve automation/mobile/allure-results</code>).</p>"
    )
    w("</main></body></html>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--allure-dir", type=Path, required=True, help="allure-results of ONE run")
    p.add_argument(
        "--checklist", type=Path, action="append", required=True, help="repeat per module"
    )
    p.add_argument("--run-label", default="", help="what was run (filter, suite)")
    p.add_argument(
        "--manual-minutes-per-check",
        type=float,
        default=None,
        help="owner's estimate for the manual comparison; omitted = not shown",
    )
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.allure_dir.is_dir():
        tr.log("ERROR", f"Blocked: no allure results at {args.allure_dir}")
        return 2
    try:
        results = tr.load_allure_results(args.allure_dir)  # raises on an unreadable file
    except tr.ResultsError as exc:
        tr.log("ERROR", str(exc))
        return 2
    if not results:
        tr.log("ERROR", "Blocked: the results directory holds no test results — an empty run")
        return 2
    items = tr.parse_checklists(args.checklist)
    rows, _orphans = tr.build_rows(items, results)
    summary = tr.summarize(rows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    page = render(
        runs=load_test_runs(args.allure_dir),
        rows=rows,
        summary=summary,
        env=read_environment(args.allure_dir),
        run_label=args.run_label,
        manual_minutes=args.manual_minutes_per_check,
        copy=AssetCopier(args.out_dir),
        now=datetime.now(UTC),
    )
    out = args.out_dir / "index.html"
    out.write_text(page, encoding="utf-8")
    tr.log("INFO", f"{summary.line()} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
