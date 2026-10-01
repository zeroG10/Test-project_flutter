# BUG-AUTH-003 — After a connection error on the code screen, Verify does nothing until a digit is changed

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-10-01 on the owner's go
> (mykola.zhuchenko, answer to D-OFF-1: «ок» — file after the automated run shows it). Tracker: not configured
> (`setup/project.yaml → tracker.system`), so nothing was sent anywhere.

## Summary

When the code check fails because the device is offline, the code screen shows "No internet connection". After the
connection is back, tapping Verify does nothing — no request, no message — although the button looks active. The
check runs again only when the user changes a digit of the code.

## Layer

- [x] App (UI) — the code screen's state is never reset after the error: `OtpVerificationBloc._onOtpVerifyRequested`
  returns at once unless the status is `initial`; after a failed check the status is `error`, and only an edited digit
  (`OtpChanged`) sets it back to `initial` (`lib/features/auth/presentation/bloc/otp_verification/
  otp_verification_bloc.dart`, read-only).
- [ ] Backend / API
- [ ] Unclear

## Severity / Priority

- **Severity:** S3 (minor) — **branch fired:** #3 — sign-in is broken on its visible path (Verify), but a workaround
  exists (change a digit, or go back and continue again).
- **Priority:** *proposal* P2 — owner / PM decide.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on Android |
| Platforms checked | Android ✓ reproduced · iOS — not checked (the iOS simulator's network cannot be switched off; the code path is shared) |
| OS version | Android 16 (API 36) |
| Device | Pixel 7 (`Pixel_7_API_36`) |
| Form factor | phone |
| Device type | emulator (Google APIs arm64) |
| App version | `[DEV] CT Mobile` 1.1.1 (178), `development` @ 85a84f3 |
| Build type | debug (flavor `development`, `CLIENT_BUILD=true`) |
| Install method | sideload (.apk) |
| Network | emulator; Wi-Fi + mobile data switched off, then on |
| Locale | en |
| Orientation | portrait |
| User role | Field Technician (signed out, signing in) |
| Feature flags | — |
| Permissions state | notifications=granted, location=granted |

## Preconditions

- A registered technician account; the app is signed out.
- The device is online.

## Steps to reproduce

1. Open the app and tap Login.
2. Enter the account's email and tap Continue.
3. On the code screen, switch the device's network off (Wi-Fi and mobile data).
4. Enter the 4-digit code.
5. Switch the network back on and wait until the device is online.
6. Tap Verify.

## Actual result

Step 4: "No internet connection" appears under the code fields (correct). Step 6: nothing happens — the screen stays
on the code with "No internet connection", no request is sent (the app's own log shows none), Verify stays enabled.
Tapping Verify again changes nothing. Only after deleting and re-entering a digit does the app check the code by itself
and sign in.
// [1-verify-does-nothing-online.png](evidence/BUG-AUTH-003/android/1-verify-does-nothing-online.png) — online (Wi-Fi in
the status bar), the code entered, the old error still shown, Verify enabled; the account's email is masked.

## Expected result

The error is generic and the user can retry (SRS FR-OTP-12): with the connection back, tapping Verify checks the code
again and, with a valid code, signs the user in.

## Frequency

- [x] Always — **3 of 3**: recon A2 (2026-10-01; Verify tapped twice by accessibility click and once by a real touch —
  no request in the app's log), the automated TC-AUTH-017 in run `offline-01021112-r1` and in run `offline-all-r1`.

## Crash? ANR?

- [ ] App crashed
- [x] No crash

## Evidence

- Screenshot: [evidence/BUG-AUTH-003/android/](evidence/BUG-AUTH-003/android/).
- Automated test: `automation/mobile/tests/android/test_offline_authentication.py::test_otp_offline_then_verify_retry`
  (TC-AUTH-017) — red at "expect screen jobs-list open" after Verify; Allure results
  `automation/mobile/results/android/2026-10-01-offline-01021112-r1/` (local only).
- Recon: `qa/shared/recon-2026-10-01-android-offline.md`, row 4; dumps `otp_retry_online*.xml`,
  `otp_after_reentry.xml` (the workaround).

## Workaround

Change any digit of the code (delete it and type it again) — the app then checks the code by itself. Or go back to
Login and tap Continue again.

## Regression info

- Last known good version: unknown.
- First broken version: unknown.

## Related

- SRS §3.1.1.3 FR-OTP-12: "If OTP verification fails due to network issues, display a generic error and allow retry."
- Checklist: `CHK-AUTH-100` — "Check that the user can retry OTP verification after network-related failures."
  (`CHK-AUTH-099`, the error itself, passes.)
- Test case: `TC-AUTH-017` ([../android/authentication-test-cases.md](../android/authentication-test-cases.md)).
- Question: `D-OFF-1` (owner, 2026-10-01: «ок»).
- Invariant: none fits — missing invariant: "an error state never leaves a primary action enabled but inert".
- Tracker: not filed (no tracker configured).
