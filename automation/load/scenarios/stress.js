// Stress: ramp beyond the expected target to find the breaking point and verify
// recovery. PEAK_VUS is a hard cap — raising it is an owner decision (cost +
// safety). Watch for 429/409 during ramp: that is a finding to record in
// runs.md, not an obstacle to push through.
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, PEAK_VUS, authHeaders } from '../config.js';

export const options = {
  stages: [
    { duration: '1m', target: Math.ceil(PEAK_VUS / 4) },
    { duration: '2m', target: Math.ceil(PEAK_VUS / 2) },
    { duration: '2m', target: PEAK_VUS },
    { duration: '1m', target: 0 }, // recovery — errors here are their own finding
  ],
  // No pass/fail thresholds on purpose: a stress run's outcome is the measured
  // breaking point + recovery behaviour, recorded in runs.md — not a green tick.
};

export default function () {
  const res = http.get(`${BASE_URL}/health`, {
    headers: authHeaders(),
    tags: { kind: 'light' },
  });
  check(res, {
    'not 5xx': (r) => r.status < 500,
    'rate-limited (record it)': (r) => r.status !== 429,
  });
  sleep(1);
}
