// Smoke: minimal traffic proving the harness and the target work at all.
// ALWAYS run this before load.js / stress.js — a target that fails at 2 VUs
// makes every bigger run meaningless.
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, LIGHT_P95_MS, authHeaders } from '../config.js';

export const options = {
  vus: 2,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{kind:light}': [`p(95)<${LIGHT_P95_MS}`],
  },
};

export default function () {
  // Placeholder endpoint — replace with the project's real cheap read.
  const res = http.get(`${BASE_URL}/health`, {
    headers: authHeaders(),
    tags: { kind: 'light' },
  });
  check(res, {
    'status is 200': (r) => r.status === 200,
    'body is not empty': (r) => (r.body || '').length > 0,
  });
  sleep(1);
}
