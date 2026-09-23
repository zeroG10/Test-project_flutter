# QA Checklist: Authentication

> Source: CSV export `docs/00-intake/checklist-concert-technologies-flutter.csv` of the Google Sheet "Working_Regression Check-list_Concert Technologies– Flutter App" (id `1HX1obTdusEYgDQjR6NCwdxjNVkj-8eZKsHOiSRxbvsg`, worksheet `Check-list`, rows 22–162), imported 2026-09-23 by `automation/tools/import_checklist_from_csv.py` (adapter over `import_checklist_from_sheets.py`). IDs assigned at import; they are now the contract — never renumber.

## Welcome Screen

1. [CHK-AUTH-001] Check that the Welcome Screen is displayed as a full-screen view when the application is opened by a non-authenticated user.
2. [CHK-AUTH-002] Check that the Welcome Screen is not displayed when a valid user session token exists and the app navigates directly to the Home / Jobs screen.
3. [CHK-AUTH-003] Check that no navigation bar or back button is displayed on the Welcome Screen.
4. [CHK-AUTH-004] Check that the header text “Welcome to the Concert Technologies” is displayed and centered on the Welcome Screen.
5. [CHK-AUTH-005] Check that the subtext “Create an account or log in to get started.” is displayed below the header text.
6. [CHK-AUTH-006] Check that the Welcome Screen layout remains visually centered and consistent across different screen sizes and orientations.
7. [CHK-AUTH-007] Check that the “Sign up” button is displayed as the primary (filled) call-to-action at the bottom of the Welcome Screen.
8. [CHK-AUTH-008] Check that the “Login” button is displayed as the secondary (outlined or neutral) call-to-action below the “Sign up” button.
9. [CHK-AUTH-009] Check that tapping the “Sign up” button navigates the user to the Account Registration / Sign Up screen.
10. [CHK-AUTH-010] Check that tapping the “Login” button navigates the user to the Login screen.
11. [CHK-AUTH-011] Check that multiple rapid taps on the “Sign up” button do not trigger multiple navigation events.
12. [CHK-AUTH-012] Check that multiple rapid taps on the “Login” button do not trigger multiple navigation events.
13. [CHK-AUTH-013] Check that navigation from the Welcome Screen to the Sign Up screen completes successfully without visual glitches or delays.
14. [CHK-AUTH-014] Check that navigation from the Welcome Screen to the Login screen completes successfully without visual glitches or delays.
15. [CHK-AUTH-015] Check that a generic error message is displayed if navigation to the Sign Up screen fails and the user is allowed to retry.

## Registration Screen / General & Layout

1. [CHK-AUTH-016] Check that the Registration screen is displayed when the user taps “Sign up” from the Welcome screen.
2. [CHK-AUTH-017] Check that the Registration screen displays the logo, title “Registration”, and subtitle “Good to see you! Let’s get you registered.”
3. [CHK-AUTH-018] Check that the Registration screen displays input fields in the following order: First name, Last name, Phone number, Email.
4. [CHK-AUTH-019] Check that the Registration screen displays the “Preferred channel for job notifications” section below the Email field.
5. [CHK-AUTH-020] Check that the Registration screen displays SMS and Email radio button options in the notification channel section.
6. [CHK-AUTH-021] Check that the Registration screen displays the SMS consent checkbox and disclaimer text below the preferred notification channel section.
7. [CHK-AUTH-022] Check that the Continue button is disabled by default when required fields are empty.
8. [CHK-AUTH-023] Check that the Privacy Policy and Terms & Conditions links are displayed below the Continue button.
9. [CHK-AUTH-024] Check that the “Already have an account? Log in” link is displayed at the bottom of the Registration screen.
10. [CHK-AUTH-025] Check that the Registration screen layout remains correctly aligned on different screen sizes and orientations.

## Registration Screen / First Name / Last Name Validation

1. [CHK-AUTH-026] Check that the First name field is required on the Registration screen.
2. [CHK-AUTH-027] Check that the Last name field is required on the Registration screen.
3. [CHK-AUTH-028] Check that inline validation is displayed if the First name field is empty after validation is triggered.
4. [CHK-AUTH-029] Check that inline validation is displayed if the Last name field is empty after validation is triggered.
5. [CHK-AUTH-030] Check that the First name field accepts alphabetical characters only.
6. [CHK-AUTH-031] Check that the Last name field accepts alphabetical characters only.
7. [CHK-AUTH-032] Check that invalid characters are rejected in the First name and Last name fields.
8. [CHK-AUTH-033] Check that validation messages are cleared dynamically after correcting invalid First name or Last name values.

## Registration Screen / Phone Number Field & Country Selector

1. [CHK-AUTH-034] Check that the Phone number field is required on the Registration screen.
2. [CHK-AUTH-035] Check that the Phone number field displays the selected country code prefix.
3. [CHK-AUTH-036] Check that tapping the country code selector opens the country selection bottom sheet.
4. [CHK-AUTH-037] Check that the country selection bottom sheet displays country flags, country names, and dialing codes.
5. [CHK-AUTH-038] Check that the country search field filters countries dynamically while typing.
6. [CHK-AUTH-039] Check that selecting a country updates the phone number prefix in the Registration form.
7. [CHK-AUTH-040] Check that the Phone number field validates the entered value according to the selected country format.
8. [CHK-AUTH-041] Check that invalid phone number formats display a validation error message.
9. [CHK-AUTH-042] Check that the numeric keyboard is displayed when focusing the Phone number field.

## Registration Screen / Email Field

1. [CHK-AUTH-043] Check that the Email field is required on the Registration screen.
2. [CHK-AUTH-044] Check that the Email field validates entered email format correctly.
3. [CHK-AUTH-045] Check that invalid email values display a validation error message.
4. [CHK-AUTH-046] Check that valid email values enable successful form validation.
5. [CHK-AUTH-047] Check that validation errors are cleared dynamically after correcting invalid email values.

## Registration Screen / Preferred Notification Channel

1. [CHK-AUTH-048] Check that only one preferred notification channel option can be selected at a time.
2. [CHK-AUTH-049] Check that the user can select SMS as the preferred notification channel.
3. [CHK-AUTH-050] Check that the user can select Email as the preferred notification channel.
4. [CHK-AUTH-051] Check that the selected preferred notification channel remains selected while editing other form fields.
5. [CHK-AUTH-052] Check that the selected preferred notification channel is sent correctly in the registration request payload.

## Registration Screen / SMS Consent Logic

1. [CHK-AUTH-053] Check that tapping the SMS consent checkbox opens the “SMS Messaging Terms & Conditions” screen.
2. [CHK-AUTH-054] Check that the SMS Messaging Terms & Conditions screen displays the close icon, title, and legal content.
3. [CHK-AUTH-055] Check that the SMS Messaging Terms & Conditions screen displays the “I Accept SMS Terms & Conditions” button.
4. [CHK-AUTH-056] Check that tapping “I Accept SMS Terms & Conditions” closes the Terms screen and marks the SMS checkbox as selected.
5. [CHK-AUTH-057] Check that tapping the close icon on the Terms screen closes the screen without selecting the SMS checkbox.
6. [CHK-AUTH-058] Check that the SMS consent checkbox state persists after returning from the Terms screen.
7. [CHK-AUTH-059] Check that the SMS consent checkbox can be deselected after acceptance if allowed by business logic.
8. [CHK-AUTH-060] Check that the Continue button remains disabled if SMS notification channel is selected but SMS consent is not accepted.
9. [CHK-AUTH-061] Check that OTP-related SMS consent text is displayed correctly below the checkbox.

## Registration Screen / Continue Action & Registration Flow

1. [CHK-AUTH-062] Check that the Continue button becomes enabled only when all required fields contain valid values.
2. [CHK-AUTH-063] Check that tapping Continue submits registration data to the backend.
3. [CHK-AUTH-064] Check that successful registration navigates the user to the correct OTP verification flow based on the selected notification channel.
4. [CHK-AUTH-065] Check that selecting SMS notification channel opens the Phone number verification screen after successful registration.
5. [CHK-AUTH-066] Check that selecting Email notification channel opens the Email address verification screen after successful registration.
6. [CHK-AUTH-067] Check that multiple rapid taps on Continue do not trigger duplicate registration requests.
7. [CHK-AUTH-068] Check that entered form values remain preserved if registration fails.
8. [CHK-AUTH-069] Check that the error message “An account with this phone number already exists. Please log in to continue.” is displayed for already registered phone numbers.
9. [CHK-AUTH-070] Check that a generic error message is displayed when registration fails due to backend or network issues.
10. [CHK-AUTH-071] Check that the user can retry registration after an error without reopening the Registration screen.

## Phone/email verification screen / General & Layout

1. [CHK-AUTH-072] Check that the Phone number verification screen displays the verified phone number in masked or formatted form.
2. [CHK-AUTH-073] Check that the Email address verification screen displays the verified email address in masked or formatted form.
3. [CHK-AUTH-074] Check that the correct screen title is displayed based on verification type.
4. [CHK-AUTH-075] Check that the correct instruction text is displayed based on verification type.
5. [CHK-AUTH-076] Check that four OTP input boxes are displayed on the verification screen.
6. [CHK-AUTH-077] Check that the Verify button is disabled until all four OTP digits are entered.
7. [CHK-AUTH-078] Check that the “Request a new code” option is disabled while the countdown timer is active.
8. [CHK-AUTH-079] Check that the “Request a new code” option becomes enabled after the countdown timer expires.
9. [CHK-AUTH-080] Check that the countdown timer value decreases correctly in real time.

## Phone/email verification screen / OTP Input Behavior

1. [CHK-AUTH-081] Check that entering a digit automatically moves focus to the next OTP input field.
2. [CHK-AUTH-082] Check that deleting a digit moves focus back to the previous OTP input field.
3. [CHK-AUTH-083] Check that only numeric values are accepted in OTP input fields.
4. [CHK-AUTH-084] Check that more than four OTP digits cannot be entered.
5. [CHK-AUTH-085] Check that pasting OTP values fills the OTP fields correctly if supported.
6. [CHK-AUTH-086] Check that the numeric keyboard is displayed automatically when focusing OTP fields.

## Phone/email verification screen / Verification Flow

1. [CHK-AUTH-087] Check that tapping Verify submits the entered OTP for backend validation.
2. [CHK-AUTH-088] Check that successful OTP verification authenticates the user successfully.
3. [CHK-AUTH-089] Check that successful OTP verification navigates the user to the Jobs screen or onboarding flow.
4. [CHK-AUTH-090] Check that incorrect OTP values display an “Incorrect code” validation error.
5. [CHK-AUTH-091] Check that OTP fields remain editable after invalid OTP verification attempts.
6. [CHK-AUTH-092] Check that multiple rapid taps on Verify do not trigger duplicate OTP validation requests.
7. [CHK-AUTH-093] Check that requesting a new OTP invalidates the previously issued OTP code.
8. [CHK-AUTH-094] Check that tapping “Request a new code” sends a new OTP to the selected delivery channel.
9. [CHK-AUTH-095] Check that requesting a new code restarts the countdown timer.
10. [CHK-AUTH-096] Check that the verification flow works correctly for both SMS and Email delivery channels.

## Phone/email verification screen / Navigation & Error Handling

1. [CHK-AUTH-097] Check that tapping the back arrow returns the user to the previous authentication screen.
2. [CHK-AUTH-098] Check that OTP verification handles slow network responses without UI freezes or duplicated states.
3. [CHK-AUTH-099] Check that a generic error message is displayed if OTP verification fails due to connectivity issues.
4. [CHK-AUTH-100] Check that the user can retry OTP verification after network-related failures.
5. [CHK-AUTH-101] Check that OTP retry limits are enforced if configured by backend rules.
6. [CHK-AUTH-102] Check that OTP state is preserved or reset correctly after reopening the verification screen according to business logic.

## Login screen / General & Layout

1. [CHK-AUTH-103] Check that the Login screen is displayed when the user taps “Log in” from the Welcome screen.
2. [CHK-AUTH-104] Check that the Login screen displays the logo, title “Log in”, and subtitle “Good to see you! Let’s get you logged in.”
3. [CHK-AUTH-105] Check that the Login screen displays helper text instructing the user to enter email or phone number used during registration.
4. [CHK-AUTH-106] Check that the Login screen displays a single “Phone number / Email” input field.
5. [CHK-AUTH-107] Check that the Continue button is disabled when the input field is empty.
6. [CHK-AUTH-108] Check that the Privacy Policy and Terms & Conditions links are displayed below the Continue button.
7. [CHK-AUTH-109] Check that the “Don’t have an account yet? Sign up” link is displayed at the bottom of the Login screen.

## Login screen / Input Validation

1. [CHK-AUTH-110] Check that the Login field accepts valid email addresses.
2. [CHK-AUTH-111] Check that the Login field accepts valid phone numbers.
3. [CHK-AUTH-112] Check that invalid email or phone number formats display the “Format is incorrect.” validation message.
4. [CHK-AUTH-113] Check that validation styling is displayed for invalid Login field values.
5. [CHK-AUTH-114] Check that validation errors are removed after correcting invalid input values.
6. [CHK-AUTH-115] Check that the Continue button becomes enabled only when a valid email or phone number is entered.

## Login screen / Login Flow

1. [CHK-AUTH-116] Check that tapping Continue with a valid registered phone number triggers OTP generation via SMS.
2. [CHK-AUTH-117] Check that tapping Continue with a valid registered email triggers OTP generation via Email.
3. [CHK-AUTH-118] Check that login with a registered phone number navigates to the Phone number verification screen.
4. [CHK-AUTH-119] Check that login with a registered email navigates to the Email address verification screen.
5. [CHK-AUTH-120] Check that multiple rapid taps on Continue do not trigger duplicate login requests.
6. [CHK-AUTH-121] Check that entered login values remain preserved if login fails.
7. [CHK-AUTH-122] Check that the error message “This phone number is not registered yet. Create an account to get started.” is displayed for unregistered phone numbers.
8. [CHK-AUTH-123] Check that the error message “This email is not registered yet. Create an account to get started.” is displayed for unregistered email addresses.
9. [CHK-AUTH-124] Check that a generic error message is displayed if login fails due to backend or network issues.
10. [CHK-AUTH-125] Check that the user can retry login without reopening the Login screen after a failed request.
11. [CHK-AUTH-126] Check that authenticated-only screens remain inaccessible without successful OTP verification.
