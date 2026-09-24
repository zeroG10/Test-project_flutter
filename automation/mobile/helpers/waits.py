"""Explicit waits on ``WebDriverWait``. No sleeps — automation/README.md, "Determinism rules".

Every helper takes a locator tuple ``(strategy, value)`` — normally produced by a screen map
(``screens/``) — and a timeout in seconds; ``None`` means ``settings.default_timeout``.
Page objects (``pages/``) call these; tests rarely need them directly.
The driver fixture sets NO implicit wait, so these are the only waits in play.
"""

from collections.abc import Callable
from typing import TypeVar

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings

Locator = tuple[str, str]
T = TypeVar("T")


def _seconds(timeout: float | None) -> float:
    return settings.default_timeout if timeout is None else timeout


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
        condition, message=message or f"condition not met within {secs}s"
    )


def wait_present(driver: WebDriver, locator: Locator, timeout: float | None = None) -> WebElement:
    """Element exists in the hierarchy (may be off-screen or hidden)."""
    return wait_until(
        driver,
        EC.presence_of_element_located(locator),
        timeout,
        f"{locator} not present within {_seconds(timeout)}s",
    )


def wait_visible(driver: WebDriver, locator: Locator, timeout: float | None = None) -> WebElement:
    """Element exists and is displayed."""
    return wait_until(
        driver,
        EC.visibility_of_element_located(locator),
        timeout,
        f"{locator} not visible within {_seconds(timeout)}s",
    )


def wait_clickable(driver: WebDriver, locator: Locator, timeout: float | None = None) -> WebElement:
    """Element is displayed and enabled — use before every tap."""
    return wait_until(
        driver,
        EC.element_to_be_clickable(locator),
        timeout,
        f"{locator} not clickable within {_seconds(timeout)}s",
    )


def wait_gone(driver: WebDriver, locator: Locator, timeout: float | None = None) -> None:
    """Element is absent or hidden (the ``expect-hidden`` step). Raises if it stays visible."""
    wait_until(
        driver,
        EC.invisibility_of_element_located(locator),
        timeout,
        f"{locator} still visible after {_seconds(timeout)}s",
    )


def wait_text(
    driver: WebDriver, locator: Locator, text: str, timeout: float | None = None
) -> WebElement:
    """Element's text contains ``text`` (the ``expect-text`` step)."""
    wait_until(
        driver,
        EC.text_to_be_present_in_element(locator, text),
        timeout,
        f"{locator} does not contain {text!r} within {_seconds(timeout)}s",
    )
    return driver.find_element(*locator)


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
