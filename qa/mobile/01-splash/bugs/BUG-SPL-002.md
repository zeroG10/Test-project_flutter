# BUG-SPL-002 — Android: the system Back on the splash screen leaves the app

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-09-30 on the owner's go
> (mykola.zhuchenko, answer to Q-SPL-A2: «заведи»). Tracker: not configured (`setup/project.yaml → tracker.system`),
> so nothing was sent anywhere.

## Summary

On Android, pressing the system Back button while the brand splash screen is shown sends the app to the background: the
home screen (or the app used before) comes to the front, although the splash must not react to any user action.

## Layer

- [x] App (UI) — evidence: the splash route is `NoTransitionPage(child: SplashPage())` with no back handling
  (`lib/app/router/app_router.dart`, `_buildRoutes`), while Welcome, Sign in, Sign up and the tab shell are wrapped in
  `DoubleBackToExitScope` (`canPop: false`, `lib/core/widgets/double_back_to_exit_scope.dart`). The splash is the only
  root screen whose Back is not intercepted.
- [ ] Backend / API
- [ ] Unclear

## Severity / Priority

- **Severity:** S4 (cosmetic / minor UX) — **branch fired:** #4 — a minor UX friction on a short-lived screen with an
  easy workaround (open the app again); nothing is lost and no core feature breaks.
- **Priority:** *proposal* P3 — owner / PM decide.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on Android |
| Platforms checked | Android ✓ reproduced · iOS — not affected (no system Back; the edge swipe on the splash changes nothing, TC-SPL-001 passes on iOS) |
| OS version | Android 16 (API 36) |
| Device | Pixel 7 (`Pixel_7_API_36`) |
| Form factor | phone |
| Device type | emulator (Google APIs arm64) |
| App version | `[DEV] CT Mobile` 1.1.1 (178), `development` @ 85a84f3 |
| Build type | debug (flavor `development`, `CLIENT_BUILD=true`) |
| Install method | sideload (.apk) |
| Network | emulator network, DEV API |
| Locale | en |
| Orientation | portrait |
| User role | guest (signed out) and signed in — the splash is the same |
| Feature flags | — |
| Permissions state | notifications=granted, location=granted |

## Preconditions

- The app is installed and not running (a cold start).

## Steps to reproduce

1. Open the app.
2. Wait until the burgundy splash with the logo appears (after Android's own white start screen).
3. Press the system Back button.

## Actual result

The app goes to the background at once (in the automated runs: app state 3, "running in background", ≤ 0.5 s after the
Back); the home screen — or the app used before — is in front. The frame taken right after the press can still show the
splash while Android is already leaving the app.
// [1-splash-before-back.png](evidence/BUG-SPL-002/android/1-splash-before-back.png),
[2-home-screen-after-back.png](evidence/BUG-SPL-002/android/2-home-screen-after-back.png)

## Expected result

The splash screen allows no user interaction, the system Back included: pressing Back changes nothing, and the app goes
on by itself to Welcome (no session) or to the Jobs list (a valid session).

## Frequency

- [x] Always — **4 of 4 verified attempts** on Android: a manual reproduction on 2026-09-29 (Back right after the first
  brand frame → `NexusLauncherActivity` in front at +0.5 / 1.5 / 3 s) and three automated runs of TC-SPL-001 — module
  01+03 run 4 (2026-09-29), the TC-SPL-001 check after the Mac restart and run 6 (2026-09-30): app state 3 after the
  Back. Runs 1 and 2 of 2026-09-29 showed the same (the app behind Google Messages / the home screen) before the check
  had its window.

## Crash? ANR?

- [x] App backgrounded unexpectedly
- [x] No crash

## Evidence

- Screenshots: [evidence/BUG-SPL-002/android/](evidence/BUG-SPL-002/android/) — the splash right before the Back and
  the home screen after it (module 01+03 Android run 4).
- Automated test: `automation/mobile/tests/shared/test_splash.py::test_cold_start_splash_then_welcome` (TC-SPL-001) —
  red on Android at "expect the app to stay in the foreground (a back on the splash changes nothing)"; its other steps
  (brand splash, centred logo, no labelled or clickable node) pass. Allure results `automation/mobile/results/android/`
  `2026-09-30-0103-r6/` (local only).
- Earlier record: D-SPL-A2 / Q-SPL-A2 in [../android/splash-questions.md](../android/splash-questions.md).

## Workaround

Open the app again from the launcher or the recent apps.

## Regression info

- Last known good version: unknown.
- First broken version: unknown (the splash route has had no back handling in the code read on 2026-09-30).

## Related

- SRS §3.1.0 FR-SPL-03: "The Splash Screen shall not require or allow any user interaction."
- Checklist: `CHK-SPL-007` — "Check that no user interaction is possible on the Splash Screen, including taps, swipes,
  or system back actions." ([../splash-checklist.md](../splash-checklist.md))
- Test case: `TC-SPL-001` step 5 / 6 ([../splash-test-cases.md](../splash-test-cases.md)) — stays red on Android
  against this bug.
- Question: `Q-SPL-A2` (answered «заведи», 2026-09-30) in [../android/splash-questions.md](../android/splash-questions.md).
- Sibling: BUG-SPL-001 (same module).
- Invariant: none fits — missing invariant: "a screen that allows no interaction ignores the system Back".
- Tracker: not filed (no tracker configured).

> **When this bug is verified fixed:** re-run TC-SPL-001 on Android on the fixed build (the regression check), then add
> the invariant above to `qa/shared/oracles/invariants.md`.
