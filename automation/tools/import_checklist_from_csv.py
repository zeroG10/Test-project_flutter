#!/usr/bin/env python3
"""One-time import of a checklist from a CSV EXPORT of the team Sheet (no Google credentials).

Thin adapter over ``import_checklist_from_sheets.py``: same parser, same markdown output,
same one-time / no-renumber rules. Use it when the Sheet itself is not reachable (no service
account) but a CSV export of the worksheet exists in ``docs/00-intake/``.

The only thing it adds is boundary normalisation: the upstream parser starts a feature block
only on a row where column A holds the feature name and column B is EMPTY. Some sheets put the
first group or screen name into B on that same row. For every row whose A is a mapped feature
and whose B is filled, the adapter inserts a synthetic ``[feature, ""]`` row above it; the
original row stays as it is, so it becomes the first screen of the block and B keeps its meaning.

    uv run python import_checklist_from_csv.py \\
        --csv ../../docs/00-intake/<checklist-export>.csv \\
        --out-root ../../qa/mobile \\
        --module-map "Authentication=02-authentication:AUTH" ... \\
        --feature Authentication --dry-run
"""

from __future__ import annotations

import argparse
import csv
import sys
import tempfile
from pathlib import Path

import import_checklist_from_sheets as upstream


def normalise_boundaries(rows: list[list[str]], feature_keys: set[str]) -> list[list[str]]:
    out: list[list[str]] = []
    for idx, row in enumerate(rows):
        cells = list(row) + [""] * (2 - len(row))
        a, b = cells[0].strip(), cells[1].strip()
        if idx >= upstream.HEADER_ROWS and a and b and upstream.normalize_key(a) in feature_keys:
            out.append([a, ""])
            cells[0] = a  # keep the name as the screen of the first section
            out.append(cells)
            continue
        out.append(list(row))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--csv", required=True)
    known, rest = parser.parse_known_args(argv)
    csv_path = Path(known.csv).resolve()
    rows = list(csv.reader(csv_path.open(encoding="utf-8")))

    # feature names come from the --module-map entries passed through to upstream
    pairs = zip(rest, rest[1:], strict=False)
    feature_keys = {upstream.normalize_key(v.split("=", 1)[0]) for k, v in pairs if k == "--module-map"}
    rows = normalise_boundaries(rows, feature_keys)

    def fetch_from_csv(_sheet_id: str, _gid: int, _creds: Path):
        return csv_path.stem, "Check-list (CSV export)", rows

    # upstream insists that a credentials file exists; the CSV path needs none
    with tempfile.NamedTemporaryFile(suffix=".json") as dummy:
        return upstream.main(
            [
                "--sheet-id",
                "csv-export",
                "--gid",
                "0",
                "--credentials",
                dummy.name,
                "--source-title",
                csv_path.name,
                *rest,
            ],
            fetch=fetch_from_csv,
        )


if __name__ == "__main__":
    sys.exit(main())
