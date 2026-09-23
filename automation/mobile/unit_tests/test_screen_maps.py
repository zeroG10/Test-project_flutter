"""Offline map-health for the mobile screen maps (the step-7 "done" of CLAUDE.md, without a
device): every alias a test case uses resolves in a map, or is explicitly resolved by a page
method (unnamed controls, per-field errors) — nothing is left to a test's imagination.

    cd automation/mobile && uv run python -m unittest discover -s unit_tests -v

Whether a locator really finds its element is proven only on a device (first run, step 6).
"""

import importlib
import pkgutil
import re
import unittest
from pathlib import Path

from appium.webdriver.common.appiumby import AppiumBy

import pages
import screens
from pages.base_page import BasePage
from screens import Screen, fill, template_fields

REPO = Path(__file__).resolve().parents[3]
TEST_CASES = {
    "02-authentication": REPO / "qa/mobile/02-authentication/authentication-test-cases.md",
}
STEP_ROW = re.compile(r"^\| \d+ \| ([a-z-]+) \| ([^|]+?) \|")
# Test-case targets that are not elements: lifecycle and navigation shortcuts ("open | login").
NOT_ELEMENTS = {"app", "—", "login", "registration"}
# Aliases a page method resolves instead of a map entry — each one is a testability defect or
# a message without an id (screens/*_map.py notes,
# docs/requirements/shared/testability-contract.md).
PAGE_RESOLVED = {
    "registration.channel-sms": "RegistrationPage.choose_channel / selected_channel",
    "registration.channel-email": "RegistrationPage.choose_channel / selected_channel",
    "registration.error[{{field}}]": "RegistrationPage.field_errors (texts inside the field)",
}
REGISTRATION_FIELDS = ("first-name", "last-name", "phone", "email")


def all_screens() -> dict[str, Screen]:
    found: dict[str, Screen] = {}
    for info in pkgutil.iter_modules(screens.__path__):
        if info.name.endswith("_map"):
            module = importlib.import_module(f"screens.{info.name}")  # validates strategies
            for value in vars(module).values():
                if isinstance(value, Screen):
                    found[value.id] = value
    return found


def test_case_aliases(path: Path) -> set[str]:
    aliases: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = STEP_ROW.match(line)
        if not m:
            continue
        action, target = m.group(1), m.group(2).strip()
        if action == "open" or target in NOT_ELEMENTS:
            continue
        if target == "registration.{{field}}":
            aliases.update(f"registration.{f}" for f in REGISTRATION_FIELDS)
            continue
        aliases.add(target)
    return aliases


class MapHealth(unittest.TestCase):
    def setUp(self):
        self.screens = all_screens()

    def test_every_test_case_alias_resolves(self):
        for module, path in TEST_CASES.items():
            aliases = test_case_aliases(path)
            self.assertGreater(len(aliases), 40, f"{module}: parsed too few aliases")
            missing = []
            for alias in sorted(aliases):
                if alias in PAGE_RESOLVED:
                    continue
                screen_id, _, element = alias.partition(".")
                screen = self.screens.get(screen_id)
                if screen is None or element not in screen.elements:
                    missing.append(alias)
                    continue
                screen.locator("ios", element)  # raises when the iOS locator is absent
            self.assertEqual(missing, [], f"{module}: aliases without a map entry")

    def test_page_resolved_aliases_are_still_used(self):
        used = set().union(*(test_case_aliases(p) for p in TEST_CASES.values()))
        self.assertEqual(set(PAGE_RESOLVED) - used, set(), "stale PAGE_RESOLVED entries")

    def test_every_screen_has_an_anchor_and_ios_locators(self):
        for screen in self.screens.values():
            self.assertIsNotNone(screen.anchor, screen.id)
            for alias, el in screen.elements.items():
                self.assertIsNotNone(el.ios, f"{screen.id}.{alias}: no iOS locator")

    def test_static_locators_have_no_stray_braces(self):
        # A "{" outside a declared {text} placeholder would break str.format at run time.
        for screen in self.screens.values():
            for alias, el in screen.elements.items():
                fields = template_fields(el.ios)
                self.assertLessEqual(fields, {"text"}, f"{screen.id}.{alias}: {fields}")
                if fields:
                    self.assertTrue(
                        el.note, f"{screen.id}.{alias}: a parametrised locator needs a note"
                    )

    def test_every_page_is_bound_to_a_map(self):
        for info in pkgutil.iter_modules(pages.__path__):
            if not info.name.endswith("_page") or info.name == "base_page":
                continue
            module = importlib.import_module(f"pages.{info.name}")
            classes = [
                v
                for v in vars(module).values()
                if isinstance(v, type) and issubclass(v, BasePage) and v is not BasePage
            ]
            self.assertTrue(classes, info.name)
            for cls in classes:
                self.assertIn(cls.screen.id, self.screens, cls.__name__)

    def test_pages_the_fixtures_drive_exist(self):
        # fixtures/app_state.py drives these (step 4b contract)
        from pages.jobs_list_page import JobsListPage
        from pages.login_page import LoginPage
        from pages.otp_page import OtpPage
        from pages.welcome_page import WelcomePage

        self.assertTrue(callable(WelcomePage.open_login))
        self.assertTrue(callable(LoginPage.request_code))
        self.assertTrue(callable(OtpPage.enter_code))
        self.assertEqual(JobsListPage.screen.anchor, "root")


class Templates(unittest.TestCase):
    def test_predicate_values_are_quoted(self):
        loc = (AppiumBy.IOS_PREDICATE, "name == {text}")
        self.assertEqual(fill(loc, {"text": 'say "hi"'})[1], 'name == "say \\"hi\\""')
        self.assertEqual(fill(loc, {"text": "Let's go"})[1], 'name == "Let\'s go"')

    def test_accessibility_id_is_raw(self):
        loc = (AppiumBy.ACCESSIBILITY_ID, "{text}")
        self.assertEqual(fill(loc, {"text": "Incorrect code."}), (loc[0], "Incorrect code."))

    def test_parameters_must_match(self):
        with self.assertRaises(LookupError):
            fill((AppiumBy.IOS_PREDICATE, "name == {text}"), {})
        with self.assertRaises(LookupError):
            fill((AppiumBy.ACCESSIBILITY_ID, "Continue"), {"text": "x"})


if __name__ == "__main__":
    unittest.main()
