import assert from 'node:assert/strict';
import { test } from 'node:test';
import type { APIResponse } from '@playwright/test';
import { expectStatus } from '../playwright/utils/api';
import { cleanupRegistry } from '../playwright/utils/cleanup';
import { redact, safeBody, safeUrl } from '../playwright/utils/reporting';

const response = (status: number, body: unknown = {}): APIResponse => ({
  status: () => status,
  text: async () => typeof body === 'string' ? body : JSON.stringify(body),
} as APIResponse);

test('nested and configured fields are redacted without mutating assertion data', () => {
  const prior = process.env.QA_REDACT_FIELDS;
  process.env.QA_REDACT_FIELDS = 'customer-email';
  try {
    const body = { nested: [{ accessToken: 'token-value', PASSWORD: 'password-value' }],
      customer_email: 'private-value', count: 2 };
    const original = JSON.stringify(body);
    const rendered = safeBody(body);
    for (const secret of ['token-value', 'password-value', 'private-value']) {
      assert.ok(!rendered.includes(secret));
    }
    assert.ok(rendered.includes('"count":2'));
    assert.equal(JSON.stringify(body), original);
  } finally {
    if (prior === undefined) delete process.env.QA_REDACT_FIELDS;
    else process.env.QA_REDACT_FIELDS = prior;
  }
});

test('raw text and URL credentials are omitted, embedded credentials masked', () => {
  assert.ok(!safeBody('raw-secret').includes('raw-secret'));
  const url = safeUrl('POST https://user:password@local.invalid/path?code=query-secret#fragment-secret');
  for (const value of ['password', 'query-secret', 'fragment-secret']) assert.ok(!url.includes(value));
  const text = JSON.stringify(redact({ message: 'Bearer abc.def token="two words" password=secret' }));
  for (const value of ['abc.def', 'two words', '=secret']) assert.ok(!text.includes(value));
});

test('status assertions preserve response bodies and support expected errors', async () => {
  const body = { token: 'original-token', error: 'forbidden' };
  assert.deepEqual(await expectStatus(response(403, body), 403, 'GET /orders'), body);
  await assert.rejects(expectStatus(response(403, body), 204, 'DELETE /orders?key=query-secret'),
    (error: Error) => error.message.includes('forbidden') &&
      !error.message.includes('original-token') && !error.message.includes('query-secret'));
});

test('cleanup runs LIFO, attempts all records, and rejects an unchecked HTTP failure', async () => {
  const registry = cleanupRegistry();
  const calls: number[] = [];
  registry.track(async () => { calls.push(1); return response(204); }, 'record-1', 204);
  registry.track(async () => { calls.push(2); return response(500, { token: 'private-token' }); }, 'record-2');
  registry.track(async () => { calls.push(3); return response(204); }, 'record-3', 204);
  await assert.rejects(registry.finish(), (error: Error) =>
    error.message.includes('record-2') && error.message.includes('500') &&
    !error.message.includes('private-token'));
  assert.deepEqual(calls, [3, 2, 1]);
  await registry.finish(); // entries are drained, never delete twice on the same registry
  assert.deepEqual(calls, [3, 2, 1]);
});

test('cleanup accepts the contract status and existing void callbacks, rejects a mismatch', async () => {
  const registry = cleanupRegistry();
  registry.track(async () => response(404), 'already-gone', 404);
  let visible = true;
  registry.track(async () => { visible = false; assert.equal(visible, false); }, 'UI cleanup');
  await registry.finish();
  registry.track(async () => response(200), 'wrong-contract-status', 204);
  await assert.rejects(registry.finish(), /expected 204/);
});

test('cleanup is performed after a failed test body and retains the original failure', async () => {
  const registry = cleanupRegistry();
  let removed = false;
  registry.track(async () => { removed = true; return response(204); }, 'owned-record', 204);
  await assert.rejects(async () => {
    try { throw new Error('body failed'); }
    finally { await registry.finish(); }
  }, /body failed/);
  assert.equal(removed, true);
});
