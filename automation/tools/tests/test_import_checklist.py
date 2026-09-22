"""Self-test for import_checklist_from_sheets.py.

Offline: an inline fake grid stands in for the worksheet — no Sheets access.
Covers every row variant seen in the real sheet: feature rows (with trailing
spaces), screen+group rows, screen+first-check rows, in-line group headers
that carry statuses, checks with line breaks, empty and status-only rows,
features without screens, and the round trip through the sync parser.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

import import_checklist_from_sheets as imp
import sync_checklist_to_sheets as sync

P4 = ["Passed", "Passed", "Passed", "Passed"]

# A, B, C..F statuses  (rows 1-4 are the sheet header)
GRID: list[list[str]] = [
    ["TASK", "Checklist \nUp to date according to 15 May 2026 ", "Platform"],
    ["", "", "Chrome", "Firefox", "Edge", "Safari"],
    ["", "", "", "", "", "", "4212"],
    ["", "", "", "", "", "", " Comments"],
    # 5
    ["Authentication", ""],
    ["", ""],                                                        # 6 empty
    ["Login page", "General", *P4],                                  # 7 screen + group (statuses!)
    ["", 'Check that the "Log in" title is visible.', *P4],          # 8
    ["", "  Check that the logo matches\nthe design ", *P4],         # 9 newline + padding, no dot
    ["", "Access control after login", *P4],                         # 10 in-line group, statuses
    ["", "Verify that a Manager cannot open Root-only pages.", *P4], # 11 other verb
    ["Forgot password", "Check that the email field is required.", *P4],  # 12 screen + check
    ["", "Check that informative error messages are displayed.", *P4],    # 13
    ["", "Check that informative error messages are displayed.", *P4],    # 14 duplicate text
    ["Orders  ", ""],                                     # 15 trailing spaces
    ["Orders list page", "Check that the Orders list page is accessible for a Root User", *P4],  # 16
    ["", "Layout, navigation, header", *P4],                         # 17 group
    ["", "Check that the page header reads “Orders”.", *P4],   # 18
    ["", "", *P4],                                                   # 19 empty with statuses
    ["Responses", ""],                                               # 20 no screens at all
    ["", "Responses List Access and Layout", *P4],                   # 21 group only
    ["", "Check that the Responses page opens from the left nav.", *P4],  # 22
    ["", "Empty group", *P4],                                        # 23 group with no checks
    ["", "   "],                                                     # 24 whitespace-only = empty
    [],                                                              # 25 short row
]

NOTE = "Source: test note."


# The template ships no built-in map (features belong to the product under test), so the
# tests pass the same explicit map the CLI would receive via --module-map.
TEST_MODULE_MAP = [
    "Authentication=01-authentication:AUTH",
    "Managers=02-managers:MGR",
    "Orders=03-orders:ORD",
    "Responses=06-responses:RESP",
]
TEST_MODULE_MAP_ARGS = [arg for entry in TEST_MODULE_MAP for arg in ("--module-map", entry)]


@pytest.fixture
def module_map():
    return imp.build_module_map(TEST_MODULE_MAP)


def test_no_module_map_refuses_to_guess():
    with pytest.raises(SystemExit, match="No module map"):
        imp.build_module_map(None)


@pytest.fixture
def report(module_map):
    return imp.parse_grid(GRID, module_map)


def test_feature_blocks_in_sheet_order_with_trimmed_names(report):
    assert [b.module.feature for b in report.blocks] == [
        "Authentication", "Orders", "Responses"
    ]
    assert [b.module.code for b in report.blocks] == ["AUTH", "ORD", "RESP"]
    assert [b.start_row for b in report.blocks] == [5, 15, 20]


def test_sections_and_checks(report):
    auth, ft, resp = report.blocks
    assert [(s.screen, s.group, len(s.checks)) for s in auth.sections] == [
        ("Login page", "General", 2),
        ("Login page", "Access control after login", 1),
        ("Forgot password", None, 3),
    ]
    assert [c.text for c in auth.sections[0].checks] == [
        'Check that the "Log in" title is visible.',
        "Check that the logo matches the design",  # newline collapsed, trimmed, no dot added
    ]
    assert auth.screens == ["Login page", "Forgot password"]
    assert auth.groups == 2
    assert len(auth.checks) == 6

    assert [(s.screen, s.group, len(s.checks)) for s in ft.sections] == [
        ("Orders list page", None, 1),
        ("Orders list page", "Layout, navigation, header", 1),
    ]
    assert [(s.screen, s.group, len(s.checks)) for s in resp.sections] == [
        (None, "Responses List Access and Layout", 1),
        (None, "Empty group", 0),
    ]
    assert resp.screens == []


def test_skipped_rows_and_warnings(report):
    assert report.empty_rows == 4          # rows 6, 19, 24, 25
    assert report.empty_rows_with_status == 1
    assert report.rows_before_first_feature == 0
    joined = "\n".join(report.warnings)
    assert "row 19" in joined and "other cells filled" in joined
    assert "identical check text 2x" in joined
    assert "'Empty group' has no checks" in joined


def test_group_header_heuristic():
    assert imp.is_group_header("General")
    assert imp.is_group_header("Loading, empty and no-results states")
    assert imp.is_group_header("Custom Answer Toggle (“Other”)")
    assert not imp.is_group_header("Check that a section can be expanded.")
    assert not imp.is_group_header("check lowercase verb")
    assert not imp.is_group_header("Verify the toast")
    assert not imp.is_group_header("Something without a verb but with a dot.")
    assert not imp.is_group_header("x" * (imp.GROUP_MAX_LEN + 1))


def test_rows_before_first_feature_are_counted_not_imported(module_map):
    grid = GRID[:4] + [["", "Check that orphan.", *P4], ["Login page", "General"]] + GRID[4:9]
    rep = imp.parse_grid(grid, module_map)
    assert rep.rows_before_first_feature == 2
    assert len(rep.blocks[0].checks) == 2


def test_unknown_a_only_row_is_a_screen(module_map):
    grid = GRID[:4] + [["Authentication", ""], ["Mystery page", ""], ["", "Check it.", *P4]]
    rep = imp.parse_grid(grid, module_map)
    assert [(s.screen, s.group) for s in rep.blocks[0].sections] == [("Mystery page", None)]
    assert any("not in the module map" in w for w in rep.warnings)


def test_module_map_parsing():
    m = imp.parse_module_map_entry("Order list=07-order-list:ord")
    assert (m.feature, m.folder, m.slug, m.code, m.filename) == (
        "Order list", "07-order-list", "order-list", "ORD", "order-list-checklist.md"
    )
    with pytest.raises(SystemExit, match="2-5 uppercase"):
        imp.parse_module_map_entry("X=01-x:TOOLONG")
    with pytest.raises(SystemExit, match="expected"):
        imp.parse_module_map_entry("no-separator")
    with pytest.raises(SystemExit, match="used by both"):
        imp.build_module_map(["A=01-a:AA", "B=02-b:AA"])


EXPECTED_AUTH_MD = """\
# QA Checklist: Authentication

> Source: test note.

## Login page / General

1. [CHK-AUTH-001] Check that the "Log in" title is visible.
2. [CHK-AUTH-002] Check that the logo matches the design

## Login page / Access control after login

1. [CHK-AUTH-003] Verify that a Manager cannot open Root-only pages.

## Forgot password

1. [CHK-AUTH-004] Check that the email field is required.
2. [CHK-AUTH-005] Check that informative error messages are displayed.
3. [CHK-AUTH-006] Check that informative error messages are displayed.
"""


def test_render_markdown_exact(report):
    assert imp.render_markdown(report.blocks[0], NOTE) == EXPECTED_AUTH_MD
    resp_md = imp.render_markdown(report.blocks[2], NOTE)
    assert "## Responses List Access and Layout\n" in resp_md
    assert "Empty group" not in resp_md        # empty sections are not emitted
    assert "[CHK-RESP-001]" in resp_md


def test_render_refuses_headings_the_sync_parser_drops(module_map):
    grid = GRID[:4] + [["Authentication", ""], ["", "Coverage summary", *P4], ["", "Check it.", *P4]]
    rep = imp.parse_grid(grid, module_map)
    with pytest.raises(SystemExit, match="would be dropped"):
        imp.render_markdown(rep.blocks[0], NOTE)


def test_round_trip_through_sync_parser(report, tmp_path: Path):
    """The rendered file must parse with the sync script's own parser, with the
    expected feature code, section names, monotonically increasing unique IDs."""
    for block in report.blocks:
        path = tmp_path / block.module.folder / block.module.filename
        path.parent.mkdir(parents=True)
        path.write_text(imp.render_markdown(block, NOTE), encoding="utf-8")
        parsed = sync.parse_markdown(path, {block.module.slug: block.module.code})
        assert parsed.feature_code == block.module.code
        assert parsed.display_name == block.module.feature
        assert len(parsed.items) == len(block.checks)
        assert [it.check_id for it in parsed.items] == [
            f"CHK-{block.module.code}-{n:03d}" for n in range(1, len(block.checks) + 1)
        ]
        assert [it.section for it in parsed.items[:1]] == [
            block.sections[0].heading(block.module.feature)
        ]
        # sync strips a trailing '.'; everything else must be verbatim
        assert [it.text for it in parsed.items] == [c.text.rstrip(".") for c in block.checks]


def test_source_note_shape():
    note = imp.source_note("Check-list", "Working copy", "SHEET", 42, date(2026, 9, 17))
    assert note.startswith('Source: Google Sheet `Check-list` (copy of "Working copy"), ')
    assert "gid `42`" in note and "imported 2026-09-17" in note
    assert note.endswith("never renumber.")


def _fake_fetch(sheet_id, gid, creds):
    return "Copy of Working sheet", "Check-list", GRID


def _run(tmp_path: Path, *extra: str) -> int:
    creds = tmp_path / "creds.json"
    creds.write_text("{}")
    return imp.main(
        ["--sheet-id", "X", "--gid", "1", "--out-root", str(tmp_path / "qa" / "web"),
         "--credentials", str(creds), *TEST_MODULE_MAP_ARGS, *extra],
        fetch=_fake_fetch,
    )


def test_cli_dry_run_writes_nothing(tmp_path: Path, capsys):
    assert _run(tmp_path, "--dry-run") == 0
    assert not (tmp_path / "qa").exists()
    out = capsys.readouterr().out
    assert "[dry-run] nothing written." in out
    assert "Authentication" in out and "TOTAL" in out
    assert "'Managers' from the module map not found" in out


def test_cli_writes_then_refuses_overwrite_unless_forced(tmp_path: Path):
    assert _run(tmp_path) == 0
    auth = tmp_path / "qa/web/01-authentication/authentication-checklist.md"
    resp = tmp_path / "qa/web/06-responses/responses-checklist.md"
    assert auth.is_file() and resp.is_file()
    assert not (tmp_path / "qa/web/02-managers").exists()   # not in the sheet → no file
    assert auth.read_text(encoding="utf-8").splitlines()[0] == "# QA Checklist: Authentication"
    assert 'copy of "Copy of Working sheet"' in auth.read_text(encoding="utf-8")

    with pytest.raises(SystemExit, match="break that\\s+contract"):
        _run(tmp_path)
    assert _run(tmp_path, "--force") == 0


def test_cli_feature_filter(tmp_path: Path):
    assert _run(tmp_path, "--feature", "responses") == 0
    assert (tmp_path / "qa/web/06-responses/responses-checklist.md").is_file()
    assert not (tmp_path / "qa/web/01-authentication").exists()
    with pytest.raises(SystemExit, match="not in the module map"):
        _run(tmp_path, "--feature", "Nope")


def test_cli_empty_import_is_a_failure(tmp_path: Path):
    creds = tmp_path / "creds.json"
    creds.write_text("{}")
    rc = imp.main(
        ["--sheet-id", "X", "--gid", "1", "--out-root", str(tmp_path), "--credentials", str(creds),
         *TEST_MODULE_MAP_ARGS],
        fetch=lambda *_: ("t", "w", GRID[:4] + [["Authentication", ""]]),
    )
    assert rc == 1
