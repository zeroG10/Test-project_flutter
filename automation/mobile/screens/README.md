# screens/ — screen maps (alias → locator per platform)

Layer 2 of the automation chain ([`automation/README.md`](../../README.md)). A map is the
**only** place a locator lives: test cases name elements by alias, page objects and generated
tests resolve the alias here. Change a locator → one file changes.

## File format — `screens/<screen>_map.py`

```python
from appium.webdriver.common.appiumby import AppiumBy
from screens import El, Screen

LOGIN = Screen(
    id="login",                       # lower-kebab, stable, same as the web map id
    anchor="title",                   # alias whose visibility proves the screen is open
    elements={
        "title":  El(android=(AppiumBy.ID, "com.example.app:id/login_title"),
                     ios=(AppiumBy.ACCESSIBILITY_ID, "login-title")),
        "email":  El(android=(AppiumBy.ID, "com.example.app:id/login_email"),
                     ios=(AppiumBy.ACCESSIBILITY_ID, "login-email")),
        "submit": El(android=(AppiumBy.ACCESSIBILITY_ID, "login-submit"),
                     ios=(AppiumBy.ACCESSIBILITY_ID, "login-submit")),
    },
)
```

`AppiumBy.ID == "id"` and `AppiumBy.ACCESSIBILITY_ID == "accessibility id"` — the raw-string
form in `automation/README.md` is the same thing. One `Screen` constant per file, named in
UPPER_CASE after the screen id. Example: [`login_map.py`](login_map.py).

## Alias rules

- Fully-qualified alias is `screen.element` (`login.email`); the map key is the element part.
- Lower-kebab only: `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` — `forgot-password`, not `forgotPassword`.
  Validated when the map is imported.
- Aliases are **the same across web and mobile** for the same screen, so one test case
  serves both stacks. Name by role/meaning (`submit`, `error`), never by look (`blue-button`).
- Every screen names an `anchor` — a unique, always-present element (title, header). Pages use
  it for `assert_open()` / `is_open()`.
- An element may carry `note=` to record the id's source (testability-contract row, Figma node)
  or why a text fallback is in place.

## Locator rules

Priority (same as web): role/label → test-id / accessibility id → text. Allowed strategies:

| Strategy | Android | iOS |
|---|---|---|
| `AppiumBy.ACCESSIBILITY_ID` | `content-desc` | `accessibilityIdentifier` (falls back to label) |
| `AppiumBy.ID` | `resource-id` (`<package>:id/<name>`; Flutter: the identifier as-is) | name / label |
| `AppiumBy.ANDROID_UIAUTOMATOR` | `new UiSelector().text("Sign in")` — text fallback | — |
| `AppiumBy.IOS_PREDICATE` / `IOS_CLASS_CHAIN` | — | `label == 'Sign in'` — text fallback (class chain only with a predicate, never by index) |
| `AppiumBy.FLUTTER_INTEGRATION_*` | `flutter=` slot, integration driver only | same |

`XPATH`, `CSS_SELECTOR` and `CLASS_NAME` are rejected at import time. If the only way to reach
an element is structural, the element is missing an id: file it as a testability defect
(`docs/requirements/shared/testability-contract.md`), use a text fallback with a `note=`, and
replace it when the id ships.

## Resolving

```python
from screens import resolve
from screens.login_map import LOGIN

el = resolve(driver, platform, LOGIN, "identifier")  # WebElement, explicit presence wait
loc = LOGIN.locator("ios", "continue")                # ("-ios predicate string", "type == … 'Continue'")
```

Page objects (`pages/`) do this for you: `LoginPage(driver).tap("continue")`.

## Parametrised locators

A message known only at run time (the expected error text, the address an OTP went to) is
one alias with a `{text}` placeholder — never a locator built inside a test or a page:

```python
"error": El(ios=(AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' AND name == {text}"),
            note="parametrised by the expected message"),
```

`page.visible("error", text="Format is incorrect.")` fills it; for predicate / UiSelector
strategies the value is inserted as a quoted literal (`screens.fill`). Only `{text}` is allowed,
static values contain no braces (NSPredicate `IN {…}` → write `OR`), and a parametrised entry
carries a `note=` — checked offline by `unit_tests/test_screen_maps.py`.

## Flutter note

A Flutter app with `Semantics(identifier: "login-email", child: ...)` (Flutter ≥ 3.19) exposes
that identifier as `resource-id` on Android and `accessibilityIdentifier` on iOS. So the map is
the **same format**, driven by the **native** drivers, on **release** builds:

```python
"email": El(android=(AppiumBy.ID, "login-email"), ios=(AppiumBy.ACCESSIBILITY_ID, "login-email")),
```

Only under `FLUTTER_DRIVER=integration` (debug builds, opt-in) may an element add a `flutter=`
locator, e.g. `flutter=(AppiumBy.FLUTTER_INTEGRATION_KEY, "login_email")`. It is used instead of
the platform locator when that driver is active and ignored otherwise; elements without one fall
back to `android=` / `ios=`, which the integration driver proxies to the native driver.

## Harvesting ids from a real screen (mobile MCP)

There is no mobile crawler. Ids come from three sources, in this order:

1. **`docs/requirements/shared/testability-contract.md`** — what the dev team owes. For a
   Flutter app that is `Semantics(identifier: "login-email", child: ...)` on every element a
   test must address.
2. **The real screen**, read through the `mobile` MCP server on a booted device:
   `mobile_list_elements_on_screen` returns every element with its accessibility id, text and
   coordinates. That is how you confirm an id actually shipped and spell it exactly right.
   Verify the server first: `python3 setup/check_mcp.py mobile`.
3. **Appium Inspector** — the manual fallback when no agent is driving.

Write what you observed; leave what you did not as a placeholder. An element nobody has seen
keeps a `<...>` value so it fails loudly instead of matching something by accident — the same
rule as the web maps. Missing stable ids are a testability defect, filed against the contract,
never worked around with a coordinate tap or an XPath over the widget tree.
