#!/usr/bin/env python3
"""Mobile regression report — a small static site over ONE clean mobile run.

Third reporting level, next to the Allure report (per test, for engineers) and the
traceability matrix (``trace_results.py``, per CHK id). The look is the shared brand of the web
reports (``brand.py``), so a project's web and mobile reports read alike:

* ``index.html`` — for a PM first: the verdict, the numbers, open defects, what could not
  run, why checks are not automated, stability and pace; technical detail below;
* ``<NN-module>.html`` — every check of a module with its verdict, the test that proved it
  and the phone screens it saw; every test with its steps;
* ``bugs/<BUG-ID>.html`` — each filed defect report, rendered from its markdown.

Verdicts per CHK id come from ``trace_results.py`` itself (same loader, same rules: Passed
only if every tagged result passed, Blocked if any was skipped, empty if no tagged test
exists), so the pages and the traceability matrix can never disagree. Reasons for checks
without a test come from ``qa/mobile/<platform>/not-automated.md``.

The pages show screenshots of the client's app: they are written locally only
(``automation/mobile/reports/`` is gitignored). Publishing is an owner call; ``--public``
builds the copy that may leave this machine.

    cd automation/tools
    uv run python mobile_summary.py \\
        --allure-dir ../mobile/results/ios/<run> \\
        --checklist ../../qa/mobile/02-authentication/authentication-checklist.md \\
        --run-label "pytest --platform=ios, Authentication" \\
        [--history-dir ../mobile/results/ios/<earlier full run> ...] [--note "…"] [--decision "…"] \\
        [--public --redact-boxes boxes.json --redact-text-env NAME] [--out-dir …]
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import mobile_brand as brand
import trace_results as tr

PLATFORMS = ("ios", "android")  # each platform's records live in its own subfolder
PLATFORM_NAME = {"ios": "iOS", "android": "Android"}
MOBILE_QA = tr.REPO_ROOT / "qa" / "mobile"
REPORTS = tr.REPO_ROOT / "automation" / "mobile" / "reports"  # gitignored: the full copy holds API bodies and videos


def default_out(platform: str) -> Path:
    return REPORTS / platform / "internal"


def build_info(platform: str) -> dict[str, str]:
    """`automation/mobile/builds/<platform>/BUILD_INFO.txt` as key → value (the build the runs used)."""
    path = tr.REPO_ROOT / "automation" / "mobile" / "builds" / platform / "BUILD_INFO.txt"
    info: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return info
    for line in lines:
        key, sep, value = line.partition(":")
        if sep and key.strip() and not line.startswith(" "):
            info[key.strip()] = value.strip()
    return info


def run_facts(env: dict[str, str], platform: str) -> dict[str, str]:
    """What a mobile report states about the run: OS, device (simulator / emulator / device), build and its
    type, the kind of app — read from the run's environment and the build's BUILD_INFO.txt."""
    info = build_info(platform)
    target = (info.get("target", "") + " " + info.get("type", "")).lower()
    kind = "simulator" if "simulator" in target else "emulator" if "emulator" in target else "device"
    build_type = "release" if "release" in target and "debug" not in target else "debug" if "debug" in target else ""
    device_cell = env.get("Device", "")
    parts = [x.strip() for x in device_cell.split("·")]
    device = re.sub(r"_API_\d+$", "", parts[0]).replace("_", " ") if parts and parts[0] else "not recorded"
    os_name = parts[1] if len(parts) > 1 else env.get("Platform", "not recorded")
    api = re.search(r"API_(\d+)", device_cell)
    if api:
        os_name += f" · API {api.group(1)}"
    app_kind = env.get("App kind", "")
    return {
        "os": os_name,
        "device": f"{device} — {kind}",
        "build": " · ".join(x for x in (env.get("Build", ""), f"{build_type} build" if build_type else "") if x)
        or "not recorded",
        "app_type": "Flutter"
        if "flutter" in app_kind.lower()
        else (app_kind.split(" ")[0].capitalize() or "not recorded"),
        "app": env.get("App", "not recorded"),
    }


def tool_versions(platform: str) -> str:
    """Appium and the platform's driver, as installed on the QA machine when the report is built."""
    driver = "xcuitest" if platform == "ios" else "uiautomator2"
    try:
        appium = subprocess.run(["appium", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
        listing = subprocess.run(
            ["appium", "driver", "list", "--installed"], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return "not recorded"
    found = re.search(rf"{driver}@([\d.]+)", re.sub(r"\x1b\[[0-9;]*m", "", listing.stdout + listing.stderr))
    name = "XCUITest" if platform == "ios" else "UiAutomator2"
    return f"Appium {appium or '?'} · {name} {found.group(1) if found else '?'}"


def default_reasons(platform: str) -> Path:
    return MOBILE_QA / platform / "not-automated.md"


def rel_to_repo(path: Path) -> str:
    """How the page names a repository file: repo-relative when it is inside the repository."""
    try:
        return path.resolve().relative_to(tr.REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


MOBILE_ROOT = tr.REPO_ROOT / "automation" / "mobile"
MARKER = ".generated-by-mobile_summary"  # only a folder carrying it is ever cleaned
CHECKPOINT_PREFIX = "· "  # checkpoint attachments are named "NN · name" (helpers/evidence.py)
STATUS = {"passed": "Passed", "failed": "Failed", "skipped": "Blocked"}
SHOTS_PER_CHECK = 6

# --public: the copy that leaves this machine. Text attachments (API response bodies, page
# sources) and screen videos are left out — they can carry other users' data and the test
# account's name, and a recording starts before sign-in.
PUBLIC = False


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
    uid: str = ""  # anchor on the module page
    func: str = ""  # test function name (fullName after "#") — links a test to its bug file
    package: str = ""  # "tests.shared.test_profile" — where the test lives
    chk_ids: tuple[str, ...] = ()
    key: str = ""  # the trace_results test id — same test across runs
    message: str = ""  # full status message (the detail is its first line)
    steps: list[dict] = field(default_factory=list)
    fixtures: list[tuple[str, dict]] = field(default_factory=list)  # ("setup"|"teardown", part)
    attachments: list[dict] = field(default_factory=list)  # attached to the test body itself
    checkpoints: list[tuple[str, Path]] = field(default_factory=list)
    failure_shots: list[Path] = field(default_factory=list)
    videos: list[Path] = field(default_factory=list)

    @property
    def screens(self) -> list[tuple[str, Path]]:
        return self.checkpoints + [("on failure", shot) for shot in self.failure_shots]


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
        tags: list[str] = []
        for lbl in d.get("labels") or []:
            labels.setdefault(str(lbl.get("name")), str(lbl.get("value") or ""))
            if lbl.get("name") == "tag":
                tags.append(str(lbl.get("value") or ""))
        name, full_name = str(d.get("name") or ""), str(d.get("fullName") or "")
        key = full_name or name or f.name  # the same test id trace_results builds
        if full_name and name and name not in full_name:
            key = f"{full_name} ({name})"
        raw = str(d.get("status") or "unknown")
        start, stop = int(d.get("start") or 0), int(d.get("stop") or 0)
        run = TestRun(
            title=name or f.name,
            status=STATUS[tr.ALLURE_STATUS.get(raw, "skipped")],
            detail=tr._first_line((d.get("statusDetails") or {}).get("message")),
            module=labels.get("suite") or "Unmapped",
            tc=labels.get("feature", ""),
            duration_s=max(stop - start, 0) / 1000,
            start_ms=start,
            stop_ms=stop,
            uid=str(d.get("uuid") or f.name.removesuffix("-result.json")),
            func=full_name.partition("#")[2],
            package=labels.get("package", ""),
            chk_ids=tr.extract_chk_ids(name, full_name, *tags),
            key=key,
            message=str((d.get("statusDetails") or {}).get("message") or ""),
            steps=list(d.get("steps") or []),
            fixtures=from_fixtures.get(str(d.get("uuid")), []),
            attachments=list(d.get("attachments") or []),
        )
        fixture_atts = [a for _, part in run.fixtures for a in _attachments(part)]
        for att in _attachments(d) + fixture_atts:
            source = allure_dir / str(att.get("source") or "")
            att_name = str(att.get("name") or "")
            if not source.is_file():
                continue
            if CHECKPOINT_PREFIX in att_name and att_name[:2].isdigit():
                run.checkpoints.append((att_name, source))
            elif att_name.startswith("screenshot-"):
                run.failure_shots.append(source)
            elif att_name.startswith("video"):
                run.videos.append(source)
        run.checkpoints.sort(key=lambda c: c[0])  # "01 · …", "02 · …" — the order they were taken
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


# The test accounts a run may sign in with: the shared one and one per platform (parallel runs —
# automation/mobile/PARALLEL-RUNS.md). A shared report hides all of them.
ACCOUNT_PREFIXES = ("APP_USER", "IOS_USER", "ANDROID_USER")


class Redactor:
    """Hides the test accounts' identifiers on a page that leaves this machine.

    Text: every known form of the accounts' emails and phones (APP_USER_* / IOS_USER_* /
    ANDROID_USER_* in automation/mobile/.env, never printed) becomes ``‹test account›``. Images: boxes listed in a redactions file
    (attachment source → [[x0, y0, x1, y1] in points]) are pixelated on the page's copy;
    the original results stay untouched.
    """

    MASK = "‹test account›"

    def __init__(self, env_file: Path | None, boxes_file: Path | None, extra: list[str] | None = None):
        self.values: list[str] = [v for v in (extra or []) if v]
        if env_file and env_file.exists():
            from dotenv import dotenv_values

            env = dotenv_values(env_file)
            for prefix in ACCOUNT_PREFIXES:  # the shared account and each platform's own
                email = (env.get(f"{prefix}_EMAIL") or "").strip()
                phone = (env.get(f"{prefix}_PHONE") or "").strip()
                digits = re.sub(r"\D", "", phone)[-10:]
                forms = [email, email.lower(), phone]
                if len(digits) == 10:
                    forms += [f"+1{digits}", f"({digits[:3]}) {digits[3:6]}-{digits[6:]}", digits]
                self.values += [v for v in forms if v]
        self.values = sorted(set(self.values), key=len, reverse=True)
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
    severity: str  # "S3"
    path: Path
    severity_label: str = ""  # "minor"
    priority: str = ""  # "P2"
    priority_proposed: bool = False  # QA's proposal, not yet the owner's / PM's decision
    regression_tc: str = ""  # the TC that stays red until the fix ("- Test case: `TC-…`")
    filed: bool = True  # a draft the owner decided not to file is not an open defect
    # ...but its red test is no surprise: the owner triaged it ("known, not filed")
    owner_not_filed: bool = False

    @property
    def module_dir(self) -> str:
        return self.path.parent.parent.name


def load_bugs(pattern_root: Path = tr.REPO_ROOT / "qa" / "mobile") -> list[Bug]:
    """``qa/mobile/<NN-module>/bugs/BUG-*.md`` — id, title, severity and priority, as filed."""
    bugs: list[Bug] = []
    for f in sorted(pattern_root.glob("*/bugs/BUG-*.md")):
        text = f.read_text(encoding="utf-8")
        first = text.splitlines()[0] if text else ""
        title = first.split("—", 1)[1].strip() if "—" in first else f.stem
        sev = re.search(r"\*\*Severity:\*\*\s*(S\d)(?:\s*\(([^)]*)\))?", text)
        pri = re.search(r"\*\*Priority:\*\*\s*(\*proposal\*\s*)?(P\d)", text)
        tc = re.search(r"^- Test cases?:\s*`(TC-[A-Z]+-\d+[a-z]?)`", text, re.MULTILINE)
        bugs.append(
            Bug(
                bug_id=f.stem,
                title=title,
                severity=sev.group(1) if sev else "",
                path=f,
                severity_label=(sev.group(2) or "").split("/")[0].strip() if sev else "",
                priority=pri.group(2) if pri else "",
                priority_proposed=bool(pri and pri.group(1)),
                regression_tc=tc.group(1) if tc else "",
                filed=not re.search(r"Status:\s*NOT FILED", text),
                owner_not_filed=bool(re.search(r"Status:\s*NOT FILED\s*—\s*owner's decision", text)),
            )
        )
    return bugs


def bug_for(run: TestRun, bugs: list[Bug]) -> Bug | None:
    """The filed bug whose report names this test as its regression check — by the test
    function, or by the test case on its "Test case:" line. Failing that, a draft the owner
    decided not to file that names it: the failure is known, not unexpected."""
    cited = re.compile(rf"::{re.escape(run.func)}(?!\[)\b") if run.func else None
    for wanted in (lambda b: b.filed, lambda b: not b.filed and b.owner_not_filed):
        for b in bugs:
            if not wanted(b):
                continue
            if run.tc and run.tc == b.regression_tc:
                return b
            # "::test_name" not followed by "[": a bug citing ONE parametrised row never claims them all
            if cited and cited.search(b.path.read_text(encoding="utf-8")):
                return b
    return None


def module_of_checklist(path: Path) -> str:
    """``qa/mobile/02-authentication/…`` -> ``02 · Authentication``."""
    number, _, slug = path.parent.name.partition("-")
    if number.isdigit() and slug:
        return f"{number} · {slug.replace('-', ' ').capitalize()}"
    return path.stem


# --- reasons for checks without an automated test ----------------------------------------


@dataclass(frozen=True)
class Kind:
    key: str
    title: str
    meaning: str


@dataclass(frozen=True)
class Reason:
    kind: str
    why: str
    source: str


_IDS = re.compile(r"CHK-([A-Z]{2,5})-(\d{3,})((?:\s*(?:,|…|\.\.\.)\s*-?\d{3,})*)")
_TAIL = re.compile(r"\s*(,|…|\.\.\.)\s*-?(\d{3,})")


def expand_ids(cell: str) -> list[str]:
    """``CHK-AUTH-081…-086, -090`` -> every id it names (a range includes both ends)."""
    ids: list[str] = []
    for m in _IDS.finditer(cell):
        code, first = m.group(1), m.group(2)
        nums = [int(first)]
        for sep, num in _TAIL.findall(m.group(3)):
            if sep == ",":
                nums.append(int(num))
            else:
                nums.extend(range(nums[-1] + 1, int(num) + 1))
        ids += [f"CHK-{code}-{n:0{len(first)}d}" for n in nums]
    return ids


def _md_tables(text: str) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                current.append(cells)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def load_reasons(path: Path) -> tuple[dict[str, Kind], dict[str, Reason]]:
    """``not-automated-ios.md``: a Kinds table and a Checks table (ids may be ranges)."""
    kinds: dict[str, Kind] = {}
    reasons: dict[str, Reason] = {}
    if not path.exists():
        return kinds, reasons
    for table in _md_tables(path.read_text(encoding="utf-8")):
        head, body = table[0], table[1:]
        if head[:1] == ["Kind"]:
            for key, title, meaning, *_ in body:
                kinds[key] = Kind(key, title, meaning)
        elif head[:1] == ["Checks"]:
            for ids, kind, why, source, *_ in body:
                for chk in expand_ids(ids):
                    reasons[chk] = Reason(kind, why, source)
    return kinds, reasons


# --- run history, stability and pace -------------------------------------------------------


@dataclass
class RunRecord:
    label: str
    finished: datetime
    minutes: float
    harness: str
    tests: int
    counts: dict[str, int]  # Passed / Failed / Blocked tests
    unexpected: int  # failed tests no filed bug (or owner-decided draft) names as its regression check
    checks: tr.Summary
    statuses: dict[str, str]  # test key -> status


def load_record(directory: Path, items: list[tr.CheckItem], bugs: list[Bug], label: str = "") -> RunRecord | None:
    try:
        results = tr.load_allure_results(directory)
    except tr.ResultsError as exc:
        tr.log("WARN", f"history: {exc}")
        return None
    runs = load_test_runs(directory)
    if not runs:
        return None
    rows, _ = tr.build_rows(items, results)
    counts = {s: sum(1 for r in runs if r.status == s) for s in ("Passed", "Failed", "Blocked")}
    env = read_environment(directory)
    return RunRecord(
        label=label or directory.name.removeprefix("allure-results-"),
        finished=datetime.fromtimestamp(max(r.stop_ms for r in runs) / 1000, UTC),
        minutes=(max(r.stop_ms for r in runs) - min(r.start_ms for r in runs)) / 60000,
        harness=env.get("Harness commit", ""),
        tests=len(runs),
        counts=counts,
        unexpected=sum(1 for r in runs if r.status == "Failed" and not bug_for(r, bugs)),
        checks=tr.summarize(rows),
        statuses={r.key: r.status for r in runs},
    )


def identical_streak(records: list[RunRecord]) -> int:
    """How many runs at the end of the history gave the same verdict for every test."""
    if not records:
        return 0
    last = records[-1].statuses
    streak = 0
    for rec in reversed(records):
        if rec.statuses != last:
            break
        streak += 1
    return streak


@dataclass
class PaceStep:
    when: datetime
    modules: list[str]
    checks: int


def _git_first_added(path: Path) -> datetime | None:
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", str(path)],
            cwd=tr.REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return None
    return datetime.fromisoformat(out[-1]) if out else None


def _git_first_commit() -> datetime | None:
    try:
        out = subprocess.run(
            ["git", "log", "--reverse", "--format=%aI"],
            cwd=tr.REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return None
    return datetime.fromisoformat(out[0]) if out else None


def load_pace(runs: list[TestRun], automated: dict[str, int]) -> list[PaceStep]:
    """Each module at the commit that first added its test file, with the checks it automates
    today. Commit times, not effort."""
    by_package: dict[str, str] = {}
    for r in runs:
        if r.package:
            by_package.setdefault(r.package, r.module)
    steps: dict[datetime, PaceStep] = {}
    for package, module in sorted(by_package.items()):
        path = MOBILE_ROOT / (package.replace(".", "/") + ".py")
        when = _git_first_added(path) if path.exists() else None
        if when is None:
            continue
        step = steps.setdefault(when, PaceStep(when, [], 0))
        step.modules.append(module)
        step.checks += automated.get(module, 0)
    return [steps[k] for k in sorted(steps)]


def source_of(run: TestRun) -> str:
    """``test_profile.py:330`` — where the test function is defined."""
    if not run.package or not run.func:
        return ""
    path = MOBILE_ROOT / (run.package.replace(".", "/") + ".py")
    func = run.func.split("[")[0]
    if not path.exists():
        return ""
    for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if re.match(rf"\s*(async\s+)?def {re.escape(func)}\(", line):
            return f"{path.name}:{no}"
    return path.name


# --------------------------------------------------------------------------- #
# Rendering — shared pieces
# --------------------------------------------------------------------------- #

# Palette, faces and logo are TRIARE's (brand.py — the same look as the web project's reports). "Held red" is
# amber (a known defect), "Failed" is red (nobody explained it yet), "Blocked" is violet (could not run) and never
# looks like a pass.
FONTS = brand.FONTS_LINK
CSS = (
    brand.TOKENS_CSS
    + """
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.55 var(--body);
-webkit-font-smoothing:antialiased}
.wrap{max-width:1040px;margin:0 auto;padding:28px 20px 64px}
a{color:var(--accent)}a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
h1,h2,h3{font-family:var(--display);font-weight:700;line-height:1.15;text-wrap:balance;margin:0}
h1{font-size:34px;letter-spacing:-.01em}h2{font-size:22px;margin-bottom:14px}h3{font-size:16px;margin-bottom:8px}
p{margin:0 0 10px;max-width:70ch}
.eyebrow{font:600 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
header{display:grid;gap:10px;padding-bottom:22px;border-bottom:1px solid var(--line)}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px 22px;margin:6px 0 0}
.facts div{display:grid;gap:2px}
.facts dt{font:600 11px/1.2 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.facts dd{margin:0;font:500 14px/1.35 var(--body);overflow-wrap:anywhere}
.layer{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 0}
.layer a{font:600 13px/1 var(--body);text-decoration:none;color:var(--ink);border:1px solid var(--line);
background:var(--surface);padding:8px 12px;border-radius:999px}.layer a:hover{border-color:var(--accent)}
.pill{display:inline-flex;align-items:center;gap:6px;font:700 12px/1 var(--mono);letter-spacing:.05em;
text-transform:uppercase;padding:6px 10px;border-radius:999px;vertical-align:middle;white-space:nowrap}
.pill::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
.pill.pass{background:var(--pass-soft);color:var(--pass)}.pill.known{background:var(--known-soft);color:var(--known)}
.pill.fail{background:var(--fail-soft);color:var(--fail)}.pill.block{background:var(--block-soft);color:var(--block)}
section{padding-top:34px}.lead{font-size:17px;max-width:72ch}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:18px 0 14px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:4px}
.kpi b{font:700 30px/1 var(--display);font-variant-numeric:tabular-nums;color:var(--figure)}.kpi span{color:var(--muted);font-size:13px}
.kpi.pass b{color:var(--pass)}.kpi.known b{color:var(--known)}.kpi.fail b{color:var(--fail)}.kpi.block b{color:var(--block)}
.bar{display:flex;height:14px;border-radius:7px;overflow:hidden;background:var(--idle)}
.bar i{display:block;height:100%}.bar .p{background:var(--pass)}.bar .k{background:var(--known)}
.bar .f{background:var(--fail)}.bar .b{background:var(--block)}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:10px;font-size:13px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{width:10px;height:10px;border-radius:2px;display:inline-block}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}
th{font:600 11px/1.2 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:10px;border-bottom:1px solid var(--line);vertical-align:top}
td.num,th.num{text-align:right}.mono{font-family:var(--mono);font-size:13px}
td.id,td.nowrap{white-space:nowrap}.mods td:first-child{font-weight:600;white-space:nowrap}
.mods .barcell{min-width:160px;width:34%}.mods .bar{height:10px;margin-top:5px}
.sev{font:700 12px/1 var(--mono);padding:4px 7px;border-radius:5px;white-space:nowrap}
.sev.S1,.sev.S2{background:var(--fail-soft);color:var(--fail)}.sev.S3{background:var(--known-soft);color:var(--known)}
.sev.S4{background:var(--accent-soft);color:var(--accent)}
.muted{color:var(--muted)}.note{font-size:13px;color:var(--muted);margin-top:10px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.box{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
.box ul{margin:6px 0 0;padding-left:18px}.box li{margin:4px 0}
code{font-family:var(--mono);font-size:12.5px;background:var(--accent-soft);padding:1px 5px;border-radius:4px;
overflow-wrap:anywhere}
details summary{cursor:pointer}
.divider{margin-top:40px;padding-top:26px;border-top:2px solid var(--ink)}
svg text{fill:var(--muted);font:11px var(--mono)}svg .lbl{fill:var(--ink);font:600 11px var(--body)}
svg .axis{stroke:var(--line)}svg .line{stroke:var(--accent);fill:none;stroke-width:2}
svg .dot{fill:var(--accent)}svg .num{fill:var(--surface);font:700 10px var(--mono)}
ol.pace{columns:2 260px;margin:10px 0 0;padding-left:22px;font-size:13px}ol.pace li{margin:2px 0}
.v{display:inline-block;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:600;white-space:nowrap}
.v.pass{color:var(--pass);background:var(--pass-soft)}.v.known{color:var(--known);background:var(--known-soft)}
.v.fail{color:var(--fail);background:var(--fail-soft)}.v.block{color:var(--block);background:var(--block-soft)}
.v.idle{color:var(--muted);background:var(--line)}
.why{color:var(--muted);font-size:12.5px;margin-top:3px;overflow-wrap:anywhere}
table.checks{table-layout:fixed;min-width:760px}
table.checks col.c1{width:128px}table.checks col.c3{width:170px}table.checks col.c4{width:150px}
table.checks col.c5{width:104px}.src{font:11.5px/1.35 var(--mono);color:var(--muted);overflow-wrap:anywhere}
.sect{margin:26px 0 6px;font:600 12px/1.2 var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:18px 0 12px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.card b{display:block;font:700 24px/1.1 var(--display);font-variant-numeric:tabular-nums;color:var(--figure)}
.card span{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.05em}
nav.top{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:22px}
nav.top a{font:600 13px/1 var(--body);text-decoration:none;color:var(--ink);border:1px solid var(--line);
background:var(--surface);padding:8px 12px;border-radius:999px}nav.top a:hover{border-color:var(--accent)}
.shots,.strip{display:flex;gap:12px}.shots{flex-wrap:wrap;margin-top:8px}
.strip{overflow-x:auto;padding:4px 2px 10px;scroll-snap-type:x mandatory}
.shots figure,.strip figure{margin:0;flex:0 0 auto;scroll-snap-align:start}
.shots figure{width:118px}.strip figure{width:150px}
a.shot{display:block;line-height:0}
a.shot img{width:100%;height:auto;border:1px solid var(--line);border-radius:14px;background:var(--surface)}
.shots figcaption,.strip figcaption{color:var(--muted);font:11.5px/1.35 var(--body);margin-top:5px;overflow-wrap:anywhere}
details.ev>summary{color:var(--accent);font-size:12.5px;white-space:nowrap}
details.test{background:var(--surface);border:1px solid var(--line);border-radius:10px;margin:8px 0}
details.test>summary{padding:10px 14px}
.tbody{padding:0 14px 12px;border-top:1px solid var(--line)}
.dur{font:12px var(--mono);color:var(--muted);margin-left:8px}
.phase{font:600 11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:14px 0 4px}
ol.steps{list-style:none;margin:0;padding-left:16px;border-left:1px solid var(--line)}
ol.steps>li{margin:3px 0;font-size:14px}.mark{display:inline-block;width:18px;font-weight:600}
.st-passed>.mark{color:var(--pass)}.st-failed>.mark,.st-broken>.mark{color:var(--fail)}
.st-skipped>.mark{color:var(--block)}.sname{overflow-wrap:anywhere}
.atts{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 6px 18px}.atts figure{margin:0;width:118px}
.att-omitted{font:12px var(--mono);color:var(--muted);margin:4px 0 4px 18px}
details.att-text{width:100%}details.att-text>summary{font:12px var(--mono);color:var(--muted)}
pre{font:12px/1.5 var(--mono);background:var(--ground);border:1px solid var(--line);border-radius:6px;
padding:8px 10px;overflow:auto;max-height:280px;white-space:pre-wrap;overflow-wrap:anywhere}
pre.err{color:var(--fail);margin:12px 0}
video{max-width:100%;width:260px;border-radius:14px;border:1px solid var(--line)}
.md h2{font-size:19px;margin:30px 0 10px;padding-top:14px;border-top:1px solid var(--line)}
.md h3{margin:20px 0 8px}.md table{margin:8px 0}.md th,.md td{border:1px solid var(--line);padding:6px 10px}
.md blockquote{margin:10px 0;padding:8px 14px;border-left:3px solid var(--known);background:var(--known-soft)}
.md li{max-width:72ch}.md p{max-width:72ch}
.md a.shot{display:inline-block;width:150px;margin:6px 8px 6px 0;vertical-align:top}
dialog.lb{border:0;padding:0;background:transparent;max-width:min(94vw,520px);color:#fff}
dialog.lb::backdrop{background:rgb(9 18 33/.82)}
dialog.lb img{display:block;max-width:100%;max-height:84vh;width:auto;margin:0 auto;border-radius:22px}
dialog.lb p{text-align:center;font-size:13px;margin:10px auto 0}
footer.note{margin-top:34px}
@media (max-width:560px){h1{font-size:27px}.kpi b{font-size:25px}.wrap{padding:20px 16px 56px}
.shots figure{width:96px}.strip figure{width:120px}td,th{padding:8px 7px}}
@media print{body{background:#fff;font-size:12px}.wrap{max-width:none;padding:0}.layer,nav.top{display:none}
.strip{flex-wrap:wrap;overflow:visible}.strip figure{width:118px}
section{padding-top:22px}h2,h3{break-after:avoid}tr,.kpis,.kpi,.box,.facts,svg{break-inside:avoid}
.divider{break-before:page}}
"""
)
LIGHTBOX = """<dialog class="lb" id="lb" aria-label="Screen"><img alt=""><p></p></dialog>
<script>(()=>{const d=document.getElementById('lb');if(!d||!d.showModal)return;
const im=d.querySelector('img'),cap=d.querySelector('p');
document.addEventListener('click',e=>{const a=e.target.closest('a.shot');
if(a){e.preventDefault();const i=a.querySelector('img');im.src=a.getAttribute('href');
im.alt=i?i.alt:'';cap.textContent=im.alt;d.showModal();return}
if(d.open&&e.target.closest('#lb'))d.close()})})();</script>"""


def _reason(detail: str) -> str:
    """A skip message without its pytest / harness prefixes: the reason itself."""
    return re.sub(r"^(Skipped:\s*)?(Blocked:\s*)?", "", detail)


def _e(text: object) -> str:
    return html.escape(str(text))


def _minutes(seconds: float) -> str:
    if seconds >= 3600:
        return f"{int(seconds // 3600)} h {int(seconds % 3600 // 60)} min"
    return f"{seconds / 60:.1f} min" if seconds >= 60 else f"{seconds:.0f} s"


def _pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.3f}%" if whole else "0%"


def _count(n: int, noun: str) -> str:
    return "" if n == 0 else f"{n} {noun}{'' if n == 1 else 's'}"


def _plural(n: int, noun: str, many: str = "") -> str:
    return f"{n} {noun if n == 1 else (many or noun + 's')}"


def _bar(parts: list[tuple[str, int, str]], total: int, label: str) -> str:
    cells = "".join(
        f'<i class="{cls}" style="width:{_pct(n, total)}" title="{_e(title)}"></i>' for cls, n, title in parts if n
    )
    return f'<div class="bar" role="img" aria-label="{_e(label)}">{cells}</div>'


class AssetCopier:
    """Copies the attachments the page shows next to it; names stay unique and stable."""

    def __init__(self, out_dir: Path, redactor: Redactor | None = None, source_root: Path = Path(".")):
        self.redactor = redactor
        self.source_root = source_root
        self.dir = out_dir / "assets"
        if self.dir.exists() and (self.dir / MARKER).exists():
            shutil.rmtree(self.dir)  # our own previous output only
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / MARKER).write_text("generated by automation/tools/mobile_summary.py\n")

    def __call__(self, source: Path) -> str:
        shared = PUBLIC and source.suffix.lower() in (".png", ".jpg", ".jpeg")
        name = f"{source.stem}.jpg" if shared else source.name
        if not (self.dir / name).exists():
            target = self.dir / source.name
            shutil.copy2(source, target)
            if self.redactor:
                self.redactor.image(target)  # on the full-size screen: the boxes are in its pixels
            if shared:
                try:
                    _shrink(target, self.dir / name)
                except OSError:  # not an image Pillow reads: shared as it is
                    return f"assets/{source.name}"
        return f"assets/{name}"


SHARED_WIDTH = 720  # the shared copy's screens: enough to read a phone screen, a tenth of the bytes


def _shrink(source: Path, target: Path) -> None:
    """A screen for the shared copy: at most SHARED_WIDTH wide, JPEG — the original (already pixelated) goes."""
    from PIL import Image  # noqa: PLC0415

    with Image.open(source) as img:
        img = img.convert("RGB")
        if img.width > SHARED_WIDTH:
            img = img.resize((SHARED_WIDTH, round(img.height * SHARED_WIDTH / img.width)), Image.LANCZOS)
        img.save(target, "JPEG", quality=82, optimize=True, progressive=True)
    if source != target:
        source.unlink()


MARK = {"passed": "✓", "failed": "✗", "broken": "✗", "skipped": "–"}
TEXT_LIMIT = 3000


def _duration(node: dict) -> str:
    start, stop = node.get("start"), node.get("stop")
    if not start or not stop:
        return ""
    return _minutes(max(int(stop) - int(start), 0) / 1000)


def shot_html(src: str, caption: str, t) -> str:
    return (
        f"<figure><a class='shot' href='{t(src)}'><img loading='lazy' src='{t(src)}' "
        f"alt='{t(caption)}'></a><figcaption>{t(caption)}</figcaption></figure>"
    )


def attachments_html(node: dict, t, copy: AssetCopier, root: Path) -> str:
    out: list[str] = []
    for att in node.get("attachments") or []:
        source = root / str(att.get("source") or "")
        name = str(att.get("name") or "")
        if not source.is_file():
            continue
        suffix = source.suffix.lower()
        if suffix in (".png", ".jpg", ".jpeg"):
            out.append(shot_html(copy(source), name, t))
        elif suffix == ".mp4" and PUBLIC:
            out.append(
                f"<p class='att-omitted'>{t(name)} — video, not in the shared copy "
                "(the recording starts before sign-in and may show the test account)</p>"
            )
        elif suffix == ".mp4":
            out.append(
                f"<figure><video controls preload='none' src='{t(copy(source))}'>"
                f"</video><figcaption>{t(name)}</figcaption></figure>"
            )
        elif PUBLIC:
            out.append(f"<p class='att-omitted'>{t(name)} — text, not in the shared copy</p>")
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


# --------------------------------------------------------------------------- #
# The report
# --------------------------------------------------------------------------- #


@dataclass
class Module:
    key: str  # "02-authentication" — the checklist's folder
    label: str  # "02 · Authentication"
    rows: list[tr.TraceRow]
    runs: list[TestRun]

    @property
    def page(self) -> str:
        return f"{self.key}.html"

    @property
    def name(self) -> str:
        return self.label.split("·", 1)[-1].strip()

    @property
    def number(self) -> str:
        return self.key.split("-", 1)[0]


@dataclass
class Report:
    runs: list[TestRun]
    rows: list[tr.TraceRow]
    summary: tr.Summary
    env: dict[str, str]
    run_label: str
    target: str
    copy: AssetCopier
    now: datetime
    bugs: list[Bug]
    kinds: dict[str, Kind]
    reasons: dict[str, Reason]
    history: list[RunRecord]
    pace: list[PaceStep]
    notes: list[str]
    decisions: list[str]
    history_note: str = ""
    manual_minutes: float | None = None
    red: Redactor = field(default_factory=lambda: Redactor(None, None))
    first_commit: datetime | None = None
    platform: str = "ios"
    reasons_file: str = "qa/mobile/ios/not-automated.md"
    slice: brand.Slice | None = None
    tools: str = ""  # Appium and driver versions (technical layer)

    def __post_init__(self) -> None:
        self.by_chk: dict[str, list[TestRun]] = {}
        for r in self.runs:
            for chk in r.chk_ids:
                self.by_chk.setdefault(chk, []).append(r)
        self.bug_of: dict[str, Bug | None] = {r.uid: bug_for(r, self.bugs) for r in self.runs if r.status == "Failed"}
        suites = {r.module.split("·")[0].strip(): r.module for r in self.runs}
        grouped: dict[str, list[tr.TraceRow]] = {}
        for row in self.rows:
            grouped.setdefault(row.item.source.parent.name, []).append(row)
        self.modules: list[Module] = []
        for key, rows in sorted(grouped.items()):
            number = key.split("-", 1)[0]
            label = suites.get(number) or module_of_checklist(rows[0].item.source)
            runs = [r for r in self.runs if r.module == label]
            self.modules.append(Module(key, label, rows, runs))
        self.module_of_chk = {row.item.chk_id: m for m in self.modules for row in m.rows}
        self.open_bugs = [b for b in self.bugs if b.filed]
        # drafts the owner decided not to file whose tests stay red in this run
        self.known_drafts = [b for b in self.bugs if not b.filed and any(v is b for v in self.bug_of.values())]

    # --- text helpers ------------------------------------------------------------------

    def t(self, value: object) -> str:
        return _e(self.red.text(value))

    def bug_ref(self, bug: Bug) -> str:
        """A filed defect links to its page; a draft the owner decided not to file has none."""
        if bug.filed:
            return f"<a href='bugs/{self.t(bug.bug_id)}.html'>{self.t(bug.bug_id)}</a>"
        return f"{self.t(bug.bug_id)} <span class='muted'>(known, not filed — owner's decision)</span>"

    def verdict(self, row: tr.TraceRow) -> str:
        """Passed | Held red | Failed | Blocked | Not automated."""
        v = tr.verdict_for(row.results)
        if v == tr.VERDICT_FAILED:
            failed = [r for r in self.by_chk.get(row.item.chk_id, []) if r.status == "Failed"]
            if failed and all(self.bug_of.get(r.uid) for r in failed):
                return "Held red"
            return "Failed"
        return v or "Not automated"

    def row_bugs(self, row: tr.TraceRow) -> list[Bug]:
        found: list[Bug] = []
        for r in self.by_chk.get(row.item.chk_id, []):
            bug = self.bug_of.get(r.uid)
            if bug and bug not in found:
                found.append(bug)
        return found

    def counts(self, rows: list[tr.TraceRow]) -> dict[str, int]:
        c = {"Passed": 0, "Held red": 0, "Failed": 0, "Blocked": 0, "Not automated": 0}
        for row in rows:
            c[self.verdict(row)] += 1
        return c

    def held_by(self, bug: Bug) -> list[str]:
        return [row.item.chk_id for row in self.rows if bug in self.row_bugs(row)]

    def test_counts(self) -> dict[str, int]:
        return {s: sum(1 for r in self.runs if r.status == s) for s in ("Passed", "Failed", "Blocked")}

    def unexpected_tests(self) -> list[TestRun]:
        return [r for r in self.runs if r.status == "Failed" and not self.bug_of.get(r.uid)]

    # --- documents ---------------------------------------------------------------------

    def head(self, title: str) -> str:
        return f"<title>{_e(title)}</title>{FONTS}<style>{CSS}</style>"

    def document(self, title: str, body: str) -> str:
        return (
            "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1,viewport-fit=cover'>"
            f"{self.head(title)}</head><body>{body}</body></html>"
        )

    def facts(self) -> list[tuple[str, str]]:
        wall = (max(r.stop_ms for r in self.runs) - min(r.start_ms for r in self.runs)) / 1000 if self.runs else 0
        finished = datetime.fromtimestamp(max(r.stop_ms for r in self.runs) / 1000, UTC) if self.runs else self.now
        env = self.env
        rf = run_facts(env, self.platform)
        tc = self.test_counts()
        unexpected = len(self.unexpected_tests())
        return [
            ("Run finished", f"{finished:%Y-%m-%d %H:%M} UTC · {_minutes(wall)}"),
            ("Operating system", rf["os"]),
            ("Device", self.target or rf["device"]),
            ("App build", f"{rf['app']} · {rf['build']}"),
            ("App type", rf["app_type"]),
            ("App source", env.get("App source", "not recorded")),
            ("Harness code", env.get("Harness commit", "not recorded")),
            (
                "Tests run",
                f"{len(self.runs)} · {tc['Failed']} red · {tc['Blocked']} blocked · {unexpected} unexpected",
            ),
            ("Report generated", f"{self.now:%Y-%m-%d %H:%M} UTC"),
        ]

    def device_line(self) -> str:
        rf = run_facts(self.env, self.platform)
        return f"{rf['device']}, {rf['os']}"

    def run_date(self) -> str:
        """The date of the run this report describes — a PDF's name and the document's version carry it."""
        stop = max((r.stop_ms for r in self.runs), default=0)
        return datetime.fromtimestamp(stop / 1000, UTC).strftime("%Y-%m-%d") if stop else self.now.strftime("%Y-%m-%d")

    def docinfo(self, slc: brand.Slice) -> str:
        """Where this document lives, so a printout can never be mistaken for another version of it."""
        t = self.t
        run_date = self.run_date()
        source = f"automation/mobile/reports/{self.platform}/internal/index.html"
        online = f"<a href='{t(slc.internal_url)}'>{t(slc.internal_url)}</a>" if slc.internal_url else "—"
        return (
            f"<p class='docinfo'><b>Document.</b> Version of {t(run_date)} (the run this report describes) · "
            f"Source: <code>{t(source)}</code> · Online: {online} · PDF: "
            f"<code>{t(slc.pdf_name('TestCompletionReport_INTERNAL', run_date))}</code> · "
            f"{t(brand.CONFIDENTIALITY)}, {t(brand.COMPANY)} internal.</p>"
        )

    # --- index -------------------------------------------------------------------------

    def verdict_pill(self) -> tuple[str, str]:
        tc = self.test_counts()
        unexpected = self.unexpected_tests()
        held = [self.bug_of[r.uid] for r in self.runs if self.bug_of.get(r.uid)]
        known = sum(1 for b in held if b.filed)
        drafts = len(held) - known
        bugs_red = {b.bug_id for b in held if b.filed}
        draft_ids = sorted({b.bug_id for b in held if not b.filed})
        if unexpected:
            return (
                '<span class="pill fail">Failed</span>',
                f"{_plural(len(unexpected), 'test')} failed with no filed defect behind "
                f"{'it' if len(unexpected) == 1 else 'them'} — triage comes first: a wrong "
                "expectation is fixed in the test, a product fault becomes a bug report.",
            )
        if tc["Failed"] or tc["Blocked"]:
            parts = []
            if known:
                parts.append(
                    f"the {_plural(known, 'red test')} {'is' if known == 1 else 'are'} the "
                    f"regression check{'s' if known != 1 else ''} of "
                    f"{_plural(len(bugs_red), 'filed defect')} and stay red until "
                    f"{'it is' if len(bugs_red) == 1 else 'they are'} fixed"
                )
            if drafts:
                parts.append(
                    f"{_plural(drafts, 'red test')} {'shows' if drafts == 1 else 'show'} app "
                    f"behaviour the owner triaged and decided not to file ({', '.join(draft_ids)})"
                )
            if tc["Blocked"]:
                parts.append(
                    f"{_plural(tc['Blocked'], 'test')} could not run (Blocked), each with its "
                    "reason below — Blocked is never counted as passed"
                )
            return (
                '<span class="pill known">No unexpected failures</span>',
                "Nothing failed that is not already a known defect: " + "; ".join(parts) + ".",
            )
        return (
            '<span class="pill pass">Passed</span>',
            "Every test behaved as expected; nothing failed and nothing was blocked.",
        )

    def index(self) -> str:
        t = self.t
        s = self.summary
        c = self.counts(self.rows)
        out: list[str] = []
        w = out.append
        pill, meaning = self.verdict_pill()
        slc = self.slice or brand.slice_(self.platform)
        w("<div class='wrap'><header>")
        w(brand.brandbar("internal"))
        w(f"<div class='eyebrow'>Test completion report · Mobile regression · {PLATFORM_NAME[self.platform]}</div>")
        w(f"<h1>{t(slc.product)} — Test Completion Report <span class='tag'>Internal</span> {pill}</h1>")
        w(f"<p class='muted' style='margin:0'>{t(meaning)}</p>")
        w(
            f"<p style='margin:4px 0 0'><b>Checklist now</b> (this run): {c['Passed']} green · "
            f"{c['Held red']} red, each held by a known defect · {c['Blocked']} blocked · "
            f"{c['Failed']} red and unexplained.</p>"
        )
        w("<dl class='facts'>")
        for key, value in self.facts():
            w(f"<div><dt>{t(key)}</dt><dd>{t(value)}</dd></div>")
        w("</dl>")
        w(self.docinfo(slc))
        w("<nav class='layer' aria-label='Report layers'>")
        links = [
            ("summary", "Summary"),
            ("defects", "Open defects"),
            ("blocked", "Could not run"),
            ("not-automated", "Not automated"),
        ]
        if self.history:
            links.append(("stability", "Stability"))
        if self.pace:
            links.append(("pace", "Delivery pace"))
        links.append(("technical", "Technical detail"))
        w("".join(f"<a href='#{a}'>{label}</a>" for a, label in links))
        w("</nav></header>")

        # --- summary
        pct = f"{100 * s.automated / s.total:.0f}%" if s.total else "0%"
        bugs_red = {b.bug_id for row in self.rows for b in self.row_bugs(row) if b.filed}
        drafts_red = {b.bug_id for row in self.rows for b in self.row_bugs(row) if not b.filed}
        unexpected = c["Failed"]
        w("<section id='summary'><h2>Summary</h2>")
        w(
            f"<p class='lead'>The QA checklist for the mobile app holds <b>{s.total}</b> checks "
            f"across {len(self.modules)} modules. <b>{s.automated}</b> of them ({pct}) are "
            f"automated and ran on {t(self.target or self.device_line())}. "
            f"In this run <b>{c['Passed']}</b> passed; <b>{c['Held red']}</b> "
            f"{'is' if c['Held red'] == 1 else 'are'} held red by {_plural(len(bugs_red), 'open defect')}"
            + (f" and {_plural(len(drafts_red), 'known issue')} the owner decided not to file" if drafts_red else "")
            + f", each with a test that fails until the defect is fixed; <b>{c['Blocked']}</b> could "
            f"not run for a stated reason. "
            + (
                f"<b>{unexpected}</b> failed with no defect behind them. "
                if unexpected
                else "Nothing failed unexpectedly. "
            )
            + f"The other <b>{s.total - s.automated}</b> checks are not automated, each for a "
            "written reason (below).</p>"
        )
        w("<div class='kpis'>")
        w(f"<div class='kpi'><b>{s.total}</b><span>checks in the QA checklist</span></div>")
        w(f"<div class='kpi'><b>{s.automated}</b><span>automated · {pct}</span></div>")
        w(f"<div class='kpi pass'><b>{c['Passed']}</b><span>passed in this run</span></div>")
        w(
            f"<div class='kpi known'><b>{c['Held red']}</b><span>held red by "
            f"{_plural(len(bugs_red | drafts_red), 'known defect')}</span></div>"
        )
        if c["Failed"]:
            w(f"<div class='kpi fail'><b>{c['Failed']}</b><span>failed, no defect yet</span></div>")
        w(f"<div class='kpi block'><b>{c['Blocked']}</b><span>blocked — could not run</span></div>")
        if self.manual_minutes is not None:
            verified = c["Passed"] + c["Held red"] + c["Failed"]
            w(
                f"<div class='kpi'><b>≈ {verified * self.manual_minutes / 60:.1f} h</b><span>the "
                f"same {verified} checks by hand ({self.manual_minutes:g} min each, owner's "
                "estimate)</span></div>"
            )
        w("</div>")
        w(self.bar(c, s.total))
        w(
            "<div class='legend'><span><i style='background:var(--pass)'></i>passed</span>"
            "<span><i style='background:var(--known)'></i>held red by a known defect</span>"
            + ("<span><i style='background:var(--fail)'></i>failed, no defect yet</span>" if c["Failed"] else "")
            + "<span><i style='background:var(--block)'></i>blocked — could not run</span>"
            "<span><i style='background:var(--idle)'></i>not automated (reason written)</span></div>"
        )
        w(self.strip())
        w("<h3 style='margin-top:26px'>By module</h3><div class='scroll'><table class='mods'>")
        w(
            "<thead><tr><th>Module</th><th class='num'>Checks</th><th class='num'>Automated</th>"
            "<th class='num'>Passed</th><th class='num'>Held red</th><th class='num'>Blocked</th>"
            "<th class='num'>Not automated</th><th>Coverage</th></tr></thead><tbody>"
        )
        for m in self.modules:
            mc = self.counts(m.rows)
            ms = tr.summarize(m.rows)
            red = mc["Held red"] + mc["Failed"]
            w(
                f"<tr><td><a href='{m.page}'>{t(m.label)}</a></td><td class='num'>{ms.total}</td>"
                f"<td class='num'>{ms.automated}</td><td class='num'>{mc['Passed']}</td>"
                f"<td class='num'>{red}</td><td class='num'>{mc['Blocked']}</td>"
                f"<td class='num'>{mc['Not automated']}</td><td class='barcell'>{self.bar(mc, ms.total)}</td></tr>"
            )
        w("</tbody></table></div>")
        w("<div class='box' style='margin-top:22px'><h3>What needs a decision</h3><ul>")
        for item in self.decision_items():
            w(f"<li>{item}</li>")
        w("</ul></div></section>")

        w(self.defects_section())
        w(self.blocked_section())
        w(self.not_automated_section())
        if self.history:
            w(self.stability_section())
        if self.pace:
            w(self.pace_section())
        w(self.technical_section())
        w(
            f"<p class='note' style='margin-top:34px'>Generated by "
            f"<code>automation/tools/mobile_summary.py</code> from the repository, "
            f"{self.now:%Y-%m-%d %H:%M} UTC. Every number above is read from the Allure results "
            f"of the run, the checklists, the bug reports, <code>{t(self.reasons_file)}</code> "
            "and git.</p>"
        )
        w("</div>" + LIGHTBOX)
        return "\n".join(out)

    def bar(self, c: dict[str, int], total: int) -> str:
        label = (
            f"{c['Passed']} passed, {c['Held red']} held red by known defects, "
            f"{c['Failed']} failed, {c['Blocked']} blocked, {c['Not automated']} not automated, of {total}"
        )
        return _bar(
            [
                ("p", c["Passed"], f"{c['Passed']} passed"),
                ("k", c["Held red"], f"{c['Held red']} held red by a known defect"),
                ("f", c["Failed"], f"{c['Failed']} failed, no defect yet"),
                ("b", c["Blocked"], f"{c['Blocked']} blocked"),
            ],
            total,
            label,
        )

    def strip(self) -> str:
        """One phone screen per module — what the tests actually looked at."""
        figures = []
        for m in self.modules:
            run = next((r for r in m.runs if r.status == "Passed" and r.checkpoints), None)
            if run:
                name, source = run.checkpoints[0]
                caption = f"{m.label} — {name.split(CHECKPOINT_PREFIX, 1)[-1]}"
                figures.append(shot_html(self.copy(source), caption, self.t))
        if not figures:
            return ""
        return (
            "<h3 style='margin-top:26px'>What the tests saw</h3><p class='note' style='margin-top:0'>"
            "One screen per module, saved by a passing test at a checkpoint. Tap a screen to "
            "enlarge it; each module page has every screen next to the check it belongs to.</p>"
            f"<div class='strip'>{''.join(figures)}</div>"
        )

    def decision_items(self) -> list[str]:
        t = self.t
        items: list[str] = []
        unexpected = self.unexpected_tests()
        if unexpected:
            items.append(
                f"<b>{_plural(len(unexpected), 'test')} failed with no filed defect</b> — triage: "
                + ", ".join(t(r.tc or r.title) for r in unexpected)
            )
        proposed = [b for b in self.open_bugs if b.priority_proposed]
        if proposed:
            items.append(
                f"The priority of {_plural(len(proposed), 'open defect')} is QA's proposal — the "
                "owner / PM decide: "
                + ", ".join(f"<a href='bugs/{t(b.bug_id)}.html'>{t(b.bug_id)}</a>" for b in proposed)
            )
        missing = [row.item.chk_id for row in self.rows if not row.results and row.item.chk_id not in self.reasons]
        if missing:
            items.append(
                f"{_plural(len(missing), 'check')} without a test and without a written reason: "
                + ", ".join(t(x) for x in missing[:12])
                + (" …" if len(missing) > 12 else "")
            )
        items += [t(d) for d in self.decisions]
        return items or ["Nothing is waiting on the owner."]

    def known_drafts_html(self) -> str:
        """Red tests the owner triaged as app behaviour and decided not to file."""
        if not self.known_drafts:
            return ""
        t = self.t
        mod_by_key = {m.key: m for m in self.modules}
        rows = []
        for b in self.known_drafts:
            m = mod_by_key.get(b.module_dir)
            mod = f"<a href='{m.page}'>{t(m.label)}</a>" if m else t(b.module_dir)
            held = ", ".join(t(x.removeprefix("CHK-")) for x in self.held_by(b))
            rows.append(
                f"<tr><td class='mono id'>{t(b.bug_id)}</td><td>{mod}</td><td>{t(b.title)}</td>"
                f"<td class='mono'>{held}</td></tr>"
            )
        return (
            f"<h3 style='margin-top:22px'>Known, not filed · {len(self.known_drafts)}</h3>"
            "<p>The owner triaged these as the app's behaviour and decided not to file them. Their "
            "tests stay red and are counted as held red by a known defect, not as unexpected "
            "failures; the reports stay in the repository as drafts.</p>"
            "<div class='scroll'><table><thead><tr><th>Draft</th><th>Module</th><th>What is wrong</th>"
            "<th>Checks held red</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
        )

    def defects_section(self) -> str:
        t = self.t
        out = [f"<section id='defects'><h2>Open defects · {len(self.open_bugs)}</h2>"]
        if not self.open_bugs:
            out.append("<p>No open defects.</p>" + self.known_drafts_html() + "</section>")
            return "".join(out)
        holding = [b for b in self.open_bugs if self.held_by(b)]
        out.append(
            f"<p>{len(holding)} of them hold checklist checks red through their regression "
            "tests; a defect with no such test is listed with a dash (its report says why).</p>"
        )
        sev: dict[str, int] = {}
        labels: dict[str, str] = {}
        for b in self.open_bugs:
            sev[b.severity] = sev.get(b.severity, 0) + 1
            labels.setdefault(b.severity, b.severity_label)
        out.append(
            "<p>"
            + " · ".join(f"<span class='sev {t(k)}'>{t(k)}</span> {t(labels[k])}: {n}" for k, n in sorted(sev.items()))
            + ". Every defect is filed locally, in the repository; no tracker is configured.</p>"
        )
        out.append(
            "<div class='scroll'><table><thead><tr><th>Defect</th><th>Module</th><th>What is wrong</th>"
            "<th>Severity</th><th>Priority</th><th>Checks held red</th></tr></thead><tbody>"
        )
        order = {"S1": 1, "S2": 2, "S3": 3, "S4": 4}
        mod_by_key = {m.key: m for m in self.modules}
        for b in sorted(self.open_bugs, key=lambda b: (order.get(b.severity, 9), b.priority, b.bug_id)):
            m = mod_by_key.get(b.module_dir)
            mod = f"<a href='{m.page}'>{t(m.label)}</a>" if m else t(b.module_dir)
            held = self.held_by(b)
            held_html = (
                ", ".join(t(x.removeprefix("CHK-")) for x in held)
                if held
                else "<span class='muted'>— (no test holds a check red)</span>"
            )
            pri = t(b.priority) + (" <span class='muted'>proposed</span>" if b.priority_proposed else "")
            out.append(
                f"<tr><td class='mono id'><a href='bugs/{t(b.bug_id)}.html'>{t(b.bug_id)}</a></td>"
                f"<td>{mod}</td><td>{t(b.title)}</td>"
                f"<td><span class='sev {t(b.severity)}'>{t(b.severity)} {t(b.severity_label)}</span></td>"
                f"<td class='mono'>{pri}</td><td class='mono'>{held_html}</td></tr>"
            )
        out.append("</tbody></table></div>")
        out.append(
            "<p class='note'>Each defect has a report with steps, the expected and actual result, "
            "screenshots and its regression test, under <code>qa/mobile/&lt;module&gt;/bugs/</code>.</p>"
            + self.known_drafts_html()
            + "</section>"
        )
        return "".join(out)

    def blocked_section(self) -> str:
        t = self.t
        blocked = [r for r in self.runs if r.status == "Blocked"]
        checks = [row for row in self.rows if self.verdict(row) == "Blocked"]
        out = [f"<section id='blocked'><h2>Could not run · {_plural(len(checks), 'check')}</h2>"]
        if not blocked:
            out.append("<p>Every automated test ran.</p></section>")
            return "".join(out)
        out.append(
            f"<p>{_plural(len(blocked), 'test')} stopped before {'its' if len(blocked) == 1 else 'their'} "
            "check could decide anything. Blocked is not a pass: the check stays owed and runs "
            "again in the next round — or on the Android stage, where the reason says so.</p>"
        )
        out.append(
            "<div class='scroll'><table><thead><tr><th>Test</th><th>What it does</th><th>Checks</th><th>Why</th></tr>"
            "</thead><tbody>"
        )
        for r in blocked:
            m = next((m for m in self.modules if m.label == r.module), None)
            href = f"{m.page}#t-{t(r.uid)}" if m else "#"
            why = _reason(r.detail)
            out.append(
                f"<tr><td class='nowrap'><a href='{href}'>{t(r.tc or r.title)}</a></td>"
                f"<td>{t(r.title.removeprefix(r.tc).strip())}</td>"
                f"<td class='mono'>{t(', '.join(x.removeprefix('CHK-') for x in r.chk_ids))}</td>"
                f"<td>{t(why)}</td></tr>"
            )
        out.append("</tbody></table></div></section>")
        return "".join(out)

    def not_automated_rows(self) -> list[tr.TraceRow]:
        return [row for row in self.rows if not row.results]

    def not_automated_section(self) -> str:
        t = self.t
        rows = self.not_automated_rows()
        by_kind: dict[str, int] = {}
        for row in rows:
            reason = self.reasons.get(row.item.chk_id)
            key = reason.kind if reason else ""
            by_kind[key] = by_kind.get(key, 0) + 1
        out = [f"<section id='not-automated'><h2>Why {len(rows)} checks are not automated</h2>"]
        out.append(
            "<p>Every one of them has a reason in its module's automation plan, test cases or an "
            f"owner decision; <code>{t(self.reasons_file)}</code> collects them and the page "
            "sorts them into the kinds below. The full list, check by check, is in the technical detail.</p>"
        )
        out.append(
            "<div class='scroll'><table><thead><tr><th>Reason</th><th>What it means</th>"
            "<th class='num'>Checks</th></tr></thead><tbody>"
        )
        for key, n in sorted(by_kind.items(), key=lambda kv: (-kv[1], kv[0])):
            kind = self.kinds.get(key)
            title = kind.title if kind else "Reason missing"
            meaning = kind.meaning if kind else f"no row in {self.reasons_file} — owed"
            out.append(f"<tr><td><b>{t(title)}</b></td><td>{t(meaning)}</td><td class='num'>{n}</td></tr>")
        out.append("</tbody></table></div></section>")
        return "".join(out)

    def stability_section(self) -> str:
        t = self.t
        streak = identical_streak(self.history)
        last = self.history[-1]
        out = ["<section id='stability'><h2>Stability and run history</h2>"]
        if streak >= 2:
            out.append(
                f"<p class='lead'>The last <b>{streak}</b> full runs gave the same verdict for every "
                f"one of <b>{last.tests}</b> tests — nothing flaky. Retries are off, so a flaky test "
                "could not hide behind a second attempt.</p>"
            )
        else:
            out.append(
                "<p class='lead'>The last two full runs did not give the same verdicts for every "
                "test — see the table.</p>"
            )
        out.append(
            "<div class='scroll'><table><thead><tr><th>Run</th><th>Finished (UTC)</th><th>Harness</th>"
            "<th class='num'>Time</th><th class='num'>Tests</th><th class='num'>Passed</th>"
            "<th class='num'>Red</th><th class='num'>Unexpected</th><th class='num'>Blocked</th>"
            "<th>Verdict</th><th class='num'>Checks passed</th></tr></thead><tbody>"
        )
        for rec in reversed(self.history):
            if rec.unexpected:
                verdict = '<span class="pill fail">Failed</span>'
            elif rec.counts["Failed"] or rec.counts["Blocked"]:
                verdict = '<span class="pill known">Known only</span>'
            else:
                verdict = '<span class="pill pass">Passed</span>'
            out.append(
                f"<tr><td class='mono nowrap'>{t(rec.label)}</td><td class='mono'>{rec.finished:%Y-%m-%d %H:%M}</td>"
                f"<td class='mono'>{t(rec.harness)}</td><td class='num nowrap'>{_minutes(rec.minutes * 60)}</td>"
                f"<td class='num'>{rec.tests}</td><td class='num'>{rec.counts['Passed']}</td>"
                f"<td class='num'>{rec.counts['Failed']}</td><td class='num'>{rec.unexpected}</td>"
                f"<td class='num'>{rec.counts['Blocked']}</td><td>{verdict}</td>"
                f"<td class='num'>{rec.checks.passed} / {rec.checks.automated}</td></tr>"
            )
        out.append("</tbody></table></div>")
        out.append(
            "<p class='note'>Full-app runs only. <b>Red</b> counts every failed test; "
            "<b>Unexpected</b> is the part no filed defect names as its regression check."
            + (f" {t(self.history_note)}" if self.history_note else "")
            + "</p></section>"
        )
        return "".join(out)

    def pace_section(self) -> str:
        t = self.t
        steps = self.pace
        total = sum(s.checks for s in steps)
        start, end = steps[0].when, steps[-1].when
        hours = (end - start).total_seconds() / 3600
        tz = start.strftime("%z")
        tz_label = f"UTC{tz[:3]}:{tz[3:]}" if tz else "UTC"
        n_mod = sum(len(s.modules) for s in steps)
        out = ["<section id='pace'><h2>Delivery pace</h2>"]
        before = (
            f" the repository was set up on {self.first_commit:%-d %B}, and the harness, the "
            "checklist import and the recon on the simulator came first;"
            if self.first_commit
            else ""
        )
        out.append(
            f"<p>The first module's tests landed in git on {start:%-d %B %Y, %H:%M}, the last on "
            f"{end:%-d %B %Y, %H:%M} ({tz_label}) — {n_mod} modules and {total} automated checks "
            f"in about {hours:.0f} hours of calendar time. Each step on the line is one commit that "
            "first added a module's test file; its height is the checks that module automates "
            f"today. These are commit times, not hours of effort:{before} each module's review and "
            "fixes continued after it landed.</p>"
        )
        x0, x1, y0, y1 = 48.0, 900.0, 208.0, 18.0
        span = max((end - start).total_seconds(), 1.0)

        def x(when: datetime) -> float:
            return x0 + (x1 - x0) * (when - start).total_seconds() / span

        def y(value: int) -> float:
            return y0 - (y0 - y1) * value / max(total, 1)

        svg = [
            '<svg viewBox="0 0 960 250" width="100%" role="img" aria-label="Checks automated over time, by module">',
            f'<line class="axis" x1="{x0}" x2="{x1}" y1="{y0}" y2="{y0}"/><text x="40" y="{y0 + 4}" text-anchor="end">0</text>',
            f'<line class="axis" x1="{x0}" x2="{x1}" y1="{y(total // 2):.1f}" y2="{y(total // 2):.1f}"/>'
            f'<text x="40" y="{y(total // 2) + 4:.1f}" text-anchor="end">{total // 2}</text>',
            f'<line class="axis" x1="{x0}" x2="{x1}" y1="{y1}" y2="{y1}"/><text x="40" y="{y1 + 4}" text-anchor="end">{total}</text>',
        ]
        day = start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        while day < end:
            svg.append(
                f'<line class="axis" x1="{x(day):.1f}" x2="{x(day):.1f}" y1="{y1}" y2="{y0}" stroke-dasharray="3 4"/>'
            )
            if x(day) - x0 >= 90:  # a label clear of the start label
                svg.append(f'<text x="{x(day):.1f}" y="234" text-anchor="middle">{day:%-d %b}</text>')
            day += timedelta(days=1)
        svg.append(f'<text x="{x0}" y="234" text-anchor="start">{start:%-d %b %H:%M}</text>')
        path = [f"M{x0:.1f},{y0:.1f}"]
        running = 0
        for s in steps:
            running += s.checks
            path.append(f"H{x(s.when):.1f} V{y(running):.1f}")
        svg.append(f'<path class="line" d="{" ".join(path)}"/>')
        points, running = [], 0
        for s in steps:
            running += s.checks
            points.append((x(s.when), y(running)))
        bubbles = list(points)
        for i in range(len(bubbles) - 2, -1, -1):  # push a bubble left of its next neighbour
            (bx, by), (nx, ny) = bubbles[i], bubbles[i + 1]
            if abs(nx - bx) < 18 and abs(ny - by) < 18:
                bubbles[i] = (nx - 18, by)
        for i, ((px, py), (bx, by)) in enumerate(zip(points, bubbles, strict=True), 1):
            if (bx, by) != (px, py):
                svg.append(f'<line class="line" x1="{px:.1f}" y1="{py:.1f}" x2="{bx:.1f}" y2="{by:.1f}"/>')
            svg.append(
                f'<circle class="dot" cx="{bx:.1f}" cy="{by:.1f}" r="8"/>'
                f'<text class="num" x="{bx:.1f}" y="{by + 3.5:.1f}" text-anchor="middle">{i}</text>'
            )
        svg.append("</svg>")
        out.append(f"<div class='box scroll'>{''.join(svg)}</div><ol class='pace'>")
        for s in steps:
            out.append(
                f"<li><b>{t(' + '.join(s.modules))}</b> +{s.checks} · "
                f"<span class='muted'>{s.when:%-d %b %H:%M}</span></li>"
            )
        out.append("</ol></section>")
        return "".join(out)

    def technical_section(self) -> str:
        t = self.t
        env = self.env
        blocked = self.test_counts()["Blocked"]
        out = ["<section id='technical' class='divider'>"]
        out.append(
            "<div class='eyebrow'>For the technical team</div>"
            "<h2 style='margin-top:6px'>Technical detail</h2><div class='grid2'>"
        )
        out.append(
            "<div class='box'><h3>How a verdict is decided</h3><ul>"
            "<li><b>Passed</b> only when an assertion with a named oracle decided it: the "
            "checklist or the SRS, the app's accessibility tree, the pixels of a screenshot "
            "(a colour, the theme's brightness) or the server's own copy of what the app saved.</li>"
            "<li><b>Held red</b>: a filed defect's regression test asserts the correct behaviour "
            "and fails until the fix; its report names the test. A fix turns it green by itself.</li>"
            f"<li><b>Blocked</b> ({blocked} in this run) — a precondition the device or the test "
            "environment cannot give — is never green and never silent; each says why.</li>"
            "<li>No retries. One Appium session per run. Every test was proven red once by "
            "breaking its own expectation (<code>--prove-red</code>) before it was trusted.</li>"
            "</ul></div>"
        )
        out.append(
            "<div class='box'><h3>Where to look</h3><ul>"
            "<li>Every check, its test and the screens it saw: open a module in the table under "
            "Summary; each defect's report opens from Open defects.</li>"
            "<li>Every step of every test: the Tests list at the bottom of a module page, or "
            f"Allure — <code>allure open automation/mobile/reports/{self.platform}/allure-report</code>.</li>"
            f"<li>Traceability of record: <code>qa/mobile/{self.platform}/final-traceability.md</code> and "
            f"<code>qa/mobile/&lt;module&gt;/{self.platform}/&lt;module&gt;-traceability.md</code>.</li>"
            f"<li>Why a check is not automated: <code>{t(self.reasons_file)}</code>; "
            "owner rulings: <code>docs/notes/decisions.md</code>.</li>"
            "<li>This page: <code>automation/tools/mobile_summary.py</code>.</li></ul></div>"
        )
        app = "Flutter app" if run_facts(env, self.platform)["app_type"] == "Flutter" else "app"
        scope = [
            f"Device: {self.target or env.get('Device', 'not recorded')}.",
            f"App: {env.get('App', 'not recorded')} {env.get('Build', '')}, built from "
            f"{env.get('App source', 'not recorded')}.",
            (
                f"Driver: Appium with XCUITest — the {app} is read through the iOS accessibility "
                "tree; one test at a time, the app relaunched or reset by each test's preconditions."
                if self.platform == "ios"
                else f"Driver: Appium with UiAutomator2 — the {app} is read through the Android "
                "accessibility tree; one test at a time, one Appium session per module, the app relaunched "
                "or reset by each test's preconditions."
            ),
            f"Tools: {self.tools or 'not recorded'} (installed on the QA machine when this report was built).",
            *brand.SCOPE_NOTES,  # the project's own lines: setup/project.yaml → report.mobile.scope_notes
        ] + list(self.notes)
        out.append(
            "<div class='box'><h3>Scope of this run</h3><ul>"
            + "".join(f"<li>{t(line)}</li>" for line in scope)
            + "</ul></div>"
        )
        shared = (
            "<li>This is the shared copy: the test account's email, phone and name are hidden in "
            "the text and pixelated on the screens; API response bodies, page sources and screen "
            "videos are left out (they stay in Allure on the QA machine).</li>"
            if PUBLIC
            else "<li>This is the full local copy, with API bodies, page sources and videos. Do "
            "not share it: build the shared copy with <code>--public</code>.</li>"
        )
        out.append(
            "<div class='box'><h3>How it is built</h3><ul>"
            "<li>Checklist → automation plan → the owner's answers to D / Q questions → recon on "
            f"the {'simulator' if self.platform == 'ios' else 'emulator'} → structured test cases → screen maps (the only place a locator lives) "
            "→ page objects → pytest tests tagged with checklist ids → generated traceability.</li>"
            "<li>Each module went through a test review (<code>/bmad-testarch-test-review</code>) "
            "before it was called done.</li>"
            "<li>Evidence: named screenshots at checkpoints, a screenshot on failure, a screen "
            "video of failed and end-to-end tests.</li>" + shared + "</ul></div></div>"
        )
        rows = self.not_automated_rows()
        out.append(f"<h3 style='margin-top:26px'>Every check that is not automated, and why · {len(rows)}</h3>")
        for m in self.modules:
            mrows = [row for row in m.rows if not row.results]
            if not mrows:
                continue
            out.append(
                f"<details class='box' style='margin-top:8px'><summary><b>{t(m.label)}</b> · "
                f"{len(mrows)}</summary><div class='scroll'><table><tbody>"
            )
            for row in mrows:
                reason = self.reasons.get(row.item.chk_id)
                kind = self.kinds.get(reason.kind).title if reason and reason.kind in self.kinds else "Reason missing"
                why = f"{reason.why} ({reason.source})" if reason else f"no row in {self.reasons_file}"
                out.append(
                    f"<tr><td class='mono id'><a href='{m.page}#{t(row.item.chk_id)}'>{t(row.item.chk_id)}</a></td>"
                    f"<td>{t(kind)}</td><td>{t(why)}</td></tr>"
                )
            out.append("</tbody></table></div></details>")
        out.append("</section>")
        return "".join(out)

    # --- module pages ------------------------------------------------------------------

    def module_page(self, m: Module) -> str:
        t = self.t
        c = self.counts(m.rows)
        s = tr.summarize(m.rows)
        env = self.env
        out: list[str] = []
        w = out.append
        w(
            "<div class='wrap'>"
            + brand.brandbar("internal")
            + "<nav class='top' style='margin-top:16px'><a href='index.html'>← Summary</a>"
        )
        w("<a href='index.html#defects'>Open defects</a>")
        i = self.modules.index(m)
        if i > 0:
            w(f"<a href='{self.modules[i - 1].page}'>← {t(self.modules[i - 1].label)}</a>")
        if i + 1 < len(self.modules):
            w(f"<a href='{self.modules[i + 1].page}'>{t(self.modules[i + 1].label)} →</a>")
        w("</nav>")
        w(
            f"<p class='eyebrow'>Module {t(m.number)} · {PLATFORM_NAME[self.platform]} · "
            f"{t((self.slice or brand.slice_(self.platform)).product)}</p><h1>{t(m.name)}</h1>"
        )
        w(
            f"<p class='muted' style='margin-top:6px'>{t(self.target or env.get('Device', ''))} · "
            f"{t(env.get('Build', ''))} · harness {t(env.get('Harness commit', ''))} · generated "
            f"{self.now:%Y-%m-%d %H:%M} UTC</p>"
        )
        w("<div class='cards'>")
        for n, label in (
            (s.total, "checks"),
            (s.automated, "automated"),
            (c["Passed"], "passed"),
            (c["Held red"] + c["Failed"], "held red"),
            (c["Blocked"], "blocked"),
            (c["Not automated"], "not automated"),
        ):
            w(f"<div class='card'><b>{n}</b><span>{label}</span></div>")
        w("</div>")
        w(self.bar(c, s.total))
        w(
            "<p class='note'>A red check belongs to the defect named next to it. “Not automated” "
            "is a decision, not an outcome — the reason is written under the check. The "
            "<b>Seen</b> column opens the phone screens the test saved at its checkpoints: they "
            "are there to be looked at, not to decide anything; the assertion is what passed or failed.</p>"
        )
        bugs = [
            b
            for b in self.open_bugs
            if b.module_dir == m.key or any(self.module_of_chk.get(x) is m for x in self.held_by(b))
        ]
        if bugs:
            w("<h2 style='margin-top:26px'>Open defects</h2><ul>")
            for b in bugs:
                w(f"<li><a href='bugs/{t(b.bug_id)}.html'>{t(b.bug_id)}</a> — {t(b.title)}</li>")
            w("</ul>")
        drafts = [b for b in self.known_drafts if any(self.module_of_chk.get(x) is m for x in self.held_by(b))]
        if drafts:
            w("<h2 style='margin-top:26px'>Known, not filed</h2><ul>")
            for b in drafts:
                w(f"<li>{self.bug_ref(b)} — {t(b.title)}</li>")
            w("</ul>")
        blocked = [r for r in m.runs if r.status == "Blocked"]
        if blocked:
            w("<h2 style='margin-top:26px'>Could not run</h2><ul>")
            for r in blocked:
                why = _reason(r.detail)
                w(f"<li><a href='#t-{t(r.uid)}'>{t(r.tc or r.title)}</a> — {t(why)}</li>")
            w("</ul>")
        w("<h2 style='margin-top:30px'>Every check</h2>")
        section = None
        for row in m.rows:
            if row.item.section != section:
                if section is not None:
                    w("</tbody></table></div>")
                section = row.item.section
                w(f"<div class='sect'>{t(section or 'Checks')}</div><div class='scroll'><table class='checks'>")
                w(
                    "<colgroup><col class='c1'><col class='c2'><col class='c3'><col class='c4'>"
                    "<col class='c5'></colgroup><thead><tr><th>Check</th><th>What it verifies</th>"
                    "<th>Verdict</th><th>Proved by</th><th>Seen</th></tr></thead><tbody>"
                )
            w(self.check_row(row))
        if section is not None:
            w("</tbody></table></div>")
        w(f"<h2 style='margin-top:30px'>Tests · {len(m.runs)}</h2>")
        w(
            "<p class='note' style='margin-top:0'>Every step of every test, as the harness recorded "
            "it: <b>setup</b> = preconditions (app reset, sign-in, test data), then the test's own "
            "steps, then <b>teardown</b> = cleanup and evidence. ✓ passed · ✗ failed · – skipped.</p>"
        )
        for r in m.runs:
            w(self.test_details(r))
        w("</div>" + LIGHTBOX)
        return "\n".join(out)

    def check_row(self, row: tr.TraceRow) -> str:
        t = self.t
        chk = row.item.chk_id
        verdict = self.verdict(row)
        cls = {"Passed": "pass", "Held red": "known", "Failed": "fail", "Blocked": "block"}.get(verdict, "idle")
        runs = self.by_chk.get(chk, [])
        note = ""
        if verdict == "Held red":
            note = "".join(f"<div class='why'>{self.bug_ref(b)}</div>" for b in self.row_bugs(row))
        elif verdict in ("Failed", "Blocked"):
            detail = next((r.detail for r in runs if r.status == verdict and r.detail), "")
            note = f"<div class='why'>{t(_reason(detail)[:220])}</div>"
        what = t(row.item.text)
        if verdict == "Not automated":
            reason = self.reasons.get(chk)
            if reason:
                kind = self.kinds.get(reason.kind)
                what += (
                    f"<div class='why'><b>{t(kind.title if kind else reason.kind)}:</b> "
                    f"{t(reason.why)} ({t(reason.source)})</div>"
                )
            else:
                what += f"<div class='why'>Reason missing — owed in {t(self.reasons_file)}</div>"
        proved: list[str] = []
        seen_funcs: dict[str, list[TestRun]] = {}
        for r in runs:
            seen_funcs.setdefault(r.func.split("[")[0] or r.uid, []).append(r)
        for group in seen_funcs.values():
            first = group[0]
            m = self.module_of_run(first)
            href = f"{m.page if m else ''}#t-{t(first.uid)}"
            times = f" ×{len(group)}" if len(group) > 1 else ""
            loc = source_of(first)
            proved.append(
                f"<a href='{href}'>{t(first.tc or first.func)}</a>{times}"
                + (f"<div class='src'>{t(loc)}</div>" if loc else "")
            )
        shots: list[tuple[str, Path]] = []
        seen_paths: set[Path] = set()
        for r in runs:
            for name, source in r.screens:
                if source not in seen_paths:
                    seen_paths.add(source)
                    shots.append((f"{r.tc} · {name}", source))
        seen = ""
        if shots:
            more = len(shots) - SHOTS_PER_CHECK
            figures = "".join(shot_html(self.copy(src), cap, t) for cap, src in shots[:SHOTS_PER_CHECK])
            extra = f"<p class='why'>+{more} more in the test below</p>" if more > 0 else ""
            seen = (
                f"<details class='ev'><summary>{_plural(len(shots), 'screen')}</summary>"
                f"<div class='shots'>{figures}</div>{extra}</details>"
            )
        return (
            f"<tr id='{t(chk)}'><td class='id mono'>{t(chk)}</td><td>{what}</td>"
            f"<td><span class='v {cls}'>{t(verdict)}</span>{note}</td>"
            f"<td>{''.join(proved)}</td><td>{seen}</td></tr>"
        )

    def check_href(self, chk: str, run: TestRun) -> str:
        """A check a test covers: on this page, or on its own module's page when it belongs to another module."""
        home = self.module_of_chk.get(chk)
        here = self.module_of_run(run)
        return f"#{_e(chk)}" if home is None or home is here else f"{home.page}#{_e(chk)}"

    def module_of_run(self, run: TestRun) -> Module | None:
        return next((m for m in self.modules if m.label == run.module), None)

    def test_details(self, r: TestRun) -> str:
        t = self.t
        root = self.copy.source_root
        copy = self.copy
        cls = {"Passed": "pass", "Failed": "known" if self.bug_of.get(r.uid) else "fail", "Blocked": "block"}[r.status]
        label = "Held red" if cls == "known" else r.status
        out = [
            f"<details class='test' id='t-{t(r.uid)}'><summary><span class='v {cls}'>{t(label)}</span> "
            f"{t(r.title)}<span class='dur'>{_minutes(r.duration_s)}</span></summary><div class='tbody'>"
        ]
        meta = []
        if r.chk_ids:
            meta.append(
                "Checks: "
                + ", ".join(f"<a href='{self.check_href(x, r)}'>{t(x.removeprefix('CHK-'))}</a>" for x in r.chk_ids)
            )
        loc = source_of(r)
        if loc:
            meta.append(f"<span class='mono'>{t(loc)}</span>")
        bug = self.bug_of.get(r.uid)
        if bug:
            meta.append(f"Regression check of {self.bug_ref(bug)}")
        if meta:
            out.append(f"<p class='why' style='margin-top:10px'>{' · '.join(meta)}</p>")
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

    # --- bug pages ---------------------------------------------------------------------

    def bug_page(self, bug: Bug) -> str:
        from markdown_it import MarkdownIt

        t = self.t
        text = self.red.text(bug.path.read_text(encoding="utf-8"))
        lines = text.splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        md = MarkdownIt("commonmark", {"html": False}).enable("table").enable("strikethrough")
        body = md.render("\n".join(lines))
        body = re.sub(r"<li>\[[xX]\]", "<li>☑", body)
        body = re.sub(r"<li>\[ \]", "<li>☐", body)
        # Evidence images next to the page; any other relative link points into the
        # repository, which is not published — keep its text, drop the link.
        body = re.sub(
            r'<a href="(evidence/[^"]+\.(?:png|jpe?g))">([^<]*)</a>',
            r"<a class='shot' href='\1'><img loading='lazy' src='\1' alt='\2'></a>",
            body,
        )
        body = re.sub(
            r'<img src="(evidence/[^"]+)" alt="([^"]*)"\s*/?>',
            r"<a class='shot' href='\1'><img loading='lazy' src='\1' alt='\2'></a>",
            body,
        )
        body = re.sub(r'<a href="(?!https?://|#)[^"]*">(.*?)</a>', r"\1", body, flags=re.DOTALL)
        m = next((m for m in self.modules if m.key == bug.module_dir), None)
        nav = (
            brand.brandbar("internal")
            + "<nav class='top' style='margin-top:16px'><a href='../index.html#defects'>← All open defects</a>"
        )
        if m:
            nav += f"<a href='../{m.page}'>{t(m.label)}: every check</a>"
        nav += "</nav>"
        eyebrow = f"Defect report · {t(m.label) if m else t(bug.module_dir)}"
        return (
            f"<div class='wrap'>{nav}<p class='eyebrow'>{eyebrow}</p>"
            f"<h1 style='font-size:28px;margin:8px 0 18px'>{t(bug.bug_id)} — {t(bug.title)}</h1>"
            f"<div class='md'>{body}</div></div>{LIGHTBOX}"
        )

    def bug_evidence(self, bug: Bug) -> list[Path]:
        """Screenshots under ``evidence/<BUG-ID>/`` — per platform in ``ios/`` / ``android/``."""
        folder = bug.path.parent / "evidence" / bug.bug_id
        if not folder.is_dir():
            return []
        return sorted(p for p in folder.rglob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg"))


# --------------------------------------------------------------------------- #
# Writing the site
# --------------------------------------------------------------------------- #


def write_site(report: Report, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    body = report.index()
    title = f"{(report.slice or brand.slice_(report.platform)).product_short} QA Report"
    (out_dir / "index.html").write_text(report.document(title, body), encoding="utf-8")
    stale = out_dir / "page.html"  # the single-report artifact fragment, superseded by mobile_reports.py --share
    if stale.exists():
        stale.unlink()
    for m in report.modules:
        (out_dir / m.page).write_text(
            report.document(f"{m.name} — mobile checks", report.module_page(m)), encoding="utf-8"
        )
    bugs_dir = out_dir / "bugs"
    if bugs_dir.exists() and (bugs_dir / MARKER).exists():
        shutil.rmtree(bugs_dir)  # our own previous output only
    if report.open_bugs:
        bugs_dir.mkdir(parents=True, exist_ok=True)
        (bugs_dir / MARKER).write_text("generated by automation/tools/mobile_summary.py\n")
        for bug in report.open_bugs:
            (bugs_dir / f"{bug.bug_id}.html").write_text(
                report.document(bug.bug_id, report.bug_page(bug)), encoding="utf-8"
            )
            for src in report.bug_evidence(bug):
                target = bugs_dir / "evidence" / bug.bug_id / src.relative_to(bug.path.parent / "evidence" / bug.bug_id)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
                report.red.image(target)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--allure-dir", type=Path, required=True, help="allure-results of ONE run")
    p.add_argument("--checklist", type=Path, action="append", required=True, help="repeat per module")
    p.add_argument("--run-label", default="", help="what was run (filter, suite)")
    p.add_argument("--target", default="", help="the device the run used, as the page names it")
    p.add_argument(
        "--history-dir",
        type=Path,
        action="append",
        default=[],
        help="allure-results of an earlier FULL run, oldest first (run history, stability)",
    )
    p.add_argument("--history-note", default="", help="one note under the run history table")
    p.add_argument("--note", action="append", default=[], help="a line under 'Scope of this run'")
    p.add_argument("--decision", action="append", default=[], help="a line under 'What needs a decision'")
    p.add_argument(
        "--reasons",
        type=Path,
        default=None,
        help="why checks have no automated test (markdown: a Kinds and a Checks table); "
        "default qa/mobile/<platform>/not-automated.md",
    )
    p.add_argument(
        "--manual-minutes-per-check",
        type=float,
        default=None,
        help="owner's estimate for the manual comparison; omitted = not shown",
    )
    p.add_argument("--out-dir", type=Path, default=None, help="default automation/mobile/reports/<platform>/internal")
    p.add_argument(
        "--platform",
        choices=PLATFORMS,
        default="ios",
        help="whose records the page cites (reasons, traceability, Allure); default ios",
    )
    p.add_argument(
        "--redact-env",
        type=Path,
        default=tr.REPO_ROOT / "automation" / "mobile" / ".env",
        help="dotenv whose APP_USER_EMAIL / APP_USER_PHONE are hidden on the page (values never printed)",
    )
    p.add_argument(
        "--redact-text-env",
        action="append",
        default=[],
        help="name of an environment variable whose value is hidden on the page like the test "
        "account's email (e.g. its first / last name); values never printed",
    )
    p.add_argument(
        "--public",
        action="store_true",
        help="the copy to share: text attachments (API bodies, page sources) and videos left out",
    )
    p.add_argument(
        "--redact-boxes",
        type=Path,
        default=None,
        help="JSON {points_width, boxes: {attachment source: [[x0,y0,x1,y1], ...]}} pixelated on the page copies",
    )
    p.add_argument("--no-git", action="store_true", help="skip the delivery-pace chart (no git)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.out_dir = args.out_dir or default_out(args.platform)
    args.reasons = args.reasons or default_reasons(args.platform)
    global PUBLIC
    PUBLIC = args.public
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
    extra = [os.environ.get(name, "").strip() for name in args.redact_text_env]
    redactor = Redactor(args.redact_env, args.redact_boxes, extra)
    bugs = load_bugs()
    runs = load_test_runs(args.allure_dir)
    kinds, reasons = load_reasons(args.reasons)
    history = [rec for d in args.history_dir if (rec := load_record(d, items, bugs)) is not None]
    automated_by_module: dict[str, int] = {}
    report = Report(
        runs=runs,
        rows=rows,
        summary=summary,
        env=read_environment(args.allure_dir),
        run_label=args.run_label,
        target=args.target,
        copy=AssetCopier(args.out_dir, redactor, args.allure_dir),
        now=datetime.now(UTC),
        bugs=bugs,
        kinds=kinds,
        reasons=reasons,
        history=history,
        pace=[],
        notes=args.note,
        decisions=args.decision,
        history_note=args.history_note,
        manual_minutes=args.manual_minutes_per_check,
        red=redactor,
        platform=args.platform,
        reasons_file=rel_to_repo(args.reasons),
        slice=brand.slice_(args.platform),
        tools=tool_versions(args.platform),
    )
    if not args.no_git:
        for m in report.modules:
            automated_by_module[m.label] = tr.summarize(m.rows).automated
        report.pace = load_pace(runs, automated_by_module)
        report.first_commit = _git_first_commit()
    write_site(report, args.out_dir)
    missing = [r.item.chk_id for r in rows if not r.results and r.item.chk_id not in reasons]
    if missing:
        tr.log("WARN", f"{len(missing)} checks without a test have no written reason: {missing[:10]}")
    tr.log("INFO", f"{summary.line()} -> {args.out_dir / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
