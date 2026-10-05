# BUG-<CODE>-NNN — [Short title]

> `<CODE>` = the module's feature code from [qa/shared/feature-codes.md](../shared/feature-codes.md),
> `NNN` = zero-padded, unique within the module, never reused. File location and name:
> `qa/mobile/<NN-module>/bugs/BUG-<CODE>-NNN.md` (e.g. `qa/mobile/01-authentication/bugs/BUG-AUTH-001.md`).

> **Process:** whether it is a defect at all, the severity walk, the wording and the filing
> go are governed by [prompts/08-file-bug.md](../../prompts/08-file-bug.md). This file is the
> format only. Filing to a tracker is owner-confirmed (doctrine rule 5).

## Summary

One sentence describing the problem.

> **Wording by layer.** App bugs are written from the USER's perspective: preconditions =
> install build + log in; steps = the UI journey (navigate / tap / swipe); actual/expected
> is what the user sees. Backend/API bugs are written from the API's perspective: exact
> `METHOD /endpoint` calls, actual/expected are response fields. Same defect, two
> languages — write for the dev who will fix it.

## Layer

- [ ] App (UI) — user-perspective wording
- [ ] Backend / API — request/response wording
- [ ] Unclear (state the evidence for each side)

## Severity / Priority

Walk the tree top-down, first match wins — and record which branch fired:

1. Data loss/corruption (incl. user data wiped on upgrade), security breach (auth bypass,
   IDOR, PII leak), money charged wrongly, crash on a core path, or app unusable for all
   users? → **S1 (blocker / crash)**
2. Core feature broken for a significant user group with NO workaround, or a paid
   feature not delivering what was paid for? → **S2 (major)**
3. Feature broken but a workaround exists, or non-core feature broken, or noticeable
   quality degradation at scale? → **S3 (minor)**
4. Cosmetic, minor UX friction, rare edge case with an easy workaround? → **S4 (cosmetic)**

- **Severity:** S1 / S2 / S3 / S4 — **branch fired:** #
- **Priority:** P0 / P1 / P2 / P3 — a business decision made by the owner. QA (or an AI
  agent) may propose one, explicitly marked as a proposal. Severity is objective;
  priority is not. The two never merge.

## Environment

| Field | Value |
|---|---|
| Platform | iOS / Android / Flutter (on iOS or Android) |
| OS version | iOS 17.4 / Android 14 (API 34) |
| Device | iPhone 17 / Pixel 7 |
| Form factor | phone / tablet / foldable |
| Device type | real device / simulator / emulator |
| App version | 2.4.1 (build 1234) |
| Build type | debug / release / TestFlight / internal track |
| Install method | App Store / TestFlight / Play Internal / sideload (.apk/.ipa) |
| Network | Wi-Fi / 4G / 5G / airplane mode / poor connection |
| Locale | en-US / uk-UA |
| Orientation | portrait / landscape |
| User role | guest / authenticated / admin |
| Feature flags | flag-name=on |
| Permissions state | camera=granted, location=denied, notifications=not-determined |

## Steps to reproduce

1.
2.
3.

## Actual result

What actually happens — short prose, evidence link appended after ` // `.

## Expected result

What should happen, derived from the quoted source (AC / rule / contract) and
phrased as the rule, not as this single case. Quote the source in Related.

## Frequency

- [ ] Always
- [ ] Intermittent — **measured rate mandatory** (e.g. "3/10 attempts"), never "sometimes"
- [ ] First launch only
- [ ] After cold/warm restart
- [ ] One-time

> Could not reproduce after a stated number of attempts → record it as an observation in
> the exploratory session log or the module's `<module>-traceability.md` run notes, not as a bug.

## Crash? ANR?

- [ ] App crashed (attach crash log)
- [ ] App froze / ANR (Android)
- [ ] App backgrounded unexpectedly
- [ ] No crash

## Evidence

- Screenshot: ![screenshot](path/to/screenshot.png)
- Screen recording: [link]
- Crash log:
```
<paste from Xcode Devices or `adb logcat`>
```
- adb logcat (Android, last 100 lines):
```
adb logcat -d | tail -100
```
- iOS device logs (Console.app filtered by bundle id):
```
<paste relevant>
```
- Network capture: [Charles / Proxyman .chlsj or har]
- Appium server log (if from automation): `automation/mobile/...`

## Workaround

If any (e.g. "force-quit + reopen", "toggle airplane mode").

## Regression info

- Last known good version:
- First broken version:
- Related recent changes:

## Related

- Story / acceptance criterion: `<story id> / AC-<n>` (docs/srs/…), quoted verbatim
- Requirement / business rule: [docs/requirements/... or docs/business-rules/...]
- Known gap (if this defect was predicted): `<question id>` in `../<module>-questions.md`
- Test case: `TC-<CODE>-NNN` in `../<module>-test-cases.md`; checklist item `CHK-<CODE>-NNN` in `../<module>-checklist.md`
- Invariant violated: INV-N ([qa/shared/oracles/invariants.md](../shared/oracles/invariants.md)) — if none fits, that is a missing invariant: add it
- Crashlytics / Sentry issue ID:
- Linear / Jira: PROJ-123

> **When this bug is verified fixed:** re-verify with the ORIGINAL repro steps on the
> fixed build, then (1) add/confirm the invariant it violated in
> [invariants.md](../shared/oracles/invariants.md), and (2) create a regression test case /
> spec that traces back to this BUG ID. A fixed bug with no regression check will return.
