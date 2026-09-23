# Automation plan — Authentication (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/02-authentication/authentication-checklist.md`
> (126 items, `CHK-AUTH-001…126`). Reviewed copy for the module; the **Selected CHK IDs** table is the
> contract for `prompts/mobile/03` (test cases). Date: 2026-09-23. Owner: mykola.zhuchenko.

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| App build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` (`automation/mobile/builds/ios/BUILD_INFO.txt`) |
| Feature code | `AUTH` |
| Scope decision | **narrow pilot** (owner, 2026-09-23): screens, transitions, happy paths, key validations — `docs/notes/decisions.md` |
| Oracle model | accepted production baseline; checklist text is closer to the live app than the SRS (D-6…D-8) |

## Step 0 — Input quality

**Overall: Medium-High.** Stable IDs on every item, single-assertion wording, live recon of Welcome/Login/OTP
(`qa/shared/recon-2026-09-23-ios.md`), API spec available.

Gaps: preconditions and test data are implicit in the checklist; several items describe behaviour "according to
business logic" without the rule (CHK-AUTH-059, -102); SRS and checklist disagree on texts and on whether Email is
required (D-6…D-8, `authentication-questions.md`); network-failure items assume network control the iOS simulator
does not offer.

## Step 1 — Readiness: **Ready for automation**

Recon confirmed text locators for every element on Welcome, Login and OTP (`ACCESSIBILITY_ID` = visible text),
readable enabled/disabled state, a working test account with a hardcoded DEV OTP, and API endpoints for cleanup.
Remaining risk: time-based OTP countdown, and cleanup of self-registered users (endpoint to confirm).

## Step 2 — Approach: **Hybrid (UI-first, API for setup/cleanup)**

Every selected item is proven through the UI; the API is used only to remove users created by the registration
test and never replaces a user-visible check (owner's UI priority, CLAUDE.md).

## Step 3–4 — Candidate matrix (all 126 items)

Status legend: *Good / Medium Candidate*, *Needs API Support*, *Needs Stable Selectors*, *Needs Test Data Setup*,
*Manual Only*, *Not Recommended Now*. **deferred** = automatable, left out only by the narrow-pilot scope decision.

| CHK ID | Scenario (short) | Automation Level | ROI | Stability | Risk | Automation Status | Priority | Tags | TC | Reason / blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| CHK-AUTH-001 | Welcome Screen is displayed as a full-screen view when the application is open | E2E UI | M | H | M | Good Candidate | P1 | @smoke | TC-AUTH-001 | stable text locators; deterministic |
| CHK-AUTH-002 | Welcome Screen is not displayed when a valid user session token exists and the | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-003 | stable text locators; deterministic |
| CHK-AUTH-003 | no navigation bar or back button is displayed on the Welcome Screen. | E2E UI | M | H | M | Good Candidate | P1 | @smoke | TC-AUTH-001 | stable text locators; deterministic |
| CHK-AUTH-004 | header text “Welcome to the Concert Technologies” is displayed and centered on | E2E UI | M | H | M | Good Candidate | P1 | @smoke | TC-AUTH-001 | stable text locators; deterministic |
| CHK-AUTH-005 | subtext “Create an account or log in to get started.” is displayed below the h | E2E UI | M | H | M | Good Candidate | P1 | @smoke | TC-AUTH-001 | stable text locators; deterministic |
| CHK-AUTH-006 | Welcome Screen layout remains visually centered and consistent across differen | Manual only | L | L | L | Manual Only | — | @manual-only | — | visual layout across screen sizes/orientations — subjective; tablets out of scope |
| CHK-AUTH-007 | “Sign up” button is displayed as the primary (filled) call-to-action at the bo | E2E UI | M | H | M | Good Candidate | P1 | @smoke | TC-AUTH-001 | stable text locators; deterministic |
| CHK-AUTH-008 | “Login” button is displayed as the secondary (outlined or neutral) call-to-act | E2E UI | M | H | M | Good Candidate | P1 | @smoke | TC-AUTH-001 | stable text locators; deterministic |
| CHK-AUTH-009 | tapping the “Sign up” button navigates the user to the Account Registration /  | E2E UI | H | H | H | Good Candidate | P1 | @smoke | TC-AUTH-002 | stable text locators; deterministic |
| CHK-AUTH-010 | tapping the “Login” button navigates the user to the Login screen. | E2E UI | H | H | H | Good Candidate | P1 | @smoke | TC-AUTH-002 | stable text locators; deterministic |
| CHK-AUTH-011 | multiple rapid taps on the “Sign up” button do not trigger multiple navigation | E2E UI | M | M | M | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): rapid double-tap → single navigation; assert back-stack depth |
| CHK-AUTH-012 | multiple rapid taps on the “Login” button do not trigger multiple navigation e | E2E UI | M | M | M | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): as CHK-AUTH-011 |
| CHK-AUTH-013 | navigation from the Welcome Screen to the Sign Up screen completes successfull | Manual only | L | L | L | Manual Only | — | @manual-only | — | 'without visual glitches or delays' — subjective; the navigation itself is proven by TC-AUTH-002 |
| CHK-AUTH-014 | navigation from the Welcome Screen to the Login screen completes successfully  | Manual only | L | L | L | Manual Only | — | @manual-only | — | as CHK-AUTH-013 |
| CHK-AUTH-015 | a generic error message is displayed if navigation to the Sign Up screen fails | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | navigation failure cannot be induced without modifying the app |
| CHK-AUTH-016 | Registration screen is displayed when the user taps “Sign up” from the Welcome | E2E UI | H | H | H | Good Candidate | P1 | @smoke | TC-AUTH-002 | stable text locators; deterministic |
| CHK-AUTH-017 | Registration screen displays the logo, title “Registration”, and subtitle “Goo | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-018 | Registration screen displays input fields in the following order: First name,  | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-019 | Registration screen displays the “Preferred channel for job notifications” sec | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-020 | Registration screen displays SMS and Email radio button options in the notific | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-021 | Registration screen displays the SMS consent checkbox and disclaimer text belo | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-022 | Continue button is disabled by default when required fields are empty. | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-023 | Privacy Policy and Terms & Conditions links are displayed below the Continue b | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-024 | “Already have an account? Log in” link is displayed at the bottom of the Regis | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-025 | Registration screen layout remains correctly aligned on different screen sizes | Manual only | L | L | L | Manual Only | — | @manual-only | — | visual layout across sizes/orientations — subjective |
| CHK-AUTH-026 | First name field is required on the Registration screen. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-027 | Last name field is required on the Registration screen. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-028 | inline validation is displayed if the First name field is empty after validati | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-029 | inline validation is displayed if the Last name field is empty after validatio | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-030 | First name field accepts alphabetical characters only. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-031 | Last name field accepts alphabetical characters only. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-032 | invalid characters are rejected in the First name and Last name fields. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-033 | validation messages are cleared dynamically after correcting invalid First nam | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-034 | Phone number field is required on the Registration screen. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-035 | Phone number field displays the selected country code prefix. | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-010 | stable text locators; deterministic |
| CHK-AUTH-036 | tapping the country code selector opens the country selection bottom sheet. | E2E UI | M | M | M | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): country selector opener not yet seen in recon — alias unknown |
| CHK-AUTH-037 | country selection bottom sheet displays country flags, country names, and dial | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): flags are images; names/codes are text |
| CHK-AUTH-038 | country search field filters countries dynamically while typing. | E2E UI | M | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): country search filter |
| CHK-AUTH-039 | selecting a country updates the phone number prefix in the Registration form. | E2E UI | M | M | M | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): country change updates prefix |
| CHK-AUTH-040 | Phone number field validates the entered value according to the selected count | E2E UI | M | M | M | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): per-country phone format (EP by country) |
| CHK-AUTH-041 | invalid phone number formats display a validation error message. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-042 | numeric keyboard is displayed when focusing the Phone number field. | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): keyboard type — readable via keyboard keys only |
| CHK-AUTH-043 | Email field is required on the Registration screen. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-044 | Email field validates entered email format correctly. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-045 | invalid email values display a validation error message. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-046 | valid email values enable successful form validation. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-047 | validation errors are cleared dynamically after correcting invalid email value | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-011 | stable text locators; deterministic |
| CHK-AUTH-048 | only one preferred notification channel option can be selected at a time. | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred**: radio 'selected' state not yet observed in the tree — confirm in Registration recon |
| CHK-AUTH-049 | user can select SMS as the preferred notification channel. | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-012 | stable text locators; deterministic |
| CHK-AUTH-050 | user can select Email as the preferred notification channel. | API setup + UI assertion | H | M | H | Needs API Support | P2 | @regression @e2e | TC-AUTH-013 | needs API cleanup of the created user (endpoint to verify) |
| CHK-AUTH-051 | selected preferred notification channel remains selected while editing other f | E2E UI | L | H | L | Good Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): channel stays selected while editing |
| CHK-AUTH-052 | selected preferred notification channel is sent correctly in the registration  | E2E UI | M | M | M | Needs API Support | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): payload check via API after registration |
| CHK-AUTH-053 | tapping the SMS consent checkbox opens the “SMS Messaging Terms & Conditions”  | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-012 | stable text locators; deterministic |
| CHK-AUTH-054 | SMS Messaging Terms & Conditions screen displays the close icon, title, and le | E2E UI | L | M | L | Needs Stable Selectors | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): SMS Terms close icon has no label |
| CHK-AUTH-055 | SMS Messaging Terms & Conditions screen displays the “I Accept SMS Terms & Con | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-012 | stable text locators; deterministic |
| CHK-AUTH-056 | tapping “I Accept SMS Terms & Conditions” closes the Terms screen and marks th | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-012 | stable text locators; deterministic |
| CHK-AUTH-057 | tapping the close icon on the Terms screen closes the screen without selecting | E2E UI | M | L | M | Needs Stable Selectors | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): SMS Terms close icon has no label (testability defect) |
| CHK-AUTH-058 | SMS consent checkbox state persists after returning from the Terms screen. | E2E UI | M | H | L | Good Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): checkbox state after returning from Terms |
| CHK-AUTH-059 | SMS consent checkbox can be deselected after acceptance if allowed by business | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | requirement unclear ('if allowed by business logic') — question for the owner |
| CHK-AUTH-060 | Continue button remains disabled if SMS notification channel is selected but S | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-012 | stable text locators; deterministic |
| CHK-AUTH-061 | OTP-related SMS consent text is displayed correctly below the checkbox. | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-012 | stable text locators; deterministic |
| CHK-AUTH-062 | Continue button becomes enabled only when all required fields contain valid va | API setup + UI assertion | H | M | H | Needs API Support | P2 | @regression @e2e | TC-AUTH-013 | needs API cleanup of the created user (endpoint to verify) |
| CHK-AUTH-063 | tapping Continue submits registration data to the backend. | API setup + UI assertion | H | M | H | Needs API Support | P2 | @regression @e2e | TC-AUTH-013 | needs API cleanup of the created user (endpoint to verify) |
| CHK-AUTH-064 | successful registration navigates the user to the correct OTP verification flo | API setup + UI assertion | H | M | H | Needs API Support | P2 | @regression @e2e | TC-AUTH-013 | needs API cleanup of the created user (endpoint to verify) |
| CHK-AUTH-065 | selecting SMS notification channel opens the Phone number verification screen  | E2E UI | M | M | M | Needs Test Data Setup | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): SMS-channel registration; SMS to fictional 555-01xx numbers only |
| CHK-AUTH-066 | selecting Email notification channel opens the Email address verification scre | API setup + UI assertion | H | M | H | Needs API Support | P2 | @regression @e2e | TC-AUTH-013 | needs API cleanup of the created user (endpoint to verify) |
| CHK-AUTH-067 | multiple rapid taps on Continue do not trigger duplicate registration requests | E2E UI | M | M | M | Needs API Support | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): duplicate registration requests — count users via API |
| CHK-AUTH-068 | entered form values remain preserved if registration fails. | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-014 | stable text locators; deterministic |
| CHK-AUTH-069 | error message “An account with this phone number already exists. Please log in | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-014 | stable text locators; deterministic |
| CHK-AUTH-070 | a generic error message is displayed when registration fails due to backend or | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | backend/network failure — no network control on the iOS simulator; revisit on Android |
| CHK-AUTH-071 | user can retry registration after an error without reopening the Registration  | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-014 | stable text locators; deterministic |
| CHK-AUTH-072 | Phone number verification screen displays the verified phone number in masked  | E2E UI | H | H | H | Good Candidate | P1 | @regression @critical | TC-AUTH-006 | stable text locators; deterministic |
| CHK-AUTH-073 | Email address verification screen displays the verified email address in maske | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-074 | correct screen title is displayed based on verification type. | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-075 | correct instruction text is displayed based on verification type. | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-076 | four OTP input boxes are displayed on the verification screen. | E2E UI | L | L | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): 4 boxes are drawn; the tree holds one hidden field |
| CHK-AUTH-077 | Verify button is disabled until all four OTP digits are entered. | E2E UI | M | M | M | Medium Candidate | P2 | @regression | TC-AUTH-009 | countdown is time-based |
| CHK-AUTH-078 | “Request a new code” option is disabled while the countdown timer is active. | E2E UI | M | M | M | Medium Candidate | P2 | @regression | TC-AUTH-009 | countdown is time-based |
| CHK-AUTH-079 | “Request a new code” option becomes enabled after the countdown timer expires. | E2E UI | M | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): needs ~60 s countdown wait — slow |
| CHK-AUTH-080 | countdown timer value decreases correctly in real time. | E2E UI | M | M | M | Medium Candidate | P2 | @regression | TC-AUTH-009 | countdown is time-based |
| CHK-AUTH-081 | entering a digit automatically moves focus to the next OTP input field. | E2E UI | L | L | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): focus movement is visual (single hidden field) |
| CHK-AUTH-082 | deleting a digit moves focus back to the previous OTP input field. | E2E UI | L | L | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): as CHK-AUTH-081 |
| CHK-AUTH-083 | only numeric values are accepted in OTP input fields. | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): numeric-only input |
| CHK-AUTH-084 | more than four OTP digits cannot be entered. | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): max 4 digits |
| CHK-AUTH-085 | pasting OTP values fills the OTP fields correctly if supported. | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): paste via Appium clipboard |
| CHK-AUTH-086 | numeric keyboard is displayed automatically when focusing OTP fields. | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): numeric keyboard shown |
| CHK-AUTH-087 | tapping Verify submits the entered OTP for backend validation. | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | superseded by auto-submit after the 4th digit (D-5); proven by CHK-AUTH-088 |
| CHK-AUTH-088 | successful OTP verification authenticates the user successfully. | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-089 | successful OTP verification navigates the user to the Jobs screen or onboardin | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-090 | incorrect OTP values display an “Incorrect code” validation error. | E2E UI | H | M | H | Medium Candidate | P2 | @regression | TC-AUTH-008 | one wrong attempt only (lockout FR-OTP-13) |
| CHK-AUTH-091 | OTP fields remain editable after invalid OTP verification attempts. | E2E UI | H | M | H | Medium Candidate | P2 | @regression | TC-AUTH-008 | one wrong attempt only (lockout FR-OTP-13) |
| CHK-AUTH-092 | multiple rapid taps on Verify do not trigger duplicate OTP validation requests | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | auto-submit: duplicate Verify taps are not observable |
| CHK-AUTH-093 | requesting a new OTP invalidates the previously issued OTP code. | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | OTP is hardcoded on DEV — invalidation of the previous code cannot be observed |
| CHK-AUTH-094 | tapping “Request a new code” sends a new OTP to the selected delivery channel. | E2E UI | M | M | M | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): UI part only; delivery not observable (OTP hardcoded on DEV) |
| CHK-AUTH-095 | requesting a new code restarts the countdown timer. | E2E UI | M | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): needs countdown expiry wait |
| CHK-AUTH-096 | verification flow works correctly for both SMS and Email delivery channels. | E2E UI | H | H | H | Good Candidate | P1 | @regression @critical | TC-AUTH-006 | stable text locators; deterministic |
| CHK-AUTH-097 | tapping the back arrow returns the user to the previous authentication screen. | E2E UI | M | M | M | Medium Candidate | P2 | @regression | TC-AUTH-009 | countdown is time-based |
| CHK-AUTH-098 | OTP verification handles slow network responses without UI freezes or duplicat | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | slow network — no throttling on the iOS simulator; revisit on Android |
| CHK-AUTH-099 | a generic error message is displayed if OTP verification fails due to connecti | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | network failure — as CHK-AUTH-098 |
| CHK-AUTH-100 | user can retry OTP verification after network-related failures. | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | as CHK-AUTH-099 |
| CHK-AUTH-101 | OTP retry limits are enforced if configured by backend rules. | E2E UI | M | L | H | Needs Test Data Setup | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): lockout for 2 min (FR-OTP-13) — dedicated account, serial |
| CHK-AUTH-102 | OTP state is preserved or reset correctly after reopening the verification scr | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | expected behaviour unclear ('according to business logic') |
| CHK-AUTH-103 | Login screen is displayed when the user taps “Log in” from the Welcome screen. | E2E UI | H | H | H | Good Candidate | P1 | @smoke | TC-AUTH-002 | stable text locators; deterministic |
| CHK-AUTH-104 | Login screen displays the logo, title “Log in”, and subtitle “Good to see you! | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-004 | stable text locators; deterministic |
| CHK-AUTH-105 | Login screen displays helper text instructing the user to enter email or phone | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-004 | stable text locators; deterministic |
| CHK-AUTH-106 | Login screen displays a single “Phone number / Email” input field. | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-004 | stable text locators; deterministic |
| CHK-AUTH-107 | Continue button is disabled when the input field is empty. | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-004 | stable text locators; deterministic |
| CHK-AUTH-108 | Privacy Policy and Terms & Conditions links are displayed below the Continue b | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-004 | stable text locators; deterministic |
| CHK-AUTH-109 | “Don’t have an account yet? Sign up” link is displayed at the bottom of the Lo | E2E UI | M | H | M | Good Candidate | P2 | @regression | TC-AUTH-004 | stable text locators; deterministic |
| CHK-AUTH-110 | Login field accepts valid email addresses. | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-111 | Login field accepts valid phone numbers. | E2E UI | H | H | H | Good Candidate | P1 | @regression @critical | TC-AUTH-006 | stable text locators; deterministic |
| CHK-AUTH-112 | invalid email or phone number formats display the “Format is incorrect.” valid | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-007 | stable text locators; deterministic |
| CHK-AUTH-113 | validation styling is displayed for invalid Login field values. | Manual only | L | L | L | Manual Only | — | @manual-only | — | validation styling (colour/border) — visual judgment |
| CHK-AUTH-114 | validation errors are removed after correcting invalid input values. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-007 | stable text locators; deterministic |
| CHK-AUTH-115 | Continue button becomes enabled only when a valid email or phone number is ent | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-116 | tapping Continue with a valid registered phone number triggers OTP generation  | E2E UI | H | H | H | Good Candidate | P1 | @regression @critical | TC-AUTH-006 | stable text locators; deterministic |
| CHK-AUTH-117 | tapping Continue with a valid registered email triggers OTP generation via Ema | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-118 | login with a registered phone number navigates to the Phone number verificatio | E2E UI | H | H | H | Good Candidate | P1 | @regression @critical | TC-AUTH-006 | stable text locators; deterministic |
| CHK-AUTH-119 | login with a registered email navigates to the Email address verification scre | E2E UI | H | H | H | Good Candidate | P1 | @smoke @critical | TC-AUTH-005 | stable text locators; deterministic |
| CHK-AUTH-120 | multiple rapid taps on Continue do not trigger duplicate login requests. | E2E UI | L | M | L | Medium Candidate | P3 | @regression | — | **deferred** (narrow pilot, owner 2026-09-23): rapid taps on Continue |
| CHK-AUTH-121 | entered login values remain preserved if login fails. | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-007 | stable text locators; deterministic |
| CHK-AUTH-122 | error message “This phone number is not registered yet. Create an account to g | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-007 | stable text locators; deterministic |
| CHK-AUTH-123 | error message “This email is not registered yet. Create an account to get star | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-007 | stable text locators; deterministic |
| CHK-AUTH-124 | a generic error message is displayed if login fails due to backend or network  | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | network failure — as CHK-AUTH-098 |
| CHK-AUTH-125 | user can retry login without reopening the Login screen after a failed request | E2E UI | H | H | M | Good Candidate | P2 | @regression | TC-AUTH-007 | stable text locators; deterministic |
| CHK-AUTH-126 | authenticated-only screens remain inaccessible without successful OTP verifica | E2E UI | M | M | M | Medium Candidate | P2 | @regression | TC-AUTH-009 | countdown is time-based |

## Step 5 — Best first candidates

1. TC-AUTH-005 (CHK-AUTH-110, -117, -119, -088, -089) Login with email + OTP lands on Jobs list — gateway for every other suite, P1 smoke.
2. TC-AUTH-002 (CHK-AUTH-009, -010) Welcome → Login / Registration — the first transition every user makes.
3. TC-AUTH-003 (CHK-AUTH-002) Valid session skips Welcome — proves session persistence.
4. TC-AUTH-006 (CHK-AUTH-111, -116, -118) Login with phone — second channel of the same critical flow.
5. TC-AUTH-011 (CHK-AUTH-026…047) Registration field validation — many cheap, deterministic checks (EP/BVA).

## Step 5b — Selected CHK IDs (handoff to prompts/mobile/03)

**82 of 126 (65 %) → 14 test cases.** Far above the 10–20 % sanity band because one TC proves several items on the
same screen (screen content, parametrised validation); the TC count (14) matches the agreed narrow scope.

| CHK ID | Automation Level | Priority | Automation Status | Blockers to clear before Prompt 07 | Note |
|---|---|---|---|---|---|
| CHK-AUTH-001 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-001 |
| CHK-AUTH-002 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-003 |
| CHK-AUTH-003 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-001 |
| CHK-AUTH-004 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-001 |
| CHK-AUTH-005 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-001 |
| CHK-AUTH-007 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-001 |
| CHK-AUTH-008 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-001 |
| CHK-AUTH-009 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-002 |
| CHK-AUTH-010 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-002 |
| CHK-AUTH-016 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-002 |
| CHK-AUTH-017 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-018 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-019 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-020 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-021 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-022 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-023 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-024 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-026 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-027 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-028 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-029 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-030 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-031 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-032 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-033 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-034 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-035 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-010 |
| CHK-AUTH-041 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-043 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-044 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-045 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-046 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-047 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-011 |
| CHK-AUTH-049 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-012 |
| CHK-AUTH-050 | API setup + UI assertion | P2 | Needs API Support | cleanup endpoint verified (`DELETE /user/full-delete/{user.id}`) | → TC-AUTH-013 |
| CHK-AUTH-053 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-012 |
| CHK-AUTH-055 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-012 |
| CHK-AUTH-056 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-012 |
| CHK-AUTH-060 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-012 |
| CHK-AUTH-061 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-012 |
| CHK-AUTH-062 | API setup + UI assertion | P2 | Needs API Support | cleanup endpoint verified (`DELETE /user/full-delete/{user.id}`) | → TC-AUTH-013 |
| CHK-AUTH-063 | API setup + UI assertion | P2 | Needs API Support | cleanup endpoint verified (`DELETE /user/full-delete/{user.id}`) | → TC-AUTH-013 |
| CHK-AUTH-064 | API setup + UI assertion | P2 | Needs API Support | cleanup endpoint verified (`DELETE /user/full-delete/{user.id}`) | → TC-AUTH-013 |
| CHK-AUTH-066 | API setup + UI assertion | P2 | Needs API Support | cleanup endpoint verified (`DELETE /user/full-delete/{user.id}`) | → TC-AUTH-013 |
| CHK-AUTH-068 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-014 |
| CHK-AUTH-069 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-014 |
| CHK-AUTH-071 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-014 |
| CHK-AUTH-072 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-006 |
| CHK-AUTH-073 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-074 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-075 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-077 | E2E UI | P2 | Medium Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-009 |
| CHK-AUTH-078 | E2E UI | P2 | Medium Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-009 |
| CHK-AUTH-080 | E2E UI | P2 | Medium Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-009 |
| CHK-AUTH-088 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-089 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-090 | E2E UI | P2 | Medium Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-008 |
| CHK-AUTH-091 | E2E UI | P2 | Medium Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-008 |
| CHK-AUTH-096 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-006 |
| CHK-AUTH-097 | E2E UI | P2 | Medium Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-009 |
| CHK-AUTH-103 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-002 |
| CHK-AUTH-104 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-004 |
| CHK-AUTH-105 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-004 |
| CHK-AUTH-106 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-004 |
| CHK-AUTH-107 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-004 |
| CHK-AUTH-108 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-004 |
| CHK-AUTH-109 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-004 |
| CHK-AUTH-110 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-111 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-006 |
| CHK-AUTH-112 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-007 |
| CHK-AUTH-114 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-007 |
| CHK-AUTH-115 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-116 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-006 |
| CHK-AUTH-117 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-118 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-006 |
| CHK-AUTH-119 | E2E UI | P1 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-005 |
| CHK-AUTH-121 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-007 |
| CHK-AUTH-122 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-007 |
| CHK-AUTH-123 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-007 |
| CHK-AUTH-125 | E2E UI | P2 | Good Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-007 |
| CHK-AUTH-126 | E2E UI | P2 | Medium Candidate | screen map aliases (recon dumps exist) | → TC-AUTH-009 |

## Step 6 — Manual-only

| CHK ID | Scenario | Reason | Revisit? |
|---|---|---|---|
| CHK-AUTH-006, -025 | layout across sizes / orientations | subjective visual; tablets out of scope | if visual regression is added |
| CHK-AUTH-013, -014 | navigation "without visual glitches" | subjective; the transition itself is automated (TC-AUTH-002) | no |
| CHK-AUTH-113 | validation styling | colour/border judgment | if visual regression is added |

## Step 7 — API support

| CHK / TC | Scenario | API action | Endpoint | Priority | Notes |
|---|---|---|---|---|---|
| TC-AUTH-013 | registration happy path | delete the self-registered user after the test | `GET /technician?search=<email>` → `DELETE /user/full-delete/{user.id}` — **verified 2026-09-23** (technician 404, email sign-in 401) | P2 | resolved |
| CHK-AUTH-052, -067 (deferred) | payload / duplicate requests | read the created user | `GET /technician`, `GET /user/...` | P3 | deferred |

## Step 8 — Stable selectors

None required for the selected set (all text). Testability defects recorded for later: SMS Terms close icon
(CHK-AUTH-057), OTP back button (unlabelled — TC-AUTH-009 uses system back), logo images.

## Step 9 — Test data

| TC | Data | Source | Reusable | Cleanup |
|---|---|---|---|---|
| TC-AUTH-005, -006, -008, -009, -003 | test technician email / phone / OTP | existing account (`APP_USER_*` in `.env`) | yes | no |
| TC-AUTH-007 | unregistered email / phone | generated at runtime (`qa-auto+<ts>@example.com`, `+1 202 555 01xx`) | no | no (nothing is created) |
| TC-AUTH-011, -012 | invalid / boundary values (names 1/2/100/101 chars, digits, symbols; malformed email / phone) | data table in the TC | yes | no |
| TC-AUTH-013 | new user: names, `qa-auto+<ts>@example.com`, `+1 202 555 01xx` (fictional range) | generated at runtime | no | **yes — API delete** |
| TC-AUTH-014 | already-registered phone = the test technician's phone | existing account | yes | no |

Email/phone for new users use reserved ranges (`example.com`, NANP 555-01xx) so no real person receives a message.

## Step 10 — Authentication & session

| Role | TCs | Login method | Account | Notes |
|---|---|---|---|---|
| Field Technician | TC-AUTH-003, -005, -006, -008, -009 | **UI login** — these TCs prove login itself | existing test account | token lives in the iOS keychain (secure storage) → no token injection on mobile; other suites use a session-scoped UI-login fixture, once per run (DEV-friendly, FR-OTP-13) |
| none (logged out) | all others | fresh app state | — | app data reset between TCs that need a logged-out start |

## Step 11 — Isolation

| TC | Independent | Creates data | Cleanup | Parallel-safe | Setup / teardown |
|---|---|---|---|---|---|
| 001, 002, 004, 010, 011, 012 | yes | no | no | n/a (serial by decision) | logged-out app state |
| 003 | yes | session | logout / app reset after | n/a | UI login in setup, relaunch |
| 005, 006, 008, 009 | yes | session | app reset after | n/a | logged-out start |
| 007 | yes | no | no | n/a | logged-out start |
| 013 | yes | **user** | **API delete in `finally`** | n/a | unique generated user |
| 014 | yes | no | no | n/a | uses existing phone read-only |

Runs are **serial** (owner decision: DEV server is weak). Wrong-OTP attempts are limited to one per run (lockout).

## Step 12 — Plan

- Tests: `automation/mobile/tests/shared/test_authentication.py` (`@pytest.mark.shared`, runs on iOS and Android).
- Screen maps: `screens/welcome_map.py`, `login_map.py`, `otp_map.py`, `registration_map.py`, `sms_terms_map.py`,
  `jobs_list_map.py` (anchor only). Welcome / Login / OTP / Jobs list aliases resolvable from the recon dumps;
  Registration and SMS Terms need one recon pass.
- Fixtures / helpers: `logged_out_app` (reset app data), `ui_login` (session-scoped), `new_user` + `api_cleanup`,
  `evidence` (named screenshots, video).
- Order: 005 → 002 → 001 → 003 → 006 → 004 → 007 → 009 → 008 → 010 → 011 → 012 → 014 → 013.
- Estimate: 14 TCs × ~1.5–3 h ≈ **25–35 h** incl. screen maps and first stabilisation. Maintenance risk: **Low–Medium**
  (text locators depend on copy — one language, stable build).

## Step 13 — Runtime notes

Locators only through screen maps (`ACCESSIBILITY_ID` = visible text; predicates for multi-line cards); explicit waits
only; assertions on **visibility**, never presence (OTP keeps a hidden `Incorrect code.` in the tree); no retries
(GATES.md); CHK tags on every test (`@pytest.mark.chk` + `@allure.tag`); Allure grouping by module; screenshots at
checkpoints and on failure, video for E2E and failures.

## Step 14 — CI readiness

| Area | Status | Notes |
|---|---|---|
| Headless | Partial | iOS simulator needs macOS runner; Android emulator on Linux (workflow exists) |
| Env variables / credentials | Ready | `.env` locally; CI secrets `APP_USER_*`, `API_*` still to add |
| Test data / cleanup | Partial | cleanup endpoint for TC-AUTH-013 to confirm |
| Parallel | Not Ready — by decision | serial runs only |
| Duration | Acceptable | ~10–15 min for the module (cold starts dominate) |

## Step 15 — Risks

| Category | Risk | Impact | Action | Owner |
|---|---|---|---|---|
| Technical | countdown timer / auto-submit timing | flaky OTP tests | explicit waits on state, not on time | Automation QA |
| Technical | text locators depend on copy | break on copy changes | one language; aliases isolate the change to one map | Automation QA |
| Data | self-registered users left on DEV | DEV clutter | API delete in `finally`, unique markers | Automation QA |
| Data | account lockout (FR-OTP-13) | whole run blocked 2 min | ≤1 wrong attempt per run | Automation QA |
| Environment | weak DEV server | slow / failing runs | serial, login once, minimal API calls | QA |
| Process | SRS ≠ checklist texts (D-6…D-8) | wrong expectations | assert the live app, record deviations | Product Owner |

## Step 16 — Final recommendation

Start now: the module is ready and the selected 14 TCs need no missing ids. Automate the email-login smoke first
(it unlocks every other suite), then Welcome transitions and session persistence, then validations. Keep five visual
items manual and eleven items not recommended with their reasons; 27 automatable items are deferred only by scope.

**First sprint scope:** TC-AUTH-001…014 (82 CHK IDs).

**Must be resolved before automation starts:** ~~delete endpoint for self-registered users~~ (verified);
~~recon of Registration / SMS Terms~~ (done, recon 3c); harness additions (Allure grouping, video, named screenshots,
logged-out reset fixture).
