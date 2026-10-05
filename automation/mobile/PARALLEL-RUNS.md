# Parallel runs — iOS and Android at the same time

How one machine runs the iOS and the Android suites side by side, the rules that keep the two runs from
spoiling each other, and how to set the same thing up in another project. Written to be reused: sections
1–5 are the method, section 6 is this project's values.

## 1. One command

```bash
cd automation/mobile
scripts/qa.sh both all                 # the whole regression, iOS and Android side by side
scripts/qa.sh ios all                  # one platform
scripts/qa.sh android auth             # one module — by number (02), name or a unique part of it
scripts/qa.sh both 08,09               # several modules, both platforms
scripts/qa.sh both all --sequential    # iOS, then Android — when they may not run together
scripts/qa.sh both all --dry-run       # show the plan; start nothing
scripts/qa.sh ios tests/shared/test_splash.py::test_x -- -x   # a pytest path; args after "--"
```

`qa.sh` boots the device of each platform if none is up, starts that platform's Appium server if it does
not answer, and hands each run to `scripts/run.sh` (a committed tree, a results folder of its own —
`results/<platform>/<date>-<name>/`). At the end it prints passed / failed / blocked per platform and the
red tests. With `both`, each run's output goes to `results/.logs/<date>-<name>-<platform>.log`
(`tail -f` it). Devices and Appium servers stay up after the run.

`scripts/run.sh <platform> <name> [pytest args]` still works on its own; so does a plain
`uv run pytest --platform=…` (results in `results/_scratch/`).

## 2. The rule

**Two runs may go side by side only if they share nothing that either of them changes.** Whatever both
would write to has to exist twice — or one of them waits. `qa.sh` and `run.sh` check the two things they
can check (the account and the Appium server) and refuse instead of guessing; the rest of the table is
how the harness is built.

| What a run touches | Why sharing it breaks runs | How it is kept apart |
|---|---|---|
| **The test account** — its session, profile, theme, jobs, notifications | one run signs out or renames the profile under the other; a job seeded for one shows up in the other's list; "no active jobs" preconditions fail | **an account per platform**: `IOS_USER_*` / `ANDROID_USER_*` in `.env` (unset → the shared `APP_USER_*`) |
| **The Appium server** | at its start a run closes every session a killed run left on *its* server — on a shared server that kills the other platform's live session | **a server per platform**: `IOS_APPIUM_PORT` / `ANDROID_APPIUM_PORT`; `scripts/start_appium.sh <platform>` |
| **The device** | — | each platform has its own (a simulator, an emulator) |
| **The run lock and the results** | two runs writing one folder mix their evidence | a lock per platform (`results/.run.<platform>.lock`), results per platform and run |
| **Seeded data** — jobs, files | ids were stamped to the second: two runs seeding in the same second got the same id | the platform's letter in the stamp (`QA-AUTO-1002I201937-NEW` / `…A…`); every sweep and cleanup is scoped to the run's own technician |
| **Generated users** | — | emails are random and unique; phones come from one reserved block of 100 numbers and are checked against the server before use (a clash needs two registrations in the same second: accepted) |
| **The report's privacy check** | a second account would appear unmasked in a shared report | redaction covers every account in `.env` (`automation/tools`: `Redactor`, `redact_screens.py`) |
| Read-only things — the build, the survey template, the API admin login | nothing writes to them | shared |
| **The machine and the server** | two devices and a doubled load on the test server slow everything; a test with a tight timing may go Blocked or red | not a correctness problem but a risk: see section 4 |

Not possible with this setup: **two runs of the same platform** at once. That would need a second device, a
third account, and per-run driver ports (`systemPort` for UiAutomator2, `wdaLocalPort` for XCUITest).

## 3. Rules of use

1. One run per platform at a time; the two platforms together only when `qa.sh` says they may.
   `--dry-run` shows it without starting anything.
2. Commit before a run (`run.sh` refuses a dirty tree); a run never overwrites another's results.
3. A run is under one account from start to end. Never point both platforms at one account "just for a
   quick check" — that is the failure this document exists to prevent.
4. A red test is not re-run until green. Decide first: the app (a bug), the test, or the environment —
   and after a parallel run, check the environment first (rule 5).
5. **A verdict that differs from the same suite run alone is an environment finding until proven
   otherwise.** Re-run that module alone on that platform once; red both times → it is real.
6. A new test account is data like any other secret: its values live only in `.env`; documents name the
   variable, never the address; shared reports hide it.

## 4. Before the results of parallel runs are trusted

Parallel is a different environment from the one the suite was proven in. Prove it once:

1. `scripts/qa.sh both <one module>` — the cheapest proof that both accounts, both servers and both
   devices work together.
2. `scripts/qa.sh both all` — compare each platform's verdicts with its last full run made alone. The
   differences are the list to triage (rule 5). None → parallel is the default way to run.
3. Record the outcome where the project keeps its decisions; keep `--sequential` as the fallback.

## 5. Setting this up in another project

1. **Ask the owner for one test account per platform.** Each must be: registered and active on the test
   environment, the same role as the first, with its own phone / email, with no data the tests' "clean
   state" preconditions would trip over (here: no active job), and free of other users — nobody tests
   by hand under it while a run goes.
2. Put the second account in `automation/mobile/.env` as `IOS_USER_EMAIL` / `IOS_USER_PHONE`
   (`…_OTP` only if it differs), or the `ANDROID_USER_*` twins. Set `IOS_APPIUM_PORT` and
   `ANDROID_APPIUM_PORT` to two different ports. Mirror the variable *names* in `.env.example`.
3. `scripts/qa.sh both all --dry-run` — it must say "side by side" and show two different account
   fingerprints and two ports.
4. Go through the table in section 2 for **this** product: what else does a test write that the other
   platform's run can see? Typical: a shared admin setting the tests toggle, a global list both runs
   read, a rate limit per IP, data found "by name" instead of by owner. Each one needs to exist twice or
   to be made unique per platform (`settings.run_tag` is the letter to put in a generated name).
5. Add the second account to the environments document (variable names only) and make sure the report's
   privacy check knows it (it reads the same `.env`).
6. Do section 4.

## 6. This project (Concert Technologies Field Technicians app)

| | iOS | Android |
|---|---|---|
| Device | iPhone 17 simulator, iOS 26.5 | Pixel 7 emulator (AVD `Pixel_7_API_36`), Android 16 |
| Test account | the second account (owner, 2026-10-05) — `IOS_USER_EMAIL` / `IOS_USER_PHONE` | the first — `APP_USER_EMAIL` / `APP_USER_PHONE` |
| OTP | `APP_USER_OTP` (the DEV code is the same for every account) | same |
| Appium | `IOS_APPIUM_PORT` = 4723 | `ANDROID_APPIUM_PORT` = 4724 |
| Emulator boot | — | `ANDROID_EMULATOR_ARGS` (DNS servers, Kyiv time zone) |

The second account went to iOS because iOS has to be re-run anyway after the Android stage changed the
shared code: one verification covers both.

**Status (2026-10-05): configured; the mechanics work — the suite is not yet proven in parallel.** The
second account was read on DEV (registered, active, no active job). A quick check on the owner's go: one
read-only test (TC-PRF-005) on both platforms at the same second — each under its own account and Appium
server, both passed; its results were deleted on purpose (a check of the tool, not a test result). Section
4 is still to do; until then a parallel result of the suite is not evidence.

A phone on a USB cable does not get in the way: `qa.sh` pins the Android run to the emulator
(`ANDROID_SERIAL`).
