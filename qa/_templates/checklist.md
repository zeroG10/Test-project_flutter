# Checklist — [Feature / area name]

> Naming: `<module>-checklist.md` inside the module folder (`<module>` = the slug registered in
> [qa/shared/feature-codes.md](../shared/feature-codes.md); the path is load-bearing — the Sheets
> sync derives `--target` from the platform folder and the feature code from the file stem):
> - `qa/web/<NN-module>/<module>-checklist.md` — browser-specific (e.g. `qa/web/01-authentication/authentication-checklist.md`)
> - `qa/mobile/<NN-module>/<module>-checklist.md` — mobile-specific (sub-target ios / android / cross-platform in the Platform row below)
> - `qa/shared/checklists/checklist-<topic>.md` — a11y, security, perf, i18n (e.g. `checklist-owasp-top10.md`)

## Metadata

| Field | Value |
|---|---|
| Feature | |
| Platform | web / iOS / Android / cross-platform / shared |
| Owner | @username |
| Last reviewed | YYYY-MM-DD |
| Related requirements | [docs/requirements/.../REQ-XXX.md] |

## Status vocabulary (when executing this checklist)

Statuses: **Passed / Failed / Skipped / Blocked / (empty)** — see "Checklist status
vocabulary" in CLAUDE.md. The short version:

- **Blocked** = could not run (stays owed, re-attempt next round) — comment mandatory.
- **Skipped** = deliberately will not run (a decision) — comment mandatory.
- **(empty)** = not-run / needs-human.
- A status is Passed only when an objective check decided it — name the oracle
  (Figma node / requirement ID / API contract) in the comment when it is not obvious.
- Never upgrade Blocked/Skipped/empty to Passed because the round ended.
- "Partial" is computed for sections, never entered as an item status.

## Functional

- [ ] Happy path works end-to-end
- [ ] All required fields validated
- [ ] Optional fields work and are truly optional
- [ ] Error messages are clear and actionable
- [ ] Success states are obvious to the user

## Edge cases

- [ ] Empty input
- [ ] Maximum length / payload
- [ ] Special characters / emoji / RTL text
- [ ] Duplicate submissions / double-tap
- [ ] Slow / no network

## UI / UX

- [ ] Matches Figma designs
- [ ] Responsive at all supported viewports (web) / device classes (mobile)
- [ ] Dark mode (if supported)
- [ ] Loading states present
- [ ] Empty states present
- [ ] Error states present

## Accessibility

- [ ] Keyboard navigation (web) / TalkBack / VoiceOver labels (mobile)
- [ ] Sufficient color contrast (WCAG AA)
- [ ] Focus indicators visible
- [ ] Form labels associated with inputs
- [ ] Dynamic Type / font scaling supported (mobile)

## Security

- [ ] No sensitive data in logs
- [ ] Auth required where expected
- [ ] Session timeout handled
- [ ] Input sanitized (XSS, SQLi where applicable)

## Performance

- [ ] Initial load < target (specify)
- [ ] No jank during interactions
- [ ] No memory leaks on repeated use

## Analytics

- [ ] Events fire correctly
- [ ] No duplicate events
- [ ] Properties match spec
