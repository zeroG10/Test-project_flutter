# BUG-SPL-001 — A deleted account stays signed in: the app keeps opening the Jobs list and the profile after a cold start

> Process: [prompts/08-file-bug.md](../../../../prompts/08-file-bug.md). Filed locally 2026-09-24 on the owner's go
> (mykola.zhuchenko, answer 1 to the recon 4 questions: «Так»). Tracker: not configured
> (`setup/project.yaml → tracker.system`), so nothing was sent anywhere.

## Summary

After a technician's account is deleted on the server, the app on that technician's phone does not sign out: every cold
start opens the Jobs list ("No jobs") and the Profile still shows the deleted account's name, phone and email.

## Layer

- [ ] App (UI)
- [ ] Backend / API
- [x] Unclear — evidence for each side:
  - **App:** on start-up the app shows the cached user at once and signs out only when the profile request fails with
    HTTP **401** (`lib/features/auth/presentation/bloc/auth/auth_bloc.dart`, `_onStarted`: `failure.code == '401'` →
    local sign-out; any other failure → "stay authenticated"). A deleted user answered with anything but 401 (404, 500)
    keeps the session.
  - **Backend:** the deleted user's access / refresh token may still be accepted (the Jobs list loads as an empty list,
    not an error). The HTTP status of the profile request was not captured (no network capture in the recon).
  - Deciding check for the fixer: the status of the "current user" request made with the deleted user's token.

## Severity / Priority

- **Severity:** S3 (minor) — **branch fired:** #3 — session revocation is broken for a small group (deleted
  technicians); no access to other users' data was observed. **Re-grade to S1 (#1, security breach)** if the backend is
  shown to still accept the deleted user's token for data or actions.
- **Priority:** *proposal* P2 (security-flavoured) — owner / PM decide.

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
| User role | Field Technician (self-registered, then deleted) |
| Feature flags | — |
| Permissions state | notifications=granted |

## Preconditions

- A technician account registered in the app (Email channel) and signed in; the Jobs list is shown.
- The app is closed (terminated).
- The account is deleted on the server (in the recon: the admin API `DELETE /user/full-delete/{id}`,
  `UserController_fullDelete`; afterwards the technician is not found and email sign-in answers 401 — verified
  2026-09-23).

## Steps to reproduce

1. Open the app.
2. Wait 60 seconds.
3. Tap **Profile**.
4. Close the app and open it again.

## Actual result

The splash is followed by the Jobs list with "No jobs"; the app stays there for the whole minute and never returns to
Welcome. Profile shows the deleted account's name, phone and email. The next launch opens the Jobs list again.
// [jobs-list-60s-after-account-deleted.png](evidence/BUG-SPL-001/jobs-list-60s-after-account-deleted.png),
[profile-of-deleted-account.png](evidence/BUG-SPL-001/profile-of-deleted-account.png),
[next-launch-still-signed-in.png](evidence/BUG-SPL-001/next-launch-still-signed-in.png)

## Expected result

At start-up the app checks the session; when the session is no longer valid — the account no longer exists — the user
is signed out and sees Welcome, and no data of the deleted account stays on screen.

## Frequency

- [x] Always — **2 of 2 attempts** (recon 4, 2026-09-24: one cold start watched 20 s, one watched 60 s plus Profile and a
  second launch), each with a freshly registered and deleted account.

## Crash? ANR?

- [x] No crash

## Evidence

- Screenshots: [evidence/BUG-SPL-001/](evidence/BUG-SPL-001/) (generated test account data only).
- Screen trees: `qa/shared/recon-dumps/ios-2026-09-24/recon4b_revoked_{after_60s,profile,next_launch}.xml`.
- Recon report: [qa/shared/recon-2026-09-24-ios.md](../../../shared/recon-2026-09-24-ios.md), section Splash.
- Script: `automation/mobile/scripts/recon/recon_4.py`, passes `revoked`, `revoked2`.

## Workaround

The user can sign out manually from Profile. There is no workaround on the server side: deleting the account does not
end the session on the device.

## Regression info

- Last known good version: unknown.
- First broken version: unknown.
- Related: the Jobs list itself does not fall back to cached jobs on 401 / 403 (repository code) — so if the server
  answered 401 here, the list would error out; it loads empty instead.

## Related

- SRS §3.1.0 FR-SPL-02: "While the Splash Screen is displayed, the application shall perform the following background
  operations: • Validate existing user session (if any); • Verify authentication token status; …"
- SRS §3.1.1.1 FR-WEL-03: "The Welcome Screen shall be shown only when: • The user is not authenticated • No valid
  session token exists"
- SRS §5.2 Security: "Secure authentication mechanisms"
- Checklist: `CHK-SPL-009` ([../splash-checklist.md](../splash-checklist.md)); Auth coverage review MISS-10.
- Test case: `TC-SPL-003` ([../splash-test-cases.md](../splash-test-cases.md)) — stays red against this bug.
- Question: `Q-SPL-3` in [../splash-questions.md](../splash-questions.md).
- Invariant: none fits — missing invariant: "a session whose account no longer exists is ended on the device at the next
  start-up".
- Tracker: not filed (no tracker configured).

> **When this bug is verified fixed:** re-run TC-SPL-003 on the fixed build (the regression check), then add the invariant
> above to `qa/shared/oracles/invariants.md`.
