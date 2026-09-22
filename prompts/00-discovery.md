# Prompt 00 — Project Discovery (before any setup or artifact)

## Purpose

Learn the project before configuring anything. Every project is specific: what documents
exist, whether the product already runs, how users sign in, whether test data may be
created, which module comes first. The answers decide which route through this template
applies. Without them an agent either guesses silently or walks the full ten-step workflow
for a project that needs one API smoke run.

This prompt is **Step 0 of `/setup-project`** (Claude Code) and the stand-alone
instruction for any other agent (Cursor, Codex, Copilot): read it, ask the questions, write
the answers into `setup/project.yaml → context:` and `tracker:`, then continue with
`setup/SETUP.md`.

## When to Use

- A fresh clone, before `/setup-project` propagates values.
- `CLAUDE.md` → Project Overview still shows a `<…>` placeholder.
- The user says "new project", "налаштуй проект", "let's start", or drops the first
  documents into `docs/`.
- A returning session finds `project.yaml → context:` empty or contradicted by `docs/`.

## Rules

1. **Ask only what changes the next action.** Ten questions, one batch, with options. Do
   not ask for anything already visible in `docs/`, `setup/project.yaml` or the repository —
   read first, then ask about the gaps.
2. **Never guess an answer.** An unanswered question stays `<unknown>` in the manifest and
   is listed as TODO in the setup report. A `<unknown>` blocks only the steps that depend on
   it, never the whole setup.
3. **Answers live in the manifest, not in the chat.** Write them to
   `setup/project.yaml → context:` / `tracker:`; `/setup-project` propagates them into
   `CLAUDE.md` (Project Overview), `docs/environments.md` and the module indexes. The next
   session reads the profile; it does not re-interview.
4. **The profile selects the route** (table below). State the chosen route in the setup
   report in one sentence.

---

## Prompt

```text
You are setting up this QA automation template for a new product. Before configuring
anything, build the project profile. First read what already exists: setup/project.yaml,
docs/** (any file), README.md. Then ask the user ONLY the questions below whose answer you
could not find, in ONE batch, offering the options shown. Record every answer verbatim
into setup/project.yaml under `context:` and `tracker:`. Leave `<unknown>` where the user
does not know; never fill a value yourself.

Questions (skip any already answered by the repository):

1. Product state — Does the product already run on a reachable test environment today?
   [existing, reachable now / existing, access pending / greenfield, nothing to run yet]
2. Sources of truth — Which of these exist? Use the default precedence by layer from
   qa/shared/oracles/README.md unless you want a project/module-specific override; if so,
   name the source and scope. [Figma design / SRS or PRD / user stories with acceptance criteria /
   API spec (OpenAPI, Postman) / none — only the live product]
3. Platforms in scope now — [web / iOS / Android / Flutter / API] and which of them share
   one backend. UI flows are the default priority; standalone API and API-assisted UI
   are also available. Record the chosen focus with the first-module scope.
4. First module — Which module or flow is tested first, and why (highest risk, release
   date, client ask)?
5. Authentication and roles — How do users sign in [email+password / OTP or magic link /
   SSO / social], which roles exist, and are there test accounts per role already?
6. Test data — On the target environment, may automation create and delete its own data?
   [yes, freely / yes, with a naming rule / shared environment, read-only / unknown]
   Is there a seed script or scheduled reset?
7. Environments — Which environments exist [dev / staging / other], which one is the
   automation target, and is it reachable from CI runners without VPN?
8. Reporting — Where do results live? [markdown only in qa/ / Google Sheets checklist /
   both] — and who publishes to the Sheet?
9. Tracker — Where are bugs filed [Jira / Linear / GitLab / Redmine / none — markdown in
   qa/*/bugs/ only], project key, who confirms filing, and is there an etalon ticket?
10. Decision owner — Who answers open questions (product owner, BA, client) and how fast
    an answer can be expected?

Then:
- Write the answers to setup/project.yaml (`context:` block, `tracker:` block).
- Pick the route from the table in prompts/00-discovery.md and say which one in one
  sentence.
- List every `<unknown>` as a TODO with the step it blocks.
- Continue with setup/SETUP.md (Claude Code: the remaining steps of /setup-project).
```

---

## Routes (what the profile turns on)

| Profile | Route |
|---|---|
| Existing product, reachable, any documents | **Recon first**: `npm run pw:recon` / mobile MCP crawl → curate screen maps → `pw:smoke` + `pw:map-health` → then checklist (prompt 02) from real screens + docs; differences go to `<module>-questions.md`. |
| Existing product, no SRS/PRD (only Figma or nothing) | Recon first; capture observations, then use available design and recorded owner explanations/confirmed expectations. The owner may explicitly adopt a scoped, versioned regression baseline (oracle guide). Unconfirmed expectations remain questions; no Figma or API setup is required for independent UI checks. The RTM (prompt 04) uses `REQ-<CODE>-NNN` ids linked to these recorded sources. |
| Greenfield, documents only | Analysis (prompt 01) → checklist (prompt 02) → candidates (prompt 06) → test cases (prompt 03) now; screen maps and tests (prompt 07) wait for the first build. Nothing is marked Passed before a build exists. |
| API-only, OpenAPI available | `qa/api/<NN-module>/` chain: contract → CHK → `automation/api/tests/` with `@pytest.mark.chk` → `trace_results.py --platform api`. No screen maps. |
| Test data: shared environment, read-only | Read-only tests only; no `seed*` fixtures; the constraint is recorded in `docs/environments.md` → *Test data and seeding* and in `automation/README.md` terms ("every test owns its data" cannot be met — say so in the report). |
| Tracker: none | Bugs stay in `qa/<platform>/<NN-module>/bugs/` (prompt 08 still governs the content); no filing step. |
| Reporting: markdown only | `/qa-sheets-sync` is not wired; the checklist status column lives in the markdown until a Sheet exists. |

Routes combine (e.g. existing + API-only + tracker Jira). When two rows conflict, the
more restrictive one wins and the conflict is a line in the setup report.

## Output

- `setup/project.yaml` → `context:` and `tracker:` filled (or `<unknown>`).
- One sentence naming the route, in the setup report.
- TODO list of unknowns with the step each one blocks.
