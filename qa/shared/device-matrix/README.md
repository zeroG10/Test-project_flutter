# Device Matrix

Mobile device coverage matrix — what we test on, and at what priority.

## Format

Maintain one row per device/OS combination. Suggested columns:

| Platform | Device | OS Version | Form Factor | Priority | Notes |
|---|---|---|---|---|---|
| iOS | iPhone 17 (simulator) | 26.5 | Standard | P0 | This project's automation target |
| Android | Pixel 7 (emulator) | 16 (API 36) | Standard | P0 | This project's automation target |

List only devices the runs actually use: the final reports read the P0 rows of
[device-matrix.md](device-matrix.md) for their exit criterion "P0 devices of the device matrix covered".

## Priority guidance

- **P0** — must pass before every release (full regression).
- **P1** — smoke + critical flows per release.
- **P2** — periodic / ad-hoc coverage.

## Related

- [docs/platform-specs/](../../../docs/platform-specs/) — platform guidelines (iOS HIG, Material Design)
- [automation/mobile/.env](../../../automation/mobile/.env) — actual device used by automation
