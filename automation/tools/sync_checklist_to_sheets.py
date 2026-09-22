#!/usr/bin/env python3
"""Sync a QA checklist markdown file into a Google Sheet idempotently.

Preserves manually-entered status columns and comments. Uses stable check IDs
(hidden column, per-target) to match rows across syncs and an Obsolete flag in
the adjacent column to mark checks that no longer exist in the .md source.

Per-target layouts (sheet id + worksheet name + ID col + Obsolete col) are
configured in .env via WEB_* and MOBILE_* presets. Select with --target {web,mobile},
or omit it and let the checklist path decide: ``qa/web/<NN-module>/…`` and
``qa/shared/…`` -> web, ``qa/mobile/<NN-module>/…`` -> mobile. A path that names
neither platform is an error, never a silent default.

Usage:
    uv run python sync_checklist_to_sheets.py ../../qa/web/01-authentication/authentication-checklist.md --dry-run
    uv run python sync_checklist_to_sheets.py --target mobile <path-to-md> [--dry-run]
    uv run python sync_checklist_to_sheets.py --target web <path-to-md> --feature-code AUTH

Feature codes
-------------
Every check ID is ``CHK-<FEATURE>-<NNN>``. The feature code is resolved, in order:

1. ``--feature-code CODE`` on the command line (2-5 uppercase letters);
2. the project registry ``qa/shared/feature-codes.md`` (path relative to the
   repo root; the file is optional). It is a markdown table::

       | slug | code | platform/notes |
       |---|---|---|
       | authentication | AUTH | web + mobile (separate sheets) |
       | order-list | ORDL | mobile |

   ``slug`` is the checklist filename stem with a leading ``checklist-`` or a
   trailing ``-checklist`` removed (``checklist-order-list.md`` and
   ``order-list-checklist.md`` both map to slug ``order-list``). Header and
   ``|---|`` separator rows are ignored; the third column is free text;
3. fallback: the first 4 letters of the slug, uppercased (``order-list`` ->
   ``ORDE``), with a WARN so the code can be pinned in the registry before the
   first non-dry-run sync. Changing a code after rows exist in the Sheet
   orphans every row of that feature, so pin codes early.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import gspread
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent  # automation/tools -> repo root

# Project-level registry of checklist slug → feature code (see module docstring).
# Optional; when absent every code comes from --feature-code or the fallback rule.
FEATURE_CODES_FILE = REPO_ROOT / "qa" / "shared" / "feature-codes.md"

# Built-in slug → code map. Intentionally EMPTY in the template: project codes
# live in qa/shared/feature-codes.md, never in this script.
DEFAULT_FEATURE_PREFIX_MAP: dict[str, str] = {}

FEATURE_CODE_RE = re.compile(r"^[A-Z]{2,5}$")

HEADER_ROWS = 4
DATA_START_ROW = 5

# Column indices (1-based) — fixed across all targets
COL_TASK = 1   # A
COL_CHECK = 2  # B

SKIP_SECTIONS = {"open questions"}


def log(level: str, msg: str) -> None:
    print(f"[{level}] {msg}")


def letter_to_col(letter: str) -> int:
    """Convert column letter(s) to a 1-based column index. 'A'→1, 'O'→15, 'AA'→27."""
    letter = letter.strip().upper()
    if not letter or not letter.isalpha():
        raise SystemExit(f"Invalid column letter: {letter!r}")
    n = 0
    for ch in letter:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n


# --------------------------------------------------------------------------- #
# Target config
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class TargetConfig:
    name: str           # "web" | "mobile"
    sheet_id: str
    worksheet: str
    id_col: int         # 1-based
    obsolete_col: int   # 1-based (must == id_col + 1)

    @property
    def matrix_width(self) -> int:
        return self.obsolete_col


def load_target_config(target: str) -> TargetConfig:
    prefix = target.upper()
    sheet_id = os.environ.get(f"{prefix}_SHEET_ID")
    worksheet = os.environ.get(f"{prefix}_WORKSHEET")
    id_letter = os.environ.get(f"{prefix}_ID_COL")
    obs_letter = os.environ.get(f"{prefix}_OBSOLETE_COL")
    missing = [k for k, v in {
        f"{prefix}_SHEET_ID": sheet_id,
        f"{prefix}_WORKSHEET": worksheet,
        f"{prefix}_ID_COL": id_letter,
        f"{prefix}_OBSOLETE_COL": obs_letter,
    }.items() if not v]
    if missing:
        raise SystemExit(f"Missing env vars for target '{target}': {', '.join(missing)}")
    id_col = letter_to_col(id_letter)
    obsolete_col = letter_to_col(obs_letter)
    if obsolete_col != id_col + 1:
        raise SystemExit(
            f"Target '{target}': Obsolete col ({obs_letter}={obsolete_col}) must be "
            f"immediately after ID col ({id_letter}={id_col})."
        )
    return TargetConfig(
        name=target,
        sheet_id=sheet_id,
        worksheet=worksheet,
        id_col=id_col,
        obsolete_col=obsolete_col,
    )


# --------------------------------------------------------------------------- #
# Markdown parsing
# --------------------------------------------------------------------------- #

@dataclass
class CheckItem:
    section: str
    check_id: str | None
    text: str


@dataclass
class ParsedChecklist:
    feature_code: str
    display_name: str
    items: list[CheckItem]


# Canonical CHK id — the same pattern as trace_results.CHK_ID_PATTERN and the
# collection-time check in automation/{api,mobile}/conftest.py (automation/README.md → IDs).
_NUM_LINE_RE = re.compile(r"^\d+\.\s*(?:\[(CHK-[A-Z]{2,5}-\d{3,})\]\s*)?(.*)$")


def normalize_slug(name: str) -> str:
    """Filename / registry entry → slug: lower-case, no ``.md``, no ``checklist``
    affix. ``Checklist-Order-List.md`` → ``order-list``; ``order-list-checklist`` →
    ``order-list``."""
    slug = name.strip().strip("`").lower()
    slug = slug.removesuffix(".md")
    slug = slug.removeprefix("checklist-")
    slug = slug.removesuffix("-checklist")
    return slug


def validate_feature_code(code: str, origin: str) -> str:
    code = code.strip().strip("`").upper()
    if not FEATURE_CODE_RE.match(code):
        raise SystemExit(
            f"Invalid feature code {code!r} from {origin}: expected 2-5 uppercase letters."
        )
    return code


def derive_target(md_path: Path) -> str | None:
    """Infer the Sheets target from where the checklist lives.

    ``qa/web/<NN-module>/<module>-checklist.md`` and ``qa/shared/…`` -> ``"web"``;
    ``qa/mobile/<NN-module>/…`` -> ``"mobile"``. The platform is the segment right
    after the last ``qa`` folder in the path (so a repo checked out under a folder
    named ``qa`` or ``web`` does not fool it). Returns ``None`` when the path names
    neither platform — the caller must ask, never default.
    """
    parts = [p.lower() for p in Path(md_path).parts[:-1]]
    if "qa" in parts:
        idx = len(parts) - 1 - parts[::-1].index("qa")
        platform = parts[idx + 1] if idx + 1 < len(parts) else ""
    else:
        platform = next((p for p in reversed(parts) if p in ("web", "mobile")), "")
    if platform in ("web", "shared"):
        return "web"
    if platform == "mobile":
        return "mobile"
    return None


def parse_feature_codes(path: Path) -> dict[str, str]:
    """Parse ``qa/shared/feature-codes.md`` (``| slug | code | notes |`` table).

    Returns ``{slug: CODE}``. A missing file yields an empty map (the file is
    optional). Malformed codes and conflicting duplicate slugs fail loudly —
    a wrong code silently orphans every Sheet row of that feature.
    """
    mapping: dict[str, str] = {}
    if not path.is_file():
        return mapping
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        slug_cell, code_cell = cells[0], cells[1]
        if not slug_cell or set(slug_cell) <= set("-: "):
            continue  # |---|---| separator row
        if slug_cell.lower().strip("`") in {"slug", "feature", "checklist"}:
            continue  # header row
        if not code_cell:
            continue
        slug = normalize_slug(slug_cell)
        code = validate_feature_code(code_cell, f"{path}:{lineno}")
        if slug in mapping and mapping[slug] != code:
            raise SystemExit(
                f"{path}:{lineno}: slug '{slug}' mapped to both "
                f"'{mapping[slug]}' and '{code}'."
            )
        mapping[slug] = code
    return mapping


def load_feature_codes(path: Path = FEATURE_CODES_FILE) -> dict[str, str]:
    """Registry map merged over the (empty) built-in defaults, with logging."""
    merged = dict(DEFAULT_FEATURE_PREFIX_MAP)
    if path.is_file():
        registry = parse_feature_codes(path)
        merged.update(registry)
        log("INFO", f"Loaded {len(registry)} feature code(s) from {path}")
    else:
        log("INFO", f"No feature-code registry at {path}; using --feature-code or "
            "the filename fallback (first 4 letters).")
    return merged


def derive_feature_code(
    md_path: Path,
    feature_map: dict[str, str] | None = None,
    override: str | None = None,
) -> str:
    """Resolve the feature code: --feature-code > registry map > filename fallback."""
    if override:
        return validate_feature_code(override, "--feature-code")
    feature_map = DEFAULT_FEATURE_PREFIX_MAP if feature_map is None else feature_map
    slug = normalize_slug(md_path.stem)  # "authentication-checklist" -> "authentication"
    if slug in feature_map:
        return feature_map[slug]
    # Fallback: first 4 letters uppercased
    fallback = re.sub(r"[^A-Za-z]", "", slug)[:4].upper()
    if not fallback:
        raise SystemExit(f"Cannot derive feature code from filename: {md_path.name}")
    log("WARN", f"No feature mapping for '{slug}' in {FEATURE_CODES_FILE.name}, "
        f"falling back to '{fallback}' — pin it in the registry or pass --feature-code.")
    return fallback


def parse_markdown(
    md_path: Path,
    feature_map: dict[str, str] | None = None,
    feature_code_override: str | None = None,
) -> ParsedChecklist:
    feature_code = derive_feature_code(md_path, feature_map, feature_code_override)
    display_name = md_path.stem.replace("-", " ").title()
    items: list[CheckItem] = []
    current_section: str | None = None
    skipping = False

    for raw in md_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()

        if line.startswith("# ") and not line.startswith("## "):
            # H1: "# QA Checklist: Authentication"
            h1 = line[2:].strip()
            if ":" in h1:
                display_name = h1.split(":", 1)[1].strip()
            else:
                display_name = h1
            continue

        if line.startswith("## "):
            section = line[3:].strip()
            section_lc = section.lower().strip()
            # Skip Open Questions and Coverage summary
            if section_lc in SKIP_SECTIONS or section_lc.startswith("coverage"):
                skipping = True
                current_section = None
            else:
                skipping = False
                current_section = section
            continue

        if skipping or current_section is None:
            continue

        # "**Coverage summary:** ..." can appear without a heading
        if line.lstrip().startswith("**Coverage"):
            skipping = True
            current_section = None
            continue

        m = _NUM_LINE_RE.match(line.strip())
        if not m:
            continue
        check_id = m.group(1)
        text = m.group(2).strip().rstrip(".").strip()
        if not text:
            continue
        items.append(CheckItem(section=current_section, check_id=check_id, text=text))

    # Fail loudly on duplicate IDs in the .md
    seen: dict[str, int] = {}
    for it in items:
        if it.check_id is None:
            continue
        seen[it.check_id] = seen.get(it.check_id, 0) + 1
    dups = [k for k, v in seen.items() if v > 1]
    if dups:
        raise SystemExit(f"Duplicate IDs in {md_path.name}: {dups}")

    return ParsedChecklist(feature_code=feature_code, display_name=display_name, items=items)


def assign_missing_ids(parsed: ParsedChecklist, existing_max: int) -> int:
    """Mutate parsed.items in place, assigning new IDs starting after existing_max.
    Returns the count of newly assigned IDs."""
    next_num = existing_max + 1
    assigned = 0
    used = {it.check_id for it in parsed.items if it.check_id}
    for it in parsed.items:
        if it.check_id:
            continue
        while True:
            candidate = f"CHK-{parsed.feature_code}-{next_num:03d}"
            next_num += 1
            if candidate not in used:
                used.add(candidate)
                it.check_id = candidate
                assigned += 1
                break
    return assigned


# --------------------------------------------------------------------------- #
# Sheet sync
# --------------------------------------------------------------------------- #

@dataclass
class SheetRow:
    row_idx: int            # 1-based sheet row
    task: str               # col A
    check_text: str         # col B
    check_id: str           # ID col (per target)
    obsolete: str           # Obsolete col (per target)

    @property
    def is_feature_header(self) -> bool:
        return self.check_id.startswith("FEAT-")


def load_sheet_rows(values: list[list[str]], cfg: TargetConfig) -> list[SheetRow]:
    """values: rows from data zone (row 5 onward), padded to cfg.matrix_width cols.

    ID col is at cfg.id_col (1-based) → index cfg.id_col - 1.
    Obsolete col is at cfg.obsolete_col (1-based) → index cfg.obsolete_col - 1.
    """
    width = cfg.matrix_width
    id_idx0 = cfg.id_col - 1
    obs_idx0 = cfg.obsolete_col - 1
    rows: list[SheetRow] = []
    for i, raw in enumerate(values):
        row = list(raw) + [""] * (width - len(raw))
        # skip fully-empty trailing rows
        if not any((row[0], row[1], row[id_idx0], row[obs_idx0])):
            continue
        rows.append(
            SheetRow(
                row_idx=DATA_START_ROW + i,
                task=str(row[0] or ""),
                check_text=str(row[1] or ""),
                check_id=str(row[id_idx0] or "").strip(),
                obsolete=str(row[obs_idx0] or "").strip(),
            )
        )
    return rows


def find_feature_header(sheet_rows: list[SheetRow], feature_code: str) -> SheetRow | None:
    target_id = f"FEAT-{feature_code}"
    for r in sheet_rows:
        if r.check_id == target_id:
            return r
    return None


def max_existing_id_for_feature(sheet_rows: list[SheetRow], feature_code: str) -> int:
    pat = re.compile(rf"^CHK-{re.escape(feature_code)}-(\d+)$")
    mx = 0
    for r in sheet_rows:
        m = pat.match(r.check_id)
        if m:
            mx = max(mx, int(m.group(1)))
    return mx


def col_letter(n: int) -> str:
    s = ""
    while n:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s


def build_plan(
    parsed: ParsedChecklist,
    sheet_rows: list[SheetRow],
    cfg: TargetConfig,
):
    """Return (updates, appends, obsolete_marks, warnings).

    updates: list of (row_idx, col_idx, value) for text-mismatch / obsolete-clear fixes.
    appends: list of (section, check_id, text) to append at end of sheet (grouped).
    obsolete_marks: list of row_idx to mark obsolete (Obsolete col = '1').
    """
    by_id: dict[str, SheetRow] = {}
    for r in sheet_rows:
        if not r.check_id:
            continue
        if r.check_id in by_id:
            log("WARN", f"Duplicate ID {r.check_id} in sheet at rows "
                f"{by_id[r.check_id].row_idx} and {r.row_idx}; using first.")
            continue
        by_id[r.check_id] = r

    md_ids = {it.check_id for it in parsed.items}
    updates: list[tuple[int, int, str]] = []
    appends: list[CheckItem] = []
    obsolete_marks: list[int] = []
    warnings: list[str] = []

    # Build a quick lookup of section per sheet row via "current section" scan.
    # Feature header rows (ID col = FEAT-...) are NOT subsections; skip them.
    section_at: dict[int, str] = {}
    current = ""
    for r in sheet_rows:
        if r.is_feature_header:
            current = ""
            section_at[r.row_idx] = ""
            continue
        # New layout: group name on its own row inside the checklist column (B),
        # with no check ID. This row is the header, not a check.
        if not r.check_id and r.check_text.strip():
            current = r.check_text.strip()
            section_at[r.row_idx] = ""
            continue
        # Legacy layout: group name in column A on the first check's row.
        if r.task.strip():
            current = r.task.strip()
        section_at[r.row_idx] = current

    for it in parsed.items:
        assert it.check_id is not None
        existing = by_id.get(it.check_id)
        if existing is None:
            appends.append(it)
            continue
        # Text mismatch?
        if existing.check_text.strip() != it.text.strip():
            updates.append((existing.row_idx, COL_CHECK, it.text))
        # Obsolete flag was set but now reappears in .md → clear it
        if existing.obsolete:
            updates.append((existing.row_idx, cfg.obsolete_col, ""))
        # Section moved? warn only (don't move row, would destroy statuses)
        cur_section = section_at.get(existing.row_idx, "").lower().strip()
        if cur_section and cur_section != it.section.lower().strip():
            warnings.append(
                f"{it.check_id} moved section in .md "
                f"('{cur_section}' → '{it.section}') — row {existing.row_idx} not moved."
            )

    # Marks for IDs in sheet not in md. Only compare within the SAME feature —
    # otherwise syncing managers-checklist.md would mark all AUTH checks obsolete.
    feature_id_pat = re.compile(rf"^CHK-{re.escape(parsed.feature_code)}-\d+$")
    for r in sheet_rows:
        if r.is_feature_header:
            continue
        if not feature_id_pat.match(r.check_id):
            continue  # different feature, leave alone
        if r.check_id not in md_ids and not r.obsolete:
            obsolete_marks.append(r.row_idx)

    return updates, appends, obsolete_marks, warnings


def ensure_column_count(ws: gspread.Worksheet, needed: int, dry_run: bool) -> None:
    if ws.col_count < needed:
        log("INFO", f"Sheet has {ws.col_count} cols, expanding to {needed}.")
        if not dry_run:
            ws.add_cols(needed - ws.col_count)


def unmerge_data_zone(ws: gspread.Worksheet, dry_run: bool) -> None:
    """Unmerge any merged cells whose merge region intersects the data zone
    (rows >= DATA_START_ROW). The template may have decorative merges like
    A5:B6 / C5:F6 that block writes to A6 / B6.
    """
    meta = ws.spreadsheet.fetch_sheet_metadata()
    sheet_meta = next(
        (s for s in meta["sheets"] if s["properties"]["sheetId"] == ws.id),
        None,
    )
    if sheet_meta is None:
        return
    merges = sheet_meta.get("merges", []) or []
    requests = []
    for m in merges:
        sr = m.get("startRowIndex", 0)  # 0-based, inclusive
        er = m.get("endRowIndex", 0)    # 0-based, exclusive
        # data zone is rows >= DATA_START_ROW - 1 (0-based)
        if er <= DATA_START_ROW - 1:
            continue  # entirely above data zone
        requests.append({
            "unmergeCells": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": sr,
                    "endRowIndex": er,
                    "startColumnIndex": m.get("startColumnIndex", 0),
                    "endColumnIndex": m.get("endColumnIndex", 0),
                }
            }
        })
    if not requests:
        return
    log("INFO", f"Unmerging {len(requests)} merge regions in the data zone.")
    if dry_run:
        return
    ws.spreadsheet.batch_update({"requests": requests})


def ensure_hidden_columns(ws: gspread.Worksheet, cfg: TargetConfig, dry_run: bool) -> None:
    """Hide the ID and Obsolete columns for this target if not already hidden."""
    requests = []
    for col_1based in (cfg.id_col, cfg.obsolete_col):
        idx = col_1based - 1  # 0-based
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id,
                    "dimension": "COLUMNS",
                    "startIndex": idx,
                    "endIndex": idx + 1,
                },
                "properties": {"hiddenByUser": True},
                "fields": "hiddenByUser",
            }
        })
    if dry_run:
        log("INFO", f"[dry-run] Would hide columns {col_letter(cfg.id_col)} "
            f"and {col_letter(cfg.obsolete_col)}.")
        return
    ws.spreadsheet.batch_update({"requests": requests})


# Text format per row role: (col_start_0based, col_end_exclusive, font_size, bold)
# feature title lives in col A; group headers and checks live in col B.
ROLE_FORMAT: dict[str, tuple[int, int, int, bool]] = {
    "feature": (COL_TASK - 1, COL_TASK, 14, True),    # A, 14pt bold
    "group": (COL_CHECK - 1, COL_CHECK, 10, True),    # B, 10pt bold
    "check": (COL_CHECK - 1, COL_CHECK, 10, False),   # B, 10pt regular
}


def build_format_requests(
    roles: list[str], first_row: int, sheet_id: int
) -> list[dict]:
    """Build Sheets API repeatCell requests to format appended rows by role.

    `roles[k]` describes the row at sheet row `first_row + k` (1-based).
    Contiguous rows of the same role are coalesced into one request.
    """
    requests: list[dict] = []
    i, n = 0, len(roles)
    while i < n:
        role = roles[i]
        j = i
        while j + 1 < n and roles[j + 1] == role:
            j += 1
        col0, col1, size, bold = ROLE_FORMAT[role]
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": first_row + i - 1,  # 0-based, inclusive
                    "endRowIndex": first_row + j,        # 0-based, exclusive
                    "startColumnIndex": col0,
                    "endColumnIndex": col1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"fontSize": size, "bold": bold}
                    }
                },
                "fields": "userEnteredFormat.textFormat.fontSize,"
                          "userEnteredFormat.textFormat.bold",
            }
        })
        i = j + 1
    return requests


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("md_file", help="Path to checklist .md")
    parser.add_argument("--dry-run", action="store_true", help="Plan only; no writes")
    parser.add_argument(
        "--target",
        choices=("web", "mobile"),
        default=None,
        help="Worksheet/layout preset to use. Omit to derive it from the checklist "
             "path (qa/web/... and qa/shared/... -> web, qa/mobile/... -> mobile); "
             "a path that names neither platform is an error, never a silent default.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe all data rows (row 5 onward, up to Obsolete col) before sync. "
             "Use when layout changes.",
    )
    parser.add_argument(
        "--feature-code",
        metavar="CODE",
        default=None,
        help="Override the feature code (2-5 uppercase letters) instead of resolving "
             "it via qa/shared/feature-codes.md or the filename fallback.",
    )
    args = parser.parse_args()

    md_path = Path(args.md_file).resolve()
    if not md_path.is_file():
        raise SystemExit(f"File not found: {md_path}")

    target = args.target or derive_target(md_path)
    if target is None:
        raise SystemExit(
            f"Cannot derive --target from {md_path}: the path names neither qa/web/ "
            "nor qa/mobile/ (qa/shared/ counts as web). Pass --target web|mobile."
        )
    if args.target is None:
        log("INFO", f"--target derived from path: '{target}'")

    # Load .env: search up from CWD, plus fall back to the script directory.
    load_dotenv()
    load_dotenv(SCRIPT_DIR / ".env", override=False)

    credentials_file = os.environ.get("CREDENTIALS_FILE", ".secrets/credentials.json")

    cfg = load_target_config(target)
    log("INFO", f"Target='{cfg.name}' Sheet={cfg.sheet_id} "
        f"Worksheet='{cfg.worksheet}' "
        f"ID col={col_letter(cfg.id_col)}({cfg.id_col}) "
        f"Obsolete col={col_letter(cfg.obsolete_col)}({cfg.obsolete_col})")

    creds_path = Path(credentials_file)
    if not creds_path.is_absolute():
        creds_path = (SCRIPT_DIR / creds_path).resolve()
    if not creds_path.is_file():
        raise SystemExit(f"Credentials file not found: {creds_path}")

    log("INFO", f"Parsing {md_path}")
    feature_map = load_feature_codes()
    parsed = parse_markdown(md_path, feature_map, args.feature_code)
    log("INFO", f"Feature='{parsed.feature_code}' Display='{parsed.display_name}' "
        f"Items={len(parsed.items)}")

    log("INFO", f"Opening sheet {cfg.sheet_id} / worksheet '{cfg.worksheet}'")
    gc = gspread.service_account(filename=str(creds_path))
    sh = gc.open_by_key(cfg.sheet_id)
    ws = sh.worksheet(cfg.worksheet)

    width = cfg.matrix_width
    ensure_column_count(ws, width, args.dry_run)

    # Read data zone, cols A..(Obsolete col). Use a single get to be efficient.
    last_col = col_letter(width)
    all_values = ws.get(f"A{DATA_START_ROW}:{last_col}")
    sheet_rows = load_sheet_rows(all_values, cfg)
    log("INFO", f"Sheet has {len(sheet_rows)} non-empty data rows.")

    if args.reset:
        last_row_to_clear = max(
            (r.row_idx for r in sheet_rows), default=DATA_START_ROW - 1
        )
        if last_row_to_clear >= DATA_START_ROW:
            range_to_clear = f"A{DATA_START_ROW}:{last_col}{last_row_to_clear}"
            log("WARN", f"--reset: clearing {range_to_clear} "
                f"({last_row_to_clear - DATA_START_ROW + 1} rows).")
            if not args.dry_run:
                ws.batch_clear([range_to_clear])
            sheet_rows = []  # treat as empty going forward
        else:
            log("INFO", "--reset: data zone already empty.")
        # Unmerge any cells in the data zone (row 5+). The template may have
        # decorative merges like A5:B6 / C5:F6 that prevent writes to those cells.
        unmerge_data_zone(ws, args.dry_run)

    # Assign IDs to .md items that don't have one yet
    existing_max = max_existing_id_for_feature(sheet_rows, parsed.feature_code)
    assigned = assign_missing_ids(parsed, existing_max)
    if assigned:
        log("INFO", f"Assigned {assigned} new IDs (next number after {existing_max}).")

    updates, appends, obsolete_marks, warnings = build_plan(parsed, sheet_rows, cfg)
    for w in warnings:
        log("WARN", w)

    log("INFO", f"Plan: updates={len(updates)} appends={len(appends)} "
        f"obsolete={len(obsolete_marks)}")

    # ---- writes ---- #
    batch: list[dict] = []

    # Per-cell updates
    for row_idx, col_idx, value in updates:
        batch.append({
            "range": f"{col_letter(col_idx)}{row_idx}",
            "values": [[value]],
        })

    # Obsolete marks
    for row_idx in obsolete_marks:
        batch.append({
            "range": f"{col_letter(cfg.obsolete_col)}{row_idx}",
            "values": [["1"]],
        })

    # Appends: group by section in the order the .md presents them.
    # Determine last used row.
    last_row = max((r.row_idx for r in sheet_rows), default=DATA_START_ROW - 1)
    # Identify which subsections already exist in the sheet WITHIN THIS FEATURE
    # (for the first-row-of-section rule). Subsections with the same name in
    # other features (e.g. "Access and Permissions" under AUTH) must not block
    # writing the same subsection label under a new feature (MGR).
    existing_sections: set[str] = set()
    _current_feat: str | None = None
    for r in sheet_rows:
        if r.is_feature_header:
            _current_feat = r.check_id.removeprefix("FEAT-")
            continue
        if _current_feat != parsed.feature_code:
            continue
        # New layout: standalone group-header row (name in B, no check ID).
        if not r.check_id and r.check_text.strip():
            existing_sections.add(r.check_text.strip().lower())
        # Legacy layout: group name in column A.
        elif r.task.strip():
            existing_sections.add(r.task.strip().lower())

    # Group appends by section while preserving order
    grouped: list[tuple[str, list[CheckItem]]] = []
    for it in appends:
        if grouped and grouped[-1][0] == it.section:
            grouped[-1][1].append(it)
        else:
            grouped.append((it.section, [it]))

    next_row = last_row + 1

    # Collect all append rows into a single 2D matrix written as one range.
    # Writing many adjacent single-row ranges in one batch_update can clobber
    # cells near the feature header — using a single rectangular range avoids it.
    append_matrix: list[list[str]] = []
    # Role of each appended row, parallel to append_matrix, for text formatting.
    append_roles: list[str] = []  # "feature" | "group" | "check"

    needs_feature_header = (
        bool(appends) and find_feature_header(sheet_rows, parsed.feature_code) is None
    )
    if needs_feature_header:
        header_vals = [""] * width
        header_vals[COL_TASK - 1] = parsed.display_name
        header_vals[cfg.id_col - 1] = f"FEAT-{parsed.feature_code}"
        append_matrix.append(header_vals)
        append_roles.append("feature")

    for section, items in grouped:
        # Emit the group name as its OWN row inside the checklist column (B),
        # then the checks below it. Skip the header only if this section already
        # exists in the sheet for this feature (avoid duplicate group rows).
        if section.lower() not in existing_sections:
            header_vals = [""] * width
            header_vals[COL_CHECK - 1] = section
            append_matrix.append(header_vals)
            append_roles.append("group")
        for it in items:
            row_vals = [""] * width
            row_vals[COL_CHECK - 1] = it.text
            row_vals[cfg.id_col - 1] = it.check_id or ""
            append_matrix.append(row_vals)
            append_roles.append("check")
        existing_sections.add(section.lower())

    format_requests: list[dict] = []
    if append_matrix:
        first_append_row = next_row
        end_row = next_row + len(append_matrix) - 1
        batch.append({
            "range": f"A{next_row}:{col_letter(width)}{end_row}",
            "values": append_matrix,
        })
        next_row = end_row + 1
        format_requests = build_format_requests(append_roles, first_append_row, ws.id)

    # B1: "Up to date according to ..." date update
    today_str = date.today().strftime("%d %B %Y")
    b1_value = f"Checklist\nUp to date according to {today_str}"
    batch.append({"range": "B1", "values": [[b1_value]]})

    if args.dry_run:
        log("INFO", f"[dry-run] {len(batch)} batched writes prepared; not sending.")
        for op in batch[:10]:
            log("INFO", f"[dry-run]   {op['range']} <- {op['values']}")
        if len(batch) > 10:
            log("INFO", f"[dry-run]   ... and {len(batch) - 10} more")
        if format_requests:
            log("INFO", f"[dry-run] {len(format_requests)} text-format requests "
                f"prepared for {len(append_roles)} appended rows; not sending.")
    else:
        if batch:
            ws.batch_update(batch, value_input_option="USER_ENTERED")
        if format_requests:
            ws.spreadsheet.batch_update({"requests": format_requests})
        ensure_hidden_columns(ws, cfg, args.dry_run)

    total_after = len(sheet_rows) + len(appends)
    print(
        f"Inserted: {len(appends)}, Updated: {len(updates)}, "
        f"Marked obsolete: {len(obsolete_marks)}, Total in sheet: {total_after}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
