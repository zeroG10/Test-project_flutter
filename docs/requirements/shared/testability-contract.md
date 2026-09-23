# Testability contract — stable ids the dev team must ship

Shared requirement (applies to web, Android, iOS and Flutter clients). QA automation
locates elements ONLY through the ids below (see [automation/README.md](../../../automation/README.md),
"Locator priority"). Text, structure (CSS/XPath) and position are not locators.
**Acceptance rule: a screen without ids is not ready for QA** — it is returned as a
testability defect, not tested by hand around the gap.

## 1. Id conventions per platform

| Platform | Mechanism | Format | Example |
|---|---|---|---|
| Web | `data-testid` attribute | `<screen>-<element>` | `<button data-testid="login-submit">` |
| Android (View) | `android:id` (→ `resource-id`) **and/or** `contentDescription` | `<screen>_<element>` / `<screen>-<element>` | `android:id="@+id/login_submit"` |
| Android (Compose) | `Modifier.testTag("<screen>-<element>")` **with** `testTagsAsResourceId = true` on the root `Modifier.semantics` so tags surface as `resource-id` to UiAutomator2 | `<screen>-<element>` | `Modifier.testTag("login-submit")` |
| iOS (UIKit) | `accessibilityIdentifier` | `<screen>-<element>` | `button.accessibilityIdentifier = "login-submit"` |
| iOS (SwiftUI) | `.accessibilityIdentifier("<screen>-<element>")` | `<screen>-<element>` | `Button(...).accessibilityIdentifier("login-submit")` |
| Flutter (≥ 3.19) | `Semantics(identifier: "<screen>-<element>", child: …)` — exposed to native drivers as `resource-id` (Android) and `accessibilityIdentifier` (iOS) | `<screen>-<element>` | `Semantics(identifier: 'login-submit', child: ElevatedButton(...))` |

`<screen>` and `<element>` are lower-kebab, ASCII, stable identifiers of the screen and the
element's purpose (`order-form-save`), never its label, colour, index or layout.
`accessibilityLabel` / `contentDescription` used for screen readers stays a human string and
is NOT a substitute for the id (it is localized and changes).

## 2. Rules

1. **Stable.** An id never changes when copy, styling, layout, or locale changes. Renaming
   an id is a breaking change and must be announced to QA before merge.
2. **Not text-based.** Ids are not derived from visible text or translations.
3. **Every screen carries a root id** `<screen>-root` on its container, present as long as
   the screen is on top. Tests use it to assert "I am on screen X".
4. **List items carry the entity id**: `<screen>-row-<entityId>` (e.g. `orders-row-8f3a`),
   and the actionable controls inside a row are `<screen>-row-<entityId>-<action>`. Index-based
   ids (`row-0`) are not accepted.
5. **Every error, toast, snackbar, banner, validation message and empty state has an id**:
   `<screen>-error`, `<screen>-<field>-error`, `<screen>-toast`, `<screen>-empty-state`.
   A message that cannot be located cannot be asserted.
6. **Every loading indicator has an id** (`<screen>-spinner`, `<screen>-skeleton`) so tests
   wait for it to disappear instead of sleeping.
7. **Interactive elements** (inputs, buttons, links, switches, tabs, menu items, dialog
   actions) all carry ids. Decorative elements do not need one.
8. **Dialogs / sheets / modals** are screens: `<dialog>-root`, `<dialog>-confirm`, `<dialog>-cancel`.
9. Ids are shipped in **release builds** (they are not debug-only); Flutter identifiers must
   not be stripped by `--no-tree-shake` settings or semantics being disabled.
10. Missing or unstable ids found during map authoring or test generation are logged as a
    testability defect (bug report in `qa/{web,mobile}/<NN-module>/bugs/`, category "testability") and
    the affected checks stay **Blocked**, never Passed.

## 3. Handshake with screen maps — aliases → ids

Test cases use platform-neutral aliases `screen.element` (`qa/_templates/test-case-format.md`). The
screen map resolves an alias to the platform id. The dev team delivers the right-hand
columns; QA owns the alias column. Fill this table per screen when a feature is handed
over (a copy of the filled table goes to the map author).

| Alias (TC) | Web `data-testid` | Android `resource-id` / testTag | iOS `accessibilityIdentifier` | Flutter `Semantics(identifier:)` |
|---|---|---|---|---|
| `login.root` | `login-root` | `login-root` | `login-root` | `login-root` |
| `login.email` | `login-email` | `login-email` | `login-email` | `login-email` |
| `login.password` | `login-password` | `login-password` | `login-password` | `login-password` |
| `login.submit` | `login-submit` | `login-submit` | `login-submit` | `login-submit` |
| `login.error` | `login-error` | `login-error` | `login-error` | `login-error` |
| `login.spinner` | `login-spinner` | `login-spinner` | `login-spinner` | `login-spinner` |
| `orders.row[{{order.id}}]` | `orders-row-{{order.id}}` | `orders-row-{{order.id}}` | `orders-row-{{order.id}}` | `orders-row-{{order.id}}` |
| `orders.empty-state` | `orders-empty-state` | `orders-empty-state` | `orders-empty-state` | `orders-empty-state` |

Notes:
- Android View-based apps may deliver `android:id` values instead (`com.example.app:id/login_submit`);
  the map records the full resource-id. Compose and Flutter deliver the kebab tag as-is.
- Where a role + accessible name is the strongest locator on web (a `button` named
  "Sign in"), the map may prefer it; the `data-testid` is still required as the fallback.
- One alias, one id per platform. If a platform does not have the element (feature parity
  gap), the cell says `n/a` and the TC's Platforms row must not list that platform.
- `<screen>-root` is what the mobile map uses as the screen `anchor` (`assert_open()`), so it
  must be present on the top-level container for the whole life of the screen.

## 4. Definition of done for a feature hand-over

- [ ] Every screen of the feature has `<screen>-root`.
- [ ] Every interactive element, error, toast, empty state and spinner has an id per §2.
- [ ] Lists expose the entity id on rows.
- [ ] The alias → id table (§3) for the feature is filled and attached to the ticket.
- [ ] Ids verified present in the build QA receives (web: DevTools; Android: `uiautomatorviewer` /
      Appium Inspector; iOS: Accessibility Inspector / Appium Inspector).

## 5. Project log — Concert Technologies Field Services, mobile (Flutter)

State of the build QA received (`[DEV] CT Mobile` 1.1.1 (178)), found while writing the screen maps
(step 5, 2026-09-23). **Owner decision 2026-09-23:** the app is not changed for testing; with
`Semantics(identifier:)` absent everywhere, the visible texts serve as locators (one language, stable
copy), and every element without a text is a testability defect below. Checks that cannot be reached
around a defect stay **Blocked**, never Passed.

| ID | Where | What is missing | Workaround in the map (`note=`) | Checks affected |
|---|---|---|---|---|
| TD-ALL-001 | whole app | no `Semantics(identifier:)` on any element (audit: 0 identifiers) | visible text as locator; a copy change breaks one map entry | all — maintenance risk, not a blocker |
| TD-AUTH-001 | Welcome, Login, Registration | logo image has no label | none — logo checks stay manual | CHK-AUTH-017, -104 (partial) |
| TD-AUTH-002 | OTP | code input is a hidden 1×1 field without a label | the only text field on the screen | none (reachable) |
| TD-AUTH-003 | Registration | SMS / Email radios have no names | position inside the labelled `SMS\nEmail` container; state from `value` | none (reachable) |
| TD-AUTH-004 | Registration | SMS consent switch has no name | the only switch on the screen | none (reachable) |
| TD-AUTH-005 | SMS Terms | close icon has no name | the only unnamed button on the screen | CHK-AUTH-057 (deferred) |
| TD-AUTH-006 | OTP | back button has no name | system back (edge swipe on iOS) | CHK-AUTH-097 via system back |
| TD-AUTH-007 | Login, Registration, OTP | validation / server messages have no ids | located by their exact text (parametrised alias) or as texts inside the field's bounds | none (reachable) |
| TD-JOBS-001 | Jobs list | list ↔ calendar toggle has no name | the only unnamed button on the screen (module 03) | module 03 |
| TD-PHOTO-001 | Photo editor | four toolbar buttons unnamed; palette and canvas absent from the tree | position only; markup checks `Blocked` | module 09 (9 checks) |

Suggested ids for the dev team follow §1 (`<screen>-<element>`), e.g. `registration-channel-sms`,
`registration-sms-consent`, `otp-code`, `otp-back`, `sms-terms-close`, `jobs-list-view-toggle`.
