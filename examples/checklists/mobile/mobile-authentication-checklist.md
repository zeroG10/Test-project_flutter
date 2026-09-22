# QA Checklist: Mobile Authentication

## Access and Permissions

1. [CHK-MAUTH-001] Check that the Registration, Login, and Phone number verification screens are reachable without an authenticated session.
2. [CHK-MAUTH-002] Check that on Android the SMS auto-read permission (if requested) shows the system consent prompt on the Phone number verification screen at the moment of OTP delivery.
3. [CHK-MAUTH-003] Check that on Android denying the SMS auto-read consent on the Phone number verification screen still allows manual OTP entry.
4. [CHK-MAUTH-004] Check that on iOS the system OTP autofill suggestion appears above the keyboard on the Phone number verification screen when an SMS code arrives.

## Navigation

1. [CHK-MAUTH-005] Check that tapping the back arrow on the Phone number verification screen returns the user to the previous screen (Registration or Login).
2. [CHK-MAUTH-006] Check that on Android the hardware/system back button on the Phone number verification screen returns to the previous screen without losing entered phone number context.
3. [CHK-MAUTH-007] Check that on Android 14+ the predictive back gesture on the Registration and Login screens shows the previous screen preview before commit.
4. [CHK-MAUTH-008] Check that on iOS the swipe-back edge gesture on the Registration, Login, and Phone number verification screens returns to the previous screen.
5. [CHK-MAUTH-009] Check that submitting a valid phone number on the Login screen navigates to the Phone number verification screen.
6. [CHK-MAUTH-010] Check that submitting a valid Registration form navigates the user to the next onboarding step (Phone number verification).
7. [CHK-MAUTH-011] Check that successful OTP verification on the Phone number verification screen navigates to the next onboarding step.
8. [CHK-MAUTH-012] Check that tapping the Terms link on the Registration screen opens the Terms and Conditions web page at https://www.acme-field.example.com/sms-terms-and-conditions/.
9. [CHK-MAUTH-013] Check that tapping the Privacy Policy link on the Registration screen opens the Privacy Policy web page at https://www.acme-field.example.com/mobile-privacy/.
10. [CHK-MAUTH-014] Check that tapping the Terms link on the Login screen opens the Terms and Conditions document.
11. [CHK-MAUTH-015] Check that tapping the Privacy Policy link on the Login screen opens the Privacy Policy document.
12. [CHK-MAUTH-016] Check that tapping the "Sign up" link at the bottom of the Login screen navigates the user to the Registration screen.
13. [CHK-MAUTH-017] Check that tapping the "Already have an account? Log in" link on the Registration screen navigates the user to the Login screen.
14. [CHK-MAUTH-018] Check that tapping the back arrow on the Email address verification screen returns the user to the Registration screen.

## UI Layout

1. [CHK-MAUTH-019] Check that the Registration screen displays the title "Registration" and subtitle "Good to see you! Let's get you registered."
2. [CHK-MAUTH-020] Check that the Registration screen displays stacked First name, Last name, Phone number, and Email input fields in that order.
3. [CHK-MAUTH-021] Check that the Registration screen displays the Continue primary action button at the bottom of the form.
4. [CHK-MAUTH-022] Check that the Registration screen displays the legal text "By continuing, you accept the Acme Field Services Privacy Policy and Terms & Conditions" below the Continue button with tappable Privacy Policy and Terms & Conditions links.
5. [CHK-MAUTH-023] Check that the Phone number verification screen displays a back navigation arrow at the top.
6. [CHK-MAUTH-024] Check that the Phone number verification screen displays the title "Phone number verification" and the instruction text "Enter the 4-digit code sent to your number".
7. [CHK-MAUTH-025] Check that the Phone number verification screen displays the user's phone number in the format "+1 415 555 2314".
8. [CHK-MAUTH-026] Check that the Phone number verification screen displays four individual OTP input boxes.
9. [CHK-MAUTH-027] Check that the Phone number verification screen displays the Verify primary action button.
10. [CHK-MAUTH-028] Check that the Phone number verification screen displays the resend text "Didn't receive the code? You can request a new code in [timer]" with a live countdown.
11. [CHK-MAUTH-029] Check that the Login screen displays the title "Log in" and subtitle "Good to see you! Let's get you logged in."
12. [CHK-MAUTH-030] Check that the Login screen displays a single Phone number input field and a Continue primary action button.
13. [CHK-MAUTH-031] Check that the Login screen displays the legal text "By continuing, you accept the Acme Field Services Privacy Policy and Terms & Conditions" with tappable links below the button.
14. [CHK-MAUTH-032] Check that the Registration, Login, Phone number verification, and Email address verification screens respect the device safe area on iOS (notch, Dynamic Island, home indicator).
15. [CHK-MAUTH-033] Check that the Registration, Login, Phone number verification, and Email address verification screens render correctly on the smallest supported width (320px) without truncation or overflow.
16. [CHK-MAUTH-034] Check that the Registration, Login, Phone number verification, and Email address verification screens render correctly on the largest supported width (1440px / tablet) without overstretched controls.
17. [CHK-MAUTH-035] Check that the Registration screen displays the Acme Field Services logo centered above the "Registration" title.
18. [CHK-MAUTH-036] Check that the Registration screen displays a "Preferred channel for job notifications" label with SMS and Email radio options below the Email field.
19. [CHK-MAUTH-037] Check that the Registration screen displays an "Already have an account? Log in" link below the legal text.
20. [CHK-MAUTH-038] Check that the Login screen displays a "Don't have an account yet?" prompt with a tappable "Sign up" link pinned at the bottom of the screen.

## Fields and Controls

1. [CHK-MAUTH-039] Check that the First name field on the Registration screen is a text input accepting alphabetical characters only.
2. [CHK-MAUTH-040] Check that the Last name field on the Registration screen is a text input accepting alphabetical characters only.
3. [CHK-MAUTH-041] Check that the Phone number field on the Registration screen opens the numeric / phone keypad on focus.
4. [CHK-MAUTH-042] Check that the Email field on the Registration screen opens the email keyboard on focus and is marked as optional.
5. [CHK-MAUTH-043] Check that the Phone number field on the Login screen opens the numeric / phone keypad and supports international format (e.g., +1 415 555 2314).
6. [CHK-MAUTH-044] Check that the OTP input on the Phone number verification screen opens the numeric keypad automatically when the screen loads.
7. [CHK-MAUTH-045] Check that entering a digit in an OTP box on the Phone number verification screen auto-advances focus to the next box.
8. [CHK-MAUTH-046] Check that pressing backspace in an OTP box on the Phone number verification screen moves focus to the previous box and clears it.
9. [CHK-MAUTH-047] Check that the Continue button on the Registration screen is disabled by default until all required fields are valid.
10. [CHK-MAUTH-048] Check that the Verify button on the Phone number verification screen is disabled until all 4 OTP digits are entered.
11. [CHK-MAUTH-049] Check that the Continue button on the Login screen is disabled by default until a valid phone number is entered.
12. [CHK-MAUTH-050] Check that the Login screen displays a "+1" country-code selector with a dropdown chevron to the left of the Phone number input.
13. [CHK-MAUTH-051] Check that the Registration screen Phone number field displays a "+1" country-code selector to the left of the input that can be expanded to choose another country code.
14. [CHK-MAUTH-052] Check that the SMS and Email preferred-channel radios on the Registration screen are mutually exclusive so selecting one deselects the other.
15. [CHK-MAUTH-053] Check that no preferred-channel radio is selected by default when the Registration screen is first opened.
16. [CHK-MAUTH-054] Check that selecting SMS as the preferred channel on the Registration screen reveals the SMS consent checkbox and its supporting legal text.
17. [CHK-MAUTH-055] Check that selecting Email as the preferred channel on the Registration screen hides the SMS consent checkbox and its supporting legal text.
18. [CHK-MAUTH-056] Check that the SMS consent checkbox on the Registration screen is unchecked by default.
19. [CHK-MAUTH-057] Check that the SMS consent supporting text on the Registration screen includes the OTP disclosure, "Message frequency may vary.", "Message and data rates may apply.", and "Reply STOP to unsubscribe, HELP for help."
20. [CHK-MAUTH-058] Check that the Verify button on the Email address verification screen stays disabled until all 4 code digits are entered.
21. [CHK-MAUTH-059] Check that the Email address verification screen shows a resend countdown that becomes a tappable "Request a new code" when the timer reaches zero.

## Positive Flow

1. [CHK-MAUTH-060] Check that filling First name, Last name, and a valid Phone number on the Registration screen enables the Continue button.
2. [CHK-MAUTH-061] Check that filling First name, Last name, a valid Phone number, and a valid Email on the Registration screen enables the Continue button.
3. [CHK-MAUTH-062] Check that leaving the optional Email field empty on the Registration screen does not block the Continue button.
4. [CHK-MAUTH-063] Check that tapping Continue on a valid Registration form submits the data to the backend and proceeds to the Phone number verification screen.
5. [CHK-MAUTH-064] Check that entering a registered phone number on the Login screen and tapping Continue submits the request, triggers OTP generation, and navigates to the Phone number verification screen.
6. [CHK-MAUTH-065] Check that entering the correct 4-digit OTP and tapping Verify on the Phone number verification screen proceeds to the next onboarding step.
7. [CHK-MAUTH-066] Check that after the resend timer expires on the Phone number verification screen the "Request a new code" link becomes tappable.
8. [CHK-MAUTH-067] Check that tapping "Request a new code" on the Phone number verification screen triggers a new OTP SMS and restarts the countdown timer.
9. [CHK-MAUTH-068] Check that with all required fields valid and SMS selected as the preferred channel, the Continue button on the Registration screen enables only after the SMS consent checkbox is checked.
10. [CHK-MAUTH-069] Check that with all required fields valid and Email selected as the preferred channel, the Continue button on the Registration screen is enabled without the SMS consent checkbox.
11. [CHK-MAUTH-070] Check that submitting the Registration form with Email selected as the preferred channel navigates the user to the Email address verification screen.
12. [CHK-MAUTH-071] Check that the Email address verification screen displays the title "Email address verification", the instruction "Enter the 4-digit code sent to your email address", and the user's email address.
13. [CHK-MAUTH-072] Check that entering the correct 4-digit code on the Email address verification screen and tapping Verify proceeds to the next onboarding step.

## Validation

1. [CHK-MAUTH-073] Check that the First name field on the Registration screen rejects non-alphabetical characters.
2. [CHK-MAUTH-074] Check that the First name field on the Registration screen rejects values shorter than 2 characters with the inline error "Field is required." or equivalent length error.
3. [CHK-MAUTH-075] Check that the First name field on the Registration screen rejects values longer than 100 characters.
4. [CHK-MAUTH-076] Check that the Last name field on the Registration screen rejects non-alphabetical characters.
5. [CHK-MAUTH-077] Check that the Last name field on the Registration screen enforces a 2 to 100 character length boundary.
6. [CHK-MAUTH-078] Check that the Phone number field on the Registration screen rejects values that do not match a valid phone format with the inline error "Invalid phone number."
7. [CHK-MAUTH-079] Check that the Email field on the Registration screen, when filled, rejects invalid email formats with the inline error "Invalid email address."
8. [CHK-MAUTH-080] Check that any empty required field on the Registration screen shows the inline error "Field is required." on blur.
9. [CHK-MAUTH-081] Check that the Continue button on the Registration screen remains disabled while any required field is invalid.
10. [CHK-MAUTH-082] Check that the Phone number field on the Login screen rejects empty input with the inline error "Enter a valid phone number."
11. [CHK-MAUTH-083] Check that the Phone number field on the Login screen rejects invalid phone formats and keeps the Continue button disabled.
12. [CHK-MAUTH-084] Check that the OTP input on the Phone number verification screen only accepts numeric digits.
13. [CHK-MAUTH-085] Check that the OTP input on the Phone number verification screen rejects fewer than 4 digits by keeping the Verify button disabled.
14. [CHK-MAUTH-086] Check that entering an invalid phone number on the Login screen turns the field outline and label red.

## Negative Flow

1. [CHK-MAUTH-087] Check that submitting the Registration form with a phone number already associated with an account displays a snackbar reading "An account with this phone number already exists. Please log in to continue."
2. [CHK-MAUTH-088] Check that submitting an incorrect OTP on the Phone number verification screen displays the inline error "Incorrect code" and allows retry.
3. [CHK-MAUTH-089] Check that exceeding the maximum OTP retry attempts on the Phone number verification screen temporarily blocks the user for 2 minutes and shows an informational message.
4. [CHK-MAUTH-090] Check that during the 2-minute block on the Phone number verification screen the Verify button remains disabled and Request a new code is suppressed.
5. [CHK-MAUTH-091] Check that submitting an unregistered phone number on the Login screen displays a bottom Material snackbar reading "This phone number is not registered yet. Create an account to get started."
6. [CHK-MAUTH-092] Check that requesting a new code on the Phone number verification screen is not possible while the countdown timer is still running.
7. [CHK-MAUTH-093] Check that the Continue button on the Registration screen stays disabled when SMS is the selected channel and the consent checkbox is unchecked even though all required fields are valid.
8. [CHK-MAUTH-094] Check that entering an incorrect code on the Email address verification screen and tapping Verify displays the inline error "Incorrect code." below the code boxes.

## Notifications and Alerts

1. [CHK-MAUTH-095] Check that tapping Continue on the Login screen with a valid number triggers an SMS containing the OTP delivered to that number.
2. [CHK-MAUTH-096] Check that tapping Continue on a valid Registration form triggers an SMS containing the OTP delivered to the registered number.
3. [CHK-MAUTH-097] Check that the OTP SMS arrives within a reasonable delivery window after the request.
4. [CHK-MAUTH-098] Check that requesting a new code on the Phone number verification screen invalidates the previously sent OTP and delivers a new one.
5. [CHK-MAUTH-099] Check that error feedback on the Login screen appears as a temporary Material snackbar at the bottom of the screen that auto-dismisses without user input.
6. [CHK-MAUTH-100] Check that an unexpected registration failure displays a snackbar reading "An unexpected error occurred. Please try sign up again."

## Data Saving and Persistence

1. [CHK-MAUTH-101] Check that a session created after successful OTP verification persists across app cold restarts within its configured lifetime.
2. [CHK-MAUTH-102] Check that values entered on the Registration screen are preserved when a server error occurs on submission.
3. [CHK-MAUTH-103] Check that the Phone number entered on the Login screen is preserved when navigating back from the Phone number verification screen.

## API and Backend Error Handling

1. [CHK-MAUTH-104] Check that when Registration submission fails due to a network error the Registration screen displays a generic error and allows retry.
2. [CHK-MAUTH-105] Check that when Login submission fails due to a network error the Login screen displays a generic error and allows retry.
3. [CHK-MAUTH-106] Check that when OTP verification fails due to network issues the Phone number verification screen displays a generic error and allows retry.
4. [CHK-MAUTH-107] Check that backend error responses on Registration, Login, and Phone number verification screens do not expose stack traces or internal details.
5. [CHK-MAUTH-108] Check that submission buttons (Continue, Verify) do not allow duplicate submissions while the request is in flight.
6. [CHK-MAUTH-109] Check that an unexpected login failure on the Login screen displays a bottom Material snackbar reading "An unexpected error occurred. Please try logging in again."

## Loading States

1. [CHK-MAUTH-110] Check that the Continue button on the Registration screen shows a loading state while the registration request is in flight.
2. [CHK-MAUTH-111] Check that the Continue button on the Login screen shows a loading state while the login request is in flight.
3. [CHK-MAUTH-112] Check that the Verify button on the Phone number verification screen shows a loading state while the OTP validation request is in flight.

## Offline Behavior

1. [CHK-MAUTH-113] Check that submitting the Login form while offline displays a generic network error on the Login screen and keeps form state.
2. [CHK-MAUTH-114] Check that submitting the Registration form while offline displays a generic network error on the Registration screen and keeps the entered values.
3. [CHK-MAUTH-115] Check that submitting OTP verification while offline displays a generic network error on the Phone number verification screen and allows retry once connectivity is restored.
4. [CHK-MAUTH-116] Check that toggling airplane mode off mid-flow on the Login or Phone number verification screen allows the user to retry the submission successfully.

## App Lifecycle

1. [CHK-MAUTH-117] Check that backgrounding the app on the Phone number verification screen and returning preserves the OTP input state and remaining resend timer.
2. [CHK-MAUTH-118] Check that backgrounding the app on the Registration screen and returning preserves all entered field values.
3. [CHK-MAUTH-119] Check that switching the device locale while the app is suspended and returning re-renders the Registration, Login, and Phone number verification screens in the new language on next launch.

## Accessibility

1. [CHK-MAUTH-120] Check that all input fields on the Registration and Login screens expose accessible labels matching their visible labels.
2. [CHK-MAUTH-121] Check that the OTP input boxes on the Phone number verification screen expose a combined accessible label (e.g., "OTP digit 1 of 4") to VoiceOver and TalkBack.
3. [CHK-MAUTH-122] Check that reading order on Registration, Login, and Phone number verification screens follows top-to-bottom logical flow.
4. [CHK-MAUTH-123] Check that text on the Registration, Login, and Phone number verification screens scales correctly with iOS Dynamic Type and Android font scale up to 200% without truncation.
5. [CHK-MAUTH-124] Check that color contrast on titles, body text, button labels, and inline errors meets WCAG AA on all auth screens.

## Security

1. [CHK-MAUTH-125] Check that all authentication network requests from the Registration, Login, and Phone number verification screens are sent over HTTPS only.
2. [CHK-MAUTH-126] Check that OTP codes, phone numbers, and session tokens are not written to device logs (adb logcat / Console.app).
3. [CHK-MAUTH-127] Check that the session token is stored in the iOS Keychain on iOS and EncryptedSharedPreferences (or equivalent secure storage) on Android.
4. [CHK-MAUTH-128] Check that the app does not store the OTP value in plain SharedPreferences, UserDefaults, or local files after verification.
5. [CHK-MAUTH-129] Check that the Registration, Login, and Phone number verification screens do not display sensitive data in the iOS app switcher snapshot (privacy blur or placeholder shown).
6. [CHK-MAUTH-130] Check that the OTP entered on the Phone number verification screen cannot be copied to the device clipboard from the input boxes.
7. [CHK-MAUTH-131] Check that pasting script-like payloads into the First name, Last name, or Email field on the Registration screen does not execute as code and is either rejected by validation or treated as plain text.
8. [CHK-MAUTH-132] Check that a previously issued OTP becomes invalid after a new code is requested on the Phone number verification screen.
9. [CHK-MAUTH-133] Check that an expired OTP cannot be used to complete verification on the Phone number verification screen.

## Regression Checks

1. [CHK-MAUTH-134] Check that an account registered through the Registration flow can subsequently log in via the Login screen using the same phone number.
2. [CHK-MAUTH-135] Check that successfully completing OTP verification on the Phone number verification screen creates a session that allows access to authenticated areas on next launch.

## Open Questions

1. Offline behavior for the Login and Registration screens is not specified — common rules mandate offline capability but Phone+OTP authentication intrinsically requires connectivity. Confirm expected user-visible behavior when offline.
2. Biometric authentication (Face ID / Touch ID / Android biometrics) is not addressed in the SRS — confirm whether biometrics for returning users are in scope.
3. Remember-me / persistent session behavior is not defined — the SRS does not specify session token lifetime, refresh strategy, or whether a returning user must re-verify OTP.
4. The exact resend countdown duration on the Phone number verification screen is not specified, blocking timer boundary testing.
5. The exact OTP expiration window (time after which a delivered code becomes invalid) is not specified.
6. The maximum OTP retry attempts before the 2-minute block on the Phone number verification screen is not specified.
7. The allowed country-code set for the "+1" selector on the Registration and Login screens is not specified — the example uses US "+1" but the supported set is unclear.
8. Email address verification resend and lockout rules (code length, resend cadence, max attempts before lockout) are not specified.
9. International phone number validation rules (allowed country codes, default region, formatting) are not specified — the example uses US "+1" but the supported set is unclear.
10. Maximum phone number length and allowed characters (spaces, dashes, parentheses formatting) on Registration and Login screens are not specified.
11. Behavior when the user receives a phone call or another full-screen interruption while on the Phone number verification screen (timer behavior, OTP input preservation) is not specified.
12. Behavior of the system back navigation on the Phone number verification screen when reached from Registration vs Login is not differentiated in the SRS.
13. Whether the Registration optional Email field is used for anything downstream (notifications, account recovery) is not specified, blocking validation of its purpose.
14. Dark mode parity for the Registration, Login, Phone number verification, and Email address verification screens is not specified.
15. RTL layout support (Arabic, Hebrew) is not specified for any auth screen.

**Coverage summary:** functional: 52 / UI: 30 / validation: 14 / permissions: 4 / edge cases: 35
