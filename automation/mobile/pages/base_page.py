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
from dataclasses import dataclass

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
VIEW_MARGIN = 50  # points kept clear at the top (status bar) and bottom (home indicator)
# Android works in pixels (Pixel 7: 1080 x 2400): the status bar is 136 px, the app bar ends
# at 283 px, the gesture bar takes the last ~65 px.
VIEW_MARGIN_ANDROID = 150
KEYCODE_0 = 7  # Android KeyEvent.KEYCODE_0; KEYCODE_1..9 follow


def normalized(text: str | None) -> str:
    """Collapse whitespace: Flutter wraps long labels with ``\\n`` in the accessibility tree."""
    return " ".join((text or "").split())


@dataclass(frozen=True)
class Node:
    """One element of a page source, the same shape on both platforms.

    ``kind``: iOS type without ``XCUIElementType`` (``StaticText``, ``Image``, ``Button``…);
    Android class without the package (``View``, ``ImageView``, ``Button``, ``EditText``…).
    ``label``: iOS ``name``; Android ``content-desc``, else ``text`` (Flutter puts labels in
    ``content-desc``). ``value``: iOS ``value``; Android ``text`` (typed text of a field).
    ``visible``: iOS ``visible``; Android ``displayed``. Rect in the platform's units (iOS
    points, Android pixels) — compare only with other rects / window sizes of the same session.
    """

    kind: str
    label: str
    value: str
    x: int
    y: int
    width: int
    height: int
    visible: bool
    selected: bool = False
    checked: bool = False
    enabled: bool = True
    hint: str = ""
    clickable: bool = False  # Android only (iOS page sources carry no such attribute)


def _android_bounds(bounds: str) -> tuple[int, int, int, int]:
    left, top, right, bottom = (int(n) for n in bounds.replace("][", ",").strip("[]").split(","))
    return left, top, right - left, bottom - top


def page_nodes(source: str, platform: str) -> list[Node]:
    """Every element of ``source`` as a ``Node``, in document order (off-screen ones included)."""
    nodes: list[Node] = []
    for el in ET.fromstring(source).iter():
        a = el.attrib
        if platform == "ios":
            if not el.tag.startswith("XCUIElementType"):
                continue
            nodes.append(Node(
                kind=el.tag.removeprefix("XCUIElementType"), label=a.get("name") or "",
                value=a.get("value") or "", x=int(a.get("x", 0)), y=int(a.get("y", 0)),
                width=int(a.get("width", 0)), height=int(a.get("height", 0)),
                visible=a.get("visible") == "true", selected=a.get("selected") == "true",
                enabled=a.get("enabled") != "false",
            ))  # fmt: skip
            continue
        if not a.get("class") or not a.get("bounds"):
            continue
        x, y, w, h = _android_bounds(a["bounds"])
        nodes.append(Node(
            kind=a["class"].rsplit(".", 1)[-1], label=a.get("content-desc") or a.get("text") or "",
            value=a.get("text") or "", x=x, y=y, width=w, height=h,
            visible=a.get("displayed") != "false", selected=a.get("selected") == "true",
            checked=a.get("checked") == "true", enabled=a.get("enabled") != "false",
            hint=a.get("hint") or "", clickable=a.get("clickable") == "true",
        ))  # fmt: skip
    return nodes


class BasePage:
    screen: Screen  # set by every subclass
    # Android: where ``_drag`` puts the finger — left of every input (inputs start at x ≥ 42 px)
    # and inside the full-width scroll views. A page whose scroll view is inset overrides it.
    DRAG_X_ANDROID = 21

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
        elements = waits.find_all(self.driver, self.locator(alias, **params))
        return sum(1 for el in elements if el.is_displayed())

    # --- actions ----------------------------------------------------------------------

    def tap(self, alias: str, timeout: float | None = None, **params: object) -> None:
        with allure.step(f"tap {self._name(alias, params)}"):
            waits.wait_clickable(self.driver, self.locator(alias, **params), timeout).click()

    def type(
        self, alias: str, text: str, timeout: float | None = None, per_char: bool = False
    ) -> None:
        """The ``fill`` step. ``per_char`` for masked inputs: a formatter that rewrites the
        value on every keystroke drops characters typed in one burst (e.g. a phone number)."""
        with allure.step(f"fill {self.screen.qualified(alias)}"):
            element = waits.wait_present(self.driver, self.locator(alias), timeout)
            if not element.is_displayed():
                # e.g. a lower field hidden by the keyboard the previous field opened
                self.scroll_to(alias)
                element = waits.wait_visible(self.driver, self.locator(alias), timeout)
            element.click()  # focus it, as a user does: keys typed into a moving view go nowhere
            # Focusing rebuilds the Flutter widget: the old reference goes stale
            # — find the field again before touching it.
            element = waits.wait_present(self.driver, self.locator(alias), timeout)
            element.clear()
            self._send(element, text, per_char)
            element = waits.wait_present(self.driver, self.locator(alias), timeout)
            if text and not self.field_value(element):
                # Not one character landed (the view was still settling after a scroll).
                # Input plumbing, not a verdict — logged, then typed once more.
                with allure.step("no input landed → tap the field and type again"):
                    waits.wait_visible(self.driver, self.locator(alias), timeout).click()
                    element = waits.wait_present(self.driver, self.locator(alias), timeout)
                    self._send(element, text, per_char)

    def _send(self, element: WebElement, text: str, per_char: bool) -> None:
        """Type ``text`` into the focused ``element``.

        ``per_char`` on Android (the masked phone input — digits only): one key press per digit,
        ``mobile: pressKey``, injected by the UiAutomator2 server like a hardware key. Not
        ``send_keys`` — every call REPLACES the text there (ACTION_SET_TEXT) —
        and not ``mobile: type``: it switches to Appium's invisible IME and back for every call
        (~2.4 s measured), sent as one burst the formatter dropped keys ('(20450' for 2025550450),
        and Gboard popped up seconds later over the next button."""
        if per_char and self.platform == "android":
            if not text.isdigit():
                raise ValueError(f"per-char typing on Android takes digits only, got {text!r}")
            for digit in text:
                self.driver.execute_script("mobile: pressKey", {"keycode": KEYCODE_0 + int(digit)})
            return
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
                        self._settle_in_view(alias, height, **params)
                        return
                    self._drag(int(height * start), int(height * end))
            if not self.is_visible(alias, 1, **params):
                raise TimeoutException(
                    f"{self._name(alias, params)} not visible after scrolling both ways"
                )
            self._settle_in_view(alias, height, **params)

    def _settle_in_view(self, alias: str, height: int, **params: object) -> None:
        """A partly visible element is 'visible' too, and a tap on its centre can miss (e.g.
        a button cut by the screen edge). Nudge it fully into view."""
        margin = VIEW_MARGIN_ANDROID if self.platform == "android" else VIEW_MARGIN
        for _ in range(3):
            rect = waits.wait_visible(self.driver, self.locator(alias, **params), 2).rect
            top, bottom = rect["y"], rect["y"] + rect["height"]
            if bottom > height - margin:
                shift = -(bottom - (height - margin) + 20)
            elif top < margin:
                shift = margin - top + 20
            else:
                return
            middle = height // 2
            self._drag(middle, middle + int(shift))

    def _drag(self, from_y: int, to_y: int) -> None:
        """A vertical drag without a fling (move, hold, release), so the view stops where the
        finger stops. At the left margin: a drag that starts on an input does not scroll,
        and a fling overshoots the target."""
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(
            self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "finger"), duration=400
        )
        pointer = actions.w3c_actions.pointer_action
        x = self.DRAG_X_ANDROID if self.platform == "android" else 10
        # Android: a 0.3-s hold still let Flutter fling now and then (a long form measured
        # 1187 and 1305 px for an 840-px drag): hold longer there
        hold = 0.6 if self.platform == "android" else 0.3
        pointer.move_to_location(x, from_y).pointer_down()
        pointer.move_to_location(x, to_y).pause(hold).release()
        actions.perform()

    def tap_at(self, alias: str, fx: float, fy: float, **params: object) -> None:
        """Tap a point inside ``alias`` given as fractions of its bounds.

        The fallback for an element without a name: the map names the
        nearest labelled anchor, the page says where inside it the control sits. Every use
        is a testability defect with a ``note=`` in the map.
        """
        rect = self.visible(alias, **params).rect
        x = round(rect["x"] + rect["width"] * fx)
        y = round(rect["y"] + rect["height"] * fy)
        with allure.step(f"tap {self._name(alias, params)} at ({fx:.2f}, {fy:.2f}) → ({x}, {y})"):
            self.driver.tap([(x, y)])

    def tap_disabled(self, alias: str, **params: object) -> None:
        """Tap a control that is shown but disabled — to prove the tap does nothing. ``tap``
        waits for it to be clickable (shown AND enabled), which a disabled control never is
        (e.g. a disabled submit button)."""
        rect = self.rect(alias, **params)
        with allure.step(f"tap {self._name(alias, params)} (disabled)"):
            self.tap_xy(rect["x"] + rect["width"] / 2, rect["y"] + rect["height"] / 2)

    def tap_xy(self, x: float, y: float) -> None:
        """A tap at a screen point (session units). iOS: ``mobile: tap`` as proven on the
        simulator; Android: ``mobile: clickGesture`` (``mobile: tap`` is XCUITest-only)."""
        if self.platform == "android":
            self.driver.execute_script("mobile: clickGesture", {"x": int(x), "y": int(y)})
            return
        self.driver.execute_script("mobile: tap", {"x": x, "y": y})

    def drag_xy(self, x1: float, y1: float, x2: float, y2: float, duration: float = 0.3) -> None:
        """A drag between two screen points. iOS: ``mobile: dragFromToForDuration`` (as proven);
        Android: ``mobile: dragGesture`` with a speed that covers the distance in ``duration``."""
        if self.platform == "android":
            distance = max(1.0, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
            self.driver.execute_script("mobile: dragGesture", {
                "startX": int(x1), "startY": int(y1), "endX": int(x2), "endY": int(y2),
                "speed": int(distance / max(duration, 0.05))})  # fmt: skip
            return
        self.driver.execute_script("mobile: dragFromToForDuration", {
            "duration": duration, "fromX": x1, "fromY": y1, "toX": x2, "toY": y2})  # fmt: skip

    def nodes(self, source: str | None = None) -> list[Node]:
        """The page source as ``Node`` rows (``page_nodes``) — one read of the tree."""
        return page_nodes(source if source is not None else self.driver.page_source, self.platform)

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
        element = waits.wait_visible(self.driver, self.locator(alias, **params), timeout)
        return self.label_of(element) if self.platform == "android" else element.text

    def label_of(self, element: WebElement) -> str:
        """What the element says: iOS ``name``; Android ``content-desc``, else ``text`` — a
        Flutter label is in ``content-desc`` and ``.text`` is empty there."""
        if self.platform == "android":
            return self._attr(element, "content-desc") or self._attr(element, "text")
        return element.get_attribute("name") or ""

    def _attr(self, element: WebElement, name: str) -> str:
        """An attribute as text. UiAutomator2 answers the STRING 'null' for an attribute a native
        view does not have (a system dialog's TextView has no content-desc, so
        label_of would read 'null' instead of the text); Flutter nodes rarely lack one."""
        value = element.get_attribute(name)
        return "" if value is None or (self.platform == "android" and value == "null") else value

    def is_on(self, element: WebElement) -> bool:
        """A switch / radio / checkbox / chip is on: iOS ``value == "1"``; Android ``checked``
        (checkable elements) or ``selected``."""
        if self.platform == "android":
            return "true" in (element.get_attribute("checked"), element.get_attribute("selected"))
        return str(element.get_attribute("value") or "") == "1"

    def placeholder_of(self, element: WebElement) -> str:
        """An empty input's placeholder: iOS ``name``; Android ``hint``."""
        return self._attr(element, "hint" if self.platform == "android" else "name")

    def field_value(self, element: WebElement) -> str:
        """Typed text of an input: iOS ``value``; Android ``text`` (``value`` does not exist
        there — UiAutomator2 raises UnknownMethodException)."""
        return self._attr(element, "text" if self.platform == "android" else "value")

    def expect_text(
        self, alias: str, text: str, timeout: float | None = None, **params: object
    ) -> None:
        """The ``expect-text`` step: the element's text contains ``text``, whitespace-normalized."""
        wanted = normalized(text)
        locator = self.locator(alias, **params)

        def contains(driver: WebDriver) -> bool:
            with contextlib.suppress(WebDriverException):
                element = waits.find(driver, locator)
                shown = self.label_of(element) if self.platform == "android" else element.text
                return element.is_displayed() and wanted in normalized(shown)
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
                element = waits.find(driver, locator)
                return element.is_displayed() and element.is_enabled() == enabled
            return False

        with allure.step(f"expect {self.screen.qualified(alias)} {state}"):
            waits.wait_until(self.driver, in_state, timeout, f"{locator} not {state}")

    def expect_disabled(self, alias: str, timeout: float | None = None) -> None:
        self.expect_enabled(alias, enabled=False, timeout=timeout)

    def value(self, alias: str, **params: object) -> str:
        """``value`` attribute (switch / radio state on iOS: ``"1"`` = on / selected).

        Android has no ``value``: a checkable element answers ``"1"`` / ``"0"`` from ``checked``
        (or ``selected``), any other element its ``text`` — the same contract for the callers."""
        element = self.find(alias, **params)
        if self.platform != "android":
            return str(element.get_attribute("value") or "")
        if element.get_attribute("checkable") == "true":
            return "1" if element.get_attribute("checked") == "true" else "0"
        if element.get_attribute("selected") == "true":
            return "1"
        return self._attr(element, "text")

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
        text element without an id. The field's own label is excluded.
        """
        box = self.rect(alias, **params)
        own = normalized(self.label_of(self.find(alias, **params)))
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
        # Android twin of iOS StaticText: plain, non-interactive text. The phone field holds the
        # country-code Button ('United States + 1\n+ 1') inside its bounds.
        if a.get("displayed") == "false" or not a.get("bounds") or a.get("clickable") == "true":
            return "", None
        if a.get("class") in ("android.widget.Button", "android.widget.EditText"):
            return "", None
        left, top, right, bottom = (
            int(n) for n in a["bounds"].replace("][", ",").strip("[]").split(",")
        )
        return a.get("text") or a.get("content-desc") or "", (left, top, right - left, bottom - top)
