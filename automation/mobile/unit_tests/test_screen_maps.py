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
    "01-splash": REPO / "qa/mobile/01-splash/splash-test-cases.md",
    "02-authentication": REPO / "qa/mobile/02-authentication/authentication-test-cases.md",
    "03-order-list": REPO / "qa/mobile/03-order-list/order-list-test-cases.md",
    "04-order-details": REPO / "qa/mobile/04-order-details/order-details-test-cases.md",
    "05-check-in-out": REPO / "qa/mobile/05-check-in-out/check-in-out-test-cases.md",
    "06-order-progress": REPO / "qa/mobile/06-order-progress/order-progress-test-cases.md",
    "07-submit-deliverables": REPO
    / "qa/mobile/07-submit-deliverables/submit-deliverables-test-cases.md",
    "08-survey": REPO / "qa/mobile/08-survey/survey-test-cases.md",
    "09-photo-report": REPO / "qa/mobile/09-photo-report/photo-report-test-cases.md",
    "10-notes": REPO / "qa/mobile/10-notes/notes-test-cases.md",
    "11-notifications": REPO / "qa/mobile/11-notifications/notifications-test-cases.md",
    "12-profile": REPO / "qa/mobile/12-profile/profile-test-cases.md",
}
MIN_ALIASES = {
    "01-splash": 5, "02-authentication": 40, "03-order-list": 30, "04-order-details": 35,
    "05-check-in-out": 15, "06-order-progress": 15, "07-submit-deliverables": 15, "08-survey": 20,
    "09-photo-report": 12, "10-notes": 12, "11-notifications": 8, "12-profile": 15,
}  # fmt: skip
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
    # module 01 — the splash has no labelled element (recon 4)
    "splash.logo": "SplashPage.expect_logo_centred (pixels: centre of the light logo)",
    # module 03 — one card = one element; lists of cards and states read from the page source
    "jobs-list.card-count": "JobsListPage.card_count (whole scrolled list)",
    "jobs-list.card-order": "JobsListPage.all_cards (order top → bottom)",
    "jobs-list.card-dates": "JobsListPage.all_cards (dates top → bottom)",
    "jobs-list.any-card": "JobsListPage.expect_no_cards (card-shaped names in the page source)",
    "jobs-calendar.any-card": "JobsCalendarPage.expect_no_cards",
    "jobs-calendar.week-days": "JobsCalendarPage.week_days (day cells left → right)",
    "tabbar.jobs-selected": "TabBarPage.selected (page-source traits contain 'Selected')",
    # module 04 — what the tree does not hold (recon 5 / 5b): pixels, or another platform's app
    "job-details.updated-banner": "JobDetailsPage.expect_no_updated_banner (banner fill pixels)",
    "attachments.thumbnail": "AttachmentsPage.expect_thumbnails_drawn / tap_cell (TD-ORDD-002)",
    "pdf-viewer.page": "PdfViewerPage.expect_page_drawn (the test PDF's colour block)",
    "photo-viewer.image": "PhotoViewerPage.expect_photo_fills_width (pixels)",
    "dialer.number": "Android dialer (TC-ORDD-004); iOS Blocked — no Phone app on the simulator",
    "api.surveyResponse": "GET /job/{id} → surveyResponse (helpers/survey_response.py)",
    "api.jobPhotos": "GET /job/{id} → photos (tests/shared/test_photo_report.py)",
    "api.jobNotes": "GET /job/{id} → notes (tests/shared/test_notes.py)",
    "notes.menu": "NotesPage.open_menu — a tap on the row's right end (TD-NOTE-001)",
    "api.user": "GET /user/{id} (fixtures/profile.py)",
    "api.technicians": "GET /technician?search= (FieldServicesApi.find_technicians_by_email)",
    "api.notifications": "GET /notification?userId= (fixtures/notifications.py)",
    "api.job": "GET /job/{id} (and PATCH /job/{id} of the test's own job — TC-DLV-006)",
}
# Fields of a parsed job card (``screen.card[{{jobId}}].<field>``, pages/jobs_list_page.parse_card)
CARD_FIELDS = {"title", "date", "status", "address", "updated"}
PARAMS = re.compile(r"\[[^\]]*\]")
REGISTRATION_FIELDS = ("first-name", "last-name", "phone", "email")


def all_screens() -> dict[str, Screen]:
    """Every screen map, ``screens/android/`` included (importing validates the strategies)."""
    found: dict[str, Screen] = {}
    for info in pkgutil.walk_packages(screens.__path__, prefix="screens."):
        if info.name.endswith("_map"):
            module = importlib.import_module(info.name)
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
        if action in ("open", "api") or target in NOT_ELEMENTS:
            continue
        if target == "registration.{{field}}":
            aliases.update(f"registration.{f}" for f in REGISTRATION_FIELDS)
            continue
        if target in PAGE_RESOLVED:
            aliases.add(target)
            continue
        aliases.add(
            PARAMS.sub("", target)
        )  # "jobs-list.card[{{job.new.jobId}}].title" → ….card.title
    return aliases


class MapHealth(unittest.TestCase):
    def setUp(self):
        self.screens = all_screens()

    def test_every_test_case_alias_resolves(self):
        for module, path in TEST_CASES.items():
            aliases = test_case_aliases(path)
            self.assertGreater(len(aliases), MIN_ALIASES[module], f"{module}: too few aliases")
            missing = []
            for alias in sorted(aliases):
                if alias in PAGE_RESOLVED:
                    continue
                screen_id, _, element = alias.partition(".")
                element, _, card_field = element.partition(".")
                if card_field and card_field not in CARD_FIELDS:
                    missing.append(alias)
                    continue
                screen = self.screens.get(screen_id)
                if screen is None or element not in screen.elements:
                    missing.append(alias)
                    continue
                screen.locator("ios", element)  # raises when the iOS locator is absent
            self.assertEqual(missing, [], f"{module}: aliases without a map entry")

    def test_page_resolved_aliases_are_still_used(self):
        used = set().union(*(test_case_aliases(p) for p in TEST_CASES.values()))
        stale = {a for a in PAGE_RESOLVED if a not in used and PARAMS.sub("", a) not in used}
        self.assertEqual(stale, set(), "stale PAGE_RESOLVED entries")

    def test_every_screen_has_an_anchor_and_ios_locators(self):
        # Android-only elements and screens (Android stage) are marked "Android only: …" and
        # checked by unit_tests/test_android_maps.py.
        for screen in self.screens.values():
            self.assertIsNotNone(screen.anchor, screen.id)
            for alias, el in screen.elements.items():
                if el.ios is None and el.note.startswith("Android only"):
                    continue
                self.assertIsNotNone(el.ios, f"{screen.id}.{alias}: no iOS locator")

    def test_static_locators_have_no_stray_braces(self):
        # A "{" outside a declared {text} placeholder would break str.format at run time.
        for screen in self.screens.values():
            for alias, el in screen.elements.items():
                if el.ios is None:
                    continue
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
