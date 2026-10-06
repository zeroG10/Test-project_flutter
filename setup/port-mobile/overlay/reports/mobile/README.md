# reports/mobile — the test completion reports of the mobile regression

What the project hands over at the end of a mobile regression. Every file here is **generated** from the
repository's records — the runs, the checklists, the bug reports, the reasons files — so edit the generators, never
these files. This is the **shared copy**: the test accounts' email, phone and name are hidden in the text and
pixelated on the screens, and API bodies, page sources and screen videos are left out (they stay in the gitignored
local copy, `automation/mobile/reports/`).

Three slices, each with an internal and a client report (ISTQB / ISO/IEC/IEEE 29119-3 *test completion report*):

| Slice | Run it describes | Internal (team) | Client | PDF |
|---|---|---|---|---|
| iOS | `report.mobile.slices.ios.run` | `ios/internal/index.html` | `ios/client/test-completion-report.html` | `ios/pdf/` |
| Android | `report.mobile.slices.android.run` | `android/internal/index.html` | `android/client/test-completion-report.html` | `android/pdf/` |
| iOS & Android | both of the above | `all/internal/index.html` | `all/client/test-completion-report.html` | `all/pdf/` |

- **Internal**: every number opens what it counts — a module opens every check with its verdict; a check opens its
  test with steps and screens; a red check opens its defect report; the combined report links into both platform
  reports.
- **Client**: English, sections 1–9 (summary, scope, environment, results, not automated, defects, exit criteria,
  risks and recommendations, sign-off); no ids, paths or test accounts. **The owner approves it before it is sent**;
  until `report.client`, the slice's `product` and `report.approved_by` are set it says "Draft — not for sending".
- `internal.html` and `client.html` are the entry pages of the two published sites.
- `<slice>/run.json`: which run each report describes; the PDF names take their date from it — the date of the run,
  never the day the file was made.

## Published

`<the links, once the owner publishes — setup/project.yaml → report.mobile.slices.*.{internal_url,client_url}>`

## Rebuild

```bash
cd automation/tools
uv run python mobile_reports.py            # local full copy → automation/mobile/reports/ (gitignored)
uv run python mobile_reports.py --share    # this copy, then the privacy check (must end "… 0 · … 0 · videos: 0");
                                           # also the publish fragments → automation/mobile/reports/publish/
node mobile_export_pdf.mjs                 # the six PDFs → reports/mobile/<slice>/pdf/
```

Nothing runs against an environment: the reports read runs already made (`setup/project.yaml → report.mobile.slices`).
The privacy check reads every screen with macOS Vision on this machine (`mobile_redact_screens.py`); the accounts'
names come from `.env` (`*_USER_NAME`) or the project's hook `automation/mobile/helpers/account_names.py`, held in
memory and never written. In Claude Code: `/qa-mobile-report`.

Where things are decided: names, client, approver, links, the runs, the client's wording —
`setup/project.yaml → report:` and `report.mobile:`; the company's look — `automation/tools/brand.py`.
