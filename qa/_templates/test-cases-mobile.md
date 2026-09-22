# Test cases — [Feature name] (mobile)

> One file per feature: `qa/mobile/<NN-module>/<module>-test-cases.md`, next to the checklist
> (e.g. `qa/mobile/01-authentication/authentication-test-cases.md`). Format, step vocabulary,
> alias and oracle rules: [test-case-format.md](test-case-format.md). TCs exist only for automation
> candidates (prompt 06 selection) and high-risk manual checks. Feature code from
> [qa/shared/feature-codes.md](../shared/feature-codes.md). `click` means tap;
> `swipe` takes a direction in Data; `expect-url` does not apply — use `expect-visible <screen>.root`.

| Field | Value |
|---|---|
| Feature | |
| Platform | android / ios / flutter / cross-platform |
| Source checklist | `qa/mobile/<NN-module>/<module>-checklist.md` |
| Selection | `_bmad-output/test-artifacts/test-design/mobile/<feature>-automation-plan.md` |
| Min OS | iOS <16> / Android <13> — see [supported-devices.md](../../docs/platform-specs/supported-devices.md) |
| Devices | P0 row of the [device matrix](../shared/device-matrix/device-matrix.md) |
| Owner | @username |
| Last updated | YYYY-MM-DD |

Execution statuses when running these TCs: **Passed / Failed / Skipped / Blocked / (empty)**
(CLAUDE.md "Checklist status vocabulary"). Blocked and Skipped need a comment; nothing is
upgraded to Passed because the round ended. Record results per device in the team Sheet (manual)
or `<module>-traceability.md` (automated, via `trace_results.py`), not here.

---

## TC-<FEATURE>-001 — [Action-oriented title: what is proven]

| Field | Value |
|---|---|
| ID | TC-<FEATURE>-001 |
| Title | [same as heading] |
| Source CHK IDs | CHK-<FEATURE>-NNN, CHK-<FEATURE>-NNN |
| Platforms | android, ios / android / ios / flutter |
| Priority | P0 / P1 / P2 / P3 |
| Automation | candidate / automated(android) / automated(ios) / automated(flutter) / manual |
| Device / OS | P0 device from the matrix, e.g. Pixel 7 · Android 14 / iPhone 15 · iOS 17; `any` if not device-sensitive |
| App state | cold start / warm start / resumed from background / after OS kill — and install state (fresh install / upgraded from <version>) |
| Permissions | e.g. camera: not yet requested / granted / denied-once / denied-permanently; notifications: granted |
| Network | online Wi-Fi / cellular / offline (airplane mode) / throttled (Network Link Conditioner, `adb shell tc`) |
| Preconditions | `{{user.email}}` exists and is active with role `<role>`; auth by state (API token injected / deep link), logged in as `{{user.email}}`; `{{order.id}}` exists in status `Draft` |
| Oracle | `spec — SRS §x.y` / `spec — figma:<node-id>` / `invariant — INV-n` / `human` — see [qa/shared/oracles/README.md](../shared/oracles/README.md) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | <screen> | — | screen shown (deep link or navigation from home) |
| 2 | expect-visible | <screen>.root | — | visible |
| 3 | fill | <screen>.<field> | {{fixture.value}} | keyboard type matches field |
| 4 | click | <screen>.<button> | — | — |
| 5 | wait-for | <screen>.<spinner> | — | hidden |
| 6 | swipe | <screen>.<list> | up | — |
| 7 | scroll-to | <screen>.row[{{order.id}}] | — | — |
| 8 | expect-text | <screen>.<element> | — | exact text or {{fixture}} |
| 9 | back | — | — | previous screen; state preserved |

**Platform-specific expectations:** iOS — …; Android — … (only where observable behaviour differs; otherwise omit)
**Postconditions / cleanup:** [what state is left; permissions/app data to reset (`scripts/reset_simulator.sh`, `adb pm clear`); API cleanup — or "nothing to clean"]
**Notes:** [lifecycle / rotation / a11y (VoiceOver, TalkBack) note, known issue BUG-<FEATURE>-NNN (in `bugs/`), why manual if `manual`]

---

## Aliases used

| Alias | Screen | android map | ios map |
|---|---|---|---|
| <screen>.root | <screen> | yes / MISSING | yes / MISSING |
| <screen>.<field> | <screen> | yes / MISSING | yes / MISSING |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{user.email}} | `automation/mobile/fixtures/test_data.py` | role `<role>`, read-only account |

## Open questions

- [Unclear expectation — what is missing — which TC it blocks] or `None identified.`
