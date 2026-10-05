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

> **Concert Technologies, демо (рішення 2026-09-23; Android уточнено 2026-09-29; таблицю звужено до того, на чому
> справді тестували, — власник, 2026-10-05):** автоматизація ганялася на двох конфігураціях — **iPhone 17 / iOS 26.5**
> (симулятор) і **Pixel 7 / Android 16 (API 36)** (емулятор, Google APIs arm64, 4 ГБ пам'яті; апка зібрана під
> targetSdk 36). Інших пристроїв у тестуванні не було; шаблонні рядки прибрано, щоб матриця не обіцяла покриття,
> якого немає (фінальні звіти читають з неї пристрої P0).

## iOS

| Device | OS | Screen | Form factor | Priority | Where tested | Notes |
|---|---|---|---|---|---|---|
| **iPhone 17** | **26.5** | 6.3" | Standard | **P0** | Simulator | Ціль автоматизації: фінальний прогін 2026-09-28 |

## Android

| Device | OS | API | Screen | Form factor | Priority | Where tested | Notes |
|---|---|---|---|---|---|---|---|
| **Pixel 7** | **16** | **36** | 6.3" | Standard | **P0** | Emulator (AVD `Pixel_7_API_36`, Google APIs arm64, 4 GB) | Ціль автоматизації: фінальний прогін 2026-10-02 |

---

## Coverage gaps & risks

- **Реальних пристроїв не було** — лише симулятор iOS і емулятор Android; поведінку на реальних телефонах (камера,
  дзвінок, push від сервера, продуктивність) фінальні звіти не стверджують.
- **По одній версії ОС на платформу** (iOS 26.5, Android 16). SRS підтримує iOS 16+ і Android 12.1+
  ([supported-devices.md](../../../docs/platform-specs/supported-devices.md)) — старіші версії не перевірялись.
- **Android 15** (`Pixel_7_API_35`) — коротка перевірка сумісності була опцією «за бажанням власника» (2026-09-29);
  не проводилась.
- **Планшети** — поза скоупом.

## Related

- [docs/platform-specs/supported-devices.md](../../../docs/platform-specs/supported-devices.md) — product support policy
- [automation/mobile/.env](../../../automation/mobile/.env) — device currently used by automation
