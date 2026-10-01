# Authentication — Android offline test cases (step 5)

> Scope/selection: the four `android-stage` checks of this module (owner, android-plan §2.5; `qa/mobile/ios/not-automated.md`) that need network control the iOS simulator does not have — CHK-AUTH-124 (login), CHK-AUTH-070 (registration), CHK-AUTH-099/-100 (OTP, offline + retry), CHK-AUTH-098 (OTP, slow network). Source recon: [qa/shared/recon-2026-10-01-android-offline.md](../../../shared/recon-2026-10-01-android-offline.md) (recon A2). Format: [qa/_templates/test-case-format.md](../../../_templates/test-case-format.md) · [qa/_templates/test-cases-mobile.md](../../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`. IDs continue from the shared file (`../authentication-test-cases.md`, TC-AUTH-001…014) — numbered from TC-AUTH-015. Conventions, fixtures and the oracle model: same as `../authentication-test-cases.md`; Android texts/behaviour differences: [../android/authentication-questions.md](authentication-questions.md) (D-AUTH-A1…A3 — none of them affect these four TCs).
>
> **Status: validated by the owner 2026-10-01 (step 5 gate: D-OFF-1…9 answered, no remarks on the TCs).**

---

## TC-AUTH-015 — Login offline shows the generic connectivity error and blocks navigation; back online, Continue retries without reopening the screen

| Field | Value |
|---|---|
| ID | TC-AUTH-015 |
| Title | Login offline shows the generic connectivity error and blocks navigation; back online, Continue retries without reopening the screen |
| Source CHK IDs | CHK-AUTH-124 |
| Platforms | android |
| Priority | P1 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi → offline (adb) → online |
| Preconditions | `{{tech.email}}` is a registered, active Field Technician; no session; Login screen open, network online |
| Oracle | spec — SRS §3.1.1.4 FR-LOG-09 ("If login request fails due to network issues, show a generic error and allow retry"); spec — SRS §3.3.1 (global "No Internet connection" message); spec — checklist CHK-AUTH-124; observed (discovery, not proof) — recon A2 row 1, row 2, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | open | device.network | off | Wi-Fi and mobile data disabled |
| 3 | fill | login.identifier | {{tech.email}} | — |
| 4 | click | login.continue | — | request attempted while offline |
| 5 | expect-visible | offline-banner.message | — | "No internet connection." (after an initial ~5 s "Slow or no internet connection…" — recon A2 row 1) |
| 6 | expect-visible | login.error | An unexpected error occurred. Please try logging in again. | the generic error, checked right after the tap (recon A2 row 2 — unconfirmed live, see Notes) |
| 7 | expect-visible | login.root | — | still on Login — no navigation to the OTP screen |
| 8 | open | device.network | on | Wi-Fi and mobile data enabled |
| 9 | click | login.continue | — | retry without reopening the screen |
| 10 | expect-visible | otp.root | — | OTP requested — the retry succeeded (FR-LOG-09 "allow retry") |

**Postconditions / cleanup:** network restored to on (also guaranteed by the harness's `finally`); reset app data (sign out) so later TCs start logged out.
**Notes:** recon A2 row 2 only confirms the top offline banner (step 5) within 6 s; it did **not** observe a distinct Login-screen message live — the text in step 6 is the app's code string ("possibly brief", recon's own words), not yet seen on screen. The first automated run confirms whether `login.error` actually renders it and for how long; if it never renders (banner only), step 6 is a test defect to fix, not a bug (doctrine rule 1/4) — flagged in Open questions, not a `D-OFF-n` (the recon table does not number this row).

---

## TC-AUTH-016 — Registration offline shows the error and keeps the form; back online, Continue retries and reaches OTP

| Field | Value |
|---|---|
| ID | TC-AUTH-016 |
| Title | Registration offline shows the error and keeps the form; back online, Continue retries and reaches OTP |
| Source CHK IDs | CHK-AUTH-070 |
| Platforms | android |
| Priority | P2 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi → offline (adb) → online |
| Preconditions | Registration screen open; `{{new_user}}` generated per run (unique names, `qa-auto+<ts>@example.com`, `+1 202 555 01xx`) and not registered |
| Oracle | spec — SRS §3.1.1.2 FR-REG-10 ("Display an error message; Allow the user to retry"); spec — SRS §3.3.1 (global "No Internet connection" message); spec — checklist CHK-AUTH-070; observed (discovery, not proof) — recon A2 row 5, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | registration | — | Welcome → Sign up |
| 2 | fill | registration.first-name | {{new_user.first_name}} | — |
| 3 | fill | registration.last-name | {{new_user.last_name}} | — |
| 4 | fill | registration.phone | {{new_user.phone}} | — |
| 5 | fill | registration.email | {{new_user.email}} | — |
| 6 | click | registration.channel-email | — | Email selected |
| 7 | open | device.network | off | Wi-Fi and mobile data disabled |
| 8 | click | registration.continue | — | registration attempted while offline |
| 9 | expect-visible | registration.snackbar | No internet connection | the SnackBar shown; registration.root stays, values preserved (recon A2 row 5 — code-only, see Notes) |
| 10 | open | device.network | on | Wi-Fi and mobile data enabled |
| 11 | click | registration.continue | — | retry without reopening the screen |
| 12 | expect-visible | otp.root | — | Email address verification — the retry succeeded |

**Postconditions / cleanup:** **in `finally`:** find the user by `GET /technician?search={{new_user.email}}` → `DELETE /user/full-delete/{user.id}` (as `../authentication-test-cases.md` TC-AUTH-013); network restored to on; reset app data.
**Notes:** recon A2 row 5 only has the SnackBar text from the app's code — "наживо не проходили" (not tried live, long form); first run confirms the exact text and that it actually renders rather than only the top offline banner. Not a `D-OFF-n` item (unnumbered in the recon table) — flagged in Open questions, test-defect-not-bug if the live text differs (doctrine rule 1/4).

---

## TC-AUTH-017 — OTP offline shows "No internet connection" under the code field; the owner's retry (tap Verify) once back online

| Field | Value |
|---|---|
| ID | TC-AUTH-017 |
| Title | OTP offline shows "No internet connection" under the code field; the owner's retry (tap Verify) once back online |
| Source CHK IDs | CHK-AUTH-099, CHK-AUTH-100 |
| Platforms | android |
| Priority | P1 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (API 36) |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi → offline (adb) → online |
| Preconditions | `{{tech.email}}` registered; no session; OTP screen open (Login → Continue completed online), network then taken offline; no other wrong OTP attempt earlier in this run (FR-OTP-13) |
| Oracle | spec — SRS §3.1.1.3 FR-OTP-12 ("If OTP verification fails due to network issues, display a generic error and allow retry"); spec — SRS §3.3.1 (global "No Internet connection" message); spec — checklist CHK-AUTH-099, CHK-AUTH-100; D-OFF-1 (owner-pending, recon A2); observed (discovery, not proof) — recon A2 row 3, row 4, 2026-10-01 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | fill | login.identifier | {{tech.email}} | — |
| 3 | click | login.continue | — | OTP requested |
| 4 | expect-visible | otp.root | — | visible |
| 5 | open | device.network | off | Wi-Fi and mobile data disabled |
| 6 | fill | otp.code | {{tech.otp}} | submits automatically (D-5 baseline, `../authentication-test-cases.md`) — attempted while offline |
| 7 | expect-visible | otp.error | No internet connection | red, under the code field (CHK-AUTH-099; recon A2 row 3) |
| 8 | expect-visible | offline-banner.message | — | the top banner also shown (recon A2 row 1) |
| 9 | open | device.network | on | Wi-Fi and mobile data enabled |
| 10 | click | otp.verify | — | the user's expected retry — tap Verify again (CHK-AUTH-100) |
| 11 | expect-visible | jobs-list.root | — | signed in — the retry succeeded |

**Postconditions / cleanup:** network restored to on; reset app data (sign out).
**Notes:** exactly one OTP attempt in this run (offline) — FR-OTP-13 locks the account for 2 min after the retry limit; serialize away from TC-AUTH-008 (which already spends the run's one wrong-OTP attempt) if both run in the same session. The offline attempt is not expected to reach the server (no request sent while offline), so it should not itself count against the server-side retry limit — unconfirmed on the first run, see Open questions.
**Resolved D-OFF-1** — Owner 2026-10-01: «ок» — treated as a bug (S3); filed after the automated run shows it (evidence from the run).

---

## TC-AUTH-018 — OTP verification on a slow network: one loading/verification pass, one navigation to the Jobs list, no duplicate OTP screen left in the back stack

| Field | Value |
|---|---|
| ID | TC-AUTH-018 |
| Title | OTP verification on a slow network: one loading/verification pass, one navigation to the Jobs list, no duplicate OTP screen left in the back stack |
| Source CHK IDs | CHK-AUTH-098 |
| Platforms | android |
| Priority | P2 |
| Automation | automated(android) — `automation/mobile/tests/android/test_offline_*.py`, reviewed 2026-10-01 |
| Device / OS | Pixel 7 · Android 16 (API 36) — throttled network needs the Android emulator |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi, then throttled (emulator: gsm speed, gprs delay) from the OTP submit on |
| Preconditions | `{{tech.email}}` registered; no session; OTP screen open (Login → Continue completed online) |
| Oracle | spec — checklist CHK-AUTH-098 ("handles slow network responses without UI freezes or duplicated states"); spec — SRS §3.1.1.3 OTP flow table ("Correct OTP entered" → "Proceed to next onboarding step"), FR-OTP-06; spec — SRS §3.3.1 (general resilience to connectivity issues) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | fill | login.identifier | {{tech.email}} | — |
| 3 | click | login.continue | — | OTP requested |
| 4 | expect-visible | otp.root | — | visible |
| 5 | open | device.network | slow (emulator: gsm speed, gprs delay) | the emulator's network is throttled |
| 6 | fill | otp.code | {{tech.otp}} | submits automatically (D-5 baseline) — the request is slow |
| 7 | wait-for | jobs-list.root | — | appears once the slow request completes — a single transition, not several screens flashing |
| 8 | expect-hidden | otp.root | — | hidden — exactly one OTP screen existed, not stacked |
| 9 | back | — | system Back from the Jobs list | does not return to the OTP screen |
| 10 | expect-hidden | otp.root | — | still hidden after Back — no duplicate code screen left in the back stack |

**Postconditions / cleanup:** network restored to normal speed; reset app data (sign out).
**Notes:** "one loading state, no duplicated states" (CHK-AUTH-098) is asserted end-to-end here — a single OTP screen instance and a single navigation under throttled network — rather than through a dedicated loading/spinner element: the Flutter tree exposes no loading/spinner alias today (not probed by recon A2, which covered full offline, not throttled). If the dev team adds one, step 6 can assert exactly one visible loading indicator directly instead. Network throttling (`Data: slow (...)`) is not yet a harness capability — same gap as TC-SPL-004 (module 01), flagged once in that file's Open questions and referenced here.

---

## Aliases used

Screen maps (android column) added in step 3 of the Android stage (map-health green). `MISSING` = new from recon A2, to be added before these four TCs can run.

| Alias | Screen | android map | ios map |
|---|---|---|---|
| device.network | — (device control) | n/a — harness capability; `Adb.offline()` exists (`helpers/android/device.py`), a throttle/`slow` mode does **not** yet | n/a |
| app, login.*, otp.root/.code/.verify, registration.*, jobs-list.root | login, otp, registration, jobs-list | yes (step 7) | yes |
| otp.error | otp | existing alias, but the map hardcodes the text "Incorrect code." (`screens/otp_map.py`) — **MISSING** a parametrised variant for "No internet connection", same pattern as `login.error` | same gap on iOS |
| offline-banner.message | — (shared overlay, new from recon A2) | **MISSING** | **MISSING** |
| registration.snackbar | registration (new from recon A2, code-only) | **MISSING** | **MISSING** |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech.email}}, {{tech.otp}} | `automation/mobile/.env` → `APP_USER_EMAIL`, `APP_USER_OTP` | existing test technician, read-only; OTP hardcoded on DEV |
| {{new_user.*}} | generated at runtime (`automation/mobile/fixtures/test_data.py`) | unique names; `qa-auto+<ts>@example.com`; `+1 202 555 01xx`; deleted in `finally` |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-AUTH-124 | TC-AUTH-015 | |
| CHK-AUTH-070 | TC-AUTH-016 | |
| CHK-AUTH-099, -100 | TC-AUTH-017 | **Resolved D-OFF-1** — Owner 2026-10-01: «ок» — treated as a bug (S3); filed after the automated run shows it (evidence from the run).
| CHK-AUTH-098 | TC-AUTH-018 | |

## Open questions

- TC-AUTH-015: the Login-screen error text in step 6 ("An unexpected error occurred. Please try logging in again.") is from the app's code only (recon A2 row 2), not yet observed live within the splash window the recon used — confirm on the first run; if it never renders, fix the step, no bug (not a numbered `D-OFF`).
- TC-AUTH-016: the registration SnackBar text in step 9 ("No internet connection") is from the app's code only (recon A2 row 5) — confirm on the first run; same test-defect-not-bug rule if it differs (not a numbered `D-OFF`).
- Resolved **D-OFF-1** (owner 2026-10-01: «ок» — bug (S3), filed after the run)
- Network throttling (`Data: slow (emulator: gsm speed, gprs delay)`) used by TC-AUTH-018 is not yet implemented in `helpers/android/device.py` — same gap as `qa/mobile/01-splash/android/splash-test-cases.md` (TC-SPL-004); one harness change covers both.
- `otp.error`'s hardcoded text and the two new aliases (`offline-banner.*`, `registration.snackbar`) are testability/map work orders, not open behavioural questions — listed in Aliases used.
