"""Recon A1: which iOS locator texts are found in the Android dumps (step 2 → step 3 input).

For every screen map alias with an iOS locator, take the text it looks for (accessibility id, or the
quoted value of ``name/label ==``, ``CONTAINS``, ``BEGINSWITH`` in a predicate) and search the
Android UiAutomator2 dumps: ``content-desc``, ``text`` and ``hint``. Newlines are compared as-is
(Flutter joins lines with ``\\n`` on both platforms).

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/compare_android.py ../../qa/shared/recon-dumps/android-2026-09-29 [--md out.md]

Status per alias: ``exact`` (same text on Android) · ``contains`` (the Android node contains it) ·
``missing`` (not in any dump yet: either not recon'ed yet or the text differs) · ``no-text``
(the iOS locator is structural or parametrised — decided by hand in step 3).
"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parents[2] / "unit_tests" / "ios_locators.snapshot.json"
QUOTED = re.compile(r"(?:name|label|value)\s*(?:==|CONTAINS|BEGINSWITH)(?:\[c\])?\s*'((?:[^'\\]|\\.)*)'")


def ios_texts(strategy: str, value: str) -> list[str]:
    if "{" in value:
        return []
    if strategy == "accessibility id":
        return [value]
    return [t.replace("\\'", "'") for t in QUOTED.findall(value)]


def android_nodes(dumps: Path) -> list[tuple[str, str]]:
    out = []
    for f in sorted(dumps.glob("*.xml")):
        for el in ET.parse(f).iter():
            for key in ("content-desc", "text", "hint"):
                v = el.attrib.get(key)
                if v:
                    out.append((f.stem, v))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dumps")
    ap.add_argument("--md")
    args = ap.parse_args()
    nodes = android_nodes(Path(args.dumps))
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    rows, totals = [], {"exact": 0, "contains": 0, "missing": 0, "no-text": 0}
    for sid, screen in snap.items():
        for alias, (strategy, value) in screen["ios"].items():
            texts = ios_texts(strategy, value)
            if not texts:
                status, where = "no-text", ""
            else:
                exact = sorted({d for d, v in nodes if any(v == t for t in texts)})
                part = sorted({d for d, v in nodes if any(t in v for t in texts)})
                status = "exact" if exact else "contains" if part else "missing"
                where = ", ".join((exact or part)[:3])
            totals[status] += 1
            rows.append((sid, alias, status, " | ".join(texts)[:70], where))
    print(json.dumps(totals))
    for r in rows:
        if r[2] in ("missing",):
            print(f"  MISSING {r[0]}.{r[1]}: {r[3]!r}")
    if args.md:
        lines = ["| screen | alias | Android | iOS text | seen in dump |", "|---|---|---|---|---|"]
        lines += [f"| {a} | {b} | {c} | {d.replace('|', '/')} | {e} |" for a, b, c, d, e in rows]
        Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
