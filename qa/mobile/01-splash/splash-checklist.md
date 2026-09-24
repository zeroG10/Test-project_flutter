# QA Checklist: Splash screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-23 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Splash screen

1. [CHK-SPL-001] Check that the Splash Screen is displayed immediately after application launch on both iOS and Android devices.
2. [CHK-SPL-002] Check that the Splash Screen is displayed as a full-screen view with a white background covering the entire device screen.
3. [CHK-SPL-003] Check that the Concert Technologies logo is displayed centered both vertically and horizontally on the Splash Screen.
4. [CHK-SPL-004] Check that the logo on the Splash Screen is static and does not include any animation or loading indicator.
5. [CHK-SPL-005] Check that no text labels, buttons, links, or input fields are displayed on the Splash Screen.
6. [CHK-SPL-006] Check that the system status bar (time, network, battery) is visible while the Splash Screen is displayed.
7. [CHK-SPL-007] Check that no user interaction is possible on the Splash Screen, including taps, swipes, or system back actions.
8. [CHK-SPL-008] Check that the application validates an existing user session in the background while the Splash Screen is displayed.
9. [CHK-SPL-009] Check that the application verifies the authentication token status during the Splash Screen initialization phase.
10. [CHK-SPL-010] Check that essential application configuration and metadata are loaded while the Splash Screen is visible.
11. [CHK-SPL-011] Check that the application automatically navigates to the Login Screen after the Splash Screen if no valid user session exists.
12. [CHK-SPL-012] Check that the application automatically navigates to the Home / Jobs List or Calendar Screen after the Splash Screen if a valid user session exists.
13. [CHK-SPL-013] Check that the transition from the Splash Screen to the next screen occurs automatically without visible delays or technical artifacts.
14. [CHK-SPL-014] Check that the Splash Screen is displayed for the minimum required time needed to complete initialization without unnecessary prolongation.
15. [CHK-SPL-015] Check that the Splash Screen handles slow initialization gracefully without visual glitches, flickering, or layout shifts.
