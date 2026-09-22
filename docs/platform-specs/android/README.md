# Android Platform Notes

Android-specific UX rules, constraints, and platform behaviors that affect testing.

## Sources

- [Material Design](https://m3.material.io/)
- [Android Developer guidelines](https://developer.android.com/design)
- [Google Play policies](https://support.google.com/googleplay/android-developer/topic/9858052)

## Topics to document here

- **Back button** — system gesture, behavior expectations on each screen
- **Runtime permissions** — Android 6+ permission model, denial → "Don't ask again"
- **Notifications** — channels, importance levels, Android 13+ POST_NOTIFICATIONS
- **Deep links / App Links** — intent filters, autoVerify, App Links assetlinks.json
- **Intents** — share sheet, file picker, custom URI schemes
- **Background work** — Doze mode, App Standby, WorkManager constraints
- **Fragmentation** — OEM customizations (Samsung OneUI, Xiaomi MIUI, etc.)
- **Foldables & large screens** — adaptive layouts, configuration changes
- **Dark theme** — system-wide vs in-app toggle
- **Accessibility** — TalkBack, font scaling
- **Play Store metadata** — listing, content rating, data safety form
- **APK vs AAB** — release format (Play Store requires AAB)

Add one `.md` per topic as you discover platform-specific test expectations.
