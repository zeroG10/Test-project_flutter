# iOS Platform Notes

iOS-specific UX rules, constraints, and platform behaviors that affect testing.

## Sources

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

## Topics to document here

- **Permissions** — when prompts appear, how denial affects flows (camera, location, notifications, contacts, photos, microphone, tracking)
- **Push notifications** — APNs, foreground vs background behavior
- **Deep links / Universal Links** — handling, association file
- **Sign in with Apple** — required if app offers other social login
- **In-app purchases** — sandbox vs production, receipt validation
- **Background modes** — what's allowed, suspended/terminated states
- **Safe areas & notches** — layout expectations
- **Keyboard behavior** — dismissal, autocorrect, types
- **Dark mode** — required support, contrast checks
- **Accessibility** — VoiceOver, Dynamic Type
- **App Store metadata** — screenshots, age rating, privacy nutrition label

Add one `.md` per topic as you discover platform-specific test expectations.
