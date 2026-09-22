# Screen maps (web) — alias → locator

The screen map is the ONLY place a web locator lives (see
[automation/README.md](../../../README.md) → "Screen map format"). Test cases
(`qa/web/<NN-module>/<module>-test-cases.md`) refer to elements by alias; page objects and generated tests
resolve the alias through [`resolve.ts`](resolve.ts) → `locate(page, el)`.

## Format — one file per screen: `<screen>.map.ts`

```ts
import type { ScreenMap } from './resolve';

export const login = {
  id: 'login',            // screen id = file name = alias prefix
  route: '/login',        // relative to BASE_URL
  elements: {
    email:  { testId: 'login-email' },              // → page.getByTestId
    submit: { role: 'button', name: 'Sign in' },    // → page.getByRole
    remember: { label: 'Remember me' },             // → page.getByLabel
    hint:   { text: 'Forgot password?' },           // → page.getByText
  },
} as const satisfies ScreenMap;
```

`satisfies ScreenMap` makes `tsc` reject any strategy `locate()` does not know.

## Alias rules

- Alias = `screen.element`, lower-kebab, stable across platforms: the same alias names
  the same thing in `automation/mobile/screens/<screen>_map.py`.
- Name the element by **purpose**, not by widget or position: `login.submit`, never
  `login.blue-button` or `login.button-2`.
- One strategy per element. Priority: role/label → test-id → text. Never structural
  CSS or XPath. A missing stable id is a testability defect — record it in
  `docs/requirements/shared/testability-contract.md`, do not work around it.
- `text` is for static copy only (headings, hints). Anything data-driven needs a test-id.
- Renaming an alias is a breaking change for every test case that uses it — grep
  `qa/web/*/*-test-cases.md` first.
- Placeholders in scaffold maps use `<…>` (e.g. `'<login-email>'`) so an unfilled map
  fails loudly instead of matching something by accident.

## Conditional elements — `state`

Some elements exist only after an interaction: an error alert after a failed submit, the
revealed-password icon after the eye is clicked, a success message after a request. Mark
them with `state: '<short name of that state>'` next to the strategy:

```ts
error:         { role: 'alert', state: 'failed-sign-in' },
'email-error': { text: 'Invalid email', exact: true, state: 'invalid-email' },
```

`locate()` ignores `state`; it is documentation for the reader and the contract for the
health check: an element **without** `state` must be present and unique as soon as the
screen is open, an element **with** `state` is only checked for ambiguity.

## Registry — `index.ts`

Every curated map is listed once in [`index.ts`](index.ts), under `publicScreens` (no
session needed) or `appScreens` (Root session). The health check fails when a `*.map.ts`
on disk is missing from the registry, when an id is registered twice, or when an id does
not equal its file name — so curating a map ends with one line in the registry.

## Health check — `map-health.spec.ts`

```bash
npm run pw:map-health          # project `map-health`, Chromium, runs setup first
```

Opens every registered screen (public ones in a clean context, app ones as Root), waits
for its `root` alias, and reports each alias in one table per screen (attached to the HTML
report and printed to the console):

| verdict | meaning | fails the test? |
|---|---|---|
| `ok` | exactly one element, visible | no |
| `missing` | matched nothing — the page changed or the map is stale | **yes** |
| `ambiguous` | matched 2+ elements — strict mode would throw in every test using it | **yes** |
| `hidden` | exactly one element, attached but not visible on load | no (annotation) |
| `conditional` | has `state`, not expected on load | no (annotation) |
| `placeholder` | `<…>` value, not observed yet — owed by the testability contract | no (annotation) |

Screens whose route has a parameter (`/reset-password/:secretKey`) or whose map holds only
placeholders are **skipped with a "Blocked:" reason**, never counted as passed. The check
carries no CHK tag and closes no checklist item: it is harness health for this layer, the
first thing to run after the app's markup changes and before blaming a functional test.
