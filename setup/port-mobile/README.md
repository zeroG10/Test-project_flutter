# port-mobile — the kit for moving this project's mobile practices into the default template

> **Українською, коротко.** Це пакет для перенесення мобільних напрацювань цього проєкту в дефолтний шаблон
> (`qa-template-for-AI-automation-testing`). Нічого звідси в шаблон не копіюється автоматично: ви відкриваєте сесію
> Claude Code **в репозиторії шаблону**, вставляєте запит із розділу 5 — і той агент читає цей пакет і переносить.
> Пакет — лише мобільне (iOS / Android, Flutter і нативні застосунки); інших частин шаблону він не змінює, окрім
> мобільних рядків у кількох спільних файлах (розділ 1). Тестів проти середовищ перенесення не потребує.

**Source** (this repository): `/Users/mac/Projects/Test-project_flutter` — branch `main` (= `qa/android`), on GitHub
`https://github.com/zeroG10/Test-project_flutter`. Everything below is relative to its root unless it says
"template". **Target**: the default template, `/Users/mac/Projects/qa-template-for-AI-automation-testing`.

## 1. What is in the kit

| Path | What it is | Into the template as |
|---|---|---|
| [`files-copy.txt`](files-copy.txt) | 48 files ready to copy as they are — the mobile reports, the run scripts (one command, parallel runs), the harness helpers, the generic unit tests, the four skills, the owner's guide in two languages, the lessons, the second-platform method, `PORT-MOBILE.md` | the same paths (`rsync --files-from`) |
| [`overlay/`](overlay/) | template versions of files whose copy here holds this project's values: `automation/mobile/PARALLEL-RUNS.md` (§6 emptied), `reports/mobile/README.md` (no runs, no links) | the same paths under `overlay/` |
| [`snippets/01-shared-files.md`](snippets/01-shared-files.md) | the mobile lines to add to files the whole template shares: `CLAUDE.md`, `setup/SETUP.md`, `setup/project.yaml` (`report.mobile`, `mobile.parallel`), `.gitignore`, the tools' `pyproject.toml` and `README.md`; plus the mobile CI workflows and `bug-mobile.md` | added by hand; nothing else in those files changes |
| [`snippets/02-mobile-harness.md`](snippets/02-mobile-harness.md) | the mobile harness files the template already has (`conftest.py`, `config/settings.py`, `.env.example`, `screens/`, `README.md`, …) — what to take from here, what to keep there | merged by hand |
| [`../PORT-MOBILE.md`](../PORT-MOBILE.md) | the general list "template / adapt / project / never" for every future mobile project | `setup/PORT-MOBILE.md` (in `files-copy.txt`) |

Everything in `files-copy.txt` and `overlay/` was checked here: no client name, environment host, test account,
module number, run name, date or test-case id in it; `ruff` (tools: 120, mobile: 100), `ruff format`, the tools'
`pytest` and the mobile `unittest` are green; the reports rebuilt from them are the same as before.

## 2. Prerequisites in the template

1. The template already has what the mobile reports build on: `automation/tools/brand.py`, `automation/tools/paths.py`,
   the logo under `automation/tools/brand/`, a `report:` section in `setup/project.yaml`, and a `trace_results.py`
   with `ResultsError` and `build_run_context`. Missing → stop and ask the owner; do not bring them from here. This
   repository's `brand.py` and `paths.py` are copies of the template's — not in the kit on purpose.
2. A clean working tree in the template, then a new branch `port-mobile-practices` from the template's current branch
   (the owner switches to the right one before the session).

## 3. Steps (in the template)

```bash
SRC=/Users/mac/Projects/Test-project_flutter
TPL=/Users/mac/Projects/qa-template-for-AI-automation-testing
cd "$TPL" && git checkout -b port-mobile-practices

# 1. copy as is
rsync -a --files-from="$SRC/setup/port-mobile/files-copy.txt" "$SRC/" "$TPL/"
# 2. the template versions of the two files that hold project values here
rsync -a "$SRC/setup/port-mobile/overlay/" "$TPL/"
chmod +x automation/mobile/scripts/{run.sh,qa.sh,qa.py,run_context.py,start_appium.sh}
```

3. Merge by hand, file by file: `snippets/01-shared-files.md`, then `snippets/02-mobile-harness.md`.
4. `cd automation/tools && uv lock && uv sync`; `cd ../mobile && uv sync`.
5. Read `git diff` — every changed and new file. A product name, a host, a module number, a run name, a date or a
   test-case id from the source project in a comment is a leak even if the name guard is green.
6. Checks — the mobile files only; all green, no device, no target, no credentials:

```bash
cd "$TPL/automation/tools" && uv run ruff check mobile_*.py import_checklist_from_csv.py tests/test_mobile_*.py \
  && uv run ruff format --check mobile_*.py import_checklist_from_csv.py tests/test_mobile_*.py \
  && uv run pytest tests/test_mobile_*.py
cd "$TPL/automation/mobile" && uv run ruff check . && uv run ruff format --check . \
  && uv run python -m unittest discover -s unit_tests \
  && uv run pytest --platform=ios --collect-only -q && uv run pytest --platform=android --collect-only -q \
  && bash scripts/qa.sh both all --dry-run      # with placeholders: says why the platforms cannot run side by side
```

7. With `setup/project.yaml` at its placeholders: `uv run python mobile_reports.py` (in `automation/tools`) ends
   `Blocked: no run for ios …` — never an empty report; a client report rendered from a test fixture says
   "Draft — not for sending".
8. `CHANGELOG.md`: the mobile entries (section 6 below) under the next version. Commit; tag and push on the owner's
   word.

## 4. What must not be copied

Anything not in `files-copy.txt` or `overlay/` — in particular this project's `docs/`, `qa/mobile/<modules>/`,
`qa/shared/*` (except the device-matrix README), its screens / pages / tests / data fixtures, `helpers/app.py` and
`fixtures/{app_state,test_data,jobs,…}.py` as they are, `helpers/account_names.py`, `helpers/field_services_api.py`,
`reports/mobile/{ios,android,all}/`, `unit_tests/ios_locators.snapshot.json`, `.env` files, `results/`, `builds/`.
The full list and the reasons: `setup/PORT-MOBILE.md` §3.

## 5. The request to paste into the template session

```text
Перенеси мобільні напрацювання (iOS / Android, Flutter) з проєкту /Users/mac/Projects/Test-project_flutter у цей шаблон.
Інструкція: /Users/mac/Projects/Test-project_flutter/setup/port-mobile/README.md — прочитай її повністю,
потім snippets/01-shared-files.md, snippets/02-mobile-harness.md і setup/PORT-MOBILE.md звідти.
Правила: у проєкті-джерелі нічого не змінювати (лише читати); у шаблоні — окрема гілка port-mobile-practices
від поточної гілки шаблону; змінювати лише файли, які називає пакет; у спільних файлах лише дописати мобільні рядки
й нічого іншого в них не міняти; кожен змінений файл прочитати в git diff; прогнати перевірки з розділу 3;
показати мені підсумок і дочекатися мого «коміть» / «пуш». Тести проти середовищ не запускати.
```

## 6. CHANGELOG entries (for the template)

```markdown
### Mobile — from the first mobile product (a Flutter app on iOS and Android)

- One command for a run: `automation/mobile/scripts/qa.sh <ios|android|both> <all|module|path>` — boots the
  device, starts the platform's Appium server, runs through `run.sh` (named results, a committed tree, a lock per
  platform), summarises per platform.
- iOS and Android side by side: a test account and an Appium server per platform (`IOS_USER_*` /
  `ANDROID_USER_*`, `IOS_APPIUM_PORT` / `ANDROID_APPIUM_PORT`), refused when they would share one;
  `automation/mobile/PARALLEL-RUNS.md`.
- Test completion reports for mobile (ISTQB shape): iOS, Android and both, each internal (every check, test, step,
  screen and defect clickable) and for the client; PDFs; the shared copy hides the test accounts in the text and
  pixelates them on the screens (macOS Vision OCR), checked before it is done — `automation/tools/mobile_*.py`,
  `setup/project.yaml → report.mobile`, `reports/mobile/`.
- A run against the last final run, test by test (NEW RED, NEW BLOCKED, fixed?, known red): `mobile_compare_runs.py`.
- Skills: `/qa-mobile-run`, `/qa-mobile-regress`, `/qa-mobile-triage`, `/qa-mobile-report`; the owner's guide in
  Ukrainian and English (`docs/notes/mobile-qa-skills*.md`).
- Harness: prove-red, a session per module on Android and its revival, the ANR guard, `chk_skipped_on`, typing that
  survives the Android IME, list walking for Flutter, pixel oracles, offline network control, Android system dialogs.
- Method: `automation/mobile/LESSONS.md`, `automation/mobile/SECOND-PLATFORM.md`, `setup/PORT-MOBILE.md`.
```
