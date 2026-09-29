"""Screen maps — alias → locator per platform (layer 2 in automation/README.md).

A map is the ONLY place a locator lives. Test cases
(qa/mobile/<NN-module>/<module>-test-cases.md) refer to elements by alias
(``login.email``); page objects and generated tests resolve the alias here.
Format, alias rules and the Flutter note: screens/README.md.
"""

import re
import string
from dataclasses import dataclass, field

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement

from config.settings import normalize_platform, settings
from helpers import waits
from helpers.waits import Locator

__all__ = [
    "ALLOWED_STRATEGIES",
    "EditTextByHint",
    "El",
    "Locator",
    "Screen",
    "fill",
    "locator_for",
    "resolve",
    "template_fields",
]

ALIAS = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

# Locator priority (automation/README.md): role/label → test-id / accessibility id → text.
# Structural strategies (xpath, css, class name + index) are deliberately NOT allowed —
# a missing id is a testability defect, not a reason for a brittle locator.
ALLOWED_STRATEGIES: frozenset[str] = frozenset(
    {
        AppiumBy.ACCESSIBILITY_ID,  # content-desc (Android) / accessibilityIdentifier (iOS)
        AppiumBy.ID,  # resource-id (Android); Flutter Semantics(identifier:) lands here
        AppiumBy.NAME,
        AppiumBy.ANDROID_UIAUTOMATOR,  # text / description matchers, e.g. UiSelector().text(..)
        AppiumBy.IOS_PREDICATE,  # NSPredicate, e.g. label == 'Sign in'
        AppiumBy.IOS_CLASS_CHAIN,  # only with a predicate, never by index
        AppiumBy.FLUTTER_INTEGRATION_KEY,  # the five below: FLUTTER_DRIVER=integration only
        AppiumBy.FLUTTER_INTEGRATION_SEMANTICS_LABEL,
        AppiumBy.FLUTTER_INTEGRATION_TEXT,
        AppiumBy.FLUTTER_INTEGRATION_TEXT_CONTAINING,
        AppiumBy.FLUTTER_INTEGRATION_TYPE,
    }
)


class EditTextByHint(tuple):
    """Android text field of a multi-field form, named only by its ``hint`` (TD-A1).

    As a locator it is ``className("android.widget.EditText").instance(n)`` — the field's
    position in the recon tree, checked offline by map-health. Flutter hands Android only the
    on-screen fields, so once the form scrolls, ``instance(n)`` points at another field (module
    02 run 5: TC-AUTH-014 read Email as Phone). ``helpers.waits`` therefore resolves it by
    ``hint`` among the on-screen EditTexts, on every poll.
    """

    hint: str

    def __new__(cls, instance: int, hint: str) -> "EditTextByHint":
        self = super().__new__(
            cls,
            (
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiSelector().className("android.widget.EditText").instance({instance})',
            ),
        )
        self.hint = hint
        return self


def _check_locator(owner: str, locator: object) -> None:
    if (
        not isinstance(locator, tuple)
        or len(locator) != 2
        or not all(isinstance(part, str) and part for part in locator)
    ):
        raise ValueError(f"{owner}: locator must be a (strategy, value) tuple, got {locator!r}")
    strategy = locator[0]
    if strategy not in ALLOWED_STRATEGIES:
        raise ValueError(
            f"{owner}: strategy {strategy!r} is not allowed (structural locators are banned); "
            f"use one of {sorted(ALLOWED_STRATEGIES)} — see screens/README.md"
        )


@dataclass(frozen=True)
class El:
    """One UI element, located per platform.

    ``android`` / ``ios``: locator used by the native drivers (also by the Flutter
    integration driver, which proxies native strategies). ``flutter``: optional widget
    locator (``AppiumBy.FLUTTER_INTEGRATION_*``) used ONLY under ``FLUTTER_DRIVER=integration``.
    ``note``: where the id comes from (testability-contract row, Figma node) or why a
    text fallback is in use.
    """

    android: Locator | None = None
    ios: Locator | None = None
    flutter: Locator | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.android is None and self.ios is None and self.flutter is None:
            raise ValueError("El needs at least one of android / ios / flutter")
        for name in ("android", "ios", "flutter"):
            locator = getattr(self, name)
            if locator is not None:
                _check_locator(f"El.{name}", locator)

    def for_platform(self, platform: str, *, flutter_integration: bool = False) -> Locator:
        if flutter_integration and self.flutter is not None:
            return self.flutter
        locator = getattr(self, normalize_platform(platform))
        if locator is None:
            raise LookupError(f"element has no {platform} locator")
        return locator


@dataclass(frozen=True, eq=False)
class Screen:
    """A screen: stable ``id``, its elements by alias, and the ``anchor`` that proves it is open."""

    id: str
    elements: dict[str, El] = field(default_factory=dict)
    anchor: str | None = None

    def __post_init__(self) -> None:
        if not ALIAS.match(self.id):
            raise ValueError(f"screen id {self.id!r} must be lower-kebab (e.g. 'order-list')")
        for alias in self.elements:
            if not ALIAS.match(alias):
                raise ValueError(f"{self.id}: alias {alias!r} must be lower-kebab")
        if self.anchor is not None and self.anchor not in self.elements:
            raise ValueError(f"{self.id}: anchor {self.anchor!r} is not an element of the screen")

    def qualified(self, alias: str) -> str:
        return f"{self.id}.{alias}"

    def element(self, alias: str) -> El:
        """Accepts ``email`` or the fully-qualified ``login.email``."""
        if "." in alias:
            screen_id, _, alias = alias.partition(".")
            if screen_id != self.id:
                raise LookupError(f"alias {screen_id}.{alias} does not belong to screen {self.id}")
        try:
            return self.elements[alias]
        except KeyError:
            raise LookupError(
                f"unknown alias {self.qualified(alias)}; known: {sorted(self.elements)}"
            ) from None

    def locator(self, platform: str, alias: str, *, flutter_integration: bool = False) -> Locator:
        try:
            return self.element(alias).for_platform(
                platform, flutter_integration=flutter_integration
            )
        except LookupError as exc:
            raise LookupError(f"{self.qualified(alias)}: {exc}") from None


# Strategies whose value is a query language: a parameter goes in as a quoted literal.
_QUOTED = frozenset(
    {AppiumBy.IOS_PREDICATE, AppiumBy.IOS_CLASS_CHAIN, AppiumBy.ANDROID_UIAUTOMATOR}
)


def template_fields(locator: Locator) -> set[str]:
    """Placeholders of a parametrised locator: ``name CONTAINS {text}`` -> ``{"text"}``."""
    return {name for _, name, _, _ in string.Formatter().parse(locator[1]) if name}


def fill(locator: Locator, params: dict[str, object]) -> Locator:
    """Put runtime values into a parametrised locator (e.g. an expected message text).

    A map may hold ``"error": El(ios=(IOS_PREDICATE, "name == {text}"))`` — the text is the
    expectation a step asserts, known only at run time. Values are quoted for predicate /
    UiSelector strategies, so a quote in the value cannot change the query.
    """
    strategy, value = locator
    fields = template_fields(locator)
    if fields != set(params):
        raise LookupError(
            f"locator {value!r} needs parameters {sorted(fields)}, got {sorted(params)}"
        )
    if not fields:
        return locator

    def quote(raw: object) -> str:
        text = str(raw)
        if strategy not in _QUOTED:
            return text
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'

    return strategy, value.format(**{key: quote(val) for key, val in params.items()})


def locator_for(screen: Screen, platform: str, alias: str, **params: object) -> Locator:
    """Locator for ``screen.alias`` on ``platform``, honouring FLUTTER_DRIVER from settings."""
    locator = screen.locator(
        normalize_platform(platform), alias, flutter_integration=settings.uses_flutter_integration
    )
    try:
        return fill(locator, params)
    except LookupError as exc:
        raise LookupError(f"{screen.qualified(alias)}: {exc}") from None


def resolve(
    driver: WebDriver,
    platform: str,
    screen: Screen,
    alias: str,
    timeout: float | None = None,
    **params: object,
) -> WebElement:
    """WebElement for ``screen.alias`` on ``platform``, via an explicit presence wait."""
    return waits.wait_present(driver, locator_for(screen, platform, alias, **params), timeout)
