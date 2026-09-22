# Mobile-Specific Prompts

These prompts mirror the general prompts in [prompts/](..) but are tuned for mobile testing concerns (permissions, gestures, lifecycle, deep links, device matrix, Appium automation hints).

| Prompt | Equivalent of | Purpose |
|---|---|---|
| `01-analyze-mobile-srs-and-design.md` | `prompts/01-...` | Mobile-focused analysis (platforms, constraints) |
| `02-generate-mobile-checklist.md` | `prompts/02-...` | Platform-aware checklist (iOS / Android sections) |
| `03-generate-mobile-test-cases.md` | `prompts/03-...` | Test cases with gestures, locator hints, lifecycle |

## When to use which set

- **Web feature** → use root `prompts/01-..06-...md`
- **Mobile feature (iOS/Android/Flutter)** → use `prompts/mobile/01-analyze-mobile-srs-and-design.md`, `02-generate-mobile-checklist.md`, `03-generate-mobile-test-cases.md`
- **API** → use root prompts but specify "API tests in `automation/api/`" in the request

Prompts 04 (traceability), 05 (coverage review), 06 (automation candidates) and 07 (automation from test cases) at the root are platform-aware — pass them mobile inputs, name the mobile stack (Appium + Python + pytest) in the request, and they write into the module folder under `qa/mobile/<NN-module>/`.
