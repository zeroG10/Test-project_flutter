# qa-tools

Small Python utilities (uv-managed) that sit at the edges of the automation
chain described in [`automation/README.md`](../README.md):

| Script | Layer | Direction | Writes to |
|---|---|---|---|
| `sync_checklist_to_sheets.py` | 0 → Sheet | checklist `.md` → Google Sheet | the team Sheet (**the only Sheets writer in this repo**) |
| `import_checklist_from_sheets.py` | Sheet → 0 (one-time) | Google Sheet → per-feature checklist `.md` | markdown under `qa/web/<NN-slug>/` — **reads** Sheets, never writes them |
| `trace_results.py` | 4 (closure) | run results → checklist IDs | one markdown report, by convention `qa/web/<NN-module>/<module>-traceability.md`, mobile per platform `qa/mobile/<NN-module>/{ios,android}/<module>-traceability.md` — never Sheets |
| `build_summary.py` | 4 (report) | one mobile run → report site: summary, a page per module and per defect | local `automation/mobile/reports/<platform>/summary/` (gitignored) — publishing is an owner call |

All of them honour the QA Doctrine in `CLAUDE.md`: no result is ever upgraded to
Passed by a tool, a skip is Blocked, an empty run is not a passing run.

## Setup

```bash
cd automation/tools
uv sync                                   # runtime deps + pytest (dev group)
cp .env.example .env                      # Sheets targets — only needed for the sync
# Service-account JSON (gitignored):
#   automation/tools/.secrets/credentials.json
# Share EACH target Sheet with the service-account email as Editor.
uv run pytest                             # offline self-test of both scripts
```

Never commit `.env` or `.secrets/` (both are gitignored).

---

## sync_checklist_to_sheets.py

Pushes one checklist markdown file into its Google Sheet idempotently. Rows are
matched by the stable check ID kept in a hidden column, so re-running is safe:
the sheet's **status columns and reviewer comments are never touched**. The
script writes only column A (feature title), column B (group header / check
text), the hidden ID column and the hidden Obsolete column, plus cell B1
(`Checklist\nUp to date according to <DD Month YYYY>`).

### Dry-run first (always)

```bash
uv run python sync_checklist_to_sheets.py ../../qa/web/01-authentication/authentication-checklist.md --dry-run
uv run python sync_checklist_to_sheets.py ../../qa/mobile/01-authentication/authentication-checklist.md --dry-run
```

`--dry-run` reads the sheet, prints the plan (`updates / appends / obsolete`)
and the first batched writes, and sends nothing. Publish only after a human has
read the plan — the `qa-sheets-sync` skill enforces this order. Then drop
`--dry-run`.

Checklists live per module: `qa/{web,mobile}/<NN-module>/<module>-checklist.md`
(`NN` = order in the SRS, `<module>` = the slug registered in
`qa/shared/feature-codes.md`). The path is load-bearing: the platform folder
decides the target and the file stem decides the feature code.

### Targets: two separate Sheets, configured in `.env`

Web and mobile checklists live in **separate Google Sheets** (not tabs of one
sheet), each with its own worksheet name and hidden-column layout. Select with
`--target {web,mobile}`, or omit it and the checklist path decides: the segment
after `qa/` is the platform — `qa/web/…` and `qa/shared/…` → `web`,
`qa/mobile/…` → `mobile`. A path that names neither is an error, never a silent
default. All four values per target are required; the script refuses to start
if one is missing. The values below are the defaults from `.env.example`:

| Variable | Web target | Mobile target | Meaning |
|---|---|---|---|
| `*_SHEET_ID` | `WEB_SHEET_ID` | `MOBILE_SHEET_ID` | Spreadsheet id from the Sheet URL |
| `*_WORKSHEET` | `Check-list` | `Check-list` | Worksheet (tab) name inside that Sheet |
| `*_ID_COL` | `O` | `N` | Hidden column holding `CHK-…` / `FEAT-…` ids |
| `*_OBSOLETE_COL` | `P` | `O` | Hidden column holding the Obsolete flag (`1`) |
| `CREDENTIALS_FILE` | `.secrets/credentials.json` (shared) | | Service-account JSON, relative to this folder |

Rules baked into the script:

- The Obsolete column must be **immediately right of** the ID column (it is the
  right edge of the matrix the script reads and writes, `A..<Obsolete>`).
- Columns between B and the ID column are the team's status / comment columns.
  The script never reads or writes them, whatever their count — the layout is
  configurable per target, nothing about "columns O and P" is hardcoded.
- Data rows start at row 5 (`DATA_START_ROW`); rows 1–4 are the sheet header.
- Since the two targets are separate Sheets, feature codes cannot collide across
  platforms: `CHK-AUTH-001` in the web sheet and `CHK-AUTH-001` in the mobile
  sheet are unrelated rows.

### Stable IDs

Each check line in the markdown carries its ID after the number:

```
1. [CHK-AUTH-001] Check that the Set Password page is accessible only via …
```

Items without an ID get the next free `CHK-<FEATURE>-NNN` (numbering continues
after the highest number already in the sheet for that feature). The ID is
written into the hidden ID column and is what links the sheet row back to the
markdown source, so a check keeps its statuses even if its text is edited or
its section is renamed. Copy assigned IDs back into the `.md` — markdown is the
source of truth (`CLAUDE.md`, "single writer").

### Feature codes (`qa/shared/feature-codes.md`)

The `<FEATURE>` part of every ID is resolved in this order:

1. `--feature-code CODE` on the command line (2–5 uppercase letters).
2. The project registry **`qa/shared/feature-codes.md`** (optional file,
   resolved relative to the repo root). A markdown table:

   ```markdown
   | slug | code | platform/notes |
   |---|---|---|
   | authentication | AUTH | web + mobile (separate sheets) |
   | order-list | ORDL | mobile |
   ```

   `slug` is the checklist filename stem without the `checklist-` prefix or
   `-checklist` suffix (`checklist-order-list.md` and `order-list-checklist.md`
   both resolve to `order-list`; the registry may list either spelling). The
   module folder is ignored: `qa/web/01-authentication/authentication-checklist.md`
   resolves to `authentication`. The third column is free text. Invalid codes
   and conflicting duplicate slugs abort the run.
3. Fallback: the first four letters of the slug, uppercased (`order-list` →
   `ORDE`), logged as a `WARN`.

The script itself ships with an **empty** built-in map — client feature names
never live in the code. Pin every code in the registry before the first real
sync: changing a feature's code afterwards orphans all its rows in the sheet
(they would be marked obsolete and re-appended without their statuses).

### Behaviour

| Situation | Tool action |
|---|---|
| New check in `.md` (no row in sheet) | Append at the end, under its group header (header row added if the group is new for this feature) |
| Check text edited in `.md` | Update column B; statuses untouched |
| Check removed from `.md` | Obsolete column = `1` on the row; the row is **not** deleted, statuses survive |
| Check reappears in `.md` | Obsolete flag cleared |
| Section renamed / moved in `.md` | Warning only; the row stays where it is |
| Duplicate IDs in `.md` | Hard error, nothing written |
| Duplicate IDs in sheet | Warning; first occurrence used |
| Other features in the same sheet | Untouched — obsolete marking is scoped to the feature being synced |

### Hidden columns

The ID and Obsolete columns are hidden by the script on every real run. Do not
unhide or edit them by hand; use "View hidden columns" temporarily if you need
to inspect them.

### `--reset` — destructive, owner-only

`--reset` **clears every data row from row 5 down, across columns A through the
Obsolete column** — that range includes all status and comment columns — and
unmerges cells in that zone, before re-syncing from the markdown. It exists for
one situation only: the sheet layout (column letters, worksheet) changed and
the sheet must be rebuilt from scratch.

- Owner-only decision (doctrine rule 5). Never run it on a sheet that holds
  manually entered statuses unless the owner has explicitly accepted losing them.
- Always `--reset --dry-run` first and read the `--reset: clearing A5:P<n>`
  line; it names the exact range that would be wiped.
- Never in automation / CI / a skill loop.

---

## import_checklist_from_sheets.py — one-time Sheet → markdown (READ-ONLY)

The inverse of the sync, for exactly one situation: a checklist that was born
in a Google Sheet (no `CHK-` IDs yet) has to become markdown so that markdown
can be the source of truth from then on. The script **only reads** the Sheet
(`open_by_key`, `get_worksheet_by_id`, `get_all_values`, titles) — the sync
script stays the single Sheets writer. The service-account JSON is loaded to
authenticate and never printed.

```bash
cd automation/tools
uv run python import_checklist_from_sheets.py --sheet-id <ID> --gid <GID> \
  --module-map "Authentication=01-authentication:AUTH" --module-map "<Feature>=<NN-slug>:<CODE>" \
  --out-root ../../qa/web --dry-run                       # summary + warnings, writes nothing
uv run python import_checklist_from_sheets.py --sheet-id <ID> --gid <GID> \
  --module-map ... --out-root ../../qa/web [--feature "Authentication" ...]   # writes qa/web/<NN-slug>/<slug>-checklist.md
```

| Option | Meaning |
|---|---|
| `--sheet-id`, `--gid` | Spreadsheet id and worksheet gid from the Sheet URL (required) |
| `--out-root DIR` | Folder holding the `NN-slug` module folders, e.g. `qa/web` (required) |
| `--feature NAME` | Import only this feature (repeatable, matched case-insensitively) |
| `--module-map "Feature=NN-slug:CODE"` | Feature → folder/code map, one entry per feature in the sheet (repeatable, **required** — there is no built-in map; codes from `qa/shared/feature-codes.md`). Slug = folder minus the `NN-` prefix; file = `<slug>-checklist.md` |
| `--source-title TEXT` | Title quoted in the `> Source:` note (default: the spreadsheet title) |
| `--credentials FILE` | Service-account JSON (default `$CREDENTIALS_FILE` or `.secrets/credentials.json`) |
| `--dry-run` | Print the per-feature table (screens / groups / sections / checks) and warnings; write nothing |
| `--force` | Overwrite existing output files — **renumbers their IDs**, see below |

### What it reads (rows 1–4 header, data from row 5)

Only columns A (TASK) and B (check text / group header) matter. Status,
counter and comment columns are ignored — and are **not** used to classify
rows, because teams fill statuses on header rows too.

| Row shape | Meaning |
|---|---|
| A filled, B empty, A is a feature in the map | Feature block starts (`Orders  ` with stray spaces still matches) |
| A filled, B filled | New screen A; B is its first group name **or** its first check (heuristic below) |
| A empty, B filled | Group header (screen unchanged) or a check |
| A empty, B empty | Skipped and counted, even if status cells are filled |

Group-header heuristic: B is a group when it does not start with a check verb
(`Check` / `Verify` / `Ensure` / `Make sure` / `Confirm` / `Validate` / `Test`),
does not end with `.` and is ≤ 80 characters. Everything else is a check.
Verb-less cells over 80 characters are imported as checks with a warning so a
human can eyeball them in `--dry-run`.

### What it writes

Exactly the shape `sync_checklist_to_sheets.parse_markdown` reads:

```markdown
# QA Checklist: Authentication

> Source: Google Sheet `Check-list` (copy of "…"), spreadsheet id `…` gid `…`, imported YYYY-MM-DD by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Login page / General

1. [CHK-AUTH-001] Check that the "Log in" title is visible.
```

- Section heading = `<Screen> / <Group>`; `<Screen>` alone when the screen row
  carried a check instead of a group; `<Group>` alone when the feature has no
  screen rows at all. Sections without checks are not emitted (warning).
- Item numbers restart per section; **IDs never do** — `CHK-<CODE>-001..NNN`
  run through the whole file in sheet order.
- Check text is verbatim apart from trimming and collapsing line breaks to one
  space. Identical texts are kept (distinct IDs) and reported as warnings.
- A heading the sync parser would drop (`Open Questions`, `Coverage…`) aborts
  the run instead of silently losing checks.

### One-time per feature — the ID contract

IDs are assigned fresh at import and become the contract between the markdown,
the Sheet's hidden ID column and the automated-test tags `trace_results.py`
reads. Re-importing a feature would renumber every check, so the script
**refuses to overwrite an existing output file** and names it. `--force` is
for the case where you are certain no ID from that file is in use anywhere.
After the import, evolve the markdown by hand and publish with the sync script.

Doctrine: an import that parses zero checks exits `1` — an empty import is not
a successful import. Register the codes used by the map in
`qa/shared/feature-codes.md` before the first sync.

---

## build_summary.py — mobile report site for the lead and the team

A small static site over **one clean run**, laid out like the admin panel's report (web, same
product) so the two read alike:

- `index.html` — the verdict (*No unexpected failures* only when every red test is a filed
  defect's regression check), KPIs, one phone screen per module, coverage by module, what needs
  a decision, open defects with the checks each holds red, what could not run and why, why
  checks are not automated (kinds from `qa/mobile/<platform>/not-automated.md`), stability over the
  history runs, delivery pace from git, technical detail;
- `<NN-module>.html` — every check with its verdict, the test that proved it
  (`test_x.py:line`) and the screens that test saved; every test with its steps;
- `bugs/<BUG-ID>.html` — each filed defect report rendered from its markdown, with its
  evidence (a draft marked `Status: NOT FILED` is not an open defect).

CHK verdicts come from `trace_results.py` itself, so the pages and the traceability matrix
never disagree. A failed test is *held red* only when a filed bug names it as its regression
check (`- Test case: \`TC-…\`` or `::test_name`); any other failure is *unexpected*. Read-only
over the results; writes only `--out-dir`.

```bash
uv run python build_summary.py \
  --platform ios --allure-dir ../mobile/results/ios/stable-3 \
  --checklist ../../qa/mobile/01-splash/splash-checklist.md ...        # one per module \
  --history-dir ../mobile/results/ios/stable-1 ...                       # earlier full runs, oldest first \
  --target "iOS simulator · iPhone 17 · iOS 26.5" --run-label "…" \
  [--note "…"] [--decision "…"] [--history-note "…"] \
  [--public --redact-boxes boxes.json --redact-text-env QA_FIRST] [--out-dir ../mobile/reports/ios/summary]
```

| Option | Meaning |
|---|---|
| `--allure-dir DIR` | allure `*-result.json` of **one clean run** (required); empty → exit 2, Blocked |
| `--checklist MD` | repeat per module (required); a module page per `qa/mobile/<NN-module>/` folder |
| `--history-dir DIR` | earlier full runs, oldest first — the run history table and the "same verdicts N runs in a row" line |
| `--platform ios\|android` | whose records the page cites and the defaults below (default `ios`); results of each platform live in `automation/mobile/results/<platform>/<run>/` |
| `--reasons MD` | why checks have no test (default `qa/mobile/<platform>/not-automated.md`); a check with no row shows "reason missing" |
| `--target`, `--run-label` | the device and what was run, as the page names them |
| `--note` / `--decision` / `--history-note` | lines under *Scope of this run* / *What needs a decision* / the history table |
| `--manual-minutes-per-check N` | owner's estimate; omitted → not shown |
| `--public` | the copy that may leave this machine: no text attachments (API bodies, page sources), no videos |
| `--redact-env`, `--redact-text-env NAME`, `--redact-boxes JSON` | hide the test account in text (values never printed) and pixelate boxes on the screens |
| `--no-git` | skip the delivery-pace chart |
| `--out-dir DIR` | default `automation/mobile/reports/<platform>/summary/` (gitignored) |

The pages show screenshots of the client's app — they stay local; publishing is an owner
call, and only the `--public` build is published. For an artifact publish the main page is
`page.html` (a fragment, served as `index.html`); every other file goes in `files`.
`assets/` and `bugs/` are rebuilt on every run (only folders this script created are ever
deleted).

## trace_results.py — layer 4, traceability closure

Reads automated run results, extracts the `CHK-…` IDs that tests carry
(`automation/README.md`, "IDs and tags"), and writes one markdown report with
the automated verdict per checklist item. **Read-only**: it never touches
Google Sheets or the checklists; the only thing it writes is the `--out` file.

```bash
# Web — Playwright JSON reporter (configured in automation/web/playwright.config.ts)
uv run python trace_results.py --platform web \
  --checklist ../../qa/web/01-authentication/authentication-checklist.md \
  --playwright-json ../web/playwright/test-results/results.json \
  --out ../../qa/web/01-authentication/authentication-traceability.md

# Mobile / API — pytest + allure-pytest results directory
uv run python trace_results.py --platform mobile \
  --checklist ../../qa/mobile/01-authentication/authentication-checklist.md \
  --checklist ../../qa/shared/checklists/checklist-owasp-top10.md \
  --allure-dir ../mobile/allure-results --dry-run          # table to stdout, writes nothing
```

| Option | Meaning |
|---|---|
| `--platform web\|mobile\|api` | Label for the report header (required) |
| `--checklist MD` | Checklist with `[CHK-…]` items; repeatable (required) |
| `--playwright-json FILE` | Playwright `--reporter=json` output |
| `--allure-dir DIR` | Directory of allure `*-result.json` files from **one clean run** |
| `--out MD` | Report path; required unless `--dry-run` |
| `--dry-run` | Print the report to stdout, write nothing |

At least one results source is required.

### How IDs are matched

Bare regex `CHK-[A-Z0-9]+-\d{3}`, applied to:

- Playwright: `spec.tags` (the JSON reporter strips the leading `@`, so
  `tag: ['@CHK-AUTH-001']` arrives as `"CHK-AUTH-001"`), the spec title, and
  every ancestor `describe` title (Playwright inherits those tags too — one
  failing child makes the whole ID Failed).
- Allure: `labels` named `tag` (`@allure.tag("CHK-…")` and pytest markers such
  as `@pytest.mark.chk("CHK-…")`, which allure-pytest records as tags),
  `fullName` and `name`.
- Checklists: `1. [CHK-…] text` (the sync script's line format) and the
  `- [ ] [CHK-…] text` bullet form of shared checklists.

### Verdict rules (per CHK ID, over all tagged results)

| Verdict | When |
|---|---|
| `Passed` | every tagged test passed |
| `Failed` | any tagged test failed / timed out / broke (raw result statuses — a flaky retry or an expected `test.fail()` stays Failed) |
| `Blocked` | none failed, but any was skipped or did not execute — a skip is never a pass |
| *(empty)* | no tagged test exists → not run, manual / exploratory, never green |

The summary prints `total / automated / Passed / Failed / Blocked / Not run`
with **Not run derived by subtraction**. IDs tagged in tests but missing from
every given checklist are listed separately as orphans and count for nothing.
A results source with zero tests is flagged `BLOCKED — empty run` in the
report and makes the exit code `1` (report still written); `2` is a usage
error.

The report lands next to the checklist it closes, by convention
`qa/web/<NN-module>/<module>-traceability.md`; mobile keeps one per platform in
`qa/mobile/<NN-module>/{ios,android}/` (for `api` / shared checklists pick a path under
`qa/shared/checklists/`). `--out` is always
explicit and the file is overwritten on every run. Automated verdicts are
copied into the team Sheet by a human, if at all — this script will not do it.

---

## Self-test

```bash
cd automation/tools && uv run pytest
```

`tests/test_trace_results.py` runs the tracer against an inline fake Playwright
report and fake allure results (passed / failed / skipped / not-run / orphan);
`tests/test_sync_feature_codes.py` covers the feature-code registry parser,
the resolution order and the `--target` / slug derivation from the per-module
checklist path, without any Sheets access.
