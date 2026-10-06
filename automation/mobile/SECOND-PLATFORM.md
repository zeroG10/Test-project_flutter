# SECOND-PLATFORM.md — adding the second platform to a suite that already runs on the first

The method used on the first mobile product: the suite was built and proven on iOS (a simulator), then Android
(an emulator) was added to the same suite — one checklist, one set of test cases, one set of tests, a second
column in the screen maps. Written for "iOS first, then Android"; the other order works the same with the names
swapped. Lessons from doing it: [LESSONS.md](LESSONS.md); running both at once: [PARALLEL-RUNS.md](PARALLEL-RUNS.md).

## 1. The rules

- **Shared stays shared.** The checklist, the test cases, the tests in `tests/shared/`, the page objects and the
  screen maps exist once. Two copies are two truths: a fix in one never reaches the other.
- **The proven platform is closed.** Its locators do not change while the second is added: record them
  (`uv run python -m unit_tests.test_ios_locator_guard --update`) and let the guard fail on any change. A deliberate
  change to the first platform is the owner's call and re-records the snapshot.
- **Platform-only things live in a platform folder:** `screens/android/` (system dialogs, permissions, the browser
  tab), `pages/android/`, `helpers/android/` (adb), `tests/android/` (what only that platform can test — e.g. offline
  on an emulator whose network can be switched off), `qa/mobile/<NN-module>/android/` (its questions, its
  traceability, its own test cases).
- **One bug report per defect**, because the code and the backend are shared. A defect seen on both platforms gets a
  line "Platforms checked: iOS ✓ · Android ✓" and its evidence in `evidence/BUG-…/{ios,android}/`; a defect on one
  platform says where it was checked and where not.
- **One run at a time per platform, through `scripts/run.sh`** — named, never overwritten, from a committed tree.

## 2. The steps

Each step ends with a short report to the owner and waits for the go to the next one.

| # | Step | Done when |
|---|---|---|
| 0 | **Structure.** A platform subfolder for every per-platform record (`qa/mobile/<NN>/ios/`, `…/android/`, `qa/mobile/{ios,android}/`), results per platform (`results/<platform>/`), the locator guard recorded for the closed platform, the device matrix row for the new target | the offline checks are green (`unit_tests`, map-health), the first platform's locators unchanged |
| 1 | **Build and device.** The app built for the new platform without touching the app's repository (a build shim if a plugin needs credentials), its `BUILD_INFO.txt` (version, source commit, command, target); the emulator / simulator with fixed DNS and time zone | the app installs and opens on its first screen |
| 2 | **Recon.** Every screen dumped on the new platform (`scripts/recon/`), compared with the first platform's locators (`scripts/recon/compare_android.py`); the differences written as questions for the owner — behaviour that differs is a question, never a silent choice | the owner answered the questions; the answers are in `docs/notes/decisions.md` |
| 3 | **The second column of the maps** (`android=` next to `ios=`) and the platform's mechanics: system back, permissions, the in-app browser, the photo picker, typing, network control, pixel oracles re-calibrated on the new screens | map-health green for the new platform; the guard says the first platform is untouched |
| 4 | **The existing tests, module by module**, in the order the first platform was built. For every red: the app (a bug — one report per defect, `prompts/08`), the harness (fix it), an environment fault (Blocked with its reason), or a behaviour the owner rules (`chk_skipped_on` with the reason) | every module green or every red explained; red proven on the new platform (`--prove-red`); the module's traceability for the new platform |
| 5 | **Platform-only tests** — what the first platform could not test (offline on an emulator, a dialer intent, a system dialog), from test cases the owner validated | the tests green or held red by defects; red proven; reviewed (`/bmad-testarch-test-review`) |
| 6 | **The final run of the new platform: three identical consecutive runs** of the whole suite on one harness commit | `qa/mobile/<platform>/final-traceability.md`; repeatability stated (which runs were identical, what differed and why) |
| 7 | **The first platform again**, on the final shared code (the second platform changed shared code), then the reports of both and the combined one (`/qa-mobile-report`) | the first platform repeats its proven numbers, or every difference is explained |

## 3. What to expect

- **Most of the effort is steps 3–4,** and most red there is the harness, not the app: the second platform's
  tree, input and gestures differ (LESSONS.md, "The tree lies" and "Typing and gestures").
- **Defects found on the first platform usually reproduce on the second** (shared code): re-check each one and add
  the platform to its report — it is evidence for the developers that the cause is shared.
- **The test environment does not get faster.** Waits come from measurements on the new platform's recon, never
  from guesses; a timeout is the environment until it reproduces at normal speed.
- **Step 7 is not optional.** Shared helpers, fixtures and page objects change while the second platform is added;
  until the first platform is run again on that code, its old results describe old code.
