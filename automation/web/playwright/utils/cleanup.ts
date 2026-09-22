import type { APIResponse } from '@playwright/test';
import { bodyOf, expectStatus } from './api';
import { safeBody, safeText } from './reporting';

export type Seed = {
  /** Register only data this test created. For API callbacks, pass the contract's status. */
  track: (cleanup: () => Promise<unknown>, label: string, expectedStatus?: number) => void;
};

function isResponse(value: unknown): value is APIResponse {
  return !!value && typeof (value as APIResponse).status === 'function' &&
    typeof (value as APIResponse).text === 'function';
}

/** Attempt every undo in reverse order, even after one fails. Never silently accept HTTP errors. */
export function cleanupRegistry(): Seed & { finish: () => Promise<void> } {
  const entries: { cleanup: () => Promise<unknown>; label: string; expectedStatus?: number }[] = [];
  return {
    track(cleanup, label, expectedStatus) { entries.push({ cleanup, label, expectedStatus }); },
    async finish() {
      const failures: string[] = [];
      for (const { cleanup, label, expectedStatus } of entries.splice(0).reverse()) {
        try {
          const response = await cleanup();
          if (isResponse(response)) {
            // Legacy two-argument callbacks still work, but must return a successful response.
            if (expectedStatus !== undefined) {
              await expectStatus(response, expectedStatus, 'cleanup');
            } else if (response.status() < 200 || response.status() >= 300) {
              throw new Error(`Cleanup returned HTTP ${response.status()} (expected 2xx). ` +
                `Body: ${safeBody(await bodyOf(response))}`);
            }
          } else if (expectedStatus !== undefined) {
            throw new Error('Cleanup with an expected status must return its API response');
          }
          // A non-HTTP callback (e.g. UI cleanup) must assert its own outcome before returning.
        } catch (error) {
          failures.push(safeText(`${label}: ${error instanceof Error ? error.message : String(error)}`));
        }
      }
      if (failures.length) {
        throw new Error(`Harness: cleanup failed for ${failures.length} record(s). ` +
          `Recover only these test-owned records and fix the cleanup.\n  ${failures.join('\n  ')}`);
      }
    },
  };
}
