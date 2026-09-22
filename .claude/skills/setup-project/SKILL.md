---
name: setup-project
description: Deploy this QA template for a new project — read setup/project.yaml, ask for missing values, propagate them into all consumer files per setup/SETUP.md, wire integrations (Figma MCP, Google Sheets, Playwright, API, Appium) and verify each one. Use when the user says "setup the project", "налаштуй проект", "configure this template", "deploy the template", or right after cloning the template repo.
---

# Setup Project (template → working project)

Turns a fresh clone of this QA template into a configured project. The knowledge
lives in two files — this skill only orchestrates them:

- [setup/project.yaml](../../../setup/project.yaml) — the **manifest**: every
  project-specific value, one place.
- [setup/SETUP.md](../../../setup/SETUP.md) — the **map**: which file consumes
  each manifest key, and how to wire/verify each integration.

Do NOT improvise paths or invent config keys. If the map and reality disagree
(a consumer file moved, a key renamed), fix the map in the same session and tell
the user — the map must stay truthful.

## Step 0 — Discovery: the project profile (SETUP.md §0)

1. Read `setup/project.yaml`, `setup/SETUP.md` and whatever is already in `docs/**`.
2. If `project.yaml → context:` is empty or `<unknown>` where `docs/` could answer, run
   [prompts/00-discovery.md](../../../prompts/00-discovery.md): ask the ten questions in
   ONE batch (skip those the repository already answers), write the answers verbatim into
   `context:` and `tracker:`, name the route in one sentence. Never guess; `<unknown>`
   stays `<unknown>` and blocks only what depends on it.
3. If the profile is already filled, do not re-interview — read it and continue.
4. Collect every value still equal to a `<PLACEHOLDER>`.
5. Check which stacks are enabled (`platforms.web/mobile/api`).
6. Check which optional modules are enabled (`modules.*`).

## Step 1 — Gather missing values (ask, never guess)

Ask the user for all missing values in ONE batch (AskUserQuestion or a compact
list), grouped by: project meta → enabled platforms → sheets → figma.
Skip questions for disabled platforms entirely.

- If the user doesn't have a value yet (e.g. no mobile build, no sheet created),
  record it as still-placeholder and list it in the final report as TODO.
- Write the answers back into `setup/project.yaml` — the manifest must end the
  session up to date. It is committed; it holds no secrets.

## Step 2 — Propagate values

Apply the **value propagation map** (SETUP.md §1) mechanically:

- Edit tracked files in place (CLAUDE.md, package.json, docs/environments.md,
  the BMAD configs, figma-sources.md).
- Create `.env` files by copying `.env.example` in the same directory, then fill
  the mapped keys. Never commit `.env`.
- Respect platform toggles (SETUP.md §2): skip disabled stacks; offer (don't
  force) deleting their CI workflows.
- Respect module toggles (SETUP.md §2b): for each `modules.<name>` that is
  `false`, offer to delete its scaffold folder; for each that is `true`, do its
  "wire" step. Flag any module enabled while its required stack is disabled.

## Step 3 — Wire integrations

Follow SETUP.md §3 in order: Figma MCP → Google Sheets → Playwright → API →
Mobile. For each one either complete it, or — if it needs something only the
user has (PAT, service-account JSON, app build) — give the exact instruction
from SETUP.md and mark it TODO.

Hard rules (SETUP.md §5): never run `sync_checklist_to_sheets.py --reset` and
never run `examples/checklist-gen/` — the only permitted live-sheet writer is
`automation/tools/sync_checklist_to_sheets.py`, and during setup only with
`--dry-run`.

## Step 4 — Verify

Run each enabled stack's **Verify** command from SETUP.md §3, and each enabled
module's **Verify** command from SETUP.md §2b. A verify step that fails because a
secret/build is missing is a TODO, not an error — report it as such. A verify
step that fails with the config present is an error — fix or escalate.

## Step 5 — Report + commit

1. Summary table: value → propagated where; integration → OK / TODO (with the
   exact next action for each TODO). Name the route chosen in Step 0 and the
   "minimum to run something today" row (SETUP.md §0) that applies — what can be
   run right now, and what is Blocked on which TODO.
2. Do the post-setup hygiene pass (SETUP.md §4).
3. Offer to commit the configuration as
   `chore: configure template for <project name>`.
