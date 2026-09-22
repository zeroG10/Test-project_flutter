# Test oracles — how a verdict is decided

An oracle is the source of truth that lets you say Passed or Failed. Doctrine rule 2
(CLAUDE.md): **every verdict names its oracle; no oracle → not-run / needs-human, never
Passed.** "Correct according to WHAT?" must always have an answer.

## Source precedence and projects without documents

1. **The owner's explicit project decision takes precedence over template defaults.**
   Record the chosen source, affected module/platform/behaviour, reason, owner and date in
   `docs/notes/decisions.md`; summarise or link it in `setup/project.yaml →
   context.precedence_note`. Apply it only within its stated scope. Ask only if the scope
   is unclear; do not ask again for an already explicit decision. A new decision updates
   the documented expectation deliberately, never silently in response to a failing test.
2. **Default when there is no override:** acceptance criteria / SRS / business rules and
   invariants define behaviour and permissions; Figma defines the visual layer; the API
   contract defines request/response shape. A visual difference does not establish a
   permission. Record the applied precedence when sources disagree. If neither an owner
   decision nor this scoped default resolves the conflict, ask and block only that
   expectation; continue independent work.
3. **Only the owner and a running product is a valid starting point.** Explore the agreed
   UI flows, record observed screens, roles, states and evidence in the module analysis
   (environment/build/date), and collect questions about intended behaviour in batches.
   Observations describe what happens; they are not automatically requirements or bugs.
   Record the owner's explanations and confirmed expectations in `docs/notes/` with the
   owner/date/scope and cite them as `spec` in checklists and TCs. No SRS, Figma or API
   integration is required for this UI route. Unknown expectations stay questions.
4. **An observed baseline can be adopted explicitly.** The owner may accept particular
   current flows/screens as the regression reference. Capture the version and evidence,
   record the approval and limitations, then cite `golden-master` (or `spec` for written
   expectations). A passing comparison means "matches the accepted baseline", not that
   every existing behaviour is correct. Unapproved observations never become a baseline
   automatically. A `human` oracle remains manual only when each run needs human judgement;
   a precise expectation already confirmed by the owner can be automated.

## The 8 oracle strategies, ordered by strength

Within the agreed project precedence, use the **strongest oracle available** for each
area. Don't LLM-judge what a schema can validate; don't eyeball what a pixel-diff can decide.

| # | Type | The verdict comes from | Typical use here |
|---|---|---|---|
| 1 | `spec` | An explicit requirement: a user story's acceptance criterion (`US-n/AC-m`), an SRS / PRD section, a Figma node, an API contract in `docs/api/`, or a recorded owner-confirmed expectation | Most functional checks. Precedence by layer: **AC / SRS / invariants decide behaviour, rules and permissions; Figma decides the visual layer and wins over SRS there; the live product decides only what exists today** (observations need owner confirmation or explicit baseline adoption as described above) |
| 2 | `golden-master` | A captured known-good artifact (screenshot baseline, response snapshot) | Visual regression, contract snapshots |
| 3 | `differential` | Two implementations/platforms must agree (web vs mobile vs API on the same data) | Cross-platform features, compatibility cells |
| 4 | `invariant` | A property that must always hold — see [invariants.md](invariants.md) | Business rules, post-bug regression checks |
| 5 | `metamorphic` | A relation between two runs (`?limit=10` is a prefix of `?limit=100`; LTR↔RTL show the same elements) | API list endpoints, i18n |
| 6 | `consistency` | HICCUPPS: consistent with history, image, comparable products, claims, user expectations, product itself, purpose, statutes | Exploratory sessions |
| 7 | `llm-judge` | A fixed written rubric, calibrated on known-good/known-bad, judge independent of generator | Generated content, translation quality |
| 8 | `human` | A person decides | Real UX, screen-reader experience, anything above can't decide |

## Rules

- **Record the oracle, don't just think it.** Test cases carry an `Oracle` metadata row
  (`type — source`, e.g. `spec — figma:123-456` or `invariant — INV-3`). Checklist items
  name the oracle in the comment when it is not obvious. A pass/fail result whose oracle
  cannot be named is an incomplete artifact.
- **Do not fabricate a Fail either — an oracle can be wrong.** When a check goes red,
  first ask whether the expectation encodes a wrong assumption. If the agreed sources
  or an explicit owner correction show that the expectation was wrong — that is a **test defect**: record the correction, fix the oracle,
  re-run, file NO bug. A false Fail wastes a triage cycle and erodes trust in the suite
  exactly as a false Pass erodes trust in the product.
- **Resolve conflicts using the precedence above.** Cite the owner decision or scoped
  default applied. Otherwise record the conflict in the module's `*-questions.md` and
  block only the affected expectation until answered. Observed behaviour alone never
  overrides a requirement or proves a permission.
- **Golden masters change deliberately, never conveniently.** Silently re-recording a
  baseline to make a test green is fabricating a Pass (doctrine rule 4). Baseline updates
  are owner-confirmed and logged.
- **Invariants are the cheapest strong oracle — harvest them.** Every business rule and
  every fixed bug implies one. See [invariants.md](invariants.md).
- **LLM-judge discipline** (only where generative output is tested): fixed written rubric
  with per-dimension scales; calibrate on known-good AND known-bad before trusting; the
  judge is independent of the generator (never the same conversation grading its own
  output); borderline scores → needs-human; every claim in a verdict must be
  re-verifiable by script — a verdict whose evidence can't be re-run is opinion.
- **Oracles are fallible — track their misses.** A bug that reached the team through a
  check that had said Passed gets a row in the table below; the fix is an oracle fix.

## Oracle misses (audit)

| Date | What slipped through | Which oracle said Passed | Fix applied |
|---|---|---|---|
| | | | |
