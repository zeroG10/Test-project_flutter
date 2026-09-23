# QA Device Coverage Matrix

What we **actually test on**, with priorities. Derived from [docs/platform-specs/supported-devices.md](../../../docs/platform-specs/supported-devices.md) but narrower — we test a representative subset, not every supported device.

> Review this matrix every release. Add/remove rows as device fleet changes.

## Priority legend

| Tier | Meaning | When tested |
|---|---|---|
| **P0** | Must-pass before every release | Full regression + smoke |
| **P1** | Critical paths | Smoke + targeted regression |
| **P2** | Periodic / ad-hoc | Monthly or feature-driven |
| **OUT** | Explicitly unsupported (below min OS / not in policy) | Never; bugs reported here are closed as out-of-scope |

---

> **Concert Technologies, демо (рішення 2026-09-23):** автоматизація ганяється на двох
> конфігураціях — **iPhone 17 / iOS 26.5** (симулятор) і **Pixel 7 / API 35** (емулятор).
> Решта рядків нижче — шаблонні орієнтири, у демо не проганяються. Планшети поза скоупом.

## iOS

| Device | OS | Screen | Form factor | Priority | Where tested | Notes |
|---|---|---|---|---|---|---|
| **iPhone 17** | **26.5** | 6.3" | Standard | **P0** | Simulator | **Ціль автоматизації (демо)** |
| iPhone 15 | 17.4 | 6.1" | Standard | P1 | Simulator + 1 real | Шаблонний орієнтир |
| iPhone SE (3rd gen) | 17.4 | 4.7" | Small | P1 | Simulator | Smallest supported screen |
| iPhone 15 Pro Max | 17.4 | 6.7" | Large | P1 | Simulator | Dynamic Island, large layouts |
| iPhone 13 | 16.7 | 6.1" | Standard | P1 | Simulator | Latest-1 OS |
| iPad Pro 11" | 17.4 | 11" | Tablet | P2 | Simulator | Only if iPad is supported |

## Android

| Device | OS | API | Screen | Form factor | Priority | Where tested | Notes |
|---|---|---|---|---|---|---|---|
| **Pixel 7** | **15** | **35** | 6.3" | Standard | **P0** | Emulator | **Ціль автоматизації (демо)** |
| Samsung Galaxy S23 | 14 | 34 | 6.1" | Standard | P0 | Real device | OneUI quirks |
| Pixel 6a | 13 | 33 | 6.1" | Mid-range | P1 | Emulator | Mid-range perf |
| Pixel 4a | 13 | 33 | 5.8" | Small + older | P1 | Emulator | Lowest supported screen + OS |
| Samsung A54 | 13 | 33 | 6.4" | Mid-range | P2 | Real device (when available) | Common in target market |

## Web (browsers)

| Browser | Version | OS | Priority | Notes |
|---|---|---|---|---|
| Chrome | latest | macOS / Windows | P0 | Primary |
| Firefox | latest | macOS / Windows | P0 | |
| Safari | latest | macOS | P0 | WebKit engine |
| Edge | latest | Windows | P1 | Chromium-based |
| Mobile Safari | latest | iOS 17 | P0 | Mobile web |
| Chrome Mobile | latest | Android 14 | P0 | Mobile web |

---

## Coverage gaps & risks

Document known gaps here. Examples:
- No real-device coverage for low-end Android (RAM ≤ 3GB) — mitigated by emulator with reduced memory
- iOS beta versions not in matrix — covered ad-hoc when Apple releases public beta

## Related

- [docs/platform-specs/supported-devices.md](../../../docs/platform-specs/supported-devices.md) — product support policy
- [automation/mobile/.env](../../../automation/mobile/.env) — device currently used by automation
