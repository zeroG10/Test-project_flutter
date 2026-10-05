# reports/mobile — the final test completion reports of the mobile regression

What the project hands over at the end of the regression (owner, 2026-10-05). Every file here is **generated** from the
repository's records — the runs, the checklists, the bug reports, the reasons files — so edit the generators, never
these files. This is the **shared copy**: the test account's email, phone and name are hidden in the text and
pixelated on the screens, and API bodies, page sources and screen videos are left out (they stay in the gitignored
local copy, `automation/mobile/reports/`).

`reports/` holds one folder per platform (`reports/web/` belongs to the web reports); this is the mobile one.

Three slices, each with an internal and a client report (ISTQB / ISO/IEC/IEEE 29119-3 *test completion report*):

| Slice | Run it describes | Internal (team) | Client | PDF |
|---|---|---|---|---|
| iOS | `stable-3`, 2026-09-28, harness 7015c46 · iPhone 17 simulator, iOS 26.5 | `ios/internal/index.html` | `ios/client/test-completion-report.html` | `ios/pdf/` |
| Android | `2026-10-02-final-u3`, harness 9101eb7 · Pixel 7 emulator, Android 16 | `android/internal/index.html` | `android/client/test-completion-report.html` | `android/pdf/` |
| iOS & Android | both of the above | `all/internal/index.html` | `all/client/test-completion-report.html` | `all/pdf/` |

- **Internal**: every number opens what it counts — a module opens every check with its verdict; a check opens its
  test with steps and screens; a red check opens its defect report; the combined report links into both platform
  reports. TRIARE · Internal.
- **Client**: English, sections 1–9 (summary, scope, environment, results, not automated, defects, exit criteria,
  risks and recommendations, sign-off); no ids, paths or test accounts. **The owner approves it before it is sent.**
- `internal.html` and `client.html` are the entry pages of the two published sites.
- `<slice>/run.json`: which run each report describes; the PDF names take their date from it — the date of the run,
  never the day the file was made.

## Published (private — shared from the page's Share menu)

- Team, all three internal reports: https://claude.ai/artifact/Vh4DJSdzZmaGH7fwRMUbde
- Client, the three test completion reports: https://claude.ai/artifact/2sTviSM7raPbMcdxjLvYk8

Earlier pages (kept, not updated): the iOS report of 2026-09-28, https://claude.ai/artifact/EdTpeAfr1wAGm4fxsYBm15, and
the Auth pilot, https://claude.ai/artifact/NvRzuhzr418nLAYMZfaf15.

## Rebuild

```bash
cd automation/tools
uv run python mobile_reports.py            # local full copy → automation/mobile/reports/ (gitignored)
uv run python mobile_reports.py --share    # this copy → reports/, then the privacy check (must end with 0 · 0 · 0);
                                          # also the publish fragments → automation/mobile/reports/publish/
node mobile_export_pdf.mjs                       # the six PDFs → reports/mobile/<slice>/pdf/
```

Nothing runs against an environment: the reports read runs already made (`setup/project.yaml → report.mobile.slices`). The
privacy check reads every screen with macOS Vision on this machine (`mobile_redact_screens.py`); the account's name is read
from the DEV API in memory and never written.

Where things are decided: names, client, approver, links, the runs, the client's wording —
`setup/project.yaml → report:`; the company's look (TRIARE logo, colours, fonts) — `automation/tools/brand.py`;
the owner's rulings — `docs/notes/decisions.md` (2026-10-05).
