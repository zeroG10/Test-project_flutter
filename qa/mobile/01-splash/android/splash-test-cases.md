# Splash — Android offline test cases (step 5)

> Scope/selection: the one `android-stage` check of this module (owner, android-plan §2.5; `qa/mobile/ios/not-automated.md`) — CHK-SPL-015, slow start-up, which needs network throttling the iOS simulator cannot do. Source recon: [qa/shared/recon-2026-10-01-android-offline.md](../../../shared/recon-2026-10-01-android-offline.md) (recon A2). Format: [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md) · [qa/_templates/test-cases-mobile.md](../../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`. Conventions and existing TC-SPL-001…003 (incl. the Android recon-A1 notes on TC-SPL-001): [../splash-test-cases.md](../splash-test-cases.md).
>
> **Status: validated by the owner 2026-10-01 (step 5 gate: D-OFF-1…9 answered, no remarks on the TCs).**

---

## TC-SPL-004 — On a slow network the splash still hands over to the next screen automatically, with no error and a centred logo; screenshots are the evidence for the subjective "no flicker" part

| Field | Value |
|---|---|
| ID | TC-SPL-004 |
| Title | On a slow network the splash still hands over to the next screen automatically, with no error and a centred logo; screenshots are the evidence for the subjective "no flicker" part |
| Source CHK IDs | CHK-SPL-015 |
| Platforms | android |
| Priority | P2 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (API 36) — throttled network needs the Android emulator (not available on the iOS simulator) |
| App state | cold start; app data reset (logged out) |
| Permissions | notifications: granted (system alert auto-accepted) |
| Network | throttled from before launch (emulator: gsm speed, gprs delay); restored to normal in Postconditions |
| Preconditions | no session; the app is terminated |
| Oracle | spec — checklist CHK-SPL-015 ("handles slow initialization gracefully without visual glitches, flickering, or layout shifts"); spec — SRS §3.1.0 FR-SPL-02 (background session/token/config checks), FR-SPL-04 (automatic navigation); spec — SRS §3.3.1 (the "No Internet connection" message is for a failed connection, not a slow one — it must not appear here); D-OFF-9 (owner-pending, recon A2); observed (discovery, not proof) — recon A2 row 17, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | device.network | slow (emulator: gsm speed, gprs delay) | the emulator's network is throttled |
| 2 | open | app | cold start | — |
| 3 | expect-visible | splash.root | — | the brand splash frame is shown (Android: after the system splash, D-SPL-A1) |
| 4 | expect-visible | splash.logo | — | the logo is visible; its centre within 2 % of the screen centre (both axes) — the frame is kept as a screenshot |
| 5 | expect-hidden | offline-banner.message | — | hidden throughout the splash — a slow connection is not "no connection" (§3.3.1) |
| 6 | wait-for | welcome.root | — | appears without any input |
| 7 | expect-visible | welcome.root | — | visible — the app moved on by itself; slow network did not block the hand-over (FR-SPL-04) |

**Postconditions / cleanup:** network restored to normal speed (the harness's `finally`); nothing else to clean.
**Notes:** this reuses the TC-SPL-001 pixel/tree oracle (`splash.root` = brand-colour share of a screenshot, `splash.logo` = centre of the light blob, both `MISSING` page methods per `../splash-test-cases.md`) and the Android two-cold-start timing note from that TC's "Android (step 4 ...)" paragraph, now under throttling instead of normal speed. **Flicker/jank itself is not asserted** — CHK-SPL-015's "without visual glitches, flickering" is subjective (same reasoning as `qa/mobile/ios/not-automated.md`, CHK-SPL-013): the harness keeps the captured splash frames as evidence for a human to judge, per D-OFF-9's proposal; only the objective parts (transition happens, no error banner, logo centred) are asserted automatically. Network throttling itself (`Data: slow (emulator: gsm speed, gprs delay)`) is **not yet implemented** in `helpers/android/device.py` (only `Adb.offline()` exists, step 5's `svc wifi/data` on/off) — a work order for whoever automates this TC, e.g. an emulator console `network speed gsm` call, analogous to the `MISSING` alias work orders below.

---

## Aliases used

| Alias | Screen | android map | ios map |
|---|---|---|---|
| device.network | — (device control, not a screen element) | n/a — harness capability; `Adb.offline()` exists, a throttle/`slow` mode does **not** yet (see Notes) | n/a |
| app | — (launch / relaunch) | n/a | n/a (`helpers/app.py`) |
| splash.root | splash | step 7 (pixels) | **MISSING** — page method: brand-colour share of a screenshot (pixels), per `../splash-test-cases.md` |
| splash.logo | splash | step 7 (pixels) | **MISSING** — page method: centre of the light blob (pixels) |
| offline-banner.message | — (shared overlay, new from recon A2) | **MISSING** | **MISSING** |
| welcome.root | welcome | step 7 | yes |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| — | — | no fixture data; the TC only needs a logged-out app and a throttled network |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-SPL-015 | TC-SPL-004 | **Resolved D-OFF-9** — Owner 2026-10-01: «ок» — automated hand-over + logo check, screenshots for a person.

## Open questions

- Resolved **D-OFF-9** (owner 2026-10-01: «ок»)
- Network throttling is not yet a harness capability on Android (`helpers/android/device.py` has `Adb.offline()` only) — needed before TC-SPL-004 can run; flag together with TC-AUTH-018 (module 02), which needs the same capability.
- `splash.root` / `splash.logo` stay `MISSING` for Android as they already are for iOS (pixel-based page methods, no locator) — not a new gap introduced by this TC, carried over from `../splash-test-cases.md`.
