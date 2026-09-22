# Platform Specs

Mobile-specific platform guidelines, conventions, and constraints. Use these as input when writing test cases and checklists.

## Structure

- `ios/` — Apple Human Interface Guidelines notes, App Store review constraints, iOS-specific behaviors (permissions, push, background modes).
- `android/` — Material Design notes, Play Store policies, Android-specific behaviors (back button, intents, fragmentation, runtime permissions).
- `supported-devices.md` — the official list of devices/OS versions the product supports (source of truth for [qa/shared/device-matrix/](../../qa/shared/device-matrix/)).

## When to add content here

- New platform OS version is released → update version-support notes
- Product decides to drop support for an OS version
- Platform-specific UX rule that affects test expectations (e.g., iOS alert auto-dismissal, Android back-button behavior)
