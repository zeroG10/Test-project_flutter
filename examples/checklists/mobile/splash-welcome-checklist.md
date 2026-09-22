# QA Checklist: Mobile Splash & Welcome

## Access and Permissions

1. [CHK-MSW-001] Check that the Splash screen is shown immediately on cold launch before any other screen.
2. [CHK-MSW-002] Check that the Splash screen does not accept any touch, tap, or gesture input while displayed.
3. [CHK-MSW-003] Check that the Welcome screen is shown only when no valid session token exists on device.
4. [CHK-MSW-004] Check that the Welcome screen is reachable without an authenticated session.
5. [CHK-MSW-005] Check that when a valid session token exists the app bypasses the Welcome screen and navigates directly to the Home / Jobs list screen.

## Navigation

1. [CHK-MSW-006] Check that the Splash screen automatically navigates to the Login screen when the user is not authenticated and initialization completes.
2. [CHK-MSW-007] Check that the Splash screen automatically navigates to the Home / Jobs list or Calendar screen when a valid session is detected.
3. [CHK-MSW-008] Check that tapping the Sign up button on the Welcome screen navigates to the Registration screen.
4. [CHK-MSW-009] Check that tapping the Login button on the Welcome screen navigates to the Login screen.
5. [CHK-MSW-010] Check that the Welcome screen does not display a system back button or navigation bar.
6. [CHK-MSW-011] Check that on Android the hardware back button on the Welcome screen exits the app (no further back stack).

## UI Layout

1. [CHK-MSW-012] Check that the Splash screen displays a full-screen maroon (#782A2A) background with the white/light Acme Field Services logo centered vertically and horizontally.
2. [CHK-MSW-013] Check that the Splash screen displays the system status bar (time, network, battery) and no text labels, buttons, or progress indicators.
3. [CHK-MSW-014] Check that the Welcome screen displays a minimal full-screen layout with a centered welcome message and two stacked CTAs at the bottom.
4. [CHK-MSW-015] Check that the Welcome screen displays the header text "Welcome to the Acme Field Services Field Services Application" and subtext "Create an account or log in to get started."
5. [CHK-MSW-016] Check that the Welcome screen displays the Sign up button as primary (filled) style.
6. [CHK-MSW-017] Check that the Welcome screen displays the Login button as a filled light-gray (secondary filled) style.
7. [CHK-MSW-018] Check that the Welcome screen respects the device safe area on iOS (notch, Dynamic Island, home indicator).
8. [CHK-MSW-019] Check that the Splash and Welcome screens render correctly on the smallest supported width (320px) without truncation or overflow.
9. [CHK-MSW-020] Check that the Splash and Welcome screens render correctly on the largest supported width (1440px / tablet) without overstretched controls.
10. [CHK-MSW-021] Check that the Welcome screen displays the Acme Field Services logo centered above the header text.
11. [CHK-MSW-022] Check that the Welcome screen uses a light off-white background with the Sign up and Login buttons stacked full-width and equal-width near the bottom.
12. [CHK-MSW-023] Check that the Welcome screen header text wraps across multiple lines and remains fully visible without truncation.

## Fields and Controls

1. [CHK-MSW-024] Check that the Welcome screen Sign up button label reads exactly "Sign up" and the Login button label reads exactly "Login".
2. [CHK-MSW-025] Check that the Welcome screen Sign up button uses a filled dark-red (maroon) fill with a light label.

## Positive Flow

1. [CHK-MSW-026] Check that on cold launch the Splash screen appears, performs session validation, token verification, and config loading, then transitions automatically.
2. [CHK-MSW-027] Check that on the Welcome screen, tapping Sign up reaches the Registration screen and the form is empty on first entry.

## API and Backend Error Handling

1. [CHK-MSW-028] Check that the Welcome screen displays a generic error and allows retry if navigation to Login or Sign up fails.

## Data Saving and Persistence

1. [CHK-MSW-029] Check that with a valid persisted session the Splash screen bypasses the Welcome and Login screens and lands on the Home / Jobs screen.

## Loading States

1. [CHK-MSW-030] Check that the Splash screen remains visible until the background initialization (session validation, token check, config load) completes.

## Offline Behavior

1. [CHK-MSW-031] Check that launching the app in airplane mode displays the Splash screen and gracefully transitions out without hanging indefinitely on session validation.

## App Lifecycle

1. [CHK-MSW-032] Check that backgrounding the app during the Splash screen and returning to foreground does not skip initialization steps or break navigation.
2. [CHK-MSW-033] Check that killing and relaunching the app while unauthenticated re-shows the Splash screen and then the Welcome screen.
3. [CHK-MSW-034] Check that killing and relaunching the app with a valid session re-shows the Splash screen and then the Home / Jobs screen.
4. [CHK-MSW-035] Check that switching the device locale while the app is suspended and returning re-renders the Welcome screen in the new language on next launch.

## Accessibility

1. [CHK-MSW-036] Check that on iOS VoiceOver announces the Sign up and Login buttons on the Welcome screen with descriptive labels.
2. [CHK-MSW-037] Check that on Android TalkBack announces the Sign up and Login buttons on the Welcome screen with descriptive labels.
3. [CHK-MSW-038] Check that reading order on the Welcome screen follows top-to-bottom logical flow.
4. [CHK-MSW-039] Check that text on the Welcome screen scales correctly with iOS Dynamic Type and Android font scale up to 200% without truncation.
5. [CHK-MSW-040] Check that the Acme Field Services logo on the Splash screen has an accessible label or is marked decorative consistently across iOS and Android.
6. [CHK-MSW-041] Check that the header text and subtext on the Welcome screen meet WCAG AA contrast against the light background.

## Security

1. [CHK-MSW-042] Check that all authentication network requests from the Splash and Welcome screens are sent over HTTPS only.

## Regression Checks

1. [CHK-MSW-043] Check that signing out (when available elsewhere in the app) returns the user to the Welcome screen on next launch.
2. [CHK-MSW-044] Check that updating the app to a new version preserves a valid session and lands the user directly on the Home / Jobs screen via the Splash screen.

## Open Questions

1. Splash screen dismissal model is partially defined: FR-SPL-02 lists background operations but does not specify a maximum splash duration, a timeout for stalled initialization, or behavior when token validation hangs. Testers cannot define expected behavior for stuck-splash scenarios.
2. Offline behavior for the Splash screen is not specified — common rules require offline support but the SRS does not state whether session validation should fall back to cached credentials or block at Splash when fully offline.
3. Dark mode parity for the Splash and Welcome screens is not specified.
4. RTL layout support (Arabic, Hebrew) is not specified for the Splash or Welcome screens.
5. Language selector on the Welcome screen is referenced in the task brief but the SRS does not describe it — confirm whether a language selector exists on the Welcome screen and which languages are supported.

**Coverage summary:** functional: 18 / UI: 16 / validation: 0 / permissions: 5 / edge cases: 5
