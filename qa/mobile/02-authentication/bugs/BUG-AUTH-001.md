# BUG-AUTH-001 — Login with an unregistered phone number shows a generic error instead of "not registered"

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-09-23 on the owner's go
> (mykola.zhuchenko: "заведи як баг"). Tracker: not configured (`setup/project.yaml → tracker.system`), so nothing was
> sent anywhere; who fixes it is decided later.

## Summary

Requesting a login code for a phone number that has no account shows "An unexpected error occurred. Please try logging
in again." instead of the "not registered" message; the same request with an unregistered email shows the correct message.

## Layer

- [ ] App (UI)
- [x] Backend / API — most likely (owner's assessment: wrong response from the backend)
- [ ] Unclear

Evidence for the layer: the app picks the "not registered" message only when the sign-in request fails with **HTTP 401**
(`lib/features/auth/presentation/bloc/sign_in/sign_in_cubit.dart`, `_messageFor`: `failure.code == '401'`); any other
failure, or a 2xx without a temp token, becomes the generic message. For an unregistered email the backend answers 401
(correct message shown); for an unregistered phone it evidently answers something else. The actual status code of the
phone request was not captured (no network capture in the run).

## Severity / Priority

- **Severity:** S3 (minor) — **branch fired:** #3 — the "account not found" guidance for phone login is broken, a
  workaround exists (the user can open Sign up from the Login screen); login itself works for registered users.
- **Priority:** *proposal* P3 — owner / PM decide.

## Environment

| Field | Value |
|---|---|
| Platform | Flutter on iOS |
| OS version | iOS 26.5 |
| Device | iPhone 17 |
| Form factor | phone |
| Device type | simulator |
| App version | `[DEV] CT Mobile` 1.1.1 (178), `development` @ 85a84f3 |
| Build type | debug (flavor `development`, `CLIENT_BUILD=true`) |
| Install method | sideload (simulator build) |
| Network | Wi-Fi (host network), DEV API |
| Locale | en |
| Orientation | portrait |
| User role | guest (signed out) |
| Feature flags | — |
| Permissions state | notifications=granted |

## Preconditions

- The app is installed and signed out (Welcome screen).
- The phone number used has no account on DEV (numbers from the fictional range `+1 202 555 01xx`).

## Steps to reproduce

1. Open the app.
2. Tap **Login**.
3. Type a phone number that has no account, e.g. `+12025550187`.
4. Tap **Continue**.

## Actual result

A red banner at the bottom for ~4 s: "An unexpected error occurred. Please try logging in again."; the app stays on Login
with the number kept in the field. // [evidence/BUG-AUTH-001/unregistered-phone-banner.png](evidence/BUG-AUTH-001/unregistered-phone-banner.png)

## Expected result

When the entered phone number is not associated with an account, the app tells the user so and points to registration:
"This phone number is not registered yet. Create an account to get started." (checklist wording, accepted by the owner
over the SRS wording — D-8).

## Frequency

- [x] Always — **3 of 3 attempts**, three different numbers from `+1 202 555 01xx` (run 1, targeted re-run, run 2 —
  2026-09-23). Not tried with a real, unregistered, non-fictional number (would send an SMS to a real person).

## Crash? ANR?

- [x] No crash

## Evidence

- Screenshot: [evidence/BUG-AUTH-001/unregistered-phone-banner.png](evidence/BUG-AUTH-001/unregistered-phone-banner.png)
- Screen recording: Allure result of run 2 (`automation/mobile/allure-results`, test
  `test_login_rejects_unregistered_phone`, attachment "video · test_login_rejects_unregistered_phone") — local only.
- Automated test: `automation/mobile/tests/shared/test_authentication.py::test_login_rejects_unregistered_phone` — red,
  kept red against the checklist (not edited, not quarantined).
- Contrast: `test_login_rejects_invalid_and_unregistered_email` — the email path shows "This email is not registered yet.
  Create an account to get started." (passed, run 2).

## Workaround

Tap **Sign up** on the Login screen and register.

## Regression info

- Last known good version: unknown (the checklist of May 2026 lists the expected message).
- First broken version: unknown.
- Open point for the fixer: whether the backend rejects the fictional 555-01xx range differently (e.g. an SMS-provider
  validation error) from a real unregistered number — if so, the app still shows a misleading message for it.

## Related

- Checklist: `CHK-AUTH-122` — "Check that the error message “This phone number is not registered yet. Create an account to
  get started.” is displayed for unregistered phone numbers." ([../authentication-checklist.md](../authentication-checklist.md))
- SRS §3.1.1.4 FR-LOG-08: "If the phone number is not associated with an account, display: No account found with this
  phone number." (wording superseded by the checklist — D-8, owner 2026-09-23)
- Test case: `TC-AUTH-007` ([../authentication-test-cases.md](../authentication-test-cases.md))
- Question: `D-15` in [../authentication-questions.md](../authentication-questions.md)
- Invariant: none fits — missing invariant: "a sign-in request for an unknown identifier yields the not-registered guidance
  for every identifier type".
- Tracker: not filed (no tracker configured).

> **When this bug is verified fixed:** re-run `test_login_rejects_unregistered_phone` on the fixed build (it is the
> regression check), then add the invariant above to `qa/shared/oracles/invariants.md`.
