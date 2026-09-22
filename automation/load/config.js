// Shared config for all k6 scenarios. Fails closed: a missing BASE_URL or a
// non-allowed environment refuses to start — a suite that silently targets the
// wrong host produces findings that read like product bugs.

const ENV = __ENV.LOAD_ENV || '';
if (ENV !== 'dev' && ENV !== 'staging') {
  throw new Error(
    `LOAD_ENV='${ENV}' — allowed: dev, staging. Never production. ` +
      'Set it explicitly: LOAD_ENV=staging k6 run ...',
  );
}

export const BASE_URL = __ENV.BASE_URL;
if (!BASE_URL) {
  throw new Error('BASE_URL is not set (e.g. BASE_URL=https://api.staging.example.com)');
}

export const TARGET_VUS = Number(__ENV.TARGET_VUS || 10);
// Hard cap for stress runs. Raising it is an owner decision (cost + safety).
export const PEAK_VUS = Number(__ENV.PEAK_VUS || 50);

// Separate p95 budgets: heavy = expensive endpoints (generation, search, reports),
// light = cheap ones (health, polling, simple reads). Mixing them in one
// threshold measures nothing.
export const HEAVY_P95_MS = Number(__ENV.HEAVY_P95_MS || 5000);
export const LIGHT_P95_MS = Number(__ENV.LIGHT_P95_MS || 800);

export const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

export function authHeaders() {
  return AUTH_TOKEN ? { Authorization: `Bearer ${AUTH_TOKEN}` } : {};
}
