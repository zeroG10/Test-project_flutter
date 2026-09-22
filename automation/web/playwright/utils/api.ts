import { request, type APIRequestContext, type APIResponse } from '@playwright/test';
import { safeBody, safeUrl } from './reporting';

/**
 * API access for the UI suite: login-by-API and data seeding / cleanup, so a UI test
 * can prepare its data independently of the UI flow it judges (automation/README.md → Determinism,
 * "every test owns its data"). API *tests* live in automation/api/ — this file only serves
 * the Playwright specs.
 *
 * SCAFFOLD. `loginByApi()` is product-specific and throws `Blocked` until it is written
 * from docs/api/openapi.json (auth endpoint, request body, token field) — every endpoint,
 * payload field and response field used here comes from that spec, never from a guess.
 * A fully cited version for one past product is in examples/automation/web/utils/api.ts:
 * copy the discipline, not the endpoints.
 */

/** API origin, fail-closed like BASE_URL: no target, no seeding, no login-by-API. */
export function apiBaseUrl(): string {
  const value = process.env.API_BASE_URL;
  if (!value || value.startsWith('<')) {
    throw new Error(
      'API_BASE_URL is not set — needed for login-by-API and data seeding (docs/environments.md → ' +
        'Test data and seeding). Set it in automation/web/.env (see .env.example). Blocked, not green.',
    );
  }
  try {
    new URL(value);
  } catch {
    throw new Error('API_BASE_URL is not a valid URL — check its configured value');
  }
  return value.replace(/\/+$/, '');
}

/** A request context against the API origin, optionally carrying a bearer token. */
export async function newApiContext(token?: string): Promise<APIRequestContext> {
  return request.newContext({
    baseURL: apiBaseUrl(),
    extraHTTPHeaders: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

/**
 * Sign in through the API and return the access token the seeding calls will carry.
 *
 * TODO(product): implement from docs/api/openapi.json — cite the operation
 * (e.g. `POST /auth/sign-in`, requestBody `SignInDto`, response field `access.token`)
 * in a comment above the call. Until then every fixture that needs it is Blocked, which
 * is the honest state: no token, no seeding, no authenticated API call.
 */
export async function loginByApi(
  _context: APIRequestContext,
  _email: string,
  _password: string,
): Promise<string> {
  throw new Error(
    'Blocked: loginByApi() is a scaffold — implement it from docs/api/openapi.json ' +
      '(auth endpoint, request body, token field; cite the operation in a comment). ' +
      'Never guess an endpoint. Pattern: examples/automation/web/utils/api.ts.',
  );
}

/** Parsed JSON body, or the raw text when the body is not JSON — for error messages. */
export async function bodyOf(response: APIResponse): Promise<unknown> {
  const text = await response.text();
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

/**
 * Assert the status of a seeding / login call and return its parsed body. A mismatch
 * throws with the operation and a redacted body — a seeding step that silently returns
 * `undefined` would make the test judge data that does not exist.
 */
export async function expectStatus<T = unknown>(
  response: APIResponse,
  expected: number,
  operation: string,
): Promise<T> {
  if (response.status() !== expected) {
    const body = await bodyOf(response);
    throw new Error(
      `${safeUrl(operation)} → ${response.status()} (expected ${expected}). Body: ${safeBody(body)}`,
    );
  }
  return (await bodyOf(response)) as T;
}
