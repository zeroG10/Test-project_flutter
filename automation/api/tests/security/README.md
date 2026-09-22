# Security tests — optional module

Enabled via `modules.security` in `setup/project.yaml`. Grey-box QA security — the
bugs QA can find and prove safely. This is NOT a pentest and does not replace one.

## Scope & ethics (non-negotiable)

- **Authorized targets only**: the project's own dev/staging. Never production,
  never third-party hosts.
- **Non-destructive by default**: prove IDOR by READING another user's object,
  never by deleting it; hit rate limits with a bounded burst, not a flood.
- **Active scanning needs an explicit owner green light** (doctrine rule 5).
  Everything in this folder is passive/read-only and safe to run repeatedly.
- **Never paste a live token or credential into a report or bug.** Findings ship
  as bug reports with safe, minimal repro — never weaponized payloads.

## Priority order (what to configure first)

1. **Access control / IDOR matrix** ([test_access_control.py](test_access_control.py)) —
   owner vs other-user vs anonymous per resource. The #1 QA-findable, high-impact
   API bug class. Severity when found: **S1** (severity tree branch 1).
2. **Headers / cookies / CORS** ([test_headers.py](test_headers.py)) — the fast
   automatable win. Severity when found: usually S3 (tree branch 3).
3. Auth & session (token after logout, reset-token single-use, bounded-burst
   rate limit) — add as the project's auth model becomes known.

The manual companion checklist: `qa/shared/checklists/checklist-owasp-top10.md`.

## Running

```bash
cd automation/api
uv run pytest -m security
```

Tests skip loudly (with the exact missing variable named) until configured in
`.env` — a skip here is `Blocked`, not green: wire the config or scope the module
out in `setup/project.yaml`. The values are read through `config/settings.py`
(`user_a_token`, `user_b_token`, `idor_resources`, `idor_resource_ids`); `.env` is
loaded by `conftest.py`. Required for the IDOR matrix:

```
USER_A_TOKEN=...        # owner of the resources below
USER_B_TOKEN=...        # a DIFFERENT user, same tenant class
IDOR_RESOURCES=/orders/{id};/profile/{id}   # ';'-separated GET paths with {id}
IDOR_RESOURCE_IDS=123;456                   # ids owned by USER A, same order
```
