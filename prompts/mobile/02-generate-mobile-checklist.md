# Prompt M02 — Generate Mobile Checklist

## Purpose
Generate a platform-aware mobile testing checklist that covers functional, UX, permissions, lifecycle, network, accessibility, and device-class concerns.

## When to Use
- After mobile SRS/design analysis (M01)
- Before writing detailed test cases
- For exploratory test charters

## Input Required
- Analysis from `_bmad-output/test-artifacts/test-design/mobile/{feature}-analysis.md`
- `docs/platform-specs/{ios,android}/` notes
- `qa/shared/device-matrix/device-matrix.md`
- Template: `qa/_templates/checklist.md`

---

## Project overrides (read first)

These rules override the prompt body below for this project:

1. **No automation markers on checklist items.** Candidate selection is a separate step: `prompts/06-select-automation-candidates.md`.
2. **Use available sources for the selected platform.** For UI, read the relevant
   web/mobile Figma map when design is available; pull structure and images via the
   project-local Figma MCP. For API, use the API contract and confirmed business rules;
   no Figma is needed. Apply `qa/shared/oracles/README.md` (recorded owner overrides,
   then defaults by layer). With only a running product, record observations and owner
   confirmations or an explicitly adopted baseline; unconfirmed expectations are Open
   Questions. Missing design blocks only checks that need that design.
3. **Every checklist item MUST start with a stable ID** in the format `[CHK-<FEATURE>-<NNN>]`:
   - `<FEATURE>` is the feature code for the slug. Codes live in [qa/shared/feature-codes.md](../../qa/shared/feature-codes.md) — look the slug up there and **create the row if it is missing** (2–5 uppercase letters, unique per platform, never reused or renamed). Fallback when no row exists yet: first 4 letters of the slug, uppercase (then register it). Web and mobile may use the same code for the same feature (separate Sheets, see rule 4).
   - `<NNN>` is a zero-padded 3-digit sequence number, monotonically increasing across the whole file (NOT restarted per section).
   - **When regenerating an existing checklist**: read the prior file first and PRESERVE existing IDs. Only assign new IDs to genuinely new checks, using numbers higher than the current max.
   - Use numbered list items (`1. [CHK-AUTH-001] Check that ...`) so the sync tool can parse them — do not rely solely on `- [ ]` boxes for items that need to be synced.
4. **Mobile and Web live in SEPARATE Google Sheets** (configured via `MOBILE_*` vs `WEB_*` in `automation/tools/.env` — different `SHEET_ID`s, not just different tabs). Feature codes can therefore **overlap freely** between web and mobile: `CHK-AUTH-001` in the mobile sheet is independent from `CHK-AUTH-001` in the web sheet. Do not try to disambiguate — use the same codes as web for the same feature.
5. **Sync command** for mobile checklists:
   ```
   uv run python sync_checklist_to_sheets.py --target mobile <path-to-md>
   ```

## Prompt

```
You are a Senior Mobile QA Engineer. Generate a comprehensive mobile testing checklist for the feature described in the analysis below.

Input: [paste analysis from _bmad-output/test-artifacts/test-design/mobile/{feature}-analysis.md]

Target platforms: [iOS / Android / Flutter / all]
Min OS versions: [from supported-devices.md]
Target device classes: [P0 devices from device matrix]

Produce a Markdown checklist organized by category. Use `- [ ]` items. Group by the sections below. Skip a section only if truly N/A and state why.

---

## Functional
- Happy path, alternative paths, edge cases.
- Form validation (all fields, error messages clear).
- Save / cancel / back navigation.
- Multi-account / multi-tenant if applicable.

## Permissions
For each permission the feature touches (camera, location, notifications, contacts, photos, microphone, tracking — iOS; same + storage on older Android):
- [ ] First-time prompt appears at the right moment
- [ ] Allow → feature works
- [ ] Deny once → graceful fallback / explainer
- [ ] Deny + "Don't ask again" (Android) / Don't Allow (iOS) → user can re-grant via Settings deep link
- [ ] Background → foreground after permission change in Settings → app reflects new state

## UI / Visual
- Matches Figma for [iOS / Android] designs.
- Safe-area / notch / Dynamic Island (iOS).
- Status bar style consistent.
- System font scaling (Dynamic Type / Android font scale): up to 200% without breaking layout.
- Dark mode parity.
- Splash / launch screen.

## Gestures & navigation
- Tap, long-press, swipe (where applicable).
- iOS swipe-back from left edge.
- Android system back button.
- Android 14+ predictive back gesture.
- Pull-to-refresh.
- Modal dismissal (swipe down on iOS sheets).

## Lifecycle & state
- Cold start.
- Warm start (from background).
- Killed by OS (memory pressure) → resume.
- App update (state preserved? migration ok?).
- Reinstall (fresh state).
- Locale change while app is running (force-stop expected behavior).

## Network
- Online (Wi-Fi, cellular).
- Offline → graceful error, retry, queueing if applicable.
- Slow / flaky network (use Network Link Conditioner / `adb shell tc`).
- Switching Wi-Fi ↔ cellular mid-request.
- Airplane mode toggled during operation.
- Token expiry → silent refresh or re-auth prompt.

## Notifications (if feature triggers/reacts)
- Foreground (banner vs in-app).
- Background.
- App killed.
- Notification tap → deep link lands on correct screen.
- Permission flow (Android 13+ requires POST_NOTIFICATIONS).

## Deep links / Universal Links / App Links
- Cold-start from link.
- Warm-start from link.
- Authenticated vs unauthenticated entry.
- Invalid / expired link → graceful error.

## Accessibility
- VoiceOver (iOS) / TalkBack (Android) labels on all interactive elements.
- Reading order is logical.
- Sufficient contrast (WCAG AA).
- Focus order with external keyboard.
- Reduced motion respected (iOS) / animations off (Android).

## Performance
- Cold start < target.
- No jank (60fps where animations exist).
- Memory does not grow unbounded with repeated use.
- Battery: no excessive background drain.

## Security
- No sensitive data in logs (`adb logcat`, Console.app).
- Sensitive data not in screenshots (iOS app switcher snapshot blur if needed).
- Tokens stored in Keychain / EncryptedSharedPreferences only.
- No data in plain SharedPreferences / UserDefaults.

## Localization & RTL
- All strings localized.
- RTL layout flipped where supported (Arabic, Hebrew).
- Date / time / number / currency formats per locale.

## Device-class coverage
Run the checklist on at least:
- [ ] P0 iOS device (e.g., iPhone 15, iOS 17)
- [ ] P0 Android device (e.g., Pixel 7, Android 14)
- [ ] Smallest supported screen
- [ ] Largest supported screen
- [ ] Lowest supported OS version

## Crash / ANR
- Run feature 10× — no crashes.
- Stress: rapid taps / pull-to-refresh spam — no ANR.
- Crashlytics / Sentry shows no new issues after smoke run.

---

End with a "Risks not covered by this checklist" section noting anything that requires deeper investigation or a dedicated test plan.
```

## Output Location
Save as `qa/mobile/<NN-module>/<module>-checklist.md` (`<NN-module>` = module folder, `NN` = order in the SRS, `<module>` = the feature slug registered in `qa/shared/feature-codes.md`; e.g. `qa/mobile/01-authentication/authentication-checklist.md`). State the sub-target the checklist is written for (ios / android / flutter / cross-platform) in the Platform metadata row, not in the path. Naming `<module>-checklist.md` matches the web convention and the `qa-checklist` skill.
