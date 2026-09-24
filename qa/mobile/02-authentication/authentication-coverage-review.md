# Coverage Review: Authentication (mobile)

**Date:** 2026-09-23
**Version:** v1
**Reviewed by:** AI-assisted (Claude Opus 5.5, `prompts/05-review-coverage.md`) — for review by mykola.zhuchenko

**Platform:** mobile (Flutter, native drivers) — iOS reviewed with run evidence; Android not yet run.
**Inputs:** [authentication-checklist.md](authentication-checklist.md) (126) ·
[authentication-test-cases.md](authentication-test-cases.md) (14 TCs) ·
[authentication-automation-plan.md](authentication-automation-plan.md) · [authentication-rtm.md](authentication-rtm.md) ·
[authentication-traceability.md](authentication-traceability.md) (run 2: 30 passed / 1 failed) ·
[authentication-questions.md](authentication-questions.md) (D-1…D-15) · bugs BUG-AUTH-001/002 · SRS 1.0.2 §3.1.1, CR-1,
§5 · Figma frames in `docs/designs/mobile/figma-sources.md` · `docs/api/openapi.json` (auth operations) ·
`docs/requirements/shared/testability-contract.md` §5 · test review `_bmad-output/test-artifacts/test-reviews/mobile/test-review-authentication-2026-09-23.md`.

Requirement-level gaps are **not repeated here** — they are rows of the RTM (65 in-scope: 30 ✅, 27 ⚠️, 2 ❌, 4 🔴,
2 ❓). This review adds what the RTM cannot show: test-case and checklist quality, negative and edge scenarios,
security, accessibility and verdict honesty.

## 1. Executive Summary

The pilot covers the core of authentication well: email and phone login with OTP, session persistence, registration
by email, all registration field validations and the main server errors — automated, proven red once, and passing on
iOS except the known BUG-AUTH-001. Coverage is thin exactly where authentication is riskiest: account lockout, OTP
expiry, signed-out access through links, and the SMS registration path. One harness issue affects honesty of the
report: the parametrised validation test tags every row with all 15 of its CHK IDs, so per-CHK verdicts are wider than
the evidence.

Overall rating: **Partial coverage**

Coverage Quality:
- Functional coverage: 7/10
- Edge case coverage: 5/10
- Negative test coverage: 6/10

Artifact Quality:
- Test case quality: 8/10
- Checklist quality: 6/10

Overall: 6/10

## 2. Not Assessable Due to Missing Input

| Area | Missing Input | Impact |
|------|---------------|--------|
| Business rules for consent, lockout, session lifetime | `docs/business-rules/` is empty; SRS gives no attempt count, no token lifetime, no rule for withdrawing consent | Lockout, session-expiry and consent-update scenarios can be named but their expected results cannot be written (questions in §15 and RTM) |
| Auth error model | OpenAPI documents only `200` / `default` for `POST /auth/sign-in/phone` and `/auth/sign-in/email` — no response for an unregistered identifier | The "not registered" expectation rests on the checklist and the app code (401 → message); what the backend *should* return is undefined — relevant to BUG-AUTH-001 |
| Module analysis | No `authentication-analysis.md` (prompt 01) — gaps were recorded straight into `authentication-questions.md` | Low: recon and D-1…D-15 cover the comparison; noted for completeness |

## 3. Coverage Review Table

| Area | Coverage Status | Priority | Evidence / Reference | Summary Finding | Recommendation |
|------|-----------------|----------|----------------------|-----------------|----------------|
| Requirement Coverage | Partial | High | RTM: 30 ✅ / 27 ⚠️ / 2 ❌ / 4 🔴 / 2 ❓ | Core flows covered; 5 Critical/High rows partial (§5.2, FR-008, FR-009, FR-012, FR-OTP-13) | Close SMS registration and lockout first (§17) |
| Design Coverage | Partial | Medium | CHK-AUTH-023, -024, -108, -109; TD-AUTH-001, -005 | Links and icons are checked for visibility, never activated; logos and SMS Terms close icon unlabelled | §7 |
| Positive Flow Coverage | Good | High | TC-AUTH-003, -005, -006, -013 | Login by email / phone, session skip, registration by email proven | Add SMS-channel registration (MISS-01) |
| Negative Flow Coverage | Partial | High | TC-AUTH-007, -008, -014 | Wrong OTP, unregistered identifiers, duplicate phone covered; lockout, expired OTP, declined Terms, deleted user not | §8 |
| Validation Coverage | Good | Medium | TC-AUTH-011 (17 rows), TC-AUTH-007 | EP/BVA on all registration fields; login format gating | Add real-world name and identifier formats (§9) |
| Permission Coverage | Partial | Critical | CHK-AUTH-126, TC-AUTH-009 | Single role; only "abandoned OTP → relaunch" proves no access without OTP | MISS-06, MISS-10 |
| Status and State Coverage | Partial | Medium | TC-AUTH-003, -009 | Session persistence covered; session expiry / token refresh, OTP screen after app kill not covered | §9, §10 |
| API and Backend Coverage | Partial | Medium | BUG-AUTH-001; `sign-in/phone` spec | UI mapping of 401 proven for email only; unregistered phone mis-mapped; network / 5xx mapping blocked on the simulator | Android network checks; ask backend for the error contract |
| Empty, Loading, and Error States | Partial | Medium | TC-AUTH-007, -008, -014 | Error banners and inline errors covered; loading state after Continue / during OTP send not checked; network errors blocked | Note loading state in recon of Android phase |
| Platform Coverage | Partial | Medium | run 2 context | iOS 26.5 iPhone 17 only; Android planned (step 7); min OS not run by decision | Keep as stated limit; Android adds back-button and keyboard differences |
| Regression Coverage | Partial | Medium | — | Logout (module 12) and consent change in the app are not linked back to auth | §10 |
| Risk Coverage | Partial | High | FR-OTP-13, CR-1 NFR | Highest-risk auth behaviours (brute-force protection, expiry) are the untested ones | §14 |
| Security Coverage | Weak | Critical | CHK-AUTH-101, -126; CR-1 NFR | No lockout, expiry, link-bypass or deleted-user check | MISS-02, MISS-06, MISS-10 |
| Automation Readiness Coverage | Good | Medium | test review 88/100; prove-red run | Deterministic, self-cleaning; per-CHK tagging of TC-AUTH-011 over-maps verdicts | §11 first row |
| Data Coverage | Partial | Medium | TC-AUTH-011 data table; `test_data.py` | Unique reserved-range data, boundaries 1/2/50/51; no hyphenated / accented names, no case / formatting variants of identifiers | §9 |
| Test Case Quality | Good | Medium | 14 TCs | Clear oracles, aliases, cleanup; a few steps don't prove the CHK they claim; stale notes | §11 |
| Checklist Quality | Partial | Medium | CHK-AUTH-004, -053, -056, -059, -087, -092, -101, -102, -112 | Several items describe behaviour the app does not have or have no expected result | §12 |
| Performance / Load Coverage | N/A | Low | SRS §5.1 | No auth-specific performance requirement; "job list within 3 s" belongs to module 03 | Assess in module 03 |
| Accessibility Coverage | Weak | Medium | SRS §5.3; TD-AUTH-001…008 | No accessibility checks; several controls unnamed; a hidden error is exposed as visible | One manual VoiceOver pass (§17) |

## 4. Missing Checklist Items

New items get new IDs (CHK-AUTH-127 and up) only after the owner validates them; existing IDs never change.

### High

1. Check that an OTP older than the configured expiry time (default 5 minutes) is rejected on the verification screen.
2. Check that opening a job link from the assignment SMS while signed out shows the Welcome screen instead of the job.

### Medium

1. Check that tapping the Terms link on the Registration screen opens the page https://www.concerttech.com/sms-terms-and-conditions/.
2. Check that tapping the Privacy Policy link on the Registration screen opens the page https://www.concerttech.com/mobile-privacy/.
3. Check that tapping the Terms link on the Login screen opens the Terms & Conditions page.
4. Check that tapping the Privacy Policy link on the Login screen opens the Privacy Policy page.
5. Check that tapping "Already have an account? Log in" on the Registration screen opens the Login screen.
6. Check that tapping "Don't have an account yet? Sign up" on the Login screen opens the Registration screen.
7. Check that the First name and Last name fields on the Registration screen stop accepting input at the maximum length defined for them.
8. Check that the app returns to the Welcome screen on the next launch after the signed-in user's account is deleted on the server.

## 5. Missing Test Cases

| ID | Title | Related Area / Requirement | Type | Priority | Reason |
|----|-------|----------------------------|------|----------|--------|
| MISS-01 | Registering with the SMS channel verifies the phone and opens the Jobs list | FR-008, FR-012, CHK-AUTH-065 | Functional | High | Half of the CR-1 registration feature has no end-to-end test; same pattern and cleanup as TC-AUTH-013 |
| MISS-02 | Too many wrong codes lock the account for 2 minutes and say so | FR-OTP-13, CHK-AUTH-101 | Security | High | Brute-force protection is untested; needs a dedicated account so the shared one is not locked |
| MISS-03 | Closing the SMS Terms leaves SMS unselected and Continue disabled | FR-009, CHK-AUTH-057 | Negative | Medium | The "Decline" half of FR-009 |
| MISS-04 | Terms and Privacy links open their pages (Registration, Login) | FR-REG-08/-09, FR-LOG-06/-07 | Functional | Medium | Four SRS requirements are proven only by link visibility |
| MISS-05 | Registration ↔ Login cross-links open the other screen | DESIGN-AUTH-001/-002 | Functional | Medium | The only in-app way back to Login from Registration (no back stack) |
| MISS-06 | A signed-out user opening a job link lands on Welcome | §5.2, CR-1 FR-006 | Security | High | Access-control bypass path; may belong to module 03 — decide once |
| MISS-07 | Network off during Continue / OTP → generic error, retry after reconnect | FR-REG-10, FR-LOG-09, FR-OTP-12 | Negative | Medium | Blocked on the iOS simulator; feasible on the Android emulator |
| MISS-08 | Resend: "Request a new code" enabled after the countdown, resend restarts it | FR-OTP-10/-11, CHK-AUTH-079/-094/-095 | Functional | Low | Slow (~60 s); fits a scheduled run |
| MISS-09 | A rapid double tap on Continue creates one user | CHK-AUTH-067 | Regression | Medium | The one rapid-tap case with data-integrity impact; count users via API |
| MISS-10 | A user deleted on the server is signed out on the next launch | §5.2 | Security | Medium | Feasible now: `new_user` fixture registers, API deletes, relaunch → Welcome |

## 6. Uncovered Requirements

Every uncovered or partially covered requirement is a row in [authentication-rtm.md](authentication-rtm.md) with its
gap in *Notes*. The ones that matter most for this review:

| Requirement / Area | Coverage Level | Evidence / Reference | Gap | Recommendation |
|--------------------|----------------|----------------------|-----|----------------|
| §5.2 Security | Partially Covered | CHK-AUTH-126, TC-AUTH-009 | One bypass path proven | MISS-06, MISS-10 |
| FR-008 / FR-012 (CR-1) | Partially Covered | CHK-AUTH-065 deferred | SMS registration path | MISS-01 |
| FR-OTP-13 | Partially Covered | CHK-AUTH-101 deferred | Lockout | MISS-02 |
| CR-1 NFR OTP expiry | Not Covered | — | No check anywhere | Checklist item High-1 |

## 7. Uncovered Design Elements

| Design Element | Screen / Area | Evidence / Reference | Gap | Recommendation |
|----------------|---------------|----------------------|-----|----------------|
| Terms / Privacy links (activation) | Registration_ Updated, Log in_Updated | CHK-AUTH-023, -108 | Visible only, never tapped | MISS-04 |
| "Log in" / "Sign up" cross-links (activation) | Registration_ Updated, Log in_Updated | CHK-AUTH-024, -109 | Visible only, never tapped | MISS-05 |
| SMS Terms close icon | SMS Terms (3608:12130) | CHK-AUTH-057, TD-AUTH-005 | Unlabelled, not automated | MISS-03; ask dev for a label |
| Country selector bottom sheet | Registration_ Updated | CHK-AUTH-036…040 | Deferred | Keep deferred unless international technicians are in scope |
| Logo | Welcome, Login, Registration | CHK-AUTH-017, -104, TD-AUTH-001 | Unlabelled image — manual only | Accept as manual |
| Four OTP boxes | Phone / Email verification | CHK-AUTH-076, TD-AUTH-002 | Drawn only; tree has one hidden field | Pixel check possible (same helper as TC-AUTH-008) if wanted |
| `Log in_Error` frame | Log in_Updated (3191:12935) | CHK-AUTH-112, D-12 | Never compared with the app | Look at the frame once; if it shows a format message, D-12 needs a second look |

## 8. Missing Negative Scenarios

| Scenario | Related Area | Priority | Reason |
|----------|--------------|----------|--------|
| Registration with an email that is already registered (phone new) | FR-REG-11 analogue | Medium | Only the duplicate *phone* is checked (CHK-AUTH-069); the duplicate email outcome is not defined anywhere |
| Wrong OTP on the registration verification screen (new user) | FR-OTP-07 | Low | The wrong code is tested on login only; registration uses the same screen but a different backend call (`/auth/confirm/*`) |

(Lockout, expired OTP, declined Terms, network failure, signed-out link, deleted user — MISS-02, High-1, MISS-03,
MISS-07, MISS-06, MISS-10 above.)

## 9. Missing Edge Cases

| Edge Case | Related Area | Priority | Reason |
|-----------|--------------|----------|--------|
| Names with a hyphen, an apostrophe or accented letters ("Anne-Marie", "O'Brien", "José") | FR-REG-01/-02, alphabetic rule | Medium | "Alphabetical only" may lock real technicians out of registration; the rule for these names is undefined |
| Login with the registered email in a different letter case | FR-LOG-02 | Medium | A case-sensitive lookup would tell a registered user "not registered" |
| Login with the phone typed with spaces / dashes / brackets ("+1 (202) 555-0123") | FR-LOG-02 | Medium | TC-AUTH-006 types strict E.164 only; users copy numbers in other formats |
| Leading / trailing spaces in registration names and email | FR-REG-01…04 | Low | Trimming is confirmed for login only (D-13) |
| Last-name maximum length row | TC-AUTH-011 | Low | Only the first name has 50 / 51 rows |
| App killed while on the OTP screen, then relaunched | FR-WEL-03 | Low | TC-AUTH-009 leaves OTP first, then relaunches; the kill-on-OTP state is untested |
| Countdown after the app returns from background | FR-OTP-08 | Low | Timers often freeze or jump on resume |

## 10. Missing Regression Scenarios

| Regression Scenario | Related Shared Logic / Component / API | Priority | Reason |
|---------------------|----------------------------------------|----------|--------|
| Log out from Profile → Welcome; relaunch still shows Welcome | session storage (keychain), module 12 | High | The inverse of TC-AUTH-003; plan it in module 12 and link it back to FR-WEL-03 |
| Session survives token refresh during a long session | `POST /auth/refresh-token` | Medium | The refresh operation exists in the API; nothing checks what the user sees when the access token expires |
| Consent / channel changed in the app is used for the next OTP | FR-010, FR-012 | Medium | Consent update location unknown (RTM question 1) |

## 11. Test Case Quality Issues

| Test Case ID | Issue | Impact | Recommendation |
|-------------|-------|--------|----------------|
| TC-AUTH-011 | Every one of the 17 parametrised rows carries all 15 CHK tags, so each CHK's automated verdict is the AND of all rows: a failing email row would mark CHK-AUTH-026 ("First name is required") Failed, and a pass of CHK-AUTH-043 is claimed by 14 rows that never touch the email field | High | Tag each row with its own CHKs (`pytest.param(..., marks=pytest.mark.chk(...))`); the test review's split by field type fits the same change |
| TC-AUTH-009 | Step 8 goes back with the system gesture; CHK-AUTH-097 is about the on-screen back arrow (labelled `Back` since recon 3d) | Medium | Tap `otp.back`; keep the gesture as an Android-phase variant |
| TC-AUTH-006 | CHK-AUTH-074 / -075 ("title / instruction based on verification type") are proven for the email variant only (TC-AUTH-005); TC-AUTH-006 asserts the phone title but not the phone instruction | Medium | Add `expect-text otp.instruction` = "Enter the 4-digit code sent to your number" (wording to confirm on the app) |
| TC-AUTH-010 | Note still says "Registration aliases are `MISSING` until the Registration recon pass" | Low | Remove — recon 3c done, maps exist |
| Coverage table (TC file) | "length/character error texts asserted as 'visible' until captured (Q-A3)" — texts are asserted verbatim now | Low | Update the note |
| All TCs vs plan | Priority scales differ: plan marks smoke items P1 (e.g. CHK-AUTH-001, -110), TCs use P0 for smoke (TC-AUTH-001, -005); TC-AUTH-004 is P1 while its CHKs are P2 in the plan | Low | State one scale in the plan header or align the values |
| TC-AUTH-009 | Carries CHK-AUTH-126 (the only security check, Critical in the RTM) at P2 | Low | Raise to P1 or move CHK-AUTH-126 into a P1 TC |

## 12. Checklist Quality Issues

The checklist is the team Sheet; wording changes go through the owner and `qa-sheets-sync` (dry-run first), IDs stay.

| Checklist Item / Section | Issue | Impact | Recommendation |
|--------------------------|-------|--------|----------------|
| CHK-AUTH-053, -056 | Describe a flow the app does not have (consent checkbox opens the Terms; Accept ticks it) — the app opens the Terms from the SMS channel (D-9) | Medium | Rewrite to the accepted flow |
| CHK-AUTH-112 | Expects "Format is incorrect." — the message does not exist in the app or its history (D-12) | Medium | Rewrite to "Continue stays disabled…" or retire with the D-12 reason |
| CHK-AUTH-004 | Header text is the pre-2026-08-04 wording (D-1) | Medium | Update the quoted text |
| CHK-AUTH-059, -085, -101, -102 | Conditional ("if allowed by business logic", "if supported", "if configured", "according to business logic") — no expected result | Medium | Replace with the rule once answered (RTM questions 1, 2, 5) |
| CHK-AUTH-087, -092 | Describe tapping Verify; the code submits itself (D-5) | Low | Rewrite to the auto-submit behaviour or retire |
| CHK-AUTH-006, -013, -014, -025 | Subjective ("visually consistent", "without visual glitches or delays") | Low | Keep as manual, or name a measurable result |
| CHK-AUTH-017, -104 | Three assertions each (logo, title, subtitle) | Low | Split the logo out — it is the only manual part |
| CHK-AUTH-032 vs -030 / -031; -026 vs -028; -027 vs -029 | Near-duplicates | Low | Merge on the next Sheet cleanup |
| CHK-AUTH-096 | Broad ("works correctly for both channels") | Low | Name the observable result per channel |
| CHK-AUTH-043 | Says Email is required; SRS FR-REG-04 says optional (D-6, accepted) | Low | Keep; add the D-6 reference in the Sheet comment |

## 13. Redundant / Low-Value Tests

No redundant or low-value tests were identified based on the provided input. (TC-AUTH-011's cost — a full reset and
cold start per row — is a performance point already raised by the test review, not redundancy.)

## 14. Risks

| Risk | Area | Severity | Likelihood | Mitigation |
|------|------|----------|------------|------------|
| A regression that removes or weakens the OTP lockout goes unnoticed | Security | High | Low | MISS-02 on a dedicated account |
| The whole suite (every module) depends on one shared test account; a lockout or deletion blocks the run | Test data | High | Low | Second account; ≤ 1 wrong OTP per run already enforced |
| Per-CHK verdicts from TC-AUTH-011 overstate or misplace coverage in the final report | Reporting | Medium | Medium | Per-row CHK tags (§11) before the final run |
| SMS-channel registration breaks without a red test | Functional | Medium | Medium | MISS-01 |
| Server banners live ~4 s; slow DEV responses can make the error checks flaky | Stability | Medium | Medium | Already noted in the test review (D-4); watch the 3 stable runs |
| The hidden `Incorrect code.` is exposed as visible to accessibility services and may be read out by VoiceOver before any input | Accessibility | Medium | Medium | One manual VoiceOver pass on the OTP screen; testability defect TD-AUTH-008 to dev |
| Android differs (hardware back, keyboards, notification permission after `pm clear`) | Platform | Medium | Medium | Step 7 plan already lists these |

## 15. Open Questions

RTM questions 1–8 ([authentication-rtm.md](authentication-rtm.md#open-questions)) apply. In addition:

| # | Question | Blocker? | Directed To |
|---|----------|----------|-------------|
| 1 | What should registration with an already registered **email** show? | No | BA / PM |
| 2 | Are hyphens, apostrophes and accented letters allowed in names? | No | BA / PM |
| 3 | Is email lookup on login case-insensitive, and are spaces / dashes in a phone number accepted? | No | Dev |
| 4 | How long does a session last, and what does the user see when the access token can no longer be refreshed? | No | Dev |
| 5 | What should `POST /auth/sign-in/phone` return for an unregistered number (OpenAPI documents only 200 / default)? | No — context for BUG-AUTH-001 | Dev (backend) |

## 16. Automation Gaps

Deferred by the narrow-pilot scope (27 CHK IDs in the plan), grouped; none is decided here.

| ID | Test / Area | Priority | Reason | Automation Notes |
|----|-------------|----------|--------|------------------|
| AG-1 | SMS registration (CHK-AUTH-065), channel state (-048, -051, -058), payload (-052) | High | Half of CR-1 registration | UI + API read-back |
| AG-2 | Lockout (CHK-AUTH-101) | High | Security | UI, dedicated account, last in the run |
| AG-3 | SMS Terms content / close (CHK-AUTH-054, -057) | Medium | FR-009 Decline | UI; close icon needs a locator |
| AG-4 | Rapid taps (CHK-AUTH-011, -012, -067, -120) | Medium | -067 is data integrity | UI; -067 + API count |
| AG-5 | Network failures (CHK-AUTH-070, -098…-100, -124) | Medium | Blocked on iOS simulator | Android emulator |
| AG-6 | OTP input behaviour (CHK-AUTH-076, -081…-086) | Low | Focus is visual only | Partly pixel-based; low value |
| AG-7 | Resend after countdown (CHK-AUTH-079, -094, -095) | Low | ~60 s wait | Scheduled run |
| AG-8 | Country selector (CHK-AUTH-036…-040, -042) | Low | +1 only in practice | UI |

## 17. Prioritized Action List

| # | Action | Priority | Owner |
|---|--------|----------|-------|
| 1 | Tag TC-AUTH-011 rows with their own CHK IDs before the final full-app run | High | QA |
| 2 | Decide on SMS-channel registration (MISS-01) and a dedicated account for the lockout (MISS-02) | High | Owner |
| 3 | Fix TC-AUTH-006 (phone instruction) and TC-AUTH-009 (tap the Back arrow); clean the stale TC notes | Medium | QA |
| 4 | Validate the new checklist items in §4 (CHK-AUTH-127+) | Medium | Owner → QA |
| 5 | Add MISS-10 (deleted user signed out) — uses existing fixtures; creates and deletes one user | Medium | QA (owner go) |
| 6 | Update outdated checklist wording (§12, Medium rows) via dry-run Sheet sync | Medium | QA + Owner |
| 7 | Send the product questions (§15 + RTM) to PO / dev | Medium | QA |
| 8 | Carry network-failure checks into the Android plan | Medium | QA |
| 9 | One manual VoiceOver pass on the OTP screen | Low | QA |
| 10 | Align priority scales between plan and TCs | Low | QA |

## 18. Final Recommendation

**Needs minor improvements before execution.**

The suite is executable and has already run (iOS run 2: 30 passed, 1 failed on BUG-AUTH-001, every test proven red
once). Before the final full-app run that feeds the demo report, fix the TC-AUTH-011 tag granularity (so the matrix
claims only what each row proved) and the two TC steps that do not prove their CHK (TC-AUTH-006, TC-AUTH-009). The
security and SMS-registration gaps are scope decisions for the owner, not blockers for running.
