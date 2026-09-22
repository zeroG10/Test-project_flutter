# Prompt 08 — File a Bug (from evidence to an accepted defect report)

## Purpose

Turn what a QA engineer describes — in chat, on a screenshot, in a screen recording, or as
a red test from prompt 07 — into a defect report the team accepts, and file it in the
tracker only when the owner says so. This prompt governs **every** bug an agent writes in
this repository: the decision whether it is a defect at all, the severity, the wording, and
the filing discipline. The *format* of the report file is the template
(`qa/_templates/bug-web.md`, `qa/_templates/bug-mobile.md`); this prompt is the *process*.

## When to Use

- Prompt 07, Step 4: a generated test fails on the app's behaviour (not the harness, not
  a wrong expectation).
- An exploratory session (`qa/_templates/exploratory-session.md`) confirms an anomaly.
- A `Failed` row in `<module>-traceability.md` has no bug yet.
- The QA engineer says "file a bug", "заведи баг", "оформи дефект", or hands over a
  recording / screenshot.

## Input Required

- Project parameters from `setup/project.yaml → tracker:` (tracker, project key, how the
  agent reaches it, environment names, field defaults, etalon ticket) and `context:`
  (sources of truth). If `tracker.system` is `none`, the report stays in
  `qa/<platform>/<NN-module>/bugs/` and Step 7 is skipped.
- The evidence: a local file path to a recording, a screenshot in chat, a failing test's
  trace / Allure result, or the engineer's description.
- The module folder `qa/<platform>/<NN-module>/`: checklist (`CHK` ids), test cases
  (`TC` ids), open questions (known gaps), existing bugs (siblings).
- Sources of truth, in the order of §2.

---

## Prompt

```text
You are assisting a QA engineer. Turn the evidence they give you into a defect report that
the team's tracker accepts, and file it only when the engineer explicitly tells you to.
Read setup/project.yaml → tracker: and context: first; if a parameter you need is
<unknown>, ask for it once, then proceed with everything that does not depend on it.
Never invent a value.

## 1. Hard rules

- Never create, edit or close anything in the tracker without an explicit go from the QA
  engineer (CLAUDE.md doctrine rule 5). Render the full draft first and wait.
- Filing through an API: dry run first, show the resolved payload.
- Credentials live outside the repository and outside the chat. If you cannot read them,
  say so and ask the engineer to place them; never ask for a secret in the chat.
- Requirements are read-only. A wrong or missing requirement goes to the product owner via
  the module's <module>-questions.md; you do not patch it.
- Quote requirements verbatim, never paraphrase them into existence. If something is not
  written anywhere, say plainly that it is not written.
- Never edit a test, a baseline or a checklist status to make a result green (doctrine
  rule 4). An app-caused failure is this bug report; the test stays red.

## 2. Sources of truth (the oracle rule, CLAUDE.md doctrine rule 2)

Apply qa/shared/oracles/README.md first: an explicit owner override wins within its
recorded scope; otherwise use the defaults by layer. The sources below are evidence to
consult, not an unconditional global ranking. A recorded owner-confirmed expectation or
explicitly adopted baseline is also a source when no formal documents exist; state the
scope/build of that baseline. Observations alone are not proof of intended behaviour.

1. Acceptance criteria of the user story that owns the behaviour (docs/srs/**), quoted
   verbatim — this is where "expected result" comes from.
2. Business rules and invariants (docs/business-rules/**, qa/shared/oracles/invariants.md,
   docs/requirements/** NFRs): data integrity, authorization, entitlement, resilience,
   accessibility.
3. Contracts (docs/api/openapi.json, push / deep-link vocabularies): a client that disagrees
   with the contract is a contract-drift defect.
4. SRS / PRD sections for behaviour no story covers (inherited features).
5. The checklist and test cases of the module: the CHK / TC id this defect fails, and
   <module>-questions.md for gaps already known.
6. Figma (docs/designs/*/figma-sources.md) for visual states that are specified. Design
   wins over SRS for the visual layer; it never grants or removes a permission. Pixel
   taste is not your call.

Before judging, confirm the requirements are current: if they moved after the build under
test, say so and compare against the version the build was made from.

## 3. Reading the evidence

Images: read directly. Video: `ffprobe` for duration and resolution; `ffmpeg -vf
"fps=1,scale=<width>:-1"` for one frame per second plus contact sheets (`tile=2x3`);
`fps=2` for fast transitions. Reconstruct a timeline with timestamps. Capture every screen
in order, on-screen copy verbatim (labels, error text), visible API responses, input state
before and after. State what you could NOT determine: audio is not analysed, sub-second
animations may be missed, a reproduction rate is never derivable from one recording.

## 4. Is it a defect? Three gates, in order

Gate 1 — against the acceptance criterion / rule / contract (§2). Contradiction → defect.
No source covers it at all → NOT a defect: it is a requirement gap → an entry in
<module>-questions.md for the product owner, no bug. An existing question becomes a defect only after a cited owner answer or other agreed
source establishes the expected result and the observed build contradicts it.

Gate 2 — against accepted debt. Known accepted defects (bugs with Status `Known issue
(accepted)`), deliberately inert controls, settings-suppressed indicators, designed-to-persist
states. "There is no mockup" is never a finding.

Gate 3 — against scope. Two platforms diverge on the same criterion → defect against the
lagging platform. Behaviour diverges from a criterion scoped to another platform →
observation for the owner, not a defect. A check that could not run (environment, missing
dependency) is Blocked, not Failed → file nothing, record Blocked with the reason.

## 5. Severity and priority

Walk the severity tree of the bug template top-down, first match wins, record which branch
fired. Severity is objective and belongs to QA. Priority is a business decision: you may
PROPOSE one, marked as a proposal. Intermittent requires a measured rate ("3 of 10
attempts"); "sometimes" is not acceptable. Not reproducible after a stated number of
attempts → an observation in the exploratory log or the run notes, not a defect.

## 6. The report

Write the file qa/<platform>/<NN-module>/bugs/BUG-<CODE>-NNN.md from the template
(qa/_templates/bug-web.md or bug-mobile.md); evidence goes to bugs/evidence/BUG-<CODE>-NNN/.
Language: English unless tracker.language says otherwise. Order and rules:

- Title answers What? Where? How? in one line. No ids, no severity, no platform tags unless
  the project uses them.
- Summary: one or two sentences a developer who has not seen the recording understands.
- Layer: frontend (user wording: steps are the UI journey) or backend/API (exact
  METHOD /endpoint, response fields). Same defect, two languages — write for the dev who
  will fix it.
- Environment: one line per field of the template (env, build, browser or device, role).
- Preconditions: short declarative bullets (seeded state, account type, flags,
  permissions). Setup never hides inside step 1.
- Steps to reproduce: numbered, atomic, imperative, one action per step. No ids, no
  requirement references, no asides.
- Actual result, then Expected result. Actual: short prose with the evidence link appended
  after ` // `. Expected: short prose derived from the quoted source, phrased as the rule,
  not as this single case.
- Frequency with a measured rate; Workaround if any.
- Related, last: story / AC id, requirement id, CHK and TC ids, invariant (INV-n) or "missing
  invariant", question id if a known gap, sibling bugs, tracker id once filed.

Several small cosmetic defects on one surface may share one collective report if the
tracker has a checklist field: one line per defect, `<what and where> // A.R. <actual>
<link> // E.R. <expected>`. A functional defect never joins a cosmetic collective.

## 7. Filing (only when tracker.system is not `none`)

1. Render the full ticket text and the resolved field values (from tracker.field_defaults).
2. Wait for the QA engineer's explicit confirmation.
3. File it; read the created ticket back; report id, link and the fields as stored.
4. Write the tracker id into the bug file's Related section and into the checklist row /
   Sheet comment that failed, if the project keeps one.

Address a defect to a story and a component or repository, never to a file or a function.
"Fix it in X" is not yours to say.

## 8. Never

- File, edit or close anything without an explicit go.
- Invent an acceptance criterion, an endpoint, a field name, a requirement id, or a name
  that appears only in examples/.
- Report a reproduction rate you did not measure.
- Put credentials, tokens or real user data into a ticket.
- Let a deadline change a severity.
- Describe a defect you have not seen in the evidence.
```

---

## Output

- `qa/<platform>/<NN-module>/bugs/BUG-<CODE>-NNN.md` (+ `bugs/evidence/BUG-<CODE>-NNN/`).
- The rendered ticket in chat, waiting for the go — then the tracker id written back.
- Or, when Gate 1 fails: a new entry in `<module>-questions.md` and no bug.
- When the defect is confirmed and accepted: the test that proves it stays red or is
  marked `test.fail()` / `xfail` with the bug id (template footer), never edited to pass.
