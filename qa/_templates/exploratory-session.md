# Exploratory session (SBTM) — [area]

> Optional module (`modules.exploratory`). Session-Based Test Management: chartered,
> time-boxed, debriefed. Place under the module folder:
> `qa/{web,mobile}/<NN-module>/exploratory/<date>-<charter>.md`.
> Naming: `qa/web/01-authentication/exploratory/2026-08-05-login-interruptions.md`.

## Charter

**Explore** `<area>` **with** `<tour>` **to find** `<risk/information>`.

> One sentence. "Clicking around to see what happens" without a charter, a time-box and a debrief
> is not a session and does not claim coverage.

## Setup

| Field | Value |
|---|---|
| Platform | web / iOS / Android |
| Build / URL | |
| Time-box | 30–90 min (human) · **tool-call budget ~40 (agent)** |
| Tester | @username / agent |
| Date | YYYY-MM-DD |

## Tours used (the move-set)

Pick what fits the charter — don't do all of them:

- [ ] Interruption (call, notification, backgrounding mid-flow)
- [ ] Repetition (do the same action many times)
- [ ] Sequence (do steps out of the intended order)
- [ ] Data extremes (min/max/empty/huge/special chars)
- [ ] State contamination (stale session, half-finished state, back button)
- [ ] Resource starvation (slow/no network, low storage, low battery)
- [ ] Back-button / backgrounding / process death

## Oracles (HICCUPPS) — how each anomaly was judged

Every anomaly logged below cites which oracle flagged it. An anomaly with no
articulable oracle is a **question for the owner** (the module's `<module>-questions.md`), not a finding.

> **H**istory · **I**mage · **C**omparable products · **C**laims · **U**ser
> expectations · **P**roduct (internal consistency) · **P**urpose · **S**tatutes

## Log (as you go)

| Time / call # | Observation | Oracle | Verdict (finding / question / ok) |
|---|---|---|---|
| | | | |

## Findings → feed-forward (always)

Exploration is worthless if nothing leaves the session:

- Confirmed bug → `BUG-<CODE>-NNN` in the module's `bugs/` per [prompts/08-file-bug.md](../../prompts/08-file-bug.md) (three gates first — a behaviour no source covers is a question, not a bug; measured repro rate).
- Confirmed surprise / rule → new invariant in [qa/shared/oracles/invariants.md](../shared/oracles/invariants.md) and/or a regression test case.
- Unresolved anomaly → the module's `<module>-questions.md` (product-level: `qa/shared/questions/`).

## Debrief (coverage honesty)

- **Charter coverage:** ~__% of the charter actually explored.
- **NOT touched:** <what in the charter's area was left unexplored>.
- Stayed on charter? (max one ~5-min side-look per session.)

> Exploration claims **charter coverage, never area coverage.** State what was not
> touched — silence is not coverage (doctrine rule 3).
