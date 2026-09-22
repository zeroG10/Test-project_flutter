# Visual regression — optional module

Enabled via `modules.visual_regression` in [setup/project.yaml](../../../../setup/project.yaml).
Mechanics: Playwright's built-in `expect(page).toHaveScreenshot()` — no extra deps.
What this module adds is the **baseline lifecycle governance**, which the mechanics
make trivially easy to violate.

## Rules

1. **Baselines are golden masters.** They change ONLY on an owner-confirmed intended
   design change, and every change is logged in [BASELINES.md](BASELINES.md)
   (page, build, date, approver). Re-recording a baseline to green a red diff without
   that confirmation is fabricating a Pass (doctrine rule 4).
2. **`--update-snapshots` is forbidden in CI** (see [.github/GATES.md](../../../../.github/GATES.md)
   rule 3). In CI a visual diff is fixed by fixing the app — never by re-recording
   the baseline that caught it. Update baselines locally, with the log entry.
3. **Determinism before coverage.** A flaky diff suite gets ignored within a week.
   Before baselining a page:
   - fixed viewport + `deviceScaleFactor: 1`;
   - animations/transitions off (`page.emulateMedia({ reducedMotion: 'reduce' })`
     and/or injected `*{animation:none!important;transition:none!important}`);
   - wait for `document.fonts.ready`;
   - seeded/mocked data, mocked clock for anything time-dependent;
   - mask variable regions (avatars, ads, timestamps) with the `mask` option;
   - pin the browser/OS in BASELINES.md — a baseline captured on macOS WebKit will
     not match Linux CI.
4. **Noise → fix the capture, NEVER raise the threshold to hide it.**
5. **A human looks at every over-threshold diff.** The pixel diff is a detector, not
   a judge. Triage: intended change (re-baseline + log, owner-confirmed) / unintended
   (file a bug, attach the diff image) / noise (fix determinism).
6. **Baseline by risk, not wall-to-wall.** Every baseline is a maintenance liability.
   Baseline the pages/states where a silent visual break would matter; don't baseline
   what nobody would act on.

## Usage

Put visual specs in this folder (`*.visual.spec.ts`). First run creates baselines —
that run is NOT a test (nothing was compared): review the captured images, log them
in BASELINES.md, commit. From then on, every run compares.

```bash
npx playwright test automation/web/playwright/visual/          # compare
npx playwright test --update-snapshots <spec>                  # local only + log entry
```
