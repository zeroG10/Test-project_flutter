"""Guard for the iOS column of the screen maps while Android is added (SECOND-PLATFORM.md).

Once the iOS suite is proven (its final runs), its locators are recorded in a snapshot. Android
locators then go into the same maps, next to ``ios=`` — this test fails when any iOS locator or
screen anchor changed, appeared or disappeared, so the Android work cannot silently touch iOS.
Without a snapshot (no platform closed yet) the guard has nothing to hold and says so.

    cd automation/mobile && uv run python -m unittest unit_tests.test_ios_locator_guard -v

A deliberate iOS change (owner's word) re-records the snapshot and shows what moved:

    uv run python -m unit_tests.test_ios_locator_guard --update
"""

import importlib
import json
import pkgutil
import sys
import unittest
from pathlib import Path

import screens
from screens import Screen

SNAPSHOT = Path(__file__).with_name("ios_locators.snapshot.json")


def ios_column() -> dict[str, dict]:
    """Every screen's anchor and iOS locators, by screen id — maps in subpackages included."""
    found: dict[str, dict] = {}
    for info in pkgutil.walk_packages(screens.__path__, prefix="screens."):
        if not info.name.endswith("_map"):
            continue
        module = importlib.import_module(info.name)
        for value in vars(module).values():
            if isinstance(value, Screen):
                ios = {a: list(el.ios) for a, el in value.elements.items() if el.ios is not None}
                if ios:
                    found[value.id] = {"anchor": value.anchor, "ios": dict(sorted(ios.items()))}
    return dict(sorted(found.items()))


def diff(old: dict[str, dict], new: dict[str, dict]) -> list[str]:
    lines: list[str] = []
    for sid in sorted(old.keys() | new.keys()):
        a, b = old.get(sid), new.get(sid)
        if a is None or b is None:
            lines.append(f"{sid}: screen {'added' if a is None else 'removed'}")
            continue
        if a["anchor"] != b["anchor"]:
            lines.append(f"{sid}: anchor {a['anchor']!r} -> {b['anchor']!r}")
        for alias in sorted(a["ios"].keys() | b["ios"].keys()):
            x, y = a["ios"].get(alias), b["ios"].get(alias)
            if x != y:
                lines.append(f"{sid}.{alias}: {x} -> {y}")
    return lines


class IosLocatorGuard(unittest.TestCase):
    def setUp(self):
        if not SNAPSHOT.is_file():
            self.skipTest(
                f"no snapshot at {SNAPSHOT.name}: iOS is not closed — record it with --update"
            )

    def test_ios_column_is_unchanged(self):
        recorded = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        changes = diff(recorded, ios_column())
        self.assertEqual(
            changes,
            [],
            "iOS locators changed — iOS is closed (its snapshot); revert, or re-record "
            "with --update only on the owner's word:\n  " + "\n  ".join(changes),
        )

    def test_snapshot_is_not_empty(self):
        recorded = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertGreater(len(recorded), 0, "an empty snapshot holds nothing")


if __name__ == "__main__":
    if "--update" in sys.argv:
        old = json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.is_file() else {}
        new = ios_column()
        SNAPSHOT.write_text(json.dumps(new, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        changes = diff(old, new)
        print(
            f"{SNAPSHOT.name}: {len(new)} screens, "
            f"{sum(len(s['ios']) for s in new.values())} iOS locators"
        )
        print("\n".join(changes[:200]) if changes else "no change")
    else:
        unittest.main()
