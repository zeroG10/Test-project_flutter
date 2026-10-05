"""One platform's run, read once and shared by every report that describes it.

The internal platform report (`build_summary.py`), the combined internal report (`mobile_report.py`) and the three
client reports (`client_report.py`) all read their numbers through `Platform` — built on the same
`build_summary.Report` — so an internal and a client report of one slice cannot disagree, and the combined report is
the two platforms' own numbers side by side.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from functools import cached_property
from pathlib import Path

import brand
import build_summary as bs
import trace_results as tr

SEVERITY_WORD = {"S1": "critical", "S2": "major", "S3": "minor", "S4": "cosmetic"}
SEVERITY_ORDER = {"S1": 1, "S2": 2, "S3": 3, "S4": 4}
VERDICT_RANK = {"pass": 0, "known": 1, "block": 2, "fail": 3}  # the combined verdict is the worse of the two


def checklists() -> list[Path]:
    return sorted(bs.MOBILE_QA.glob("*/*-checklist.md"))


class NoAssets:
    """The asset copier of a report that shows no screenshots (client, combined): it must never touch the assets
    folder of a platform report, which a real `AssetCopier` clears when it is made."""

    def __init__(self, source_root: Path) -> None:
        self.source_root = source_root
        self.redactor = None

    def __call__(self, source: Path) -> str:
        return ""


def load_report(key: str) -> bs.Report:
    """The platform's run as `build_summary` reads it: the slice's run and history (setup/project.yaml)."""
    slc = brand.slice_(key)
    if not slc.run or not slc.run.is_dir():
        raise FileNotFoundError(f"Blocked: no run for '{key}' (setup/project.yaml → report.slices.{key}.run)")
    results = tr.load_allure_results(slc.run)
    items = tr.parse_checklists(checklists())
    rows, _ = tr.build_rows(items, results)
    bugs = bs.load_bugs()
    kinds, reasons = bs.load_reasons(bs.default_reasons(key))
    red = bs.Redactor(tr.REPO_ROOT / "automation" / "mobile" / ".env", None)
    return bs.Report(
        runs=bs.load_test_runs(slc.run),
        rows=rows,
        summary=tr.summarize(rows),
        env=bs.read_environment(slc.run),
        run_label="",
        target="",
        copy=NoAssets(slc.run),  # type: ignore[arg-type]
        now=datetime.now(UTC),
        bugs=bugs,
        kinds=kinds,
        reasons=reasons,
        history=[r for d in slc.history if (r := bs.load_record(d, items, bugs))],
        pace=[],
        notes=[],
        decisions=[],
        history_note=slc.history_note,
        red=red,
        platform=key,
        reasons_file=bs.rel_to_repo(bs.default_reasons(key)),
        slice=slc,
    )


def bug_platforms(bug: bs.Bug) -> set[str]:
    """Where a defect was reproduced, from its report: "Platforms checked: iOS ✓ … · Android ✓ …"."""
    text = bug.path.read_text(encoding="utf-8")
    found = set(re.findall(r"(iOS|Android) ✓", text))
    if not found:
        m = re.search(r"^\| Platform \|\s*Flutter on (iOS|Android)", text, re.MULTILINE)
        found = {m.group(1)} if m else set()
    return {p.lower() for p in found}


def p0_devices(key: str) -> list[tuple[str, str, bool]]:
    """The P0 rows of `qa/shared/device-matrix/device-matrix.md` for this OS: (device, OS, covered by this run)."""
    path = tr.REPO_ROOT / "qa" / "shared" / "device-matrix" / "device-matrix.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    heading = "## iOS" if key == "ios" else "## Android"
    if heading not in text:
        return []
    section = re.split(r"^## ", text.split(heading, 1)[1], flags=re.MULTILINE)[0]
    return [row for row in _p0_rows(section)]


def _p0_rows(section: str):
    for line in section.splitlines():
        cells = [c.strip().strip("*").strip() for c in line.strip().strip("|").split("|")]
        if len(cells) > 5 and "P0" in cells:
            yield cells[0], cells[1], False


class Platform:
    """One platform's numbers, verdicts and records, as every report of the slice states them."""

    def __init__(self, key: str, report: bs.Report) -> None:
        self.key = key
        self.name = bs.PLATFORM_NAME[key]
        self.r = report
        self.slice = report.slice or brand.slice_(key)

    # --- numbers --------------------------------------------------------------------------

    @cached_property
    def c(self) -> dict[str, int]:
        return self.r.counts(self.r.rows)

    @property
    def s(self) -> tr.Summary:
        return self.r.summary

    @cached_property
    def tc(self) -> dict[str, int]:
        return self.r.test_counts()

    @cached_property
    def unexpected(self) -> int:
        return len(self.r.unexpected_tests())

    @cached_property
    def end(self) -> datetime:
        return datetime.fromtimestamp(max(x.stop_ms for x in self.r.runs) / 1000, UTC)

    @cached_property
    def start(self) -> datetime:
        first = datetime.fromtimestamp(min(x.start_ms for x in self.r.runs) / 1000, UTC)
        return min([h.finished for h in self.r.history] + [first])

    @property
    def run_date(self) -> str:
        return self.end.strftime("%Y-%m-%d")

    @cached_property
    def facts(self) -> dict[str, str]:
        return bs.run_facts(self.r.env, self.key)

    @cached_property
    def verdict_of(self) -> dict[str, str]:
        return {row.item.chk_id: self.r.verdict(row) for row in self.r.rows}

    @property
    def verdict(self) -> tuple[str, str]:
        """(label, css class): Failed when anything failed unexplained; otherwise "No unexpected failures" while
        known defects hold checks red or a test could not run (owner, 2026-09-28) — never "Passed" then."""
        if self.unexpected:
            return "Failed", "fail"
        if self.tc["Failed"] or self.tc["Blocked"]:
            return "No unexpected failures", "known"
        return "Passed", "pass"

    # --- defects ------------------------------------------------------------------------

    @cached_property
    def bugs(self) -> list[bs.Bug]:
        """Open defects reproduced on this platform (or holding one of its checks red)."""
        held = {b.bug_id for b in self.r.bug_of.values() if b}
        return [b for b in self.r.open_bugs if self.key in bug_platforms(b) or b.bug_id in held]

    @property
    def accepted(self) -> list[bs.Bug]:
        """Drafts the owner decided not to file whose tests stay red in this run."""
        return list(self.r.known_drafts)

    @cached_property
    def held_by_bugs(self) -> set[str]:
        return {b.bug_id for b in self.r.bug_of.values() if b and b.filed}

    @property
    def blocked(self) -> list[bs.TestRun]:
        return [x for x in self.r.runs if x.status == "Blocked"]

    def kind_counts(self) -> dict[str, int]:
        """Not-automated checks per reason kind (the records' `Kind` keys)."""
        counts: dict[str, int] = {}
        for row in self.r.rows:
            if self.verdict_of[row.item.chk_id] == "Not automated":
                reason = self.r.reasons.get(row.item.chk_id)
                kind = reason.kind if reason else ""
                counts[kind] = counts.get(kind, 0) + 1
        return counts

    def client_groups(self) -> dict[str, int]:
        groups: dict[str, int] = {}
        for kind, n in self.kind_counts().items():
            g = brand.CLIENT_GROUPS.get(kind, "Other")
            groups[g] = groups.get(g, 0) + n
        return groups

    def p0(self) -> list[tuple[str, str, bool]]:
        """P0 devices of the matrix and whether this run covered them (device name and OS version match)."""
        device = self.facts["device"].split(" — ")[0]
        os_version = re.sub(r"^(iOS|Android)\s*", "", self.facts["os"].split(" · ")[0])
        return [(d, o, d == device and o == os_version) for d, o, _ in p0_devices(self.key)]


def worst(platforms: list[Platform]) -> tuple[str, str]:
    return max((p.verdict for p in platforms), key=lambda v: VERDICT_RANK[v[1]])


def passed_on_both(a: Platform, b: Platform, chks: list[str] | None = None) -> int:
    ids = chks if chks is not None else list(a.verdict_of)
    return sum(1 for k in ids if a.verdict_of.get(k) == "Passed" and b.verdict_of.get(k) == "Passed")


def day(d: datetime) -> str:
    return d.strftime("%-d %B %Y")


def cycle(start: datetime, end: datetime) -> str:
    if start.date() == end.date():
        return day(end)
    if start.month == end.month and start.year == end.year:
        return f"{start.day}–{day(end)}"
    return f"{start:%-d %B} – {day(end)}"


def pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.0f}%" if whole else "0%"


def without_tc(title: str) -> str:
    """A test's title without its test-case id — the client reads the behaviour, not our numbering."""
    return re.sub(r"^TC-[A-Z]+-\d+[a-z]?\s+", "", title)
