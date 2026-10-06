# Shared files — the mobile lines to add (by hand, add-only)

These files are shared by the whole template. In the template, open each one and **add** the mobile lines below;
change nothing else in them and never copy this project's file over the template's. Paths are relative to the
template's root.

---

## `CLAUDE.md`

**Where things live** — add after the *Tools* row:

```markdown
| Mobile reports: six test completion reports (iOS / Android / both × internal / client), PDFs, the privacy check; a run vs the last final run | `automation/tools/mobile_*.py` → `reports/mobile/` | [automation/tools/README.md](automation/tools/README.md) *Mobile reports* |
```

**Commands** — in the mobile block, after `uv run pytest --platform=android -m smoke   # or --platform=ios`:

```bash
scripts/qa.sh <ios|android|both> <all|module|path> [--name N] [--sequential] [--dry-run]   # one command: devices, Appium, the run(s), a summary (PARALLEL-RUNS.md)
```

and in the *Tools* block, after the `sync_checklist_to_sheets.py` line:

```bash
uv run python mobile_compare_runs.py --platform <ios|android> ../mobile/results/<platform>/<run>   # a mobile run vs the last final run
uv run python mobile_reports.py [--share] && node mobile_export_pdf.mjs                           # the mobile test completion reports
```

**Skills** — add to the skills table:

```markdown
| `/qa-mobile-run` | MOBILE: run a module, several or one test on iOS, Android or both side by side (`scripts/qa.sh`); what is new red vs the last final run |
| `/qa-mobile-regress` | MOBILE: the whole regression on a platform or both; every test compared with the baseline (`mobile_compare_runs.py`) |
| `/qa-mobile-triage` | MOBILE: why a test is red or blocked — environment / test / expectation / app / no oracle — with evidence; bug drafts per `prompts/08` |
| `/qa-mobile-report` | MOBILE: from a regression run to the reports — traceability, six test completion reports, PDFs, privacy check; publish on the owner's word |
```

**When Starting a New Project** — after "run `bash automation/mobile/scripts/doctor.sh` on the mobile machine":
"; for iOS and Android at the same time, a test account and an Appium port per platform
([automation/mobile/PARALLEL-RUNS.md](automation/mobile/PARALLEL-RUNS.md))".

---

## `setup/SETUP.md`

§3, *Mobile (Appium — Android, iOS, Flutter)* — after the **Verify** line:

```markdown
- **One command** for a run: `scripts/qa.sh <ios|android|both> <all|module>` (devices and Appium started for you).
- **Both platforms at the same time** (optional): a test account and an Appium port per platform —
  [automation/mobile/PARALLEL-RUNS.md](../automation/mobile/PARALLEL-RUNS.md) §5; check with `scripts/qa.sh both all --dry-run`.
- Adding the second platform to a suite proven on the first: [automation/mobile/SECOND-PLATFORM.md](../automation/mobile/SECOND-PLATFORM.md).
```

The `report.*` row (if it has a placeholder for the mobile reports, replace that): add
"`report.mobile:` — the mobile reports' slices (`ios`, `android`, `all`: product names, PDF prefixes, the runs they
describe, published links), their wording (`environment`, `subject`, `scope_notes`, `out_of_scope`,
`client_groups`, `client_blocked`); read by `automation/tools/mobile_brand.py`".

Where the template names its porting guide (*Moving the template's own improvements between clones*), add
"[PORT-MOBILE.md](PORT-MOBILE.md) (mobile)".

---

## `setup/project.yaml`

Under `report:` add (if there is a placeholder comment for the mobile reports, replace it):

```yaml
  mobile:                                       # the mobile reports (automation/tools/mobile_brand.py)
    environment: "<dev|staging>"                # the test environment, as the reports name it
    subject: "<the app in running prose>"       # "regression of the <subject>"
    scope_notes: []                             # lines added to the internal reports' "Scope of this run"
    out_of_scope: []                            # the client report's "Out of scope" list
    client_groups: {}                           # why checks are not automated, as the client reads it: <kind>: "<group>"
    client_blocked: {}                          # why a test could not run, as the client reads it: TC-…: "<text>"
    slices:                                     # ios, android, all (both)
      ios:
        product: "<Product> iOS App"
        product_short: "iOS App"                # browser tabs: "<short> QA Report" / "<short> Test Completion"
        file_prefix: "<Prefix>_iOS"             # PDF names: <prefix>_TestCompletionReport[_INTERNAL]_<run date>.pdf
        run: ""                                 # automation/mobile/results/ios/<run> — the run the report describes
        history: []                             # earlier full runs, oldest first
        history_note: ""
        internal_url: ""
        client_url: ""
      android:
        product: "<Product> Android App"
        product_short: "Android App"
        file_prefix: "<Prefix>_Android"
        run: ""
        history: []
        history_note: ""
        internal_url: ""
        client_url: ""
      all:
        product: "<Product> App (iOS & Android)"
        product_short: "Mobile App"
        file_prefix: "<Prefix>_Mobile"
        internal_url: ""
        client_url: ""
```

and under `mobile:` (after `ios:`):

```yaml
  # iOS and Android at the same time (automation/mobile/PARALLEL-RUNS.md): a test account and an Appium server per
  # platform. Variable NAMES only — the values live in automation/mobile/.env.
  parallel:
    enabled: false
    accounts: { ios: "IOS_USER_*", android: "ANDROID_USER_*" }   # unset → the shared APP_USER_*
    appium_ports: { ios: 4723, android: 4724 }
```

---

## `.gitignore`

Under *Python / Appium mobile automation*, if not there yet:

```gitignore
automation/mobile/results/
automation/mobile/reports/
```

(`reports/mobile/` — the shared copy — is committed.)

---

## `automation/tools/pyproject.toml`

`dependencies` — add (keep what is there):

```toml
    "markdown-it-py>=3.0",
    "pillow>=10.0",
```

`[tool.ruff.lint.per-file-ignores]` — add:

```toml
"mobile_summary.py" = ["E501"]
"mobile_client_report.py" = ["E501"]
"mobile_combined_report.py" = ["E501"]
```

Then `uv lock` (or `uv sync`) in `automation/tools/`.

---

## `automation/tools/README.md`

1. In the table at the top, after the `brand.py`, `paths.py` row, add the row:

```markdown
| `mobile_reports.py` + `mobile_*.py` | 4 (report) | the mobile runs named in `setup/project.yaml → report.mobile` → six test completion reports (iOS / Android / both × internal / client), PDFs, the privacy check; `mobile_compare_runs.py` — a run vs the last final run | local `automation/mobile/reports/` (gitignored); `--share` → `reports/mobile/` — see *Mobile reports* below; publishing is an owner call |
```

2. Copy the whole section **`## Mobile reports — mobile_*.py`** from this project's `automation/tools/README.md` (from
   that heading to the line before `## trace_results.py`) and put it before the template's `## trace_results.py`.

---

## `.github/workflows/mobile-android-tests.yml`, `mobile-ios-tests.yml`

The unattended smoke run keeps the video of a failed test:

```yaml
            EVIDENCE_VIDEO=auto uv run pytest --platform=<os> -m "smoke and not quarantine" --tb=short
```

## `qa/_templates/bug-mobile.md`

The device example line: `| Device | iPhone 17 / Pixel 7 |` (the old line named a device no run used).
