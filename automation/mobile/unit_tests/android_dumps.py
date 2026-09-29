"""Evaluate Android locators against the recon trees (offline map-health for the Android column).

The recon dumps (``qa/shared/recon-dumps/android-*/``) are UiAutomator2 page sources of the real
app on the emulator. A locator of a screen map is evaluated on them the way UiAutomator2 would:

* ``accessibility id`` — ``content-desc`` equals the value (newlines included);
* ``id`` — ``resource-id`` equals the value, or ``<package>:id/<value>`` (the driver completes it);
* ``-android uiautomator`` — a ``new UiSelector()...`` chain of the matchers below; ``instance(n)``
  picks the n-th match in document order, as UiAutomator does.

UiSelector does NOT unescape ``\\n`` in a quoted value (checked on the device, 2026-09-29): a label
with a newline needs ``accessibility id`` or a ``…Contains`` / ``…StartsWith`` matcher.

    cd automation/mobile
    PYTHONPATH=. uv run python -m unit_tests.android_dumps [screen-id ...]   # one line per alias
"""

import re
import sys
import xml.etree.ElementTree as ET
from functools import cache
from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy

REPO = Path(__file__).resolve().parents[3]
DUMPS = sorted((REPO / "qa" / "shared" / "recon-dumps").glob("android-*"))
APP_PACKAGE = "com.concerttechnologies.app.dev"

_CALL = re.compile(r'\.(\w+)\((?:"((?:[^"\\]|\\.)*)"|(\d+)|(true|false))?\)')
_STRING = {
    "text": lambda a, v: a.get("text", "") == v,
    "textContains": lambda a, v: v in a.get("text", ""),
    "textStartsWith": lambda a, v: a.get("text", "").startswith(v),
    # Java's Pattern.matches: whole value, and "." does NOT cross a newline (no DOTALL)
    "textMatches": lambda a, v: re.fullmatch(v, a.get("text", "")) is not None,
    "description": lambda a, v: a.get("content-desc", "") == v,
    "descriptionContains": lambda a, v: v in a.get("content-desc", ""),
    "descriptionStartsWith": lambda a, v: a.get("content-desc", "").startswith(v),
    "descriptionMatches": lambda a, v: re.fullmatch(v, a.get("content-desc", "")) is not None,
    "className": lambda a, v: a.get("class", "") == v,
    "classNameMatches": lambda a, v: re.fullmatch(v, a.get("class", "")) is not None,
    "resourceId": lambda a, v: a.get("resource-id", "") == v,
    "resourceIdMatches": lambda a, v: re.fullmatch(v, a.get("resource-id", "")) is not None,
    "packageName": lambda a, v: a.get("package", "") == v,
}
_BOOL = {
    "clickable": "clickable",
    "checkable": "checkable",
    "checked": "checked",
    "enabled": "enabled",
    "selected": "selected",
    "scrollable": "scrollable",
    "focused": "focused",
    "longClickable": "long-clickable",
}


class Unsupported(ValueError):
    """A UiSelector method the offline evaluator does not model — check it on a device."""


def parse_selector(expr: str) -> tuple[list[tuple[str, str | bool]], int | None]:
    """``new UiSelector().description("A").instance(1)`` -> ([("description", "A")], 1)."""
    body = expr.strip()
    if not body.startswith("new UiSelector()"):
        raise Unsupported(f"not a single UiSelector chain: {expr!r}")
    rest = body[len("new UiSelector()") :]
    calls, instance, pos = [], None, 0
    for m in _CALL.finditer(rest):
        if m.start() != pos:
            raise Unsupported(f"cannot parse {rest[pos:]!r} in {expr!r}")
        pos = m.end()
        name, sval, ival, bval = m.groups()
        if name == "instance":
            instance = int(ival)
        elif name in _STRING and sval is not None:
            calls.append((name, sval.replace('\\"', '"').replace("\\\\", "\\")))
        elif name in _BOOL and bval is not None:
            calls.append((name, bval == "true"))
        else:
            raise Unsupported(f"UiSelector.{name} is not modelled offline: {expr!r}")
    if pos != len(rest):
        raise Unsupported(f"cannot parse {rest[pos:]!r} in {expr!r}")
    return calls, instance


@cache
def _nodes(path: Path) -> tuple[dict[str, str], ...]:
    return tuple(el.attrib for el in ET.parse(path).iter() if el.attrib.get("class"))


def dump_files() -> list[Path]:
    return [f for d in DUMPS for f in sorted(d.glob("*.xml"))]


def matches(locator: tuple[str, str], path: Path) -> list[dict[str, str]]:
    """Nodes of one dump the locator finds (instance() already applied)."""
    strategy, value = locator
    nodes = _nodes(path)
    if strategy == AppiumBy.ACCESSIBILITY_ID:
        return [a for a in nodes if a.get("content-desc") == value]
    if strategy == AppiumBy.ID:
        full = value if ":id/" in value else f"{APP_PACKAGE}:id/{value}"
        return [a for a in nodes if a.get("resource-id") in (value, full)]
    if strategy == AppiumBy.ANDROID_UIAUTOMATOR:
        calls, instance = parse_selector(value)
        found = [
            a
            for a in nodes
            if all(
                _STRING[n](a, v) if n in _STRING else a.get(_BOOL[n]) == ("true" if v else "false")
                for n, v in calls
            )
        ]
        if instance is not None:
            return found[instance : instance + 1]
        return found
    raise Unsupported(f"strategy {strategy!r} is not evaluated offline")


def where(locator: tuple[str, str]) -> list[tuple[str, list[dict[str, str]]]]:
    """(dump name, matched nodes) for every dump the locator finds something in."""
    out = []
    for f in dump_files():
        found = matches(locator, f)
        if found:
            out.append((f.stem, found))
    return out


HINT_NOTE = re.compile(r"hint '([^']+)'")


def all_screen_objects() -> list:
    """Every ``Screen`` of every ``*_map`` module, ``screens/android/`` included."""
    import importlib
    import pkgutil

    import screens
    from screens import Screen

    found = {}
    for info in pkgutil.walk_packages(screens.__path__, prefix="screens."):
        if info.name.endswith("_map"):
            for value in vars(importlib.import_module(info.name)).values():
                if isinstance(value, Screen):
                    found[value.id] = value
    return [found[k] for k in sorted(found)]


def main(screen_ids: list[str]) -> None:
    for screen in all_screen_objects():
        if screen_ids and screen.id not in screen_ids:
            continue
        print(f"== {screen.id}")
        for alias, el in screen.elements.items():
            if el.android is None:
                print(f"   {alias:28} —  no android locator")
                continue
            if "{" in el.android[1]:
                print(f"   {alias:28} ~  parametrised {el.android[1]!r} (checked on a device)")
                continue
            try:
                hits = where(el.android)
            except Unsupported as exc:
                print(f"   {alias:28} ?  {exc}")
                continue
            names = ", ".join(n for n, _ in hits[:4]) + (" …" if len(hits) > 4 else "")
            mark = "OK" if hits else "!!"
            print(f"   {alias:28} {mark} {len(hits)} dump(s) {names}")


if __name__ == "__main__":
    main(sys.argv[1:])
