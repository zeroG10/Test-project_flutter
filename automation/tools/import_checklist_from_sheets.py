#!/usr/bin/env python3
"""One-time, READ-ONLY import of a Google Sheet checklist into per-feature markdown.

This script is the inverse of ``sync_checklist_to_sheets.py`` for exactly one
situation: a checklist that was born in a Google Sheet (no ``CHK-`` IDs yet)
must become markdown so that markdown can be the source of truth from then on.

Read-only guarantee
-------------------
The only Sheets calls made are ``open_by_key``, ``get_worksheet_by_id``,
``get_all_values`` and reading titles. Nothing is ever written to the Sheet —
``sync_checklist_to_sheets.py`` remains the single writer (``CLAUDE.md``,
"Checklist → Google Sheets: single writer"). The service-account JSON is loaded
to authenticate and never printed.

One-time per feature
--------------------
IDs (``CHK-<CODE>-NNN``) are assigned fresh at import, in sheet order, and become
the contract between the markdown, the Sheet's hidden ID column and the
automated-test tags. Re-importing a feature would renumber every check, so the
script refuses to overwrite an existing output file unless ``--force`` is given
explicitly. After the import, evolve the markdown by hand and publish with the
sync script; never run this importer again for that feature.

Sheet layout understood (rows 1-4 are the header, data from row 5)
------------------------------------------------------------------
- Column A = TASK, column B = check text / group header. Every other column
  (browser statuses, counters, comments) is ignored — statuses are NOT used to
  classify rows because teams fill them on header rows too.
- ``A filled, B empty``   → feature block start when A (stripped, case-insensitive)
  is a feature in the module map; otherwise a screen with no group (WARN).
- ``A filled, B filled``  → new screen A; B is either the first group name of
  that screen or its first check (see the heuristic below).
- ``A empty,  B filled``  → a group header (screen unchanged) or a check.
- ``A empty,  B empty``   → skipped and counted, whatever the status cells hold.

Group-header heuristic: a B cell is a group header when it does NOT start with a
check verb (``Check`` / ``Verify`` / ``Ensure`` / ``Make sure`` / ``Confirm`` /
``Validate`` / ``Test``), does NOT end with ``.`` and is at most
``GROUP_MAX_LEN`` characters. Everything else is a check. Ambiguous cells are
reported as warnings so a human can eyeball them in ``--dry-run``.

Output format (what ``sync_checklist_to_sheets.parse_markdown`` reads)::

    # QA Checklist: Authentication

    > Source: Google Sheet `Check-list` (copy of "..."), imported ... never renumber.

    ## Login page / General

    1. [CHK-AUTH-001] Check that the "Log in" title is displayed.

Section heading = ``<Screen> / <Group>``; ``<Screen>`` alone when the screen row
carried a check instead of a group; ``<Group>`` alone when the feature has no
screen rows. Item numbers restart per section; IDs never do.

Usage::

    uv run python import_checklist_from_sheets.py --sheet-id ID --gid GID \\
        --out-root ../../qa/web [--feature NAME ...] [--dry-run] [--force]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import gspread
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent  # automation/tools -> repo root

HEADER_ROWS = 4
DATA_START_ROW = HEADER_ROWS + 1
COL_TASK = 0   # A (0-based)
COL_CHECK = 1  # B (0-based)

# Cells that start with one of these are always checks, never group headers.
CHECK_VERB_RE = re.compile(
    r"^(check|verify|ensure|make sure|confirm|validate|test)\b", re.IGNORECASE
)
GROUP_MAX_LEN = 80
FEATURE_CODE_RE = re.compile(r"^[A-Z]{2,5}$")

# Section names the sync parser silently drops — refuse to emit them.
SYNC_SKIP_SECTIONS = {"open questions"}
SYNC_SKIP_PREFIX = "coverage"

SCRIPT_REL = "automation/tools/import_checklist_from_sheets.py"


def log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}")


# --------------------------------------------------------------------------- #
# Module map: feature name in the sheet → output folder / slug / feature code
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Module:
    feature: str   # display name, exactly as the sheet spells it (stripped)
    folder: str    # NN-slug folder under --out-root
    code: str      # CHK-<code>-NNN

    @property
    def slug(self) -> str:
        return re.sub(r"^\d+-", "", self.folder)

    @property
    def filename(self) -> str:
        return f"{self.slug}-checklist.md"

    @property
    def key(self) -> str:
        return normalize_key(self.feature)


# No built-in map: the features of the product under test are not known to the template.
# Pass one --module-map entry per feature in the sheet, with the codes registered in
# qa/shared/feature-codes.md — the script refuses to guess folders or codes.
DEFAULT_MODULE_MAP: tuple[Module, ...] = ()


def normalize_key(name: str) -> str:
    """Feature-name matching key: trimmed, inner whitespace collapsed, case-folded."""
    return " ".join(name.split()).casefold()


def parse_module_map_entry(entry: str) -> Module:
    """``"Order list=07-order-list:ORD"`` → Module. Fails loudly on bad shape."""
    if "=" not in entry or ":" not in entry.split("=", 1)[1]:
        raise SystemExit(
            f"--module-map entry {entry!r}: expected 'Feature name=NN-slug:CODE'."
        )
    feature, rest = entry.split("=", 1)
    folder, code = rest.rsplit(":", 1)
    feature, folder, code = feature.strip(), folder.strip(), code.strip().upper()
    if not feature or not folder:
        raise SystemExit(f"--module-map entry {entry!r}: empty feature or folder.")
    if not FEATURE_CODE_RE.match(code):
        raise SystemExit(
            f"--module-map entry {entry!r}: code {code!r} must be 2-5 uppercase letters."
        )
    return Module(feature, folder, code)


def build_module_map(entries: list[str] | None) -> dict[str, Module]:
    modules = tuple(parse_module_map_entry(e) for e in entries) if entries else DEFAULT_MODULE_MAP
    if not modules:
        raise SystemExit(
            "No module map: pass --module-map 'Feature name=NN-slug:CODE' once per feature in "
            "the sheet (codes from qa/shared/feature-codes.md). Nothing is guessed."
        )
    mapping: dict[str, Module] = {}
    codes: dict[str, str] = {}
    for m in modules:
        if m.key in mapping:
            raise SystemExit(f"Module map: feature {m.feature!r} listed twice.")
        if m.code in codes:
            raise SystemExit(
                f"Module map: code {m.code} used by both {codes[m.code]!r} and {m.feature!r}."
            )
        mapping[m.key] = m
        codes[m.code] = m.feature
    return mapping


# --------------------------------------------------------------------------- #
# Grid → structure
# --------------------------------------------------------------------------- #

@dataclass
class Check:
    row: int          # 1-based sheet row, for diagnostics only
    text: str


@dataclass
class Section:
    screen: str | None
    group: str | None
    checks: list[Check] = field(default_factory=list)

    def heading(self, fallback: str) -> str:
        if self.screen and self.group:
            return f"{self.screen} / {self.group}"
        return self.screen or self.group or fallback


@dataclass
class FeatureBlock:
    module: Module
    start_row: int
    sections: list[Section] = field(default_factory=list)

    @property
    def checks(self) -> list[Check]:
        return [c for s in self.sections for c in s.checks]

    @property
    def screens(self) -> list[str]:
        seen: list[str] = []
        for s in self.sections:
            if s.screen and s.screen not in seen:
                seen.append(s.screen)
        return seen

    @property
    def groups(self) -> int:
        return sum(1 for s in self.sections if s.group)


@dataclass
class ParseReport:
    blocks: list[FeatureBlock]
    warnings: list[str]
    empty_rows: int = 0
    empty_rows_with_status: int = 0
    rows_before_first_feature: int = 0


def normalize_text(cell: str) -> str:
    """Trim, and collapse internal line breaks (with surrounding blanks) to one
    space. Nothing else is touched — wording stays verbatim."""
    return re.sub(r"[ \t]*[\r\n]+[ \t]*", " ", cell).strip()


def is_group_header(text: str) -> bool:
    return (
        not CHECK_VERB_RE.match(text)
        and not text.endswith(".")
        and len(text) <= GROUP_MAX_LEN
    )


def parse_grid(rows: list[list[str]], module_map: dict[str, Module]) -> ParseReport:
    """Classify every data row (from row 5) and group checks into
    feature → section (screen / group) → checks, preserving sheet order."""
    report = ParseReport(blocks=[], warnings=[])
    block: FeatureBlock | None = None
    section: Section | None = None
    screen: str | None = None

    def open_section(new_screen: str | None, new_group: str | None) -> Section:
        assert block is not None
        sec = Section(screen=new_screen, group=new_group)
        block.sections.append(sec)
        return sec

    for idx in range(HEADER_ROWS, len(rows)):
        row_no = idx + 1
        raw = list(rows[idx]) + [""] * (COL_CHECK + 1 - len(rows[idx]))
        task = normalize_text(raw[COL_TASK])
        text = normalize_text(raw[COL_CHECK])
        other_cells = any(str(c).strip() for c in raw[COL_CHECK + 1:])

        if not task and not text:
            report.empty_rows += 1
            if other_cells:
                report.empty_rows_with_status += 1
                report.warnings.append(
                    f"row {row_no}: no text in A/B but other cells filled — skipped."
                )
            continue

        # Feature block start: A filled, B empty, A is a known feature.
        if task and not text and normalize_key(task) in module_map:
            module = module_map[normalize_key(task)]
            if any(b.module.key == module.key for b in report.blocks):
                report.warnings.append(
                    f"row {row_no}: feature {module.feature!r} appears twice — "
                    "rows are appended to the first block."
                )
                block = next(b for b in report.blocks if b.module.key == module.key)
            else:
                block = FeatureBlock(module=module, start_row=row_no)
                report.blocks.append(block)
            section = None
            screen = None
            continue

        if block is None:
            report.rows_before_first_feature += 1
            continue

        if task and not text:
            # A-only row that is not a feature: treat as a screen without a group.
            report.warnings.append(
                f"row {row_no}: A={task!r} is not in the module map — treated as a screen."
            )
            screen = task
            section = open_section(screen, None)
            continue

        if task:
            # A+B row: new screen; B is its first group or its first check.
            screen = task
            if is_group_header(text):
                section = open_section(screen, text)
                continue
            section = open_section(screen, None)
        elif is_group_header(text):
            section = open_section(screen, text)
            continue

        # A check.
        if len(text) > GROUP_MAX_LEN and not CHECK_VERB_RE.match(text) and not text.endswith("."):
            report.warnings.append(
                f"row {row_no}: verb-less text longer than {GROUP_MAX_LEN} chars treated "
                f"as a check: {text[:60]!r}…"
            )
        if section is None:
            report.warnings.append(
                f"row {row_no}: check before any screen/group in {block.module.feature!r} — "
                f"section falls back to the feature name."
            )
            section = open_section(None, None)
        section.checks.append(Check(row=row_no, text=text))

    # Post-checks per feature.
    for b in report.blocks:
        seen_headings: dict[str, int] = {}
        seen_texts: dict[str, int] = {}
        for s in b.sections:
            h = s.heading(b.module.feature)
            if not s.checks:
                report.warnings.append(
                    f"{b.module.feature}: section {h!r} has no checks — not emitted."
                )
                continue
            seen_headings[h] = seen_headings.get(h, 0) + 1
            for c in s.checks:
                seen_texts[c.text] = seen_texts.get(c.text, 0) + 1
        for h, n in seen_headings.items():
            if n > 1:
                report.warnings.append(
                    f"{b.module.feature}: heading {h!r} occurs {n} times (kept as-is)."
                )
        for t, n in seen_texts.items():
            if n > 1:
                report.warnings.append(
                    f"{b.module.feature}: identical check text {n}x (kept verbatim, "
                    f"distinct IDs): {t[:70]!r}"
                )
        if not b.checks:
            report.warnings.append(f"{b.module.feature}: feature block has zero checks.")
    return report


# --------------------------------------------------------------------------- #
# Structure → markdown
# --------------------------------------------------------------------------- #

def source_note(ws_title: str, source_title: str, sheet_id: str, gid: int, today: date) -> str:
    return (
        f"Source: Google Sheet `{ws_title}` (copy of \"{source_title}\"), "
        f"spreadsheet id `{sheet_id}` gid `{gid}`, imported {today.isoformat()} by "
        f"{SCRIPT_REL}. IDs assigned at import; they are now the contract — never renumber."
    )


def render_markdown(block: FeatureBlock, note: str) -> str:
    """Render one feature block in the exact shape ``parse_markdown`` reads."""
    code = block.module.code
    lines = [f"# QA Checklist: {block.module.feature}", "", f"> {note}", ""]
    next_id = 0
    for sec in block.sections:
        if not sec.checks:
            continue
        heading = sec.heading(block.module.feature)
        h_lc = heading.lower().strip()
        if h_lc in SYNC_SKIP_SECTIONS or h_lc.startswith(SYNC_SKIP_PREFIX):
            raise SystemExit(
                f"{block.module.feature}: section heading {heading!r} would be dropped by "
                "sync_checklist_to_sheets.parse_markdown — rename the group in the sheet "
                "copy or handle it by hand."
            )
        lines += [f"## {heading}", ""]
        for i, chk in enumerate(sec.checks, 1):
            next_id += 1
            lines.append(f"{i}. [CHK-{code}-{next_id:03d}] {chk.text}")
        lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Sheets access — READ ONLY
# --------------------------------------------------------------------------- #

def fetch_grid(sheet_id: str, gid: int, creds_path: Path) -> tuple[str, str, list[list[str]]]:
    """Return (spreadsheet title, worksheet title, all cell values). Read-only."""
    gc = gspread.service_account(filename=str(creds_path))
    sh = gc.open_by_key(sheet_id)
    ws = sh.get_worksheet_by_id(gid)
    return sh.title, ws.title, ws.get_all_values()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def summarize(report: ParseReport) -> None:
    log("INFO", f"{'feature':<20} {'screens':>7} {'groups':>6} {'sections':>8} {'checks':>6}   file")
    total = 0
    for b in report.blocks:
        emitted = [s for s in b.sections if s.checks]
        total += len(b.checks)
        log("INFO", f"{b.module.feature:<20} {len(b.screens):>7} {b.groups:>6} "
            f"{len(emitted):>8} {len(b.checks):>6}   {b.module.folder}/{b.module.filename}")
    log("INFO", f"{'TOTAL':<20} {'':>7} {'':>6} {'':>8} {total:>6}")
    log("INFO", f"Empty rows skipped: {report.empty_rows} "
        f"(of which {report.empty_rows_with_status} carried status cells); "
        f"rows before the first feature: {report.rows_before_first_feature}.")
    for w in report.warnings:
        log("WARN", w)


def main(argv: list[str] | None = None, fetch=fetch_grid) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--sheet-id", required=True, help="Spreadsheet id from the Sheet URL")
    parser.add_argument("--gid", required=True, type=int, help="Worksheet gid from the Sheet URL")
    parser.add_argument("--out-root", required=True,
                        help="Folder that holds the NN-slug module folders (e.g. qa/web)")
    parser.add_argument("--feature", action="append", metavar="NAME",
                        help="Import only this feature (repeatable). Default: all in the map.")
    parser.add_argument("--module-map", action="append", metavar="FEATURE=NN-slug:CODE",
                        help="Feature → folder/code map, one entry per feature in the sheet "
                             "(repeatable, REQUIRED); codes from qa/shared/feature-codes.md.")
    parser.add_argument("--source-title", default=None,
                        help="Title quoted in the Source note (default: the spreadsheet title).")
    parser.add_argument("--credentials", default=None,
                        help="Service-account JSON (default: $CREDENTIALS_FILE or "
                             ".secrets/credentials.json next to this script).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the per-feature summary and warnings; write nothing.")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing output files (renumbers their IDs!).")
    args = parser.parse_args(argv)

    load_dotenv()
    load_dotenv(SCRIPT_DIR / ".env", override=False)
    creds = Path(args.credentials or os.environ.get("CREDENTIALS_FILE", ".secrets/credentials.json"))
    if not creds.is_absolute():
        creds = (SCRIPT_DIR / creds).resolve()
    if not creds.is_file():
        raise SystemExit(f"Credentials file not found: {creds}")

    module_map = build_module_map(args.module_map)
    selected: set[str] | None = None
    if args.feature:
        selected = set()
        for name in args.feature:
            key = normalize_key(name)
            if key not in module_map:
                raise SystemExit(
                    f"--feature {name!r} is not in the module map "
                    f"({', '.join(m.feature for m in module_map.values())})."
                )
            selected.add(key)

    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = (Path.cwd() / out_root).resolve()

    log("INFO", f"Reading sheet {args.sheet_id} gid={args.gid} (read-only)")
    sh_title, ws_title, rows = fetch(args.sheet_id, args.gid, creds)
    log("INFO", f"Spreadsheet={sh_title!r} Worksheet={ws_title!r} rows={len(rows)}")
    if len(rows) <= HEADER_ROWS:
        raise SystemExit("Sheet has no data rows below the header — nothing to import.")

    report = parse_grid(rows, module_map)
    found = {b.module.key for b in report.blocks}
    for m in module_map.values():
        if m.key not in found and (selected is None or m.key in selected):
            report.warnings.append(f"feature {m.feature!r} from the module map not found in the sheet.")
    if selected is not None:
        report.blocks = [b for b in report.blocks if b.module.key in selected]
    summarize(report)

    if not report.blocks or not any(b.checks for b in report.blocks):
        log("ERROR", "No checks parsed — an empty import is not a successful import.")
        return 1

    if args.dry_run:
        log("INFO", "[dry-run] nothing written.")
        return 0

    targets = [(b, out_root / b.module.folder / b.module.filename) for b in report.blocks if b.checks]
    existing = [p for _, p in targets if p.exists()]
    if existing and not args.force:
        raise SystemExit(
            "Refusing to overwrite existing checklist file(s):\n  "
            + "\n  ".join(str(p) for p in existing)
            + "\nThose files may already carry CHK IDs that live in the team Sheet and in "
              "automated-test tags; re-importing would renumber them and break that "
              "contract. Evolve the markdown by hand instead. Pass --force only if you "
              "are certain no ID from these files is in use anywhere."
        )
    if existing:
        log("WARN", f"--force: overwriting {len(existing)} existing file(s); their IDs are renumbered.")

    note = source_note(ws_title, args.source_title or sh_title, args.sheet_id, args.gid, date.today())
    for block, path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_markdown(block, note), encoding="utf-8")
        log("INFO", f"Wrote {path} ({len(block.checks)} checks, CHK-{block.module.code}-001..-{len(block.checks):03d})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
