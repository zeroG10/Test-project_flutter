// Load: sustained traffic at the agreed target (TARGET_VUS) to verify the SLA
// holds at expected usage. Run smoke.js first.
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, TARGET_VUS, HEAVY_P95_MS, LIGHT_P95_MS, authHeaders } from '../config.js';

export const options = {
  stages: [
    { duration: '1m', target: TARGET_VUS }, // ramp up
    { duration: '5m', target: TARGET_VUS }, // hold
    { duration: '30s', target: 0 }, // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.02'],
    'http_req_duration{kind:light}': [`p(95)<${LIGHT_P95_MS}`],
    'http_req_duration{kind:heavy}': [`p(95)<${HEAVY_P95_MS}`],
  },
};

export default function () {
  // Placeholder flow — replace with the project's real user journey.
  // Chain through returned values, never hardcoded ids.
  const light = http.get(`${BASE_URL}/health`, {
    headers: authHeaders(),
    tags: { kind: 'light' },
  });
  check(light, { 'light: 200': (r) => r.status === 200 });

  // Example heavy call (uncomment and adapt):
  // const heavy = http.post(`${BASE_URL}/search`, JSON.stringify({ q: `run-${__VU}` }), {
  //   headers: { 'Content-Type': 'application/json', ...authHeaders() },
  //   tags: { kind: 'heavy' },
  // });
  // check(heavy, { 'heavy: 200': (r) => r.status === 200 });

  sleep(1);
}
