# BUG-AUTH-002 — Registration caps first and last name at 50 characters while the SRS allows 100

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-09-23 on the owner's go
> (mykola.zhuchenko: "заведи, але це не критично — потім ПМ або поправить у СРС, або девелопер пофіксить").
> Tracker: not configured, nothing sent anywhere. Resolution is either a requirement change (SRS → 50) or an app change
> (limit → 100) — the owner / PM decide.

## Summary

The First name and Last name fields on Registration stop accepting input after 50 characters, without any message; the
SRS field table specifies a maximum of 100 characters.

## Layer

- [x] App (UI) — the limit is an input formatter in the app: `LengthLimitingTextInputFormatter(50)` on both name fields
  (`lib/features/auth/presentation/pages/sign_up_page.dart`). What the backend accepts was not checked.
- [ ] Backend / API
- [ ] Unclear

## Severity / Priority

- **Severity:** S4 (cosmetic / minor) — **branch fired:** #4 — rare edge case (names longer than 50 characters), the user
  can still register with a shortened name; no data is lost silently beyond the 50th character being refused at typing.
- **Priority:** *proposal* P4 — owner / PM decide (possibly an SRS correction rather than a code change).

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

## Steps to reproduce

1. Open the app.
2. Tap **Sign up**.
3. Type 101 letters into **First name**.
4. Look at the field's value.

## Actual result

The field keeps the first 50 letters and ignores the rest; no message is shown. Same for **Last name**.
// automated check `test_registration_field_validation[first-51-chars]` (51 typed → 50 kept, run 2, passed as the app behaves)

## Expected result

First name and Last name accept alphabetical input from 2 up to 100 characters (SRS field table, quoted in Related).

## Frequency

- [x] Always — 2 of 2 attempts (probe 2026-09-23: 101 typed → 50 kept; run 2: 51 typed → 50 kept); deterministic by code.

## Crash? ANR?

- [x] No crash

## Evidence

- Automated test: `automation/mobile/tests/shared/test_authentication.py::test_registration_field_validation[first-51-chars]`
  and `[first-50-chars]` — they assert the **current** app behaviour (limit 50) by the standing oracle rule (the app is
  the accepted baseline; the discrepancy is recorded, not asserted against). When this bug is resolved, the two rows
  follow the decision: SRS → 50 (rows stay), app → 100 (rows move to 100 / 101).
- App code: `sign_up_page.dart` lines with `LengthLimitingTextInputFormatter(50)` (read-only audit).

## Workaround

Enter a shortened name.

## Regression info

- Last known good version: unknown — no version known to allow 100.

## Related

- SRS §3.1.1.2, Registration input fields: "First name | Text | Yes | Alphabetical characters only(Minimum: 2 characters,
  Maximum: 100 characters)" and "Last name | Text | Yes | Alphabetical characters only (Minimum: 2 characters, Maximum:
  100 characters)".
- Checklist: no item covers the maximum length (CHK-AUTH-026…033 cover required / min / characters).
- Test case: `TC-AUTH-011` rows `first-50-chars`, `first-51-chars` ([../authentication-test-cases.md](../authentication-test-cases.md))
- Question: `D-14` in [../authentication-questions.md](../authentication-questions.md)
- Tracker: not filed (no tracker configured).
