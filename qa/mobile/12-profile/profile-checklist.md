# QA Checklist: Profile screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-27 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## General layout & navigation

1. [CHK-PRF-001] Check that the Profile screen is opened when the user taps the Profile tab in the bottom navigation bar.
2. [CHK-PRF-002] Check that the Profile tab is visually highlighted as active when the Profile screen is displayed.
3. [CHK-PRF-003] Check that the Profile screen contains a user information card, settings section, footer section, and bottom navigation bar.
4. [CHK-PRF-004] Check that all Profile screen elements are displayed correctly after app relaunch.

## User Information Card

1. [CHK-PRF-005] Check that the user’s first name and last name are displayed correctly in the user information card.
2. [CHK-PRF-006] Check that the phone number is displayed in read-only mode in the user information card.
3. [CHK-PRF-007] Check that the email address is displayed correctly in the user information card.
4. [CHK-PRF-008] Check that the Edit button is visible and enabled in the user information card.

## Edit Profile

1. [CHK-PRF-009] Check that tapping the Edit button navigates the user to the Edit Profile screen.
2. [CHK-PRF-010] Check that the Edit Profile screen header contains a Back button and a Save button.
3. [CHK-PRF-011] Check that First name, Last name, Phone number, and Email fields are pre-filled with current user data.
4. [CHK-PRF-012] Check that the Phone number field is disabled and not editable on the Edit Profile screen.
5. [CHK-PRF-013] Check that the Save button is disabled when the First name field is empty.
6. [CHK-PRF-014] Check that the Save button is disabled when the Last name field is empty.
7. [CHK-PRF-015] Check that an error is shown when an invalid email format is entered and the Save button is tapped.
8. [CHK-PRF-016] Check that the Save button is enabled when all required fields contain valid values.
9. [CHK-PRF-017] Check that tapping Save updates the user profile data and returns the user to the Profile screen.
10. [CHK-PRF-018] Check that updated profile data is immediately reflected on the Profile screen after saving.
11. [CHK-PRF-019] Check that tapping the Back button returns the user to the Profile screen without saving changes.
12. [CHK-PRF-020] Check that unsaved changes are discarded when the user navigates back from Edit Profile.

## Dark Mode

1. [CHK-PRF-021] Check that toggling the Dark mode switch changes the app theme immediately.
2. [CHK-PRF-022] Check that the Dark mode toggle state is preserved after app restart.
3. [CHK-PRF-023] Check that all Profile screen elements adapt correctly to Dark mode.

## Privacy Policy

1. [CHK-PRF-024] Check that tapping Privacy Policy opens the policy document in a web view or external browser.
2. [CHK-PRF-025] Check that the user can return to the app after viewing the Privacy Policy.

## Log Out Flow

1. [CHK-PRF-026] Check that tapping Log out opens the logout confirmation dialog.
2. [CHK-PRF-027] Check that tapping Cancel closes the logout dialog without logging the user out.
3. [CHK-PRF-028] Check that tapping Log out clears the user session and navigates to the Welcome screen.
4. [CHK-PRF-029] Check that the user cannot access authenticated screens after logging out.
5. [CHK-PRF-030] Check that logout clears local user data even when the device is offline.

## Delete Account Flow

1. [CHK-PRF-031] Check that tapping Delete account opens the account deletion confirmation pop-up.
2. [CHK-PRF-032] Check that account deletion is blocked until the user types the required “Delete” confirmation text.
3. [CHK-PRF-033] Check that tapping Cancel closes the delete account dialog without any changes.
4. [CHK-PRF-034] Check that confirming account deletion removes the user account and logs the user out.
5. [CHK-PRF-035] Check that deleted accounts cannot log in again using the same credentials.
