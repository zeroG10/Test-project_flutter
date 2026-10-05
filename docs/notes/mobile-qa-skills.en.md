# Running tests and reports — the QA skills

> Українською: [mobile-qa-skills.md](mobile-qa-skills.md)

Four commands for Claude Code. Type the command, or just say what you need — Claude picks the
skill. They all sit on one tool (`automation/mobile/scripts/qa.sh`), so everything can also be done
by hand — the commands are at the end.

| Skill | When | What you say |
|---|---|---|
| `/qa-mobile-run` | run a module, several modules or one test | "run auth on android", "module 08 on both" |
| `/qa-mobile-regress` | run the whole regression | "regression on both platforms", "iOS regression" |
| `/qa-mobile-triage` | find out why a test is red | "triage what failed" |
| `/qa-mobile-report` | update the final reports and PDFs | "rebuild the reports from the last regression" |

The usual cycle: **`/qa-mobile-regress` → (if something new is red) `/qa-mobile-triage` → `/qa-mobile-report`**.
`/qa-mobile-run` goes in between, to check one module after a fix.

## /qa-mobile-run — a module or a test

- **Start:** `/qa-mobile-run android auth` · `/qa-mobile-run both 08,09` · `/qa-mobile-run ios tests/shared/test_splash.py::test_x`
- **What to say:** the platform (`ios`, `android`, or `both` — the two at the same time) and what to
  run (a module's number, its name or a part of it). No platform given — Claude asks; it never guesses.
- **What it does:** shows the plan → checks that the changes are committed → boots the simulator /
  emulator and Appium itself → runs → compares with the last final run.
- **What you get:** how many passed / failed / could not run, and above all what is **new** (new
  red, new "could not run") and what is a known defect.
- **What it does not do:** it does not touch reports, traceability or bugs; it does not re-run a red
  test "until green".

## /qa-mobile-regress — the whole regression

- **Start:** `/qa-mobile-regress both` · `/qa-mobile-regress android` · `/qa-mobile-regress ios`
- **Time:** iOS ≈ 1.5 h, Android ≈ 2 h 45 min, both at the same time ≈ 2 h 45 min. The Mac stays on
  the charger with the lid open.
- **What it does:** the same as `/qa-mobile-run` for the whole suite, with video kept for failed tests, and
  it compares **every test** with the last final run.
- **What you get:** either "the run repeats the previous one" with the numbers, or the list of
  differences: new red, new "could not run", tests that went missing, and "looks fixed" (was red
  because of a defect, green now).
- **At the end it asks:** triage the new red (`/qa-mobile-triage`)? make this run the basis of the reports
  (`/qa-mobile-report`)? shut the devices down?
- You can ask for several runs in a row ("three times") to check repeatability.

## /qa-mobile-triage — why it is red

- **Start:** `/qa-mobile-triage` (the last run) or "find out why TC-AUTH-007 failed on iOS".
- **What it does:** for each new red test it reads the evidence (the step, the screenshot, the video,
  the server's answers), the test's code and the requirement the test checks against, and decides
  one of five:

  | Cause | What follows |
  |---|---|
  | the environment (device, network, server, load) | "could not run" with the reason; the test is still owed |
  | the test itself | a proposed fix of the test — made on your word |
  | a wrong expectation in the test | the test case and the test are corrected to the requirement; no bug |
  | the app | a bug draft with evidence; filed only on your word |
  | nobody wrote what should happen | a question to you; the check is not counted as passed |

- **The only re-run allowed:** once, one test, alone — only to tell "the environment" from the rest.
  Both results are shown.
- **What you get:** a table — the test, what happened in plain words, the decision, the evidence, the
  proposal — and, as a separate block, the questions only you can answer.

## /qa-mobile-report — the reports

- **Start:** `/qa-mobile-report` — after a whole regression.
- **What it does:** asks which runs to take → checks each is a whole, clean regression → updates the
  traceability → rebuilds the 6 reports (iOS / Android / combined × internal / client) and the 6
  PDFs → checks that the shared copy holds nothing of the test accounts (it must end 0 · 0 · 0).
- **What you get:** the numbers of each report, what changed against the previous ones, the local
  pages opened.
- **Only on your word:** updating the published pages ("publish"), "commit", "push". You approve the
  client report before it is sent.

## Rules in every skill

1. Starting a skill is your go for that one run. Nothing else starts without you.
2. Changes must be committed before a run; a commit only on "commit" («коміть»), a push only on
   "push" («пуш»).
3. A red test is not re-run until it turns green. The cause comes first.
4. "Could not run" is never counted as "passed".
5. Bugs are filed and reports published only on your word.
6. iOS and Android at the same time — yes (each has its own account and its own Appium server);
   two runs of one platform at the same time — no. Details: `automation/mobile/PARALLEL-RUNS.md`.

## The same by hand

```bash
cd automation/mobile
scripts/qa.sh both all                  # the regression of both platforms at the same time
scripts/qa.sh android auth              # a module
scripts/qa.sh both all --dry-run        # the plan only

cd ../tools
uv run python mobile_compare_runs.py --platform android ../mobile/results/android/<run>   # what changed
uv run python mobile_reports.py --share && node mobile_export_pdf.mjs                      # reports and PDFs
```
