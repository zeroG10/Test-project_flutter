# Supported Devices & Platforms

**Source of truth** for what the product officially supports. QA device coverage in [qa/shared/device-matrix/](../../qa/shared/device-matrix/) must align with this list.

> Update this file when product changes its support policy (e.g., drops an OS version, adds a new device tier).

## Last reviewed

- **Date:** YYYY-MM-DD
- **Owner:** [Product / Engineering lead]
- **Source:** [link to PRD / support policy doc]

---

## Web

### Browsers (desktop)

| Browser | Minimum version | Tier |
|---|---|---|
| Chrome | latest, latest-1 | P0 |
| Firefox | latest, latest-1 | P0 |
| Safari | latest, latest-1 | P0 |
| Edge | latest | P1 |

### Browsers (mobile web)

| Browser | OS | Tier |
|---|---|---|
| Mobile Safari | iOS 16+ | P0 |
| Chrome Mobile | Android 12+ | P0 |

### Screen sizes

| Breakpoint | Width | Tier |
|---|---|---|
| Mobile | 360–428 px | P0 |
| Tablet | 768–1024 px | P1 |
| Desktop | 1280–1920 px | P0 |
| Wide desktop | 1920+ px | P2 |

---

## Mobile — iOS

| OS version | Status | Notes |
|---|---|---|
| iOS 17 | Supported (current) | Primary target |
| iOS 16 | Supported | Latest-1 |
| iOS 15 | Best-effort | Critical bugs only |
| iOS 14 and below | Unsupported | — |

### Device classes

| Class | Example | Tier |
|---|---|---|
| Standard phone | iPhone 15, 14 | P0 |
| Small phone | iPhone SE (3rd gen), 13 mini | P1 |
| Large phone | iPhone 15 Pro Max | P1 |
| Tablet | iPad Pro 11" | P2 (only if iPad supported) |

---

## Mobile — Android

| OS version | API level | Status |
|---|---|---|
| Android 14 | 34 | Supported (current) |
| Android 13 | 33 | Supported |
| Android 12 | 31–32 | Supported |
| Android 11 | 30 | Best-effort |
| Android 10 and below | ≤29 | Unsupported |

### Device classes

| Class | Example | Tier |
|---|---|---|
| Reference (Pixel) | Pixel 7, Pixel 6a | P0 |
| Samsung flagship | Galaxy S23, S22 | P0 |
| Mid-range | Pixel 4a, Galaxy A54 | P1 |
| Low-end | RAM ≤ 3GB | P2 |
| Tablet | Galaxy Tab S9 | P2 (only if tablet supported) |

---

## Flutter (if applicable)

If the app ships as a Flutter build, support is defined by:
- The minimum Flutter SDK version in `pubspec.yaml`
- The above iOS/Android OS-version policies (Flutter inherits native OS support)

---

## Related

- [qa/shared/device-matrix/device-matrix.md](../../qa/shared/device-matrix/device-matrix.md) — QA coverage matrix (what we *actually test*, with priorities)
- [docs/platform-specs/ios/](ios/) — iOS HIG notes
- [docs/platform-specs/android/](android/) — Material / Play Store notes
