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
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import trace_results as tr

PAGE_TITLE = "Field Services Regression"
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
    func: str = ""  # test function name (fullName after "#") — links a test to its bug file
    message: str = ""  # full status message (the detail is its first line)
    steps: list[dict] = field(default_factory=list)
    fixtures: list[tuple[str, dict]] = field(default_factory=list)  # ("setup"|"teardown", part)
    attachments: list[dict] = field(default_factory=list)  # attached to the test body itself
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


def _fixture_parts(allure_dir: Path) -> dict[str, list[tuple[str, dict]]]:
    """Fixture setup / teardown parts by test uuid (allure-pytest ``*-container.json``).

    Preconditions (app reset, UI login, test data) and cleanup live here, not in the test
    result — as does the per-test screen video, attached in a teardown (conftest.py).
    """
    by_test: dict[str, list[tuple[str, dict]]] = {}
    for f in sorted(allure_dir.glob("*-container.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        parts = [("setup", b) for b in d.get("befores") or []]
        parts += [("teardown", a) for a in d.get("afters") or []]
        for uuid in d.get("children") or []:
            by_test.setdefault(str(uuid), []).extend(parts)
    return by_test


def load_test_runs(allure_dir: Path) -> list[TestRun]:
    runs: list[TestRun] = []
    from_fixtures = _fixture_parts(allure_dir)
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
            func=str(d.get("fullName") or "").partition("#")[2],
            message=str((d.get("statusDetails") or {}).get("message") or ""),
            steps=list(d.get("steps") or []),
            fixtures=from_fixtures.get(str(d.get("uuid")), []),
            attachments=list(d.get("attachments") or []),
        )
        fixture_atts = [a for _, part in run.fixtures for a in _attachments(part)]
        for att in _attachments(d) + fixture_atts:
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


class Redactor:
    """Hides the test account's identifiers on a page that leaves this machine.

    Text: every known form of APP_USER_EMAIL / APP_USER_PHONE (from automation/mobile/.env,
    never printed) becomes ``‹test account›``. Images: boxes listed in a redactions file
    (attachment source → [[x0, y0, x1, y1] in points]) are pixelated on the page's copy;
    the original results stay untouched.
    """

    MASK = "‹test account›"

    def __init__(self, env_file: Path | None, boxes_file: Path | None):
        self.values: list[str] = []
        if env_file and env_file.exists():
            from dotenv import dotenv_values

            env = dotenv_values(env_file)
            email = (env.get("APP_USER_EMAIL") or "").strip()
            phone = (env.get("APP_USER_PHONE") or "").strip()
            digits = re.sub(r"\D", "", phone)[-10:]
            forms = [email, email.lower(), phone]
            if len(digits) == 10:
                forms += [f"+1{digits}", f"({digits[:3]}) {digits[3:6]}-{digits[6:]}", digits]
            self.values = sorted({v for v in forms if v}, key=len, reverse=True)
        self.boxes: dict[str, list[list[float]]] = {}
        self.points_width = 402.0
        if boxes_file and boxes_file.exists():
            data = json.loads(boxes_file.read_text(encoding="utf-8"))
            self.points_width = float(data.get("points_width", 402))
            self.boxes = data.get("boxes", {})

    def text(self, value: object) -> str:
        out = str(value)
        for secret in self.values:
            out = out.replace(secret, self.MASK)
        return out

    def image(self, path: Path) -> None:
        boxes = self.boxes.get(path.name)
        if not boxes:
            return
        from PIL import Image

        img = Image.open(path).convert("RGB")
        scale = img.width / self.points_width
        for x0, y0, x1, y1 in boxes:
            box = tuple(round(v * scale) for v in (x0, y0, x1, y1))
            region = img.crop(box)
            small = region.resize((max(1, region.width // 28), max(1, region.height // 28)))
            img.paste(small.resize(region.size, Image.NEAREST), box)
        img.save(path)


@dataclass(frozen=True)
class Bug:
    bug_id: str
    title: str
    severity: str
    path: Path


def load_bugs(pattern_root: Path = tr.REPO_ROOT / "qa" / "mobile") -> list[Bug]:
    """``qa/mobile/<NN-module>/bugs/BUG-*.md`` — id, title and severity, as filed."""
    bugs: list[Bug] = []
    for f in sorted(pattern_root.glob("*/bugs/BUG-*.md")):
        text = f.read_text(encoding="utf-8")
        first = text.splitlines()[0] if text else ""
        title = first.split("—", 1)[1].strip() if "—" in first else f.stem
        m = re.search(r"\*\*Severity:\*\*\s*(S\d)", text)
        bugs.append(Bug(f.stem, title, m.group(1) if m else "", f))
    return bugs


def bug_for(run: TestRun, bugs: list[Bug]) -> Bug | None:
    """The bug whose report names this test function (the regression check it cites)."""
    if not run.func:
        return None
    # "::test_name" not followed by "[": a bug citing ONE parametrised row never claims them all
    cited = re.compile(rf"::{re.escape(run.func)}(?!\[)\b")
    return next((b for b in bugs if cited.search(b.path.read_text(encoding="utf-8"))), None)


def module_of_checklist(path: Path) -> str:
    """``qa/mobile/02-authentication/…`` -> ``02 · Authentication``."""
    number, _, slug = path.parent.name.partition("-")
    if number.isdigit() and slug:
        return f"{number} · {slug.replace('-', ' ').capitalize()}"
    return path.stem


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

# Palette: cool neutrals with the product's own maroon as the only accent; semantic status
# colours are separate. Light tokens on :root; dark under the system query AND the explicit
# data-theme stamp (artifact viewers have three theme states).
_DARK = (
    "--bg:#121417;--surface:#1b1e23;--text:#e8eaed;--muted:#9aa1ac;--line:#2c3037;"
    "--accent:#e0868c;--pass:#6fd19c;--pass-bg:#16342a;--fail:#ff9b91;--fail-bg:#3b1d1b;"
    "--block:#f0c060;--block-bg:#372c12;--none:#9aa1ac;--none-bg:#262a30;color-scheme:dark"
)
FONTS = (
    "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
    "&family=IBM+Plex+Sans:wght@400;500;600&display=swap'>"
)
CSS = (
    """
:root{--bg:#f6f7f9;--surface:#fff;--text:#16191f;--muted:#5b6270;--line:#e2e5ea;
--accent:#7a2b30;--pass:#1d7048;--pass-bg:#e2f2e9;--fail:#b3261e;--fail-bg:#fbe7e5;
--block:#835400;--block-bg:#fbefd6;--none:#5b6270;--none-bg:#eceef2;
--sans:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
--mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){"""
    + _DARK
    + """}}
:root[data-theme="dark"]{"""
    + _DARK
    + """}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 var(--sans)}
main{max-width:1100px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:28px;font-weight:600;margin:0 0 6px;text-wrap:balance}
h2{font-size:18px;font-weight:600;margin:44px 0 12px;padding-top:12px;
border-top:2px solid var(--accent);text-wrap:balance}
h3{font-size:15px;font-weight:600;margin:22px 0 8px;text-wrap:balance}
.muted{color:var(--muted)}.id{font-family:var(--mono);font-size:13px}
.eyebrow{font:500 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
.tile b{display:block;font:600 28px/1.2 var(--mono);font-variant-numeric:tabular-nums;margin-bottom:4px}
.box{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:4px 16px}
.box ul{margin:12px 0;padding-left:18px}.box li{margin:6px 0}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--muted);font-weight:600;letter-spacing:.03em;text-transform:uppercase}
tr:last-child td{border-bottom:0}
.wrap{overflow-x:auto}.pill{display:inline-block;padding:1px 8px;border-radius:999px;
font-size:12px;font-weight:600;white-space:nowrap}
.Passed{color:var(--pass);background:var(--pass-bg)}.Failed{color:var(--fail);background:var(--fail-bg)}
.Blocked{color:var(--block);background:var(--block-bg)}.NotRun{color:var(--none);background:var(--none-bg)}
.bug{font-family:var(--mono);font-size:13px;color:var(--fail)}
.gallery{display:flex;flex-wrap:wrap;gap:12px}.gallery figure{margin:0;width:170px;max-width:100%}
.gallery img{width:100%;border:1px solid var(--line);border-radius:6px}
figcaption{font:12px/1.4 var(--mono);color:var(--muted);margin-top:4px}
video{max-width:100%;width:300px;border-radius:6px;border:1px solid var(--line)}
dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px;margin:12px 0}
dt{color:var(--muted)}dd{margin:0;overflow-wrap:anywhere}code{font:13px var(--mono)}
details.test{background:var(--surface);border:1px solid var(--line);border-radius:8px;margin:8px 0}
details.test>summary{cursor:pointer;padding:10px 14px;list-style-position:inside}
details.test>summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.tbody{padding:0 14px 12px;border-top:1px solid var(--line)}
.dur{font:12px var(--mono);color:var(--muted);margin-left:8px}
.phase{font:500 11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:14px 0 4px}
ol.steps{list-style:none;margin:0;padding-left:16px;border-left:1px solid var(--line)}
ol.steps>li{margin:3px 0;font-size:14px}.mark{display:inline-block;width:18px;font-weight:600}
.st-passed>.mark{color:var(--pass)}.st-failed>.mark,.st-broken>.mark{color:var(--fail)}
.st-skipped>.mark{color:var(--block)}.sname{overflow-wrap:anywhere}
.atts{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 6px 18px}
figure.att{margin:0;width:150px;max-width:100%}figure.att img,figure.att video{width:100%;
border:1px solid var(--line);border-radius:6px}
details.att-text{width:100%}details.att-text>summary{cursor:pointer;font:12px var(--mono);color:var(--muted)}
pre{font:12px/1.5 var(--mono);background:var(--bg);border:1px solid var(--line);border-radius:6px;
padding:8px 10px;overflow:auto;max-height:280px;white-space:pre-wrap;overflow-wrap:anywhere}
pre.err{color:var(--fail);margin:12px 0}
@media (max-width:520px){dl{grid-template-columns:1fr}dd{margin-bottom:6px}}
"""
)


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

    def __init__(
        self, out_dir: Path, redactor: Redactor | None = None, source_root: Path = Path(".")
    ):
        self.redactor = redactor
        self.source_root = source_root
        self.dir = out_dir / "assets"
        if self.dir.exists() and (self.dir / MARKER).exists():
            shutil.rmtree(self.dir)  # our own previous output only
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / MARKER).write_text("generated by automation/tools/build_summary.py\n")

    def __call__(self, source: Path) -> str:
        target = self.dir / source.name
        if not target.exists():
            shutil.copy2(source, target)
            if self.redactor:
                self.redactor.image(target)
        return f"assets/{source.name}"


MARK = {"passed": "✓", "failed": "✗", "broken": "✗", "skipped": "–"}
TEXT_LIMIT = 3000


def _duration(node: dict) -> str:
    start, stop = node.get("start"), node.get("stop")
    if not start or not stop:
        return ""
    return _minutes(max(int(stop) - int(start), 0) / 1000)


def attachments_html(node: dict, t, copy: AssetCopier, root: Path) -> str:
    out: list[str] = []
    for att in node.get("attachments") or []:
        source = root / str(att.get("source") or "")
        name = str(att.get("name") or "")
        if not source.is_file():
            continue
        suffix = source.suffix.lower()
        if suffix in (".png", ".jpg", ".jpeg"):
            out.append(
                f"<figure class='att'><img loading='lazy' src='{t(copy(source))}' alt='{t(name)}'>"
                f"<figcaption>{t(name)}</figcaption></figure>"
            )
        elif suffix == ".mp4":
            out.append(
                f"<figure class='att'><video controls preload='none' src='{t(copy(source))}'>"
                f"</video><figcaption>{t(name)}</figcaption></figure>"
            )
        else:
            text = source.read_text(encoding="utf-8", errors="replace")
            cut = " …(truncated)" if len(text) > TEXT_LIMIT else ""
            out.append(
                f"<details class='att-text'><summary>{t(name)}</summary>"
                f"<pre>{t(text[:TEXT_LIMIT])}{cut}</pre></details>"
            )
    return f"<div class='atts'>{''.join(out)}</div>" if out else ""


def steps_html(steps: list[dict], t, copy: AssetCopier, root: Path) -> str:
    if not steps:
        return ""
    items = []
    for st in steps:
        status = str(st.get("status") or "unknown")
        items.append(
            f"<li class='st-{t(status)}'><span class='mark'>{MARK.get(status, '·')}</span>"
            f"<span class='sname'>{t(st.get('name') or '')}</span>"
            f"<span class='dur'>{t(_duration(st))}</span>"
            f"{attachments_html(st, t, copy, root)}{steps_html(st.get('steps') or [], t, copy, root)}</li>"
        )
    return f"<ol class='steps'>{''.join(items)}</ol>"


def details_html(r: TestRun, t, copy: AssetCopier) -> str:
    root = copy.source_root
    out = [f"<details class='test'><summary>{_pill(r.status)} {t(r.title)} "]
    out.append(f"<span class='dur'>{_minutes(r.duration_s)}</span></summary><div class='tbody'>")
    if r.message:
        cut = " …" if len(r.message) > 1200 else ""
        out.append(f"<pre class='err'>{t(r.message[:1200])}{cut}</pre>")
    for kind, part in r.fixtures:
        if kind == "setup" and (part.get("steps") or part.get("attachments")):
            name = str(part.get("name") or "").split("::")[0]
            out.append(f"<p class='phase'>setup · {t(name)}</p>")
            out.append(steps_html(part.get("steps") or [], t, copy, root))
            out.append(attachments_html(part, t, copy, root))
    out.append("<p class='phase'>test</p>")
    out.append(steps_html(r.steps, t, copy, root))
    out.append(attachments_html({"attachments": r.attachments}, t, copy, root))
    for kind, part in r.fixtures:
        if kind == "teardown" and (part.get("steps") or part.get("attachments")):
            name = str(part.get("name") or "").split("::")[0]
            out.append(f"<p class='phase'>teardown · {t(name)}</p>")
            out.append(steps_html(part.get("steps") or [], t, copy, root))
            out.append(attachments_html(part, t, copy, root))
    out.append("</div></details>")
    return "".join(out)


def render(
    runs: list[TestRun],
    rows: list[tr.TraceRow],
    summary: tr.Summary,
    env: dict[str, str],
    run_label: str,
    manual_minutes: float | None,
    copy: AssetCopier,
    now: datetime,
    bugs: list[Bug] | None = None,
    redactor: Redactor | None = None,
) -> tuple[str, str]:
    """(head, body): the head is <title> + fonts + <style>; the body is the page content.
    A full document wraps both; an artifact publish takes them as a fragment."""
    bugs = bugs or []
    red = redactor or Redactor(None, None)

    def t(value: object) -> str:
        return _e(red.text(value))

    counts = {s: sum(1 for r in runs if r.status == s) for s in ("Passed", "Failed", "Blocked")}
    wall = (max(r.stop_ms for r in runs) - min(r.start_ms for r in runs)) / 1000 if runs else 0
    verified = summary.passed + summary.failed  # an objective verdict either way
    out: list[str] = []
    w = out.append
    head = f"<title>{PAGE_TITLE}</title>{FONTS}<style>{CSS}</style>"
    w("<main><p class='eyebrow'>Automated regression · run summary</p>")
    w(f"<h1>{PAGE_TITLE}</h1>")
    w(
        f"<p class='muted'>{t(env.get('App', 'App not recorded'))} · build "
        f"{t(env.get('Build', 'not recorded'))} · {t(env.get('Platform', ''))} "
        f"{t(env.get('Device', ''))} · generated {now:%Y-%m-%d %H:%M} UTC</p>"
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
            "<div class='tile'><b>—</b>comparison with manual regression: waiting for the "
            "team's estimate of minutes per check</div>"
        )
    w("</div>")
    failed = [r for r in runs if r.status == "Failed"]
    blocked = [r for r in runs if r.status == "Blocked"]
    w("<h3>What needs attention</h3><div class='box'><ul>")
    if not failed and not blocked:
        w("<li>Nothing failed and nothing was blocked in this run.</li>")
    for r in failed:
        bug = bug_for(r, bugs)
        why = (
            f"<span class='bug'>{t(bug.bug_id)}</span> ({t(bug.severity)}) — {t(bug.title)}"
            if bug
            else f"<span class='muted'>{t(r.detail)}</span>"
        )
        w(f"<li>{_pill('Failed')} {t(r.title)} — {why}</li>")
    for r in blocked:
        w(f"<li>{_pill('Blocked')} {t(r.title)} — <span class='muted'>{t(r.detail)}</span></li>")
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
            f"<tr><td>{t(module)}</td><td>{s.total}</td><td>{s.automated}</td>"
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
        bug = bug_for(r, bugs) if r.status == "Failed" else None
        detail = f"<br><span class='muted'>{t(r.detail)}</span>" if r.detail else ""
        if bug:
            detail = f"<br><span class='bug'>{t(bug.bug_id)}</span> <span class='muted'>{t(bug.title)}</span>"
        w(
            f"<tr><td>{t(r.title)}{detail}</td><td>{t(r.module)}</td><td>{_pill(r.status)}</td>"
            f"<td>{_minutes(r.duration_s)}</td><td>{t(evidence)}</td></tr>"
        )
    w("</table></div>")

    shown = [r for r in runs if r.checkpoints or r.failure_shots or r.videos]
    if shown:
        w("<h2>Key screens</h2>")
    for r in shown:
        w(f"<h3>{t(r.title)} {_pill(r.status)}</h3><div class='gallery'>")
        pictures = r.checkpoints + [("on failure", shot) for shot in r.failure_shots]
        for name, source in pictures:
            w(
                f"<figure><img loading='lazy' src='{t(copy(source))}' alt='{t(name)}'>"
                f"<figcaption>{t(name)}</figcaption></figure>"
            )
        for video in r.videos:
            w(f"<video controls preload='none' src='{t(copy(video))}'></video>")
        w("</div>")

    w("<h2 id='details'>Test details</h2>")
    w(
        "<p class='muted'>Every step of every test, as the harness recorded it: <b>setup</b> = "
        "preconditions (app reset, sign-in, test data), then the test's own steps, then "
        "<b>teardown</b> = cleanup and evidence. ✓ passed · ✗ failed · – skipped.</p>"
    )
    by_mod: dict[str, list[TestRun]] = {}
    for r in runs:
        by_mod.setdefault(r.module, []).append(r)
    for module, module_runs in sorted(by_mod.items()):
        w(f"<h3>{t(module)}</h3>")
        for r in module_runs:
            w(details_html(r, t, copy))
    w("<h2>Run context</h2><div class='box'><dl>")
    for key, value in env.items():
        w(f"<dt>{t(key)}</dt><dd>{t(value)}</dd>")
    w(f"<dt>Run label</dt><dd>{t(run_label or tr.NOT_RECORDED.strip('*'))}</dd></dl></div>")
    w(
        "<p class='muted'>Every verdict is limited to this configuration. Per-item verdicts: "
        "the traceability matrix (<code>trace_results.py</code>); step-by-step detail: the "
        "Allure report (<code>allure serve automation/mobile/allure-results</code>).</p>"
    )
    w("</main>")
    return head, "\n".join(out)


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
    p.add_argument(
        "--redact-env",
        type=Path,
        default=tr.REPO_ROOT / "automation" / "mobile" / ".env",
        help="dotenv whose APP_USER_EMAIL / APP_USER_PHONE are hidden on the page (values never printed)",
    )
    p.add_argument(
        "--redact-boxes",
        type=Path,
        default=None,
        help="JSON {points_width, boxes: {attachment source: [[x0,y0,x1,y1], ...]}} pixelated on the page copies",
    )
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
    redactor = Redactor(args.redact_env, args.redact_boxes)
    head, body = render(
        runs=load_test_runs(args.allure_dir),
        rows=rows,
        summary=summary,
        env=read_environment(args.allure_dir),
        run_label=args.run_label,
        manual_minutes=args.manual_minutes_per_check,
        copy=AssetCopier(args.out_dir, redactor, args.allure_dir),
        now=datetime.now(UTC),
        bugs=load_bugs(),
        redactor=redactor,
    )
    out = args.out_dir / "index.html"
    out.write_text(
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"{head}</head><body>{body}</body></html>",
        encoding="utf-8",
    )
    # Artifact publish: the host wraps the skeleton itself — a fragment, head first.
    (args.out_dir / "page.html").write_text(f"{head}\n{body}\n", encoding="utf-8")
    tr.log("INFO", f"{summary.line()} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
