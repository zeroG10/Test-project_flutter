"""Offline map-health for the Android column (Android stage, step 3 — docs/notes/android-plan.md).

    cd automation/mobile && uv run python -m unittest unit_tests.test_android_maps -v
    PYTHONPATH=. uv run python -m unit_tests.android_dumps <screen-id> ...   # per-alias detail

1. Every alias a test case uses (outside ``PAGE_RESOLVED``) has an Android locator, or its map
   module explains why not in ``ANDROID_WITHOUT = {"screen.alias": "reason"}`` (iOS system UI
   with an Android counterpart elsewhere, a page method on Android, Blocked by decision).
2. Every static Android locator finds at least one element in the recon trees
   (``qa/shared/recon-dumps/android-*``), evaluated the way UiAutomator2 would
   (``unit_tests/android_dumps.py``) — unless its module lists it in
   ``ANDROID_UNVERIFIED = {"screen.alias": "reason"}`` (screen not reached in recon A1).
3. A ``className("android.widget.EditText").instance(n)`` locator — Flutter text fields carry
   their name only as a hint, which UiSelector cannot match — names that hint in its note
   (``hint 'Phone number / Email'``), and the n-th field of some recon tree has that hint.
4. An element without an iOS locator is marked ``note="Android only: …"``; parametrised
   Android locators use only ``{text}``; every screen with Android locators has an Android anchor.

Whether a locator is right on a live device is proven by the module runs (step 4).
"""

import importlib
import unittest

from screens import template_fields
from unit_tests import android_dumps as ad
from unit_tests.test_screen_maps import PAGE_RESOLVED, TEST_CASES, test_case_aliases


def _module_dicts(name: str) -> dict[str, str]:
    import pkgutil

    import screens

    merged: dict[str, str] = {}
    for info in pkgutil.walk_packages(screens.__path__, prefix="screens."):
        if info.name.endswith("_map"):
            merged.update(getattr(importlib.import_module(info.name), name, {}))
    return merged


class AndroidMapHealth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.screens = {s.id: s for s in ad.all_screen_objects()}
        cls.without = _module_dicts("ANDROID_WITHOUT")
        cls.unverified = _module_dicts("ANDROID_UNVERIFIED")

    def test_explanations_name_real_aliases(self):
        for key in list(self.without) + list(self.unverified):
            screen_id, _, alias = key.partition(".")
            self.assertIn(screen_id, self.screens, f"{key}: unknown screen")
            self.assertIn(alias, self.screens[screen_id].elements, f"{key}: unknown alias")
        for key, reason in {**self.without, **self.unverified}.items():
            self.assertTrue(reason.strip(), f"{key}: empty reason")

    def test_every_test_case_alias_has_an_android_locator(self):
        missing = []
        for module, path in TEST_CASES.items():
            for alias in sorted(test_case_aliases(path)):
                if alias in PAGE_RESOLVED:
                    continue
                screen_id, _, element = alias.partition(".")
                element = element.partition(".")[0]  # card fields live on the card element
                screen = self.screens.get(screen_id)
                if screen is None or element not in screen.elements:
                    continue  # the iOS map-health reports it
                key = f"{screen_id}.{element}"
                if screen.elements[element].android is None and key not in self.without:
                    missing.append(f"{module}: {key}")
        self.assertEqual(sorted(set(missing)), [], "test-case aliases without an Android locator")

    def test_android_locators_find_elements_in_recon_trees(self):
        self.assertTrue(ad.dump_files(), "no Android recon trees under qa/shared/recon-dumps/")
        problems = []
        for screen in self.screens.values():
            for alias, el in screen.elements.items():
                key = f"{screen.id}.{alias}"
                if el.android is None or template_fields(el.android) or key in self.unverified:
                    continue
                try:
                    hits = ad.where(el.android)
                except ad.Unsupported as exc:
                    problems.append(f"{key}: {exc}")
                    continue
                if not hits:
                    problems.append(f"{key}: {el.android[1]!r} finds nothing in the recon trees")
        self.assertEqual(problems, [])

    def test_edit_text_by_position_names_its_hint(self):
        problems = []
        for screen in self.screens.values():
            for alias, el in screen.elements.items():
                key = f"{screen.id}.{alias}"
                if el.android is None or "android.widget.EditText" not in el.android[1]:
                    continue
                if ".instance(" not in el.android[1] or key in self.unverified:
                    continue
                m = ad.HINT_NOTE.search(el.note)
                if not m:
                    problems.append(f"{key}: note must name the field's hint ('hint \\'…\\'')")
                    continue
                hints = {a.get("hint") for _, found in ad.where(el.android) for a in found}
                if m.group(1) not in hints:
                    problems.append(f"{key}: hint {m.group(1)!r} not at that position ({hints})")
                if getattr(el.android, "hint", m.group(1)) != m.group(1):
                    problems.append(f"{key}: EditTextByHint({el.android.hint!r}) ≠ note hint")
        self.assertEqual(problems, [])

    def test_android_only_elements_are_marked_and_templates_are_text_only(self):
        for screen in self.screens.values():
            has_android = False
            for alias, el in screen.elements.items():
                if el.android is not None:
                    has_android = True
                    self.assertLessEqual(
                        template_fields(el.android), {"text"}, f"{screen.id}.{alias}"
                    )
                if el.ios is None and el.flutter is None:
                    self.assertTrue(
                        el.note.startswith("Android only"),
                        f"{screen.id}.{alias}: no iOS locator — note must start 'Android only'",
                    )
            if has_android:
                anchor = screen.elements[screen.anchor]
                self.assertTrue(
                    anchor.android is not None or f"{screen.id}.{screen.anchor}" in self.without,
                    f"{screen.id}: the anchor {screen.anchor!r} has no Android locator",
                )


class Evaluator(unittest.TestCase):
    def test_uiselector_chain_and_instance(self):
        calls, inst = ad.parse_selector(
            'new UiSelector().className("android.widget.Button").description("Log out").instance(1)'
        )
        self.assertEqual(
            calls, [("className", "android.widget.Button"), ("description", "Log out")]
        )
        self.assertEqual(inst, 1)

    def test_unknown_method_is_reported(self):
        with self.assertRaises(ad.Unsupported):
            ad.parse_selector('new UiSelector().fromParent(new UiSelector().text("x"))')


if __name__ == "__main__":
    unittest.main()
