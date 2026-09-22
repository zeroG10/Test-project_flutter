# QA Checklist: Authentication

## Access and Permissions

1. [CHK-AUTH-001] Check that the Set Password page is accessible only via a valid activation link sent by email.
2. [CHK-AUTH-002] Check that the Set Password page blocks access and shows an error if the activation token is invalid.
3. [CHK-AUTH-003] Check that the Set Password page blocks access and shows an error if the activation token is expired.
4. [CHK-AUTH-004] Check that the Set Password page blocks access and shows an error if the activation token was already used.
5. [CHK-AUTH-005] Check that the Login page is reachable without an authenticated session.
6. [CHK-AUTH-006] Check that the Login page redirects an already authenticated user away from the form.
7. [CHK-AUTH-007] Check that the Login page denies access when credentials belong to a non-activated account.
8. [CHK-AUTH-008] Check that the Login page denies access when credentials belong to a disabled account.
9. [CHK-AUTH-009] Check that after successful login as Root User the system grants access to the Admin Panel landing page.
10. [CHK-AUTH-010] Check that after successful login as Manager User the system grants access to the Admin Panel landing page.
11. [CHK-AUTH-011] Check that after successful login as Manager User the Managers list page is not accessible.
12. [CHK-AUTH-012] Check that the Forgot Password page is reachable from the Login page without authentication.
13. [CHK-AUTH-013] Check that the Set Password, Login, and Forgot Password pages are not accessible while a valid session is already active unless explicitly allowed.

## Navigation

1. [CHK-AUTH-014] Check that the Login page exposes a Forgot Password link that navigates to the Forgot Password page.
2. [CHK-AUTH-015] Check that the Forgot Password page exposes a Back to Login link that navigates to the Login page.
3. [CHK-AUTH-016] Check that after successful password creation on the Set Password page the user is redirected to the Login page (or auto-logged in, if configured).
4. [CHK-AUTH-017] Check that after successful login the user is redirected to the Admin Panel landing page.
5. [CHK-AUTH-018] Check that the password reset email link navigates the user to the Set Password page.
6. [CHK-AUTH-019] Check that the Back to Login link on the Forgot Password page remains available after the success confirmation is shown.
7. [CHK-AUTH-020] Check that using the browser Back button after a successful Set Password submission does not return the user to a usable form state.
8. [CHK-AUTH-021] Check that using the browser Back button after a successful login does not return the user to the Login page in an authenticated state.

## UI Layout

1. [CHK-AUTH-022] Check that the Set Password page displays a centered card layout on a neutral background.
2. [CHK-AUTH-023] Check that the Login page displays a centered card layout on a neutral background.
3. [CHK-AUTH-024] Check that the Forgot Password page displays a centered card layout on a neutral background.
4. [CHK-AUTH-025] Check that the Acme Field Services logo is displayed above the form on the Set Password page.
5. [CHK-AUTH-026] Check that the Acme Field Services logo is displayed above the form on the Login page.
6. [CHK-AUTH-027] Check that the Acme Field Services logo is displayed above the form on the Forgot Password page.
7. [CHK-AUTH-028] Check that the Set Password page shows the title "Set password".
8. [CHK-AUTH-029] Check that the Login page shows the title "Log in using your credentials".
9. [CHK-AUTH-030] Check that the Forgot Password page shows the title "Forgot your password?".
10. [CHK-AUTH-031] Check that the Set Password page shows instructional text describing the password requirements.
11. [CHK-AUTH-032] Check that the Forgot Password page shows instructional text describing the reset process.
12. [CHK-AUTH-033] Check that each authentication page uses a single-column form optimized for desktop and tablet.

## Fields and Controls

1. [CHK-AUTH-034] Check that the Set Password page contains a New Password field with masked input by default.
2. [CHK-AUTH-035] Check that the Set Password page contains a Confirm Password field with masked input by default.
3. [CHK-AUTH-036] Check that the New Password field on the Set Password page provides a visibility toggle to show or hide the password.
4. [CHK-AUTH-037] Check that the Confirm Password field on the Set Password page provides a visibility toggle to show or hide the password.
5. [CHK-AUTH-038] Check that the Set Password page contains a primary "Set password" button disabled by default.
6. [CHK-AUTH-039] Check that the Login page contains an Email field with placeholder "Please enter".
7. [CHK-AUTH-040] Check that the Login page contains a Password field with masked input by default.
8. [CHK-AUTH-041] Check that the Password field on the Login page provides a visibility toggle to show or hide the password.
9. [CHK-AUTH-042] Check that the Login page contains a Remember Me checkbox.
10. [CHK-AUTH-043] Check that the Login page contains a Forgot Password link.
11. [CHK-AUTH-044] Check that the Login page contains a primary "Log in" button disabled when required fields are empty or invalid.
12. [CHK-AUTH-045] Check that the Forgot Password page contains an Email field with placeholder "Please enter".
13. [CHK-AUTH-046] Check that the Forgot Password page contains a primary "Request password reset" button disabled by default.
14. [CHK-AUTH-047] Check that the Forgot Password page contains a Back to Login link.
15. [CHK-AUTH-129] Check that the Remember Me checkbox on the Login page is selected by default when the page loads.
16. [CHK-AUTH-130] Check that the Forgot Password link on the Login page reads "Forgot password?" and is right-aligned on the same row as the Remember Me checkbox.
17. [CHK-AUTH-131] Check that the Log in button spans the full width of the Login form card.
18. [CHK-AUTH-132] Check that the Password field on the Login page shows the visibility toggle as an eye icon at the right edge of the field.

## Positive Flow

1. [CHK-AUTH-048] Check that opening a valid activation link loads the Set Password page without errors.
2. [CHK-AUTH-049] Check that entering a New Password that satisfies all rules and a matching Confirm Password enables the "Set password" button on the Set Password page.
3. [CHK-AUTH-050] Check that clicking "Set password" with valid matching passwords activates the account and persists the password securely.
4. [CHK-AUTH-051] Check that after successful password creation on the Set Password page the activation token is invalidated and cannot be reused.
5. [CHK-AUTH-052] Check that entering a valid email and a non-empty password on the Login page enables the "Log in" button.
6. [CHK-AUTH-053] Check that submitting valid credentials on the Login page creates an authenticated session and redirects to the landing page.
7. [CHK-AUTH-054] Check that selecting Remember Me on the Login page persists the session beyond the default expiration according to the security configuration.
8. [CHK-AUTH-055] Check that not selecting Remember Me on the Login page limits session persistence to the default expiration window.
9. [CHK-AUTH-056] Check that entering a valid email format on the Forgot Password page enables the "Request password reset" button.
10. [CHK-AUTH-057] Check that submitting a valid email on the Forgot Password page replaces the form with the success confirmation message.
11. [CHK-AUTH-058] Check that submitting a valid email associated with an existing account on the Forgot Password page triggers a password reset email containing a single-use reset link.
12. [CHK-AUTH-059] Check that opening the reset link from the password reset email loads the Set Password page with a valid token.

## Validation

1. [CHK-AUTH-060] Check that the Set Password page rejects a New Password shorter than 12 characters with an inline error.
2. [CHK-AUTH-061] Check that the Set Password page rejects a New Password without at least one digit with an inline error.
3. [CHK-AUTH-062] Check that the Set Password page rejects a New Password without at least one letter with an inline error.
4. [CHK-AUTH-063] Check that the Set Password page rejects a New Password without at least one special character or one uppercase letter with an inline error.
5. [CHK-AUTH-064] Check that the Set Password page shows inline validation errors in real time as the user types.
6. [CHK-AUTH-065] Check that the Set Password page rejects submission when Confirm Password does not exactly match New Password.
7. [CHK-AUTH-066] Check that the "Set password" button remains disabled while any password rule is unmet.
8. [CHK-AUTH-067] Check that the "Set password" button remains disabled while New Password and Confirm Password do not match.
9. [CHK-AUTH-068] Check that invalid inputs on the Set Password page are highlighted with an error style.
10. [CHK-AUTH-069] Check that the Login page rejects an invalid email format with an inline error and prevents submission.
11. [CHK-AUTH-070] Check that the "Log in" button stays disabled when the email field is empty.
12. [CHK-AUTH-071] Check that the "Log in" button stays disabled when the password field is empty.
13. [CHK-AUTH-072] Check that the "Log in" button stays disabled when the email field contains an invalid format.
14. [CHK-AUTH-073] Check that the Forgot Password page rejects an invalid email format with an inline error.
15. [CHK-AUTH-074] Check that the "Request password reset" button stays disabled when the email field is empty or invalid.
16. [CHK-AUTH-133] Check that entering an email in an invalid format on the Login page shows the inline error "Please enter a valid email address." below the Email field.
17. [CHK-AUTH-134] Check that the Email field on the Login page shows a red border and a red error icon inside the field when the entered email format is invalid.

## Negative Flow

1. [CHK-AUTH-075] Check that opening an invalid activation link on the Set Password page shows an error state and blocks the form.
2. [CHK-AUTH-076] Check that opening an expired activation link on the Set Password page shows an error state and blocks the form.
3. [CHK-AUTH-077] Check that opening a previously used activation link on the Set Password page shows an error state and blocks the form.
4. [CHK-AUTH-078] Check that submitting incorrect credentials on the Login page displays a generic "Incorrect email or password" error.
5. [CHK-AUTH-079] Check that the Login error message does not reveal whether the email or the password was incorrect.
6. [CHK-AUTH-080] Check that submitting credentials for a disabled account on the Login page displays an authentication error without disclosing account state.
7. [CHK-AUTH-081] Check that submitting credentials for a non-activated account on the Login page displays an authentication error.
8. [CHK-AUTH-082] Check that submitting a non-existent email on the Forgot Password page still displays the same success confirmation message to prevent account enumeration.
9. [CHK-AUTH-083] Check that submitting the Login form with leading or trailing whitespace in the email is treated according to backend trimming rules.
10. [CHK-AUTH-135] Check that submitting incorrect credentials on the Login page shows the banner "Incorrect email or password." at the top of the form card.

## Status Behavior

1. [CHK-AUTH-084] Check that the account status changes to active only after a successful password creation on the Set Password page.
2. [CHK-AUTH-085] Check that the activation token is marked as used immediately after successful password submission.
3. [CHK-AUTH-086] Check that a previously issued password reset token becomes invalid after being used once.
4. [CHK-AUTH-087] Check that a Remember Me session ends at the configured expiration time even if the browser remains open.

## Notifications and Alerts

1. [CHK-AUTH-088] Check that a password reset email is sent when a valid email is submitted on the Forgot Password page and an account exists.
2. [CHK-AUTH-089] Check that the password reset email contains a single-use, time-limited reset link.
3. [CHK-AUTH-090] Check that the success confirmation message on the Forgot Password page reads "Please check your email. If an account is associated with this address, we've sent a reset link."
4. [CHK-AUTH-091] Check that no password reset email is sent when the submitted email does not match any account.
5. [CHK-AUTH-092] Check that the activation email sent after Root User creates a new account contains a single-use, time-limited activation link.

## Data Saving and Persistence

1. [CHK-AUTH-093] Check that a password set on the Set Password page is persisted and usable to log in on the Login page.
2. [CHK-AUTH-094] Check that an authenticated session created at login persists across page reloads within its configured lifetime.
3. [CHK-AUTH-095] Check that Remember Me persists the session across browser restarts according to the configured expiration. 
4. [CHK-AUTH-096] Check that without Remember Me the session does not persist beyond the default session expiration.
5. [CHK-AUTH-097] Check that input entered in the Set Password form is preserved when a server error occurs during submission.

## API and Backend Error Handling

1. [CHK-AUTH-098] Check that the Set Password page displays a generic error message and allows retry when the password submission fails due to a server error.
2. [CHK-AUTH-099] Check that the Login page displays a generic error message and allows retry when the authentication service is unavailable.
3. [CHK-AUTH-100] Check that the Forgot Password page displays a generic error message and allows retry when the password reset service is unavailable.
4. [CHK-AUTH-101] Check that backend errors on any authentication page do not expose stack traces or internal details to the user.
5. [CHK-AUTH-102] Check that submission buttons on all authentication pages do not allow duplicate submissions while a request is in flight.

## Loading States

1. [CHK-AUTH-103] Check that the Set Password page shows a loading state on the "Set password" button while the submission request is in flight.
2. [CHK-AUTH-104] Check that the Login page shows a loading state on the "Log in" button while the authentication request is in flight.
3. [CHK-AUTH-105] Check that the Forgot Password page shows a loading state on the "Request password reset" button while the request is in flight.
4. [CHK-AUTH-106] Check that the Set Password page shows a loading state while validating the activation token on page load.

## Cross-browser

1. [CHK-AUTH-107] Check that the Set Password page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.
2. [CHK-AUTH-108] Check that the Login page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.
3. [CHK-AUTH-109] Check that the Forgot Password page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.
4. [CHK-AUTH-110] Check that the password visibility toggle works on the latest versions of Chrome, Firefox, and Edge.
5. [CHK-AUTH-111] Check that browser password autofill on the Login page does not break the enabled/disabled state of the "Log in" button.
6. [CHK-AUTH-112] Check that browser password manager prompts to save the new password after a successful Set Password submission.

## Security

1. [CHK-AUTH-113] Check that all authentication page requests are transmitted over HTTPS only.
2. [CHK-AUTH-114] Check that passwords are never sent or displayed in plaintext in network logs or browser dev tools.
3. [CHK-AUTH-115] Check that activation links on the Set Password page are single-use and become invalid after a successful submission.
4. [CHK-AUTH-116] Check that password reset tokens on the Forgot Password flow are single-use and expire after the configured time.
5. [CHK-AUTH-117] Check that the Forgot Password response is identical regardless of whether the email is registered to prevent account enumeration.
6. [CHK-AUTH-118] Check that session tokens are stored in a manner that protects against XSS access.
7. [CHK-AUTH-119] Check that authenticated requests include CSRF protection where applicable.
8. [CHK-AUTH-120] Check that pasting script payloads into the email or password fields does not execute as code.
9. [CHK-AUTH-121] Check that the password visibility toggle does not reveal the password value in the DOM in a way that persists after toggle-off.
10. [CHK-AUTH-122] Check that role-based access enforced after login restricts Manager Users from Root-only areas such as the Managers list.
11. [CHK-AUTH-123] Check that logout invalidates the session token on the server side and prevents reuse.
12. [CHK-AUTH-124] Check that an expired session redirects the user back to the Login page on the next protected action.

## Regression Checks

1. [CHK-AUTH-125] Check that after a password reset the previous password can no longer be used to log in on the Login page.
2. [CHK-AUTH-126] Check that after a successful login the role-based navigation menu reflects the user's role on the landing page.
3. [CHK-AUTH-127] Check that existing active sessions remain valid after a different user resets their password.
4. [CHK-AUTH-128] Check that the activation flow does not interfere with previously activated accounts attempting to log in.

## Open Questions

1. Activation token expiration time on the Set Password page is described as "configurable" (NFR-AUTH-SP-02) without a specific value, and `00-common-rules_and_info.md` does not pin it down — testers cannot verify the exact expiration boundary.
2. Password reset token expiration time on the Forgot Password page is described as "configurable" (NFR-AUTH-FP-01) without a specific value — testers cannot verify the exact expiration boundary.
3. Login rate limiting after repeated failed attempts is marked "may be rate-limited (recommended)" (FR-AUTH-LG-11) — it is unclear whether rate limiting is in scope, what the threshold is, and what user-visible behavior should occur on lockout.
4. Forgot Password rate limiting is required (NFR-AUTH-FP-02) but no threshold, time window, or user-visible behavior is specified — testers cannot define expected behavior on the boundary.
5. Remember Me session duration vs default session duration is described as "configured expiration rules" (FR-AUTH-LG-08) without concrete values — testers cannot verify persistence boundaries.
6. The Set Password redirect target is ambiguous: FR-AUTH-SP-08 says "Redirect the user to the Login page (or auto-login, if configured)" — it is unclear which behavior is enabled in this build.
7. The Admin Panel landing page after login is described as "Dashboard or default page" (FR-AUTH-LG-05) — the actual landing route per role is not specified, blocking redirect verification.
8. Password complexity instructional text on the Set Password page is given as an example ("e.g., …longer than 12 characters…") — it is unclear whether "longer than 12" means strictly greater than 12 or at least 12 (FR-AUTH-SP-04 says "≥ 12"), creating a boundary-test conflict.
9. Maximum password length, allowed character set, and whether spaces or Unicode are permitted in the New Password field are not specified — testers cannot define upper-bound and edge-case behavior.
10. Email field constraints on the Login and Forgot Password pages (max length, allowed local-part/domain rules, case sensitivity, trimming) are not specified.
11. Behavior when the same activation link is opened in two browser tabs simultaneously is not specified.
12. Server-side vs client-side error placement on the Login page: the SRS left this as "inline or as a banner" (Error Feedback); the design resolves it as a top banner ("Incorrect email or password.") for server-side errors and inline text for client-side field errors — confirm this is the final intended behavior.
13. Mobile responsiveness scope is unclear: SRS section 2.5 says responsive design with min width 1366px and explicitly states mobile is not required (2.3), so the Mobile Responsiveness section is omitted from this checklist — confirm this is intentional for the Authentication pages.
14. Account enumeration protection on the Login page is not addressed — it is unclear whether "Account disabled or not activated" errors (Server-Side Errors) should reveal account state or be folded into a generic error like the Forgot Password flow.
15. Logout endpoint behavior and the redirect target on session expiration are not defined within the Authentication SRS section.
16. Design↔SRS conflict on the Login "Client-side error" state: the design shows the "Log in" button enabled while the Email field holds an invalid format, but FR-AUTH-LG-04 and check CHK-AUTH-072 require it to stay disabled until the email format is valid — confirm which behavior is correct (source: Figma node 31:19850).
17. The Login design shows the "Remember me" checkbox pre-selected by default; the SRS does not specify a default state, and defaulting session persistence to on has security implications — confirm whether pre-checked is intended (source: Figma node 31:19825).

**Coverage summary:** functional: 39 / UI: 30 / validation: 17 / permissions: 13 / edge cases: 14
