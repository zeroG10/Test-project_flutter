"""Base page object: alias-level actions over a screen map, with explicit waits only.

Pages never hold locators. A page names its ``screen`` (``screens/<x>_map.py``) and acts on
element aliases; the map resolves each alias to a ``(strategy, value)`` for the platform of
the live session. Every action waits explicitly (helpers/waits.py) — no sleeps, no implicit wait.

A parametrised alias (``"error": El(ios=(IOS_PREDICATE, "name == {text}"))``) takes its value
as a keyword: ``page.visible("error", text="Format is incorrect.")``.

Step vocabulary of the test cases → methods here:
``click`` tap · ``fill`` type · ``expect-visible`` visible · ``expect-hidden`` wait_gone ·
``expect-text`` expect_text · ``expect-enabled`` / ``expect-disabled`` · ``scroll-to`` ·
``back`` go_back · positional expectations (``below``, ``centred``, ``bottom area``) —
expect_below / expect_centred / expect_in_bottom_area, from element bounds.
"""

import contextlib
import io
import xml.etree.ElementTree as ET

import allure
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from config.settings import normalize_platform
from helpers import pixels, waits
from helpers.device import platform_of
from helpers.waits import Locator
from screens import Screen, locator_for

# Positional expectations (test-case conventions): 2 % of the screen width for "centred";
# "bottom area" = the lower third of the screen.
CENTRE_TOLERANCE = 0.02
BOTTOM_AREA = 1 / 3
SCROLL_ATTEMPTS = 6


def normalized(text: str | None) -> str:
    """Collapse whitespace: Flutter wraps long labels with ``\\n`` in the accessibility tree."""
    return " ".join((text or "").split())


class BasePage:
    screen: Screen  # set by every subclass

    def __init__(self, driver: WebDriver, platform: str | None = None):
        if getattr(self, "screen", None) is None:
            raise TypeError(f"{type(self).__name__} must set `screen` to a Screen map")
        self.driver = driver
        self.platform = normalize_platform(platform) if platform else platform_of(driver)

    def _name(self, alias: str, params: dict) -> str:
        suffix = f"[{', '.join(f'{v}' for v in params.values())}]" if params else ""
        return f"{self.screen.qualified(alias)}{suffix}"

    # --- resolution -------------------------------------------------------------------

    def locator(self, alias: str, **params: object) -> Locator:
        return locator_for(self.screen, self.platform, alias, **params)

    def find(self, alias: str, timeout: float | None = None, **params: object) -> WebElement:
        """Element is present (may be hidden)."""
        return waits.wait_present(self.driver, self.locator(alias, **params), timeout)

    def visible(self, alias: str, timeout: float | None = None, **params: object) -> WebElement:
        """Element is displayed — the ``expect-visible`` step."""
        with allure.step(f"expect {self._name(alias, params)} visible"):
            return waits.wait_visible(self.driver, self.locator(alias, **params), timeout)

    def count_visible(self, alias: str, **params: object) -> int:
        """How many displayed elements match (e.g. "the only input on the screen")."""
        elements = self.driver.find_elements(*self.locator(alias, **params))
        return sum(1 for el in elements if el.is_displayed())

    # --- actions ----------------------------------------------------------------------

    def tap(self, alias: str, timeout: float | None = None, **params: object) -> None:
        with allure.step(f"tap {self._name(alias, params)}"):
            waits.wait_clickable(self.driver, self.locator(alias, **params), timeout).click()

    def type(
        self, alias: str, text: str, timeout: float | None = None, per_char: bool = False
    ) -> None:
        """The ``fill`` step. ``per_char`` for masked inputs: a formatter that rewrites the
        value on every keystroke drops characters typed in one burst (phone, recon 3d)."""
        with allure.step(f"fill {self.screen.qualified(alias)}"):
            element = waits.wait_present(self.driver, self.locator(alias), timeout)
            if not element.is_displayed():
                # e.g. a lower field hidden by the keyboard the previous field opened (recon 3d)
                self.scroll_to(alias)
                element = waits.wait_visible(self.driver, self.locator(alias), timeout)
            element.click()  # focus it, as a user does: keys typed into a moving view go nowhere
            element.clear()
            self._send(element, text, per_char)
            if text and not element.get_attribute("value"):
                # Not one character landed (the view was still settling after a scroll,
                # recon 3d). Input plumbing, not a verdict — logged, then typed once more.
                with allure.step("no input landed → tap the field and type again"):
                    element = waits.wait_visible(self.driver, self.locator(alias), timeout)
                    element.click()
                    self._send(element, text, per_char)

    @staticmethod
    def _send(element: WebElement, text: str, per_char: bool) -> None:
        for chunk in text if per_char else (text,):
            element.send_keys(chunk)

    def clear(self, alias: str, timeout: float | None = None) -> None:
        with allure.step(f"clear {self.screen.qualified(alias)}"):
            waits.wait_visible(self.driver, self.locator(alias), timeout).clear()

    def hide_keyboard(self) -> None:
        """Best effort: iOS raises when no keyboard is shown, which is not a failure."""
        with contextlib.suppress(WebDriverException):
            self.driver.hide_keyboard()

    def scroll_to(self, alias: str, attempts: int = SCROLL_ATTEMPTS, **params: object) -> None:
        """The ``scroll-to`` step: short drags until the element is displayed — first towards
        the end of the content, then back (an element above the view is found too)."""
        with allure.step(f"scroll to {self._name(alias, params)}"):
            height = self.driver.get_window_size()["height"]
            # Upper half only: an open keyboard covers the lower third of the screen.
            for start, end in ((0.55, 0.35), (0.3, 0.5)):
                for _ in range(attempts):
                    if self.is_visible(alias, 0.5, **params):
                        return
                    self._drag(int(height * start), int(height * end))
            if not self.is_visible(alias, 1, **params):
                raise TimeoutException(
                    f"{self._name(alias, params)} not visible after scrolling both ways"
                )

    def _drag(self, from_y: int, to_y: int) -> None:
        """A vertical drag without a fling (move, hold, release), so the view stops where the
        finger stops. At the left margin: a drag that starts on an input does not scroll,
        and a fling overshoots the target (recon 3d)."""
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(
            self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "finger"), duration=400
        )
        pointer = actions.w3c_actions.pointer_action
        pointer.move_to_location(10, from_y).pointer_down()
        pointer.move_to_location(10, to_y).pause(0.3).release()
        actions.perform()

    def tap_at(self, alias: str, fx: float, fy: float, **params: object) -> None:
        """Tap a point inside ``alias`` given as fractions of its bounds.

        The fallback for an element without a name (decision 2026-09-23): the map names the
        nearest labelled anchor, the page says where inside it the control sits. Every use
        is a testability defect with a ``note=`` in the map.
        """
        rect = self.visible(alias, **params).rect
        x = round(rect["x"] + rect["width"] * fx)
        y = round(rect["y"] + rect["height"] * fy)
        with allure.step(f"tap {self._name(alias, params)} at ({fx:.2f}, {fy:.2f}) → ({x}, {y})"):
            self.driver.tap([(x, y)])

    def go_back(self) -> None:
        """The ``back`` step: system back on Android, edge swipe on iOS (no system button)."""
        with allure.step("back (system)"):
            if self.platform == "android":
                self.driver.back()
                return
            size = self.driver.get_window_size()
            y = size["height"] // 2
            actions = ActionChains(self.driver)
            # Edge swipe: every pointer move of this builder lasts 300 ms.
            actions.w3c_actions = ActionBuilder(
                self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "finger"), duration=300
            )
            pointer = actions.w3c_actions.pointer_action
            pointer.move_to_location(2, y).pointer_down()
            pointer.move_to_location(int(size["width"] * 0.8), y).release()
            actions.perform()

    # --- expectations -----------------------------------------------------------------

    def text(self, alias: str, timeout: float | None = None, **params: object) -> str:
        return waits.wait_visible(self.driver, self.locator(alias, **params), timeout).text

    def expect_text(
        self, alias: str, text: str, timeout: float | None = None, **params: object
    ) -> None:
        """The ``expect-text`` step: the element's text contains ``text``, whitespace-normalized."""
        wanted = normalized(text)
        locator = self.locator(alias, **params)

        def contains(driver: WebDriver) -> bool:
            with contextlib.suppress(WebDriverException):
                element = driver.find_element(*locator)
                return element.is_displayed() and wanted in normalized(element.text)
            return False

        with allure.step(f"expect {self._name(alias, params)} contains {text!r}"):
            waits.wait_until(self.driver, contains, timeout, f"{locator} does not show {text!r}")

    def expect_enabled(
        self, alias: str, enabled: bool = True, timeout: float | None = None
    ) -> None:
        """The ``expect-enabled`` / ``expect-disabled`` steps (visible AND in that state)."""
        locator = self.locator(alias)
        state = "enabled" if enabled else "disabled"

        def in_state(driver: WebDriver) -> bool:
            with contextlib.suppress(WebDriverException):
                element = driver.find_element(*locator)
                return element.is_displayed() and element.is_enabled() == enabled
            return False

        with allure.step(f"expect {self.screen.qualified(alias)} {state}"):
            waits.wait_until(self.driver, in_state, timeout, f"{locator} not {state}")

    def expect_disabled(self, alias: str, timeout: float | None = None) -> None:
        self.expect_enabled(alias, enabled=False, timeout=timeout)

    def value(self, alias: str, **params: object) -> str:
        """``value`` attribute (switch / radio state on iOS: ``"1"`` = on / selected)."""
        return str(self.find(alias, **params).get_attribute("value") or "")

    def is_visible(self, alias: str, timeout: float | None = None, **params: object) -> bool:
        """Non-raising probe for branching. For assertions use ``visible`` / ``wait_gone``."""
        return waits.is_visible(self.driver, self.locator(alias, **params), timeout)

    def wait_gone(self, alias: str, timeout: float | None = None, **params: object) -> None:
        """The ``expect-hidden`` step: raises if the element is still visible."""
        with allure.step(f"expect {self._name(alias, params)} hidden"):
            waits.wait_gone(self.driver, self.locator(alias, **params), timeout)

    def assert_open(self, timeout: float | None = None) -> None:
        """The screen's anchor element is visible; raises TimeoutException otherwise."""
        if self.screen.anchor is None:
            raise ValueError(f"screen {self.screen.id!r} defines no anchor")
        with allure.step(f"expect screen {self.screen.id} open"):
            waits.wait_visible(self.driver, self.locator(self.screen.anchor), timeout)

    def is_open(self, timeout: float | None = None) -> bool:
        if self.screen.anchor is None:
            raise ValueError(f"screen {self.screen.id!r} defines no anchor")
        return self.is_visible(self.screen.anchor, timeout)

    # --- position (from bounds; test-case conventions) -------------------------------------

    def rect(self, alias: str, **params: object) -> dict:
        return self.visible(alias, **params).rect

    def expect_centred(self, alias: str, tolerance: float = CENTRE_TOLERANCE) -> None:
        width = self.driver.get_window_size()["width"]
        rect = self.rect(alias)
        offset = abs(rect["x"] + rect["width"] / 2 - width / 2)
        with allure.step(f"expect {self.screen.qualified(alias)} centred (offset {offset:.1f}pt)"):
            assert offset <= width * tolerance, (
                f"{self.screen.qualified(alias)} is {offset:.1f}pt off centre "
                f"(tolerance {width * tolerance:.1f}pt)"
            )

    def expect_below(self, alias: str, other: str) -> None:
        """``alias`` starts at or below the bottom edge of ``other`` (same screen)."""
        top, upper = self.rect(alias), self.rect(other)
        upper_bottom = upper["y"] + upper["height"]
        with allure.step(f"expect {self.screen.qualified(alias)} below {other}"):
            assert top["y"] >= upper_bottom - 1, (
                f"{self.screen.qualified(alias)} (y={top['y']}) is not below {other} "
                f"(bottom={upper_bottom})"
            )

    def expect_in_bottom_area(self, alias: str, fraction: float = BOTTOM_AREA) -> None:
        height = self.driver.get_window_size()["height"]
        rect = self.rect(alias)
        with allure.step(f"expect {self.screen.qualified(alias)} in the bottom area"):
            assert rect["y"] >= height * (1 - fraction), (
                f"{self.screen.qualified(alias)} (y={rect['y']}) is above the bottom "
                f"{fraction:.0%} of the screen (height {height})"
            )

    # --- what is really drawn (for elements the tree misreports) ------------------------

    def ink_ratio(self, alias: str, **params: object) -> float:
        """Share of the element's box on the screenshot that is not background (helpers/pixels)."""
        box = self.find(alias, **params).rect
        png = self.driver.get_screenshot_as_png()
        scale = pixels.Image.open(io.BytesIO(png)).width / self.driver.get_window_size()["width"]
        return pixels.ink_ratio(png, box, scale)

    def expect_drawn(
        self, alias: str, drawn: bool = True, timeout: float | None = None, **params: object
    ) -> None:
        """``expect-visible`` / ``expect-hidden`` decided by pixels, not by the tree."""
        state = "drawn" if drawn else "not drawn"
        last: list[float] = []

        def in_state(_driver: WebDriver) -> bool:
            last.append(self.ink_ratio(alias, **params))
            return (last[-1] >= pixels.MIN_INK_RATIO) == drawn

        with allure.step(f"expect {self._name(alias, params)} {state} on screen (pixels)"):
            waits.wait_until(
                self.driver,
                in_state,
                timeout,
                f"{self._name(alias, params)} not {state}: ink ratio {last[-1] if last else '-'}",
            )
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"{self.screen.qualified(alias)} {state} (ink {last[-1]:.3f})",
                attachment_type=allure.attachment_type.PNG,
            )

    # --- texts inside an element (validation messages drawn inside a field) --------------

    def texts_within(self, alias: str, **params: object) -> list[str]:
        """Visible texts whose bounds lie inside ``alias`` — from ONE page-source read.

        Flutter draws a field's validation message inside the field's bounds, as a separate
        text element without an id (recon 3c). The field's own label is excluded.
        """
        box = self.rect(alias, **params)
        own = normalized(self.find(alias, **params).get_attribute("name"))
        found: list[str] = []
        for node in ET.fromstring(self.driver.page_source).iter():
            text, bounds = self._text_and_bounds(node)
            if not text or bounds is None or normalized(text) == own:
                continue
            x, y, w, h = bounds
            inside = (
                x >= box["x"] - 1
                and y >= box["y"] - 1
                and x + w <= box["x"] + box["width"] + 1
                and y + h <= box["y"] + box["height"] + 1
            )
            if inside and w > 0 and h > 0:
                found.append(normalized(text))
        return found

    def _text_and_bounds(self, node: ET.Element) -> tuple[str, tuple[int, int, int, int] | None]:
        a = node.attrib
        if self.platform == "ios":
            if node.tag != "XCUIElementTypeStaticText" or a.get("visible") != "true":
                return "", None
            return a.get("name") or "", (
                int(a.get("x", 0)),
                int(a.get("y", 0)),
                int(a.get("width", 0)),
                int(a.get("height", 0)),
            )
        if a.get("displayed") == "false" or not a.get("bounds"):
            return "", None
        left, top, right, bottom = (
            int(n) for n in a["bounds"].replace("][", ",").strip("[]").split(",")
        )
        return a.get("text") or a.get("content-desc") or "", (left, top, right - left, bottom - top)
