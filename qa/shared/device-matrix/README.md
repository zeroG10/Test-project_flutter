# Device Matrix

Mobile device coverage matrix — what we test on, and at what priority.

## Format

Maintain one row per device/OS combination. Suggested columns:

| Platform | Device | OS Version | Form Factor | Priority | Notes |
|---|---|---|---|---|---|
| iOS | iPhone 15 | 17.4 | Standard | P0 | Primary target |
| iOS | iPhone SE (3rd gen) | 17.4 | Small | P1 | Smallest supported screen |
| iOS | iPad Pro 11" | 17.4 | Tablet | P2 | If app supports iPad |
| Android | Pixel 7 | 14 | Standard | P0 | Reference device |
| Android | Samsung Galaxy S23 | 14 | Standard | P0 | OneUI quirks |
| Android | Pixel 4a | 13 | Small | P1 | Lowest supported OS |

## Priority guidance

- **P0** — must pass before every release (full regression).
- **P1** — smoke + critical flows per release.
- **P2** — periodic / ad-hoc coverage.

## Related

- [docs/platform-specs/](../../../docs/platform-specs/) — platform guidelines (iOS HIG, Material Design)
- [automation/mobile/.env](../../../automation/mobile/.env) — actual device used by automation
