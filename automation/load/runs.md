# Load-test run log

One row per run, appended IMMEDIATELY after every k6 run — **including aborted
ones**. An aborted run with no row is a silent gap.

**Agreed SLA (the oracle for verdicts)** — fill before the first load round,
confirmed by the owner:

- Light endpoints p95: `<___ ms>`
- Heavy endpoints p95: `<___ ms>`
- Error rate: `< ___%`
- Expected concurrent users (TARGET_VUS basis): `<___>`

| Run id (date-scenario) | Scenario | Env | VUs | Duration | Error rate | p95 light | p95 heavy | 429/409/5xx counts | Thresholds | Verdict (pass/fail/aborted/blocked) | Notes / BUG links |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |
