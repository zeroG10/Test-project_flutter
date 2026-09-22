# Load testing (k6) — optional module

Enabled via `modules.load_testing` in [setup/project.yaml](../../setup/project.yaml).
Stack: [k6](https://k6.io) (`brew install k6`). API load/stress from the same backend
the functional API tests hit — but a separate discipline: this module finds the
breaking point and thresholds under traffic, not correctness.

## Rules (non-negotiable)

1. **Smoke first, always.** The progression `smoke → load → stress` is mandatory.
   A stress run against an endpoint that fails at 2 VUs wastes budget and produces
   noise. Never start with load or stress.
2. **Staging/dev only — fail closed.** `config.js` refuses to start unless
   `LOAD_ENV` is `dev` or `staging`. Production is structurally unreachable.
3. **Cap the peak.** `PEAK_VUS` is a hard cap. LLM-backed or per-request-billed
   APIs cost money — confirm the target VUs and expected cost with the owner
   BEFORE a stress run (doctrine rule 5: escalate, don't decide).
4. **Back off on 429/409.** Rate-limit responses during ramp-up are a finding to
   record, not an obstacle to push through.
5. **Per-user limits → account pool.** 1 VU = 1 account. Pool lives in a gitignored
   `users.json` (commit `users.example.json` only).
6. **Separate budgets for heavy vs light endpoints.** A p95 that mixes `/generate`
   with `/health` measures nothing. Tag requests (`heavy` / `light`) and threshold
   them separately (`HEAVY_P95_MS` / `LIGHT_P95_MS`).
7. **Run log after EVERY run — including aborted ones.** One row in
   [runs.md](runs.md) immediately after each run. An aborted run with no row is a
   silent gap; the next person re-runs it blind.
8. **A threshold pass names its oracle.** The thresholds ARE the oracle — agree
   them with the owner before the first load round and record them in `runs.md`'s
   header. Numbers without an agreed SLA are observations, not verdicts.

## Usage

```bash
cd automation/load
LOAD_ENV=staging BASE_URL=https://api.staging.example.com k6 run scenarios/smoke.js
LOAD_ENV=staging BASE_URL=... TARGET_VUS=10 k6 run scenarios/load.js
LOAD_ENV=staging BASE_URL=... PEAK_VUS=50 k6 run scenarios/stress.js   # owner-confirmed
```

Adapt the endpoints in `scenarios/*.js` to the real API first — the shipped ones
are placeholders and the smoke scenario will (correctly) go red on a project where
`/health` does not exist. Fix the scenario, not the threshold.
