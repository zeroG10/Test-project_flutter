"""Explicit waits on ``WebDriverWait``. No sleeps — automation/README.md, "Determinism rules".

Every helper takes a locator tuple ``(strategy, value)`` — normally produced by a screen map
(``screens/``) — and a timeout in seconds; ``None`` means ``settings.default_timeout``.
Page objects (``pages/``) call these; tests rarely need them directly.
The driver fixture sets NO implicit wait, so these are the only waits in play.
"""

from collections.abc import Callable
from typing import TypeVar

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings

Locator = tuple[str, str]
T = TypeVar("T")


def _seconds(timeout: float | None) -> float:
    return settings.default_timeout if timeout is None else timeout


# UiAutomator2 cannot read the tree while the app's main thread is busy (a debug Flutter build's
# cold start, a starved emulator): "Timed out … waiting for the root AccessibilityNodeInfo in the
# active window". Inside a wait that is "not yet", like a missing element — the wait's own timeout
# still decides (Android stage, module 02 run 1: TC-AUTH-004 errored at its first probe).
_TREE_NOT_READY = ("waiting for the root AccessibilityNodeInfo",)


def _not_yet_when_tree_busy(condition: Callable[[WebDriver], T]) -> Callable[[WebDriver], T]:
    def probe(driver: WebDriver):
        try:
            return condition(driver)
        except WebDriverException as exc:
            if any(marker in str(exc) for marker in _TREE_NOT_READY):
                return False
            raise

    return probe


# --- finding (one place; a hinted Android field is looked up by its hint) ------------------

_EDIT_TEXTS = (
    AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().className("android.widget.EditText")',
)
_GONE_OR_STALE = (NoSuchElementException, StaleElementReferenceException)


def _hint(locator: Locator) -> str | None:
    """The hint of a ``screens.EditTextByHint`` locator; None for every other locator."""
    return getattr(locator, "hint", None)


def find_all(driver: WebDriver, locator: Locator) -> list[WebElement]:
    """All matches of ``locator``. A hinted field: the on-screen EditTexts with that hint."""
    hint = _hint(locator)
    if hint is None:
        return driver.find_elements(*locator)
    return [el for el in driver.find_elements(*_EDIT_TEXTS) if el.get_attribute("hint") == hint]


def find(driver: WebDriver, locator: Locator) -> WebElement:
    """The first match of ``locator``; raises NoSuchElementException like ``find_element``."""
    if _hint(locator) is None:
        return driver.find_element(*locator)
    found = find_all(driver, locator)
    if not found:
        raise NoSuchElementException(f"no on-screen EditText with hint {_hint(locator)!r}")
    return found[0]


def _hinted(locator: Locator, check: Callable[[WebElement], bool]) -> Callable[[WebDriver], object]:
    """A wait condition for a hinted field: the element when ``check`` holds, else False."""

    def probe(driver: WebDriver):
        try:
            element = find(driver, locator)
            return element if check(element) else False
        except _GONE_OR_STALE:
            return False

    return probe


def _gone(locator: Locator) -> Callable[[WebDriver], bool]:
    def probe(driver: WebDriver) -> bool:
        try:
            return not find(driver, locator).is_displayed()
        except _GONE_OR_STALE:
            return True

    return probe


def wait_until(
    driver: WebDriver,
    condition: Callable[[WebDriver], T],
    timeout: float | None = None,
    message: str = "",
    poll: float = 0.5,
) -> T:
    """Generic explicit wait: polls ``condition`` every ``poll`` s until it returns a truthy
    value."""
    secs = _seconds(timeout)
    return WebDriverWait(driver, secs, poll_frequency=poll).until(
        _not_yet_when_tree_busy(condition), message=message or f"condition not met within {secs}s"
    )


def wait_present(driver: WebDriver, locator: Locator, timeout: float | None = None) -> WebElement:
    """Element exists in the hierarchy (may be off-screen or hidden)."""
    return wait_until(
        driver,
        EC.presence_of_element_located(locator)
        if _hint(locator) is None
        else _hinted(locator, lambda _el: True),
        timeout,
        f"{locator} not present within {_seconds(timeout)}s",
    )


def wait_visible(driver: WebDriver, locator: Locator, timeout: float | None = None) -> WebElement:
    """Element exists and is displayed."""
    return wait_until(
        driver,
        EC.visibility_of_element_located(locator)
        if _hint(locator) is None
        else _hinted(locator, lambda el: el.is_displayed()),
        timeout,
        f"{locator} not visible within {_seconds(timeout)}s",
    )


def wait_clickable(driver: WebDriver, locator: Locator, timeout: float | None = None) -> WebElement:
    """Element is displayed and enabled — use before every tap."""
    return wait_until(
        driver,
        EC.element_to_be_clickable(locator)
        if _hint(locator) is None
        else _hinted(locator, lambda el: el.is_displayed() and el.is_enabled()),
        timeout,
        f"{locator} not clickable within {_seconds(timeout)}s",
    )


def wait_gone(driver: WebDriver, locator: Locator, timeout: float | None = None) -> None:
    """Element is absent or hidden (the ``expect-hidden`` step). Raises if it stays visible."""
    wait_until(
        driver,
        EC.invisibility_of_element_located(locator) if _hint(locator) is None else _gone(locator),
        timeout,
        f"{locator} still visible after {_seconds(timeout)}s",
    )


def wait_text(
    driver: WebDriver, locator: Locator, text: str, timeout: float | None = None
) -> WebElement:
    """Element's text contains ``text`` (the ``expect-text`` step)."""
    wait_until(
        driver,
        EC.text_to_be_present_in_element(locator, text)
        if _hint(locator) is None
        else _hinted(locator, lambda el: text in (el.text or "")),
        timeout,
        f"{locator} does not contain {text!r} within {_seconds(timeout)}s",
    )
    return find(driver, locator)


def wait_any(
    driver: WebDriver, probes: dict[str, Callable[[], bool]], timeout: float | None = None
) -> str:
    """Name of the first probe that turns true — e.g. which screen a cold start landed on.

    Probes must be instant (``page.is_open(0)``); the wait polls them together.
    """

    def first_true(_driver: WebDriver) -> str | bool:
        return next((name for name, probe in probes.items() if probe()), False)

    return wait_until(
        driver,
        first_true,
        timeout,
        f"none of {sorted(probes)} within {_seconds(timeout)}s",
    )


def is_visible(driver: WebDriver, locator: Locator, timeout: float | None = None) -> bool:
    """Non-raising probe for branching logic. For assertions use wait_visible / wait_gone."""
    try:
        wait_visible(driver, locator, timeout)
    except TimeoutException:
        return False
    return True


def focused(driver: WebDriver, timeout: float = 5.0):
    """The focused element, waiting while WebDriverAgent cannot name it yet — right after a tap
    on a Flutter field it may answer "unable to find an element using '(null)'" (stable run on
    7673885, TC-SRV-002)."""

    def probe(d):
        try:
            return d.switch_to.active_element
        except WebDriverException:
            return False

    return wait_until(driver, probe, timeout, "no focused element")
