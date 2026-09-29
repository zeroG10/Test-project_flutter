# Test cases — Authentication (mobile)

> Structured, alias-based test cases for the CHK IDs selected in
> [authentication-automation-plan.md](authentication-automation-plan.md) (narrow pilot, owner decision 2026-09-23).
> Format: [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) ·
> [qa/_templates/test-cases-mobile.md](../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`.

| Field | Value |
|---|---|
| Feature | Authentication — Welcome, Login, OTP verification, Registration, SMS Terms |
| Platform | cross-platform (Flutter app driven by native drivers) — iOS first, then Android |
| Source checklist | `qa/mobile/02-authentication/authentication-checklist.md` (CHK-AUTH-001…126) |
| Selection | `qa/mobile/02-authentication/authentication-automation-plan.md` → Selected CHK IDs (82) |
| Min OS | iOS 16.0 / Android 12.1 (SRS §2.4) — not run by decision; see [supported-devices.md](../../../docs/platform-specs/supported-devices.md) |
| Devices | iPhone 17 · iOS 26.5 (simulator); Pixel 7 · Android 15 / API 35 (emulator) — [device matrix](../../shared/device-matrix/device-matrix.md) |
| Build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko |
| Last updated | 2026-09-23 |

Execution statuses: **Passed / Failed / Skipped / Blocked / (empty)** — results go to
`ios/` / `android/authentication-traceability.md` (via `trace_results.py`), never into this file.

**Conventions used in this file**

- **Priority:** P0 = smoke, every run · P1 = release regression · P2 = full suite · P3 = edge / scheduled.
- **Oracle model:** accepted production baseline (`docs/notes/decisions.md`, 2026-09-23). Where the SRS and the
  checklist disagree, the checklist wording (written against the live app) is used and the difference is a
  question (D-1…D-11 in `authentication-questions.md`), never a silent choice. D-1…D-11 are accepted by the owner.
- **Positional expectations** ("below", "in the bottom area", "centred") are asserted from element bounds with a 2 %
  screen-width tolerance by a BasePage helper — objective, not eyeballed. Colour / filled / outlined styling is not
  asserted: those parts of a CHK item stay manual and are marked **partial** in *Coverage*.
- **Visibility, not presence:** the OTP screen keeps a hidden `Incorrect code.` in the accessibility tree
  (recon 3b); every error expectation below is `expect-visible` / `expect-hidden`.
- **Login in tests:** the token lives in the iOS keychain, so there is no token injection on mobile. UI login
  appears only in the TCs that prove login (TC-AUTH-005, -006, -008, -009, -013); other suites use a session-scoped
  UI-login fixture once per run.
- **DEV-friendly:** serial runs; at most one wrong OTP per run (FR-OTP-13 locks the account for 2 min).

---

## TC-AUTH-001 — Welcome screen shows the header, subtext and both actions, without back navigation

| Field | Value |
|---|---|
| ID | TC-AUTH-001 |
| Title | Welcome screen shows the header, subtext and both actions, without back navigation |
| Source CHK IDs | CHK-AUTH-001, CHK-AUTH-003, CHK-AUTH-004, CHK-AUTH-005, CHK-AUTH-007, CHK-AUTH-008 |
| Platforms | ios, android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; app data reset (logged out) |
| Permissions | notifications: granted (system alert auto-accepted) |
| Network | online Wi-Fi |
| Preconditions | no session |
| Oracle | spec — SRS §3.1.1.1 UI Description, FR-WEL-03; spec — accepted baseline, recon 2026-09-23 (header text D-1); spec — figma:2451:82537 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | cold start | Splash, then Welcome |
| 2 | expect-visible | welcome.root | — | visible |
| 3 | expect-text | welcome.title | — | Welcome to Concert Technologies' Field Force |
| 4 | expect-visible | welcome.title | — | visible; horizontally centred |
| 5 | expect-text | welcome.subtitle | — | Create an account or log in to get started. — below welcome.title |
| 6 | expect-visible | welcome.sign-up | — | visible; in the bottom area of the screen |
| 7 | expect-visible | welcome.login | — | visible; below welcome.sign-up |
| 8 | expect-hidden | welcome.back | — | hidden (no back button) |

**Postconditions / cleanup:** nothing to clean.
**Notes:** CHK-AUTH-004 "centred" and the positions in CHK-AUTH-005/-007/-008 are asserted from bounds; the
filled / outlined styling in CHK-AUTH-007/-008 stays manual (partial).

---

## TC-AUTH-002 — Welcome actions open Registration and Login

| Field | Value |
|---|---|
| ID | TC-AUTH-002 |
| Title | Welcome actions open Registration and Login |
| Source CHK IDs | CHK-AUTH-009, CHK-AUTH-010, CHK-AUTH-016, CHK-AUTH-103 |
| Platforms | ios, android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; app data reset (logged out) |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | no session |
| Oracle | spec — SRS §3.1.1.1 FR-WEL-01, FR-WEL-02; spec — figma:3608:11989 (Registration_Updated), figma:3191:12922 (Log in_Updated) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | cold start | Welcome |
| 2 | expect-visible | welcome.root | — | visible |
| 3 | click | welcome.sign-up | — | — |
| 4 | expect-visible | registration.root | — | visible |
| 5 | open | app | terminate, then cold start | Welcome (signed out) |
| 6 | expect-visible | welcome.root | — | visible |
| 7 | click | welcome.login | — | — |
| 8 | expect-visible | login.root | — | visible |

**Postconditions / cleanup:** nothing to clean.
**Notes:** Registration has no on-screen back control (recon 3c), and **no back stack either**: Welcome opens it with
`context.go(Routes.signUp)` — a route replace (app code, `welcome_page.dart`). The first run (2026-09-23) failed on the
old step 5 "system back → Welcome": a test-design assumption no CHK asks for, not an app defect. Step 5 is now a cold
start; the CHK coverage is unchanged.

---

## TC-AUTH-003 — A valid session skips Welcome and opens the Jobs list on relaunch

| Field | Value |
|---|---|
| ID | TC-AUTH-003 |
| Title | A valid session skips Welcome and opens the Jobs list on relaunch |
| Source CHK IDs | CHK-AUTH-002 |
| Platforms | ios, android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | terminated after sign-in → cold start |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in as `{{tech.email}}` (session created by the `ui_login` fixture) |
| Oracle | spec — SRS §3.1.0 FR-SPL-04, §3.1.1.1 FR-WEL-04 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-visible | jobs-list.root | — | visible (session active) |
| 2 | open | app | terminate, then cold start | Splash, then the Jobs list |
| 3 | expect-visible | jobs-list.root | — | visible |
| 4 | expect-hidden | welcome.root | — | hidden |

**Postconditions / cleanup:** reset app data (sign out) so later TCs start logged out.
**Notes:** also a reference check for module 01-splash (FR-SPL-04).

---

## TC-AUTH-004 — Login screen shows its content and keeps Continue disabled while the field is empty

| Field | Value |
|---|---|
| ID | TC-AUTH-004 |
| Title | Login screen shows its content and keeps Continue disabled while the field is empty |
| Source CHK IDs | CHK-AUTH-104, CHK-AUTH-105, CHK-AUTH-106, CHK-AUTH-107, CHK-AUTH-108, CHK-AUTH-109 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | no session |
| Oracle | spec — SRS §3.1.1.4 FR-LOG-04; spec — accepted baseline, recon 2026-09-23 (D-2, D-3, D-4); spec — figma:3191:12922 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | expect-text | login.title | — | Log in |
| 3 | expect-text | login.subtitle | — | Good to see you! Let's get you logged in. |
| 4 | expect-text | login.helper | — | Enter the email or phone number you used during registration |
| 5 | expect-visible | login.identifier | — | visible — the only input on the screen |
| 6 | expect-disabled | login.continue | — | disabled |
| 7 | expect-visible | login.privacy-link | — | visible |
| 8 | expect-visible | login.terms-link | — | visible |
| 9 | expect-visible | login.sign-up-link | — | visible |

**Postconditions / cleanup:** nothing to clean.
**Notes:** the logo in CHK-AUTH-104 is an unlabelled image — title/subtitle are asserted, the logo stays manual
(partial). "Only input" in step 5 is asserted as a count of text fields on the screen.

---

## TC-AUTH-005 — Login with email and the OTP opens the Jobs list

| Field | Value |
|---|---|
| ID | TC-AUTH-005 |
| Title | Login with email and the OTP opens the Jobs list |
| Source CHK IDs | CHK-AUTH-110, CHK-AUTH-115, CHK-AUTH-117, CHK-AUTH-119, CHK-AUTH-073, CHK-AUTH-074, CHK-AUTH-075, CHK-AUTH-088, CHK-AUTH-089; also CHK-ORDL-001 of module 03 (landing screen after login — owner, 2026-09-24) |
| Platforms | ios, android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | `{{tech.email}}` is a registered, active Field Technician; no session |
| Oracle | spec — SRS §3.1.1.4 FR-LOG-05, §3.1.1.3 FR-OTP-06; spec — checklist CHK-AUTH-117/119 (email channel, D-2); spec — accepted baseline (auto-submit, D-5) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | fill | login.identifier | {{tech.email}} | keyboard: email |
| 3 | expect-enabled | login.continue | — | enabled |
| 4 | click | login.continue | — | OTP requested |
| 5 | expect-text | otp.title | — | Email address verification |
| 6 | expect-text | otp.instruction | — | Enter the 4-digit code sent to your email address |
| 7 | expect-text | otp.destination | — | {{tech.email}} |
| 8 | fill | otp.code | {{tech.otp}} | submits automatically after the 4th digit (D-5) |
| 9 | expect-visible | jobs-list.root | — | visible |

**Postconditions / cleanup:** reset app data (sign out).
**Notes:** this TC proves login; it is the P0 gateway for every other suite.

---

## TC-AUTH-006 — Login with a phone number opens Phone verification and completes sign-in

| Field | Value |
|---|---|
| ID | TC-AUTH-006 |
| Title | Login with a phone number opens Phone verification and completes sign-in |
| Source CHK IDs | CHK-AUTH-111, CHK-AUTH-116, CHK-AUTH-118, CHK-AUTH-072, CHK-AUTH-096 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | `{{tech.phone}}` belongs to the registered test technician; no session |
| Oracle | spec — SRS §3.1.1.3 (Phone number verification), FR-OTP-06; spec — checklist CHK-AUTH-116/118 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | fill | login.identifier | {{tech.phone}} | — |
| 3 | expect-enabled | login.continue | — | enabled |
| 4 | click | login.continue | — | OTP requested |
| 5 | expect-text | otp.title | — | Phone number verification |
| 6 | expect-text | otp.destination | — | contains: {{tech.phone_last4}} |
| 7 | fill | otp.code | {{tech.otp}} | submits automatically |
| 8 | expect-visible | jobs-list.root | — | visible |

**Postconditions / cleanup:** reset app data (sign out).
**Notes:** SMS delivery itself is not observable on DEV (hardcoded OTP) — the TC proves the phone channel's UI flow.
`{{tech.phone}}` is typed in E.164 (`+1…`), as the field's own hint states: `Format: +1234567890 or name@example.com`
(Q-A1 resolved, recon 2026-09-23).

---

## TC-AUTH-007 — Login rejects an invalid format and an unregistered email or phone

| Field | Value |
|---|---|
| ID | TC-AUTH-007 |
| Title | Login rejects an invalid format and an unregistered email or phone |
| Source CHK IDs | CHK-AUTH-114, CHK-AUTH-121, CHK-AUTH-122, CHK-AUTH-123, CHK-AUTH-125 (CHK-AUTH-112 — Skipped, D-12) |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | `{{unregistered.email}}` and `{{unregistered.phone}}` are generated per run and not registered |
| Oracle | spec — checklist CHK-AUTH-122/123 (live-app wording) over SRS FR-LOG-03/08 — D-8; accepted baseline for invalid formats — D-12 (owner, 2026-09-23) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | fill | login.identifier | {{invalid.identifier}} | e.g. `abc@`, `12ab` |
| 3 | expect-visible | login.format-hint | — | visible — the only guidance shown; no error message (D-12) |
| 4 | expect-disabled | login.continue | — | disabled |
| 5 | fill | login.identifier | {{unregistered.email}} | replaces the value |
| 6 | expect-enabled | login.continue | — | enabled — the invalid state is cleared after correction (CHK-AUTH-114) |
| 7 | click | login.continue | — | request sent |
| 8 | expect-text | login.error | — | This email is not registered yet. Create an account to get started. |
| 9 | expect-text | login.identifier | — | {{unregistered.email}} (value preserved) |
| 10 | fill | login.identifier | {{unregistered.phone}} | retry without reopening the screen |
| 11 | click | login.continue | — | request sent |
| 12 | expect-text | login.error | — | This phone number is not registered yet. Create an account to get started. |

**Postconditions / cleanup:** nothing created, nothing to clean.
**Notes:** the moment validation fires (while typing / on focus loss) is confirmed during mapping; validation styling
(CHK-AUTH-113) stays manual.
**Recon 3d (2026-09-23):** the Login screen shows **no** format message for any invalid value tried — only Continue
stays disabled. **D-12 accepted as is (owner, 2026-09-23):** steps 3 and 6 assert that; CHK-AUTH-112 is reported
Skipped with reason D-12.
The server messages are a red banner at the bottom for ~4 s (element `Other` named by its text); the email wording is
confirmed verbatim, the phone wording is still the checklist's. `a b@c.com` enables Continue — D-13, no test (owner: spaces are trimmed).
**Run 1 (2026-09-23):** the unregistered **phone** got "An unexpected error occurred. Please try logging in again." (D-15, open).
The TC is automated as two tests so the email CHKs are not failed by the phone question: `test_login_rejects_invalid_and_unregistered_email` (steps 1–9 + retry with a second email — CHK-114/121/123/125) and `test_login_rejects_unregistered_phone` (steps 10–12 — CHK-122).

---

## TC-AUTH-008 — An incorrect OTP shows a visible error and the code stays editable; the correct code then signs in

| Field | Value |
|---|---|
| ID | TC-AUTH-008 |
| Title | An incorrect OTP shows a visible error and the code stays editable; the correct code then signs in |
| Source CHK IDs | CHK-AUTH-090, CHK-AUTH-091 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | `{{tech.email}}` registered; no session; no wrong OTP attempts earlier in this run |
| Oracle | spec — SRS FR-OTP-07; spec — checklist CHK-AUTH-090 ("Incorrect code"); spec — recon 3b (error kept hidden in the tree) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | fill | login.identifier | {{tech.email}} | — |
| 3 | click | login.continue | — | — |
| 4 | expect-visible | otp.root | — | visible |
| 5 | expect-hidden | otp.error | — | hidden before any input |
| 6 | fill | otp.code | {{otp.wrong}} | submits automatically |
| 7 | expect-visible | otp.error | — | Incorrect code. — visible |
| 8 | expect-visible | otp.root | — | still on the OTP screen (not signed in) |
| 9 | fill | otp.code | {{tech.otp}} | the code field accepts a new value |
| 10 | expect-visible | jobs-list.root | — | visible |

**Postconditions / cleanup:** reset app data (sign out).
**Notes:** exactly one wrong attempt — FR-OTP-13 locks the account for 2 minutes after the limit.
**Recon 3d (2026-09-23):** `Incorrect code.` is in the tree AND reported visible before any input while nothing is drawn
(TD-AUTH-008). Steps 5 and 7 are therefore decided by **pixels** — ink inside the element's bounds on the screenshot
(`OtpPage.expect_error_shown`, `helpers/pixels.py`: 0.000 when not drawn, 0.10–0.15 for drawn text, threshold 0.03).
The "drawn" side of the threshold is proven on the first run (the only wrong OTP of the run).

---

## TC-AUTH-009 — OTP screen: Verify disabled below 4 digits, resend locked during the countdown, back returns to Login without signing in

| Field | Value |
|---|---|
| ID | TC-AUTH-009 |
| Title | OTP screen: Verify disabled below 4 digits, resend locked during the countdown, back returns to Login without signing in |
| Source CHK IDs | CHK-AUTH-077, CHK-AUTH-078, CHK-AUTH-080, CHK-AUTH-097, CHK-AUTH-126 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | `{{tech.email}}` registered; no session |
| Oracle | spec — SRS FR-OTP-04, FR-OTP-08, FR-OTP-09; spec — checklist CHK-AUTH-097, CHK-AUTH-126 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | login | — | Welcome → Login |
| 2 | fill | login.identifier | {{tech.email}} | — |
| 3 | click | login.continue | — | — |
| 4 | fill | otp.code | 123 | three digits only |
| 5 | expect-disabled | otp.verify | — | disabled |
| 6 | expect-text | otp.resend | — | contains: You can request a new code in |
| 7 | expect-text | otp.resend | — | countdown value lower than at step 6 (read again ≥ 2 s later) |
| 8 | back | — | — | Login (system back; the OTP back button has no label) |
| 9 | expect-visible | login.root | — | visible |
| 10 | open | app | terminate, then cold start | — |
| 11 | expect-visible | welcome.root | — | visible — no session without a verified OTP |

**Postconditions / cleanup:** reset app data.
**Notes:** the enabled "Request a new code" state after expiry (CHK-AUTH-079) needs a ~60 s wait and is deferred.
**Recon 3d (2026-09-23):** Verify is disabled with 3 digits; resend text `Didn't receive the code? You can request a new
code in 0:59` counts down (58 s → 55 s); the OTP back button is labelled `Back` and the iOS edge swipe also returns to
Login — step 8 uses the system back as written.

---

## TC-AUTH-010 — Registration form shows its fields and sections in order, the +1 prefix, and Continue disabled by default

| Field | Value |
|---|---|
| ID | TC-AUTH-010 |
| Title | Registration form shows its fields and sections in order, the +1 prefix, and Continue disabled by default |
| Source CHK IDs | CHK-AUTH-017, CHK-AUTH-018, CHK-AUTH-019, CHK-AUTH-020, CHK-AUTH-021, CHK-AUTH-022, CHK-AUTH-023, CHK-AUTH-024, CHK-AUTH-035 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | no session |
| Oracle | spec — SRS §3.1.1.2 UI Description; spec — checklist CHK-AUTH-017…024; spec — figma:3608:12175; spec — decision `CLIENT_BUILD=true` (+1 default) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | registration | — | Welcome → Sign up |
| 2 | expect-text | registration.title | — | Registration |
| 3 | expect-text | registration.subtitle | — | Good to see you! Let's get you registered. |
| 4 | expect-visible | registration.first-name | — | visible; order top-to-bottom: first-name, last-name, phone, email |
| 5 | expect-text | registration.phone-prefix | — | +1 |
| 6 | expect-visible | registration.channel-section | — | visible; below registration.email |
| 7 | expect-visible | registration.channel-options | — | SMS and Email options visible |
| 8 | expect-visible | registration.sms-consent | — | visible; below the channel section |
| 9 | expect-disabled | registration.continue | — | disabled |
| 10 | expect-visible | registration.privacy-link | — | visible; below registration.continue |
| 11 | expect-visible | registration.terms-link | — | visible |
| 12 | expect-visible | registration.log-in-link | — | visible; in the bottom area |

**Postconditions / cleanup:** nothing to clean.
**Notes:** the logo in CHK-AUTH-017 is an unlabelled image (partial). Registration aliases are `MISSING` until the
Registration recon pass.

---

## TC-AUTH-011 — Registration validates first name, last name, phone and email (parametrised)

| Field | Value |
|---|---|
| ID | TC-AUTH-011 |
| Title | Registration validates first name, last name, phone and email (parametrised) |
| Source CHK IDs | CHK-AUTH-026, CHK-AUTH-027, CHK-AUTH-028, CHK-AUTH-029, CHK-AUTH-030, CHK-AUTH-031, CHK-AUTH-032, CHK-AUTH-033, CHK-AUTH-034, CHK-AUTH-041, CHK-AUTH-043, CHK-AUTH-044, CHK-AUTH-045, CHK-AUTH-046, CHK-AUTH-047 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | Registration screen open, all fields empty |
| Oracle | spec — SRS §3.1.1.2 field table (2–100 chars, alphabetic), FR-REG-01…05; spec — accepted baseline, recon 3c 2026-09-23 (error texts, D-10, D-11); spec — checklist CHK-AUTH-043 (Email required — D-6) |

Test design: **equivalence partitioning + boundary values**. One run per data row. Error texts are the live-app
wording captured in recon 3c; errors appear while typing (no blur needed).

| field | {{value}} | class | {{expected}} |
|---|---|---|---|
| first-name | *(typed, then cleared)* | required | Field is required. |
| first-name | `A` | below min (1) | 2 characters minimum. |
| first-name | `Al` | min (2) | no error |
| first-name | 50 × `a` | max (50, D-14) | no error |
| first-name | 51 × `a` | above max (51) | input capped at 50, no error (D-14) |
| first-name | `Ann3` | digit | Has invalid characters. |
| first-name | `An@n` | special character | Has invalid characters. |
| last-name | *(typed, then cleared)* | required | Field is required. |
| last-name | `B` | below min | 2 characters minimum. |
| last-name | `Bo` | min | no error |
| last-name | `B3` | digit | Has invalid characters. |
| phone | *(typed, then cleared)* | required | Phone number is required |
| phone | `123` | malformed | Enter a valid phone number |
| phone | `2025550123` | valid (US) | no error — shown as `(202) 555-0123` |
| email | *(typed, then cleared)* | required (D-6) | Field is required. |
| email | `abc@` | malformed | Email format is incorrect. |
| email | `qa-auto@example.com` | valid | no error |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | registration | — | Welcome → Sign up |
| 2 | fill | registration.{{field}} | {{value}} | — |
| 3 | click | registration.title | — | focus leaves the field (validation triggered) |
| 4 | expect-text | registration.error[{{field}}] | — | {{expected}} — or expect-hidden when "no error" |
| 5 | fill | registration.{{field}} | {{valid value for the field}} | correction |
| 6 | expect-hidden | registration.error[{{field}}] | — | hidden (error cleared dynamically) |

**Postconditions / cleanup:** nothing submitted, nothing to clean.
**Notes:** error texts captured in recon 3c (Q-A3 resolved) and asserted verbatim. Probe 2026-09-23 (step 6): required
wording `Field is required.` (names, email) / `Phone number is required` (phone); names are **capped at 50 characters**
without a message — SRS says 100 (D-14), the rows assert the app.
Step 3 is kept as a harmless focus change: validation already fires while typing.

---

## TC-AUTH-012 — Choosing the SMS channel requires accepting the SMS Terms

| Field | Value |
|---|---|
| ID | TC-AUTH-012 |
| Title | Choosing the SMS channel requires accepting the SMS Terms |
| Source CHK IDs | CHK-AUTH-049, CHK-AUTH-053, CHK-AUTH-055, CHK-AUTH-056, CHK-AUTH-060, CHK-AUTH-061 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | Registration screen open; first name, last name, phone and email filled with valid `{{new_user}}` values; nothing submitted |
| Oracle | spec — SRS §3.4.1 CR-1 FR-008, FR-009; spec — accepted baseline, recon 3c 2026-09-23 (SMS Terms opened by the SMS channel, D-9); spec — checklist CHK-AUTH-049, -055, -060, -061; spec — figma:3608:12130 (SMS Terms) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | registration.channel-sms | — | opens SMS Terms (D-9) |
| 2 | expect-visible | sms-terms.root | — | SMS Messaging Terms & Conditions |
| 3 | scroll-to | sms-terms.accept | — | — |
| 4 | click | sms-terms.accept | — | I Accept SMS Terms & Conditions |
| 5 | expect-visible | registration.root | — | Terms closed, back on Registration; SMS channel selected |
| 6 | expect-visible | registration.sms-consent-text | — | visible; below the consent checkbox |
| 7 | expect-enabled | registration.sms-consent | — | enabled once SMS is chosen |
| 8 | expect-disabled | registration.continue | — | disabled — SMS chosen, consent not given |
| 9 | click | registration.sms-consent | — | consent checked |
| 10 | expect-enabled | registration.continue | — | enabled |

**Postconditions / cleanup:** nothing submitted, nothing to clean.
**Notes:** the flow follows the live app (D-9): the SMS channel opens the Terms, Accept selects SMS, the consent
checkbox is a separate step. Radio state is readable (`value` = 1 on the selected option); the checkbox is a
`Switch` with `value` 0/1. The SMS Terms close icon has no label (CHK-AUTH-057 deferred — testability defect).

---

## TC-AUTH-013 — Registering with the Email channel verifies the email and opens the Jobs list

| Field | Value |
|---|---|
| ID | TC-AUTH-013 |
| Title | Registering with the Email channel verifies the email and opens the Jobs list |
| Source CHK IDs | CHK-AUTH-050, CHK-AUTH-062, CHK-AUTH-063, CHK-AUTH-064, CHK-AUTH-066 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | Registration screen open; `{{new_user}}` generated per run (unique names, `qa-auto+<ts>@example.com`, `+1 202 555 01xx`) and not registered |
| Oracle | spec — SRS §3.1.1.2 FR-REG-07; spec — CR-1 FR-008, FR-012 (Email channel → OTP by email); spec — checklist CHK-AUTH-064/066 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | fill | registration.first-name | {{new_user.first_name}} | — |
| 2 | fill | registration.last-name | {{new_user.last_name}} | — |
| 3 | fill | registration.phone | {{new_user.phone}} | — |
| 4 | fill | registration.email | {{new_user.email}} | — |
| 5 | click | registration.channel-email | — | Email selected |
| 6 | expect-enabled | registration.continue | — | enabled |
| 7 | click | registration.continue | — | registration request sent |
| 8 | expect-text | otp.title | — | Email address verification |
| 9 | expect-text | otp.destination | — | {{new_user.email}} |
| 10 | fill | otp.code | {{tech.otp}} | DEV code; submits automatically |
| 11 | expect-visible | jobs-list.root | — | visible — the new technician is signed in |

**Postconditions / cleanup:** **in `finally`:** find the user by `GET /technician?search={{new_user.email}}` →
`DELETE /user/full-delete/{user.id}` (verified 2026-09-23: technician 404, email sign-in 401); reset app data.
**Notes:** OTP leads straight to the Jobs list — no further onboarding (Q-A2 resolved, recon 3c); the new user's
list shows the `No jobs` empty state. Choosing Email hides the SMS consent block. Only reserved email/phone ranges
are used so no real person receives a message.

---

## TC-AUTH-014 — Registering with an already registered phone shows an error, keeps the values and allows a retry

| Field | Value |
|---|---|
| ID | TC-AUTH-014 |
| Title | Registering with an already registered phone shows an error, keeps the values and allows a retry |
| Source CHK IDs | CHK-AUTH-068, CHK-AUTH-069, CHK-AUTH-071 |
| Platforms | ios, android |
| Priority | P2 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; logged out |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | Registration screen open; `{{tech.phone}}` is already registered; `{{new_user}}` generated |
| Oracle | spec — checklist CHK-AUTH-069 (live-app wording) over SRS FR-REG-11 — D-7 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | fill | registration.first-name | {{new_user.first_name}} | — |
| 2 | fill | registration.last-name | {{new_user.last_name}} | — |
| 3 | fill | registration.phone | {{tech.phone_national}} | already registered |
| 4 | fill | registration.email | {{new_user.email}} | — |
| 5 | click | registration.channel-email | — | — |
| 6 | click | registration.continue | — | request sent |
| 7 | expect-text | registration.form-error | — | An account with this phone number already exists. Please log in to continue. |
| 8 | expect-text | registration.phone | — | {{tech.phone_national}} (value preserved) |
| 9 | fill | registration.phone | {{new_user.phone}} | retry without reopening the screen |
| 10 | expect-enabled | registration.continue | — | enabled |

**Postconditions / cleanup:** no second submit — nothing created, nothing to clean.
**Notes:** where the error is shown (inline under the phone field or a banner) is confirmed in recon; the alias
`registration.form-error` is resolved in the map accordingly.
**Recon 3d (2026-09-23):** confirmed — a red banner (element `Other`) with the checklist wording verbatim (D-7); the form
stays with its values; nothing is created (API read-back). The phone field shows its value formatted
(`(202) 555-0450`), so step 8 compares **digits**.

---

## Aliases used

Screen maps written in step 5 (2026-09-23): `automation/mobile/screens/{welcome,login,otp,registration,sms_terms,jobs_list}_map.py`,
from the recon dumps `qa/shared/recon-dumps/ios-2026-09-23/`. Offline map-health
(`automation/mobile/unit_tests/test_screen_maps.py`) checks that every alias below resolves; whether a locator
finds its element is proven on the first device run. Android maps come with step 7.
Recon 3d (2026-09-23) confirmed the OTP entries and the two server messages it could observe; the unregistered-phone
wording is still the checklist's (not requested). Unnamed controls and misreported elements are testability defects
TD-AUTH-001…008 (`docs/requirements/shared/testability-contract.md` §5).

| Alias | Screen | android map | ios map |
|---|---|---|---|
| app | — (launch / relaunch) | n/a | n/a (`helpers/app.py`) |
| welcome.root, .title, .subtitle, .sign-up, .login, .back | welcome | step 7 | yes (`back` = any back control, used only for expect-hidden) |
| login.root, .title, .subtitle, .helper, .identifier, .continue, .privacy-link, .terms-link, .sign-up-link | login | step 7 | yes |
| login.error | login | step 7 | yes — parametrised by the expected text; a transient banner (`Other`), recon 3d; no format message exists (D-12) |
| otp.root, .title, .code, .instruction, .verify, .resend | otp | step 7 | yes — recon 3d (`code` = the hidden field, TD-AUTH-002) |
| otp.error | otp | step 7 | yes — shown / hidden decided by **pixels** (TD-AUTH-008) |
| otp.destination | otp | step 7 | yes — parametrised by the address / last digits |
| jobs-list.root | jobs-list | step 7 | yes |
| registration.root, .title, .subtitle, .first-name, .last-name, .phone, .phone-prefix, .email, .channel-section, .channel-options, .sms-consent, .sms-consent-text, .continue, .privacy-link, .terms-link, .log-in-link | registration | step 7 | yes (`sms-consent` = the only switch, TD-AUTH-004) |
| registration.channel-sms, .channel-email | registration | step 7 | page method `RegistrationPage.choose_channel` / `selected_channel` (radios by position, TD-AUTH-003) |
| registration.error[{{field}}] | registration | step 7 | page method `RegistrationPage.field_errors` (texts inside the field's bounds, TD-AUTH-007) |
| registration.form-error | registration | step 7 | yes — parametrised by the expected text; a transient banner (`Other`), recon 3d |
| sms-terms.root, sms-terms.accept | sms-terms | step 7 | yes |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech.email}}, {{tech.phone}}, {{tech.otp}} | `automation/mobile/.env` → `APP_USER_EMAIL`, `APP_USER_PHONE`, `APP_USER_OTP` | existing test technician, read-only; OTP hardcoded on DEV |
| {{tech.phone_national}}, {{tech.phone_last4}} | derived from `APP_USER_PHONE` | formats for the registration field and masked display |
| {{new_user.*}} | generated at runtime (`automation/mobile/fixtures/test_data.py`) | unique names; `qa-auto+<ts>@example.com`; `+1 202 555 01xx` |
| {{unregistered.email}}, {{unregistered.phone}} | generated at runtime | never registered; nothing is created |
| {{invalid.identifier}} | data values in TC-AUTH-007 | `abc@`, `12ab` |
| {{otp.wrong}} | constant `0000` | any 4 digits except the DEV code |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-AUTH-001, -003, -005 | TC-AUTH-001 | |
| CHK-AUTH-004 | TC-AUTH-001 | text + centring from bounds |
| CHK-AUTH-007, -008 | TC-AUTH-001 | **partial** — position asserted; filled/outlined style manual |
| CHK-AUTH-002 | TC-AUTH-003 | |
| CHK-AUTH-009, -010, -016, -103 | TC-AUTH-002 | |
| CHK-AUTH-104 | TC-AUTH-004 | **partial** — logo is an unlabelled image |
| CHK-AUTH-105, -106, -107, -108, -109 | TC-AUTH-004 | |
| CHK-AUTH-073, -074, -075, -088, -089, -110, -115, -117, -119 | TC-AUTH-005 | |
| CHK-AUTH-072, -096, -111, -116, -118 | TC-AUTH-006 | -096 proven together with TC-AUTH-005 (both channels) |
| CHK-AUTH-114, -121, -122, -123, -125 | TC-AUTH-007 | -114 = Continue re-enabled after correction (D-12) |
| CHK-AUTH-112 | — | **Skipped** — the app shows no format message (D-12, owner 2026-09-23) |
| CHK-AUTH-090, -091 | TC-AUTH-008 | |
| CHK-AUTH-077, -078, -080, -097, -126 | TC-AUTH-009 | |
| CHK-AUTH-017 | TC-AUTH-010 | **partial** — logo is an unlabelled image |
| CHK-AUTH-018…024, -035 | TC-AUTH-010 | |
| CHK-AUTH-026…034, -041, -043…047 | TC-AUTH-011 | length/character error texts asserted as "visible" until captured (Q-A3) |
| CHK-AUTH-049, -053, -055, -056, -060, -061 | TC-AUTH-012 | -053 / -056 asserted as the live app behaves (D-9) |
| CHK-AUTH-050, -062, -063, -064, -066 | TC-AUTH-013 | cleanup via `DELETE /user/full-delete/{user.id}` (verified) |
| CHK-AUTH-068, -069, -071 | TC-AUTH-014 | |

**Total: 81 CHK IDs in 14 TCs** (4 of them partial) + CHK-AUTH-112 Skipped (D-12). Not covered here, with reasons, in the automation plan:
27 deferred (incl. CHK-AUTH-048), 5 manual, 11 not recommended.

## Open questions

- ~~Q-A1~~ — **resolved:** the login field takes E.164 (`+1…`), per its own hint.
- ~~Q-A2~~ — **resolved:** registration + OTP leads straight to the Jobs list.
- ~~Q-A3~~ — **resolved:** error texts captured (TC-AUTH-011 data table). Still to observe on the first run: the
  required-field wording and the 101-character behaviour.
- ~~Q-A4~~ — **resolved:** `DELETE /user/full-delete/{user.id}` removes the user and the technician.
- D-1…D-11 — accepted by the owner (the app is right); the tests assert the live app.
