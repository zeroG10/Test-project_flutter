# Web recon — crawler + locator harvester

`recon.ts` walks the web app (optionally logged in), harvests every interactive element
per page and per opened state, ranks locators by the project priority, verifies each one
for uniqueness with the same Playwright call `screens/resolve.ts → locate()` will make,
and writes the raw material for layer 2 of the automation chain
([automation/README.md](../../../README.md) → "Screen map format") and for checklists:

- **draft screen maps** — one `ScreenMap` const per page, plus one per dialog / menu /
  drawer / tab panel found;
- **inventory** — every route pattern reached, with counts and how it was reached;
- **gaps** — the testability hand-over for the dev team, per
  [docs/requirements/shared/testability-contract.md](../../../../docs/requirements/shared/testability-contract.md);
- aria snapshots, full-page screenshots, and a machine-readable `summary.json`.

It is a **reconnaissance** tool: its output is a draft, never a deliverable. Nothing it
writes goes into `screens/` or `qa/` without a human pass (see "Curation workflow").

## Run

```bash
npm run pw:recon -- --max-pages 5 --module authentication          # unauthenticated
npm run pw:recon -- --storage-state automation/web/playwright/.auth/user.json --module surveys
npx tsx automation/web/playwright/scripts/recon.ts --help
```

`BASE_URL` resolves exactly like `playwright.config.ts`: an exported variable wins, then
`automation/web/.env`; `--base-url` overrides both. No target → the run aborts
(`Blocked, not green`). Zero pages harvested → exit code 1 for the same reason.

| Flag | Default | Meaning |
|---|---|---|
| `--base-url <url>` | `$BASE_URL` | Origin to crawl; same-origin only |
| `--start <path>` | `/` | First page (`/` = the base URL itself, so a base with a path prefix works) |
| `--storage-state <file>` | — | Playwright storageState JSON → authenticated crawl. Produce it with the auth-by-state setup described in `playwright/fixtures/test-fixtures.ts`; never commit it |
| `--max-pages <n>` | 40 | Route patterns to harvest (one instance per pattern) |
| `--max-minutes <n>` | 10 | Wall-clock budget for the whole run |
| `--allow <regex>` / `--deny <regex>` | — | Matched against path+query+hash of discovered links. Logout / sign-out URLs are always denied |
| `--explore-states` / `--no-explore-states` | on | Open dialogs / menus / drawers / tab panels and harvest them as sub-states |
| `--probe-validation` | **off** | On `/new`, `/create`, `/add` pages only: click the primary save/create/submit of an **empty** form once, record the validation messages, go back |
| `--out <dir>` | `scripts/recon-out/<YYYY-MM-DD-HHmm>/` | Output folder (gitignored) |
| `--module <name>` | `unlabelled` | Label written into every output |
| `--headed` | off | Watch the browser |

## What it does

1. **Crawl** — chromium, breadth-first from `--start`, same origin only. Links come from
   `a[href]` (hidden ones too: collapsed menus hold real routes) and from SPA navigation
   that has no href: `role=link` / `role=menuitem` elements, `href="#"` anchors and
   buttons inside `nav` / `header` / sider — clicked, URL change recorded, page restored.
   URLs are normalised (volatile query params dropped, hash kept only for `#/…`-routed
   apps) and collapsed to a **route pattern** (`/items/123` → `/items/:id`); one instance
   per pattern is visited, the others are listed under "Route instances".
2. **Harvest** — per page and per sub-state: buttons, links, inputs, selects, textareas,
   ARIA widgets (`button link tab menuitem checkbox switch combobox option textbox`),
   `contenteditable`, table headers, headings, alerts / statuses / Ant Design messages,
   empty states, and *clickable icons* (`role=img` with `cursor: pointer` outside any
   control — a testability gap by definition). For each element the tool asks Playwright
   for the true role + accessible name (the element's own aria snapshot), then tries the
   locator priority in order and keeps the **first strategy that matches exactly one
   element**: `data-testid` → role + name (`exact: true`) → label → (placeholder,
   recorded only: `resolve.ts` has no such shape) → visible text. All attempts and their
   match counts are kept in `summary.json`. Tables get their column headers, row count
   and a `getByRole('row', { name: /<first cell>/ })` template; forms get their fields.
3. **Explore states** — openers (`aria-haspopup`, `aria-expanded="false"`, names starting
   with add / create / new / filter(s) / edit / more / actions / columns / export / import /
   settings) are clicked one by one; whatever appears within 3 s (`[role=dialog]`,
   `<dialog>`, `[role=menu]`, `[role=listbox]`, `.ant-modal`, `.ant-dropdown`,
   `.ant-drawer`, `.ant-popover`, `.ant-select-dropdown`) is harvested as
   `<page>#<opener-alias>` and closed with Escape → close/cancel button → page reload.
   Tabs whose panel is not the initial one are harvested as `tabpanel` sub-states.
4. **Write** everything to `--out` (see below).

Per-page hard limits: 15 s navigation, 5 s network idle, 250 elements, 25 discovery
clicks, 16 openers, 8 tabs. Errors are recorded in the inventory and the run continues.

Three rules make the opener step actually reach create flows (all three were found the hard
way on a real Ant Design admin panel):

- An opener is matched on its accessible name, its **visible text** and its **alias**. An
  icon label is glued into the accessible name (`"plus-circle Add"`), which defeats a
  start-anchored match on the name alone — and the Add button is exactly the opener that
  matters most, because it is the entry point of every create flow.
- Identical controls are **deduplicated** (at most 2 per name+kind). A 10-row table yields
  10 "edit" buttons; without this they fill the opener budget and Add is never clicked.
- Creators (`add` / `create` / `new`) are tried **first**, comboboxes last.

A click that is not actionable is retried once with `force: true` and recorded as
"opened with force" — Ant Design's `Select` reports an inner combobox as the control while
the real hit target is its wrapper (the page-size selector on every list page).

A tab the **app** opens (a preview, a printable report) is closed — the crawler drives one
tab — but its URL is recorded first and queued as a route, so a whole screen cannot vanish
behind a popup.

**Crash recovery.** A wedged tab poisons every later navigation: one heavy editor left the
page in a state where every following `page.goto` failed with `net::ERR_ABORTED`, losing 8
routes. On a page error the crawler opens a **fresh tab in the same context** (the session
lives on the context, so no re-login) and retries that route once.

## Safety rules (read before pointing it at a shared environment)

- Same origin only; never follows logout / sign-out; `--deny` narrows further.
- **Blocklist** — an element whose name matches
  `delete | remove | logout | log out | sign out | pay | purchase | send | submit | approve | reject | publish | archive | deactivate | disable | reset`
  is never clicked, in any mode.
- Forms are never filled. The only submit the tool ever performs is the opt-in
  `--probe-validation` click on an **empty** form on a `/new|create|add` page — nothing
  can be created from an empty form; it exists to capture the validation copy.
- Native `confirm()` / `alert()` dialogs are dismissed; popups are closed; downloads are
  not accepted.
- **Credentials never touch this tool.** Auth is a storageState *file* passed on the
  command line; the outputs record only whether one was used and its file name.
- Dev / staging only, like every other run in this repo. A crawl of production is a
  bug report against the person who ran it.

## Outputs (`--out`, gitignored)

| File | Purpose |
|---|---|
| `inventory.md` | One row per route pattern: title, `h1`, nav path (link texts used to reach it), interactive / forms / tables / dialogs / gaps / console-error counts, module, notes (redirects, `same content as …`, truncation, errors). Then sub-states, route instances, **routes not visited** with the reason (limit, time, denied, redirect, auth), validation probes, errors. Run metadata on top. When the crawl hit a login redirect without `--storage-state` the banner says *auth required for the rest* |
| `screens/<page-slug>.map.draft.ts` | `export const <camelSlug> = { id, route, elements } as const satisfies ScreenMap;` — type-checked by `npx tsc --noEmit` like any other file under `automation/`. Aliases are auto-generated purpose words (`save-button` → `save`, `Enter your email` → `email`), kind-suffixed on collisions between widgets (`search-input` / `search-button`), numbered only when two identical widgets collide. Every element carries `// via: <strategy> | unique | <gap or note>`; elements with no unique locator are `// GAP …` comment lines. Sub-states follow as `<camelSlug><Opener><Kind>` consts (`itemsAddItemDialog`) |
| `gaps.md` | Per page: **blocking** (no unique stable locator — same-name buttons, table-row actions, unnamed controls) and **weak** (works today, by copy: text-only, placeholder-derived names, clickable icons, messages without ids) with the hint of where the element sits and the `data-testid` to add; missing `<screen>-root` ids; and the alias → id handshake table from contract §3 ready to paste into the ticket |
| `aria/<page-slug>.aria.yaml` | `page.locator('body').ariaSnapshot()` of the base state |
| `screenshots/<page-slug>.png` | Full-page screenshot of the base state |
| `summary.json` | Everything above as data (elements with all tried alternatives and counts, sub-states, probes, console errors, timings) |

## Curation workflow (draft → screen map)

1. Read `inventory.md`. Decide which pages belong to the module you are mapping; the
   rest is context. Copy `inventory.md` / `gaps.md` into `qa/web/<NN-module>/` only if
   the team wants them as artifacts (they are inputs, not deliverables).
2. Open `screens/<page>.map.draft.ts`. **Rename every alias by purpose** — `login.submit`,
   never `login.log-in-button`; keep the same alias the mobile map will use
   (`automation/mobile/screens/<screen>_map.py`). Delete decorative and duplicate entries
   (nav links repeated on every page belong in one `shell`/`nav` map, not in every screen).
3. Keep one strategy per element, in priority order. A `text` locator is acceptable for
   static copy only; anything data-driven, every message, empty state and row action needs
   a `data-testid` — that is what `gaps.md` is for. Hand it over; the affected checks stay
   **Blocked** until the ids ship (contract §2.10). Do not work around a gap with CSS/XPath.
4. Move the const into `automation/web/playwright/screens/<module>/<screen>.map.ts`
   (one screen per file, dialogs are screens too), change the import to
   `'../resolve'`, keep `as const satisfies ScreenMap`, run `npx tsc --noEmit`.
5. Test cases (`qa/web/<NN-module>/<module>-test-cases.md`) refer to `screen.alias`; page
   objects resolve them with `locate(page, map.elements.alias)`. Renaming an alias later is
   a breaking change — grep the test cases first.
6. Re-run recon after the dev team ships ids: an element that now resolves `via: testId`
   is the signal to switch the map entry over.

## Known limits

- Runs the in-browser collector with `document.querySelectorAll`: iframes and closed
  shadow roots are not harvested (Playwright locators do pierce open shadow roots, so the
  uniqueness counts still see them — a mismatch shows up as `NOT unique`).
- Dropdown / listbox sub-states can be long (every option is an element); the 250-element
  cap applies per state. The opposite also happens: a `listbox` sub-state with **0 elements**
  means the overlay opened but its options had not rendered within the harvest window
  (Ant Design renders them in a portal, asynchronously). The state is real; write its options
  by `role=option` + name in the curated map instead of expecting them in the draft.
- Names are computed by Playwright, so an icon's `aria-label` inside a link becomes part of
  the name (`"left Back to Login"`). The locator is right; the draft notes the visible text
  and derives the alias from it.
- Non-Latin names collapse to the element kind in aliases (`button-2`) — rename them.
- The tool mutates nothing server-side, but it *does* click openers and tabs; an app that
  navigates on tab change is handled (URL change → route discovered, page restored).
- **Radio groups used as view switchers are not clicked.** A radio carries form state, so
  clicking one could change what a later harvest sees. On one real admin panel the editors'
  `Add | Preview` toggle is a radio group, which is why the preview pane never appears as a
  sub-state: it is a second state of the same page, mapped while the test that needs it is
  written, not by the crawler.
