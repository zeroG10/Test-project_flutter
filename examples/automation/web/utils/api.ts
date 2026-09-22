import { request as playwrightRequest, type APIRequestContext, type APIResponse } from '@playwright/test';

/**
 * Thin API helpers for login-by-API and test-data seeding / cleanup. API tests are OUT
 * of scope (docs/notes/decisions.md 2026-09-17); this file exists so UI tests can get a
 * token and create/delete the data they need without going through the UI.
 *
 * Every endpoint, payload field and response field below is taken from
 * docs/api/openapi.json (== live /swagger-json on DEV, diffed 2026-09-21). Nothing is
 * guessed: an optional field the spec does not name is not sent, a response field the
 * spec does not name is not read. Responses are checked for the fields we consume; a
 * mismatch throws with the endpoint and the body, never a silent undefined.
 *
 * Bearer scheme: components.securitySchemes.bearer (http, JWT).
 */

export type TokenPayload = { token: string; expiresIn: string };
/** SignInResponseDto */
export type SignInResponse = { access: TokenPayload; refresh: TokenPayload; isPhonePrimary?: boolean };
/** SuccessResponseDto-shaped body shared by forgot-password, delete, resend-link. */
export type SuccessResponse = { success: boolean; message?: string; messages?: string[]; error?: string };
export type UserRole = 'technician' | 'manager' | 'admin' | 'root';
export type UserStatus = 'pending' | 'active' | 'inactive' | 'archived';
/** GET /user/me — fields consumed here (spec lists more; all optional for us but id + role). */
export type Me = { id: string; role: UserRole; email?: string; firstName?: string; lastName?: string; isTwoFAActive?: boolean };
/** POST /user request body (spec: every property optional; the server validates). */
export type CreateUserInput = {
  email?: string;
  phone?: string;
  password?: string;
  firstName?: string;
  lastName?: string;
  role?: UserRole;
  status?: UserStatus;
  settings?: { isPhonePrimary?: boolean; isEmailVerified?: boolean; isPhoneVerified?: boolean };
};
export type CreatedUser = { id: string; role: UserRole; status: UserStatus; email?: string };
export type CreatedTag = { id: string; name?: string };

/** API origin, fail-closed like BASE_URL: no target, no seeding, no login-by-API. */
export function apiBaseUrl(): string {
  const value = process.env.API_BASE_URL;
  if (!value) {
    throw new Error(
      'API_BASE_URL is not set — needed for login-by-API and data seeding (docs/environments.md). ' +
        'Set it in automation/web/.env (see .env.example). Blocked, not green.',
    );
  }
  try {
    new URL(value);
  } catch {
    throw new Error(`API_BASE_URL is not a valid URL: '${value}'`);
  }
  return value.replace(/\/+$/, '');
}

async function bodyOf(response: APIResponse): Promise<unknown> {
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/** Like expectStatus, for an endpoint whose success code differs between spec and reality. */
async function expectAnyStatus(response: APIResponse, expected: number[], what: string): Promise<unknown> {
  const body = await bodyOf(response);
  if (!expected.includes(response.status())) {
    throw new Error(`${what} → HTTP ${response.status()} (expected ${expected.join(' or ')}): ${JSON.stringify(body).slice(0, 400)}`);
  }
  return body;
}

async function expectStatus(response: APIResponse, expected: number, what: string): Promise<unknown> {
  const body = await bodyOf(response);
  if (response.status() !== expected) {
    const snippet = typeof body === 'string' ? body.slice(0, 300) : JSON.stringify(body).slice(0, 300);
    throw new Error(`${what}: expected HTTP ${expected}, got ${response.status()} — ${snippet}`);
  }
  return body;
}

function field<T>(body: unknown, path: string, check: (v: unknown) => v is T, what: string): T {
  const value = path.split('.').reduce<unknown>((acc, key) => (acc && typeof acc === 'object' ? (acc as Record<string, unknown>)[key] : undefined), body);
  if (!check(value)) {
    throw new Error(`${what}: response field '${path}' is missing or has the wrong type (spec: docs/api/openapi.json) — ${JSON.stringify(body).slice(0, 300)}`);
  }
  return value;
}
const isString = (v: unknown): v is string => typeof v === 'string' && v.length > 0;
const isBoolean = (v: unknown): v is boolean => typeof v === 'boolean';
const ROLES: ReadonlyArray<UserRole> = ['technician', 'manager', 'admin', 'root'];
const STATUSES: ReadonlyArray<UserStatus> = ['pending', 'active', 'inactive', 'archived'];
const isRole = (v: unknown): v is UserRole => isString(v) && (ROLES as ReadonlyArray<string>).includes(v);
const isStatus = (v: unknown): v is UserStatus => isString(v) && (STATUSES as ReadonlyArray<string>).includes(v);

/**
 * Email + password login → tokens.
 *
 * `POST /auth/sign-in` — body SignInDto `{ email, password }` (both required, password
 * minLength 12) → 200 SignInResponseDto `{ access: { token, expiresIn }, refresh: { … } }`.
 * The bearer for every other call is `access.token`.
 *
 * Why not `/auth/sign-in/email` (named in docs/environments.md and decisions.md)?
 * Its body is SignInEmailDto = `{ email }` only — no password field in the spec, and DEV
 * confirms it (2026-09-21: 422 with email rules only). It is the email-only/OTP entry,
 * not the password login. The admin SPA itself posts `{ email, password }` to
 * `auth/sign-in` (bundle: signIn.url.byEmail). Both the repo spec and the live spec agree.
 */
export async function apiLogin(request: APIRequestContext, email: string, password: string): Promise<SignInResponse> {
  const what = 'POST /auth/sign-in';
  const response = await request.post(`${apiBaseUrl()}/auth/sign-in`, { data: { email, password } });
  // The spec says 200; DEV answers **201** (observed 2026-09-21, both roles). The real API
  // wins over the spec for what exists today, so both are accepted and anything else throws
  // with the body — a 401 must never be mistaken for a session.
  const body = await expectAnyStatus(response, [200, 201], what);
  return {
    access: { token: field(body, 'access.token', isString, what), expiresIn: field(body, 'access.expiresIn', isString, what) },
    refresh: { token: field(body, 'refresh.token', isString, what), expiresIn: field(body, 'refresh.expiresIn', isString, what) },
    ...(typeof (body as { isPhonePrimary?: unknown }).isPhonePrimary === 'boolean'
      ? { isPhonePrimary: (body as { isPhonePrimary: boolean }).isPhonePrimary }
      : {}),
  };
}

/** A request context bound to API_BASE_URL with `Authorization: Bearer <token>`. Dispose it when done. */
export async function apiRequest(token: string): Promise<APIRequestContext> {
  return playwrightRequest.newContext({
    baseURL: apiBaseUrl(),
    extraHTTPHeaders: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
  });
}

/**
 * `POST /auth/refresh-token` (bearer) → 200 SignInResponseDto. The spec defines no
 * request body; the SPA sends the refresh token as the bearer (bundle: refreshToken
 * config, check401 "Token has expired"). Pass the REFRESH token's context.
 */
export async function apiRefresh(api: APIRequestContext): Promise<SignInResponse> {
  const what = 'POST /auth/refresh-token';
  const body = await expectStatus(await api.post('/auth/refresh-token'), 200, what);
  return {
    access: { token: field(body, 'access.token', isString, what), expiresIn: field(body, 'access.expiresIn', isString, what) },
    refresh: { token: field(body, 'refresh.token', isString, what), expiresIn: field(body, 'refresh.expiresIn', isString, what) },
  };
}

/** `GET /user/me` (bearer) → 200 profile. Consumed: `id`, `role` (enum), optional email/name. */
export async function me(api: APIRequestContext): Promise<Me> {
  const what = 'GET /user/me';
  const body = await expectStatus(await api.get('/user/me'), 200, what);
  const b = body as Record<string, unknown>;
  return {
    id: field(body, 'id', isString, what),
    role: field(body, 'role', isRole, what),
    ...(isString(b.email) ? { email: b.email } : {}),
    ...(isString(b.firstName) ? { firstName: b.firstName } : {}),
    ...(isString(b.lastName) ? { lastName: b.lastName } : {}),
    ...(isBoolean(b.isTwoFAActive) ? { isTwoFAActive: b.isTwoFAActive } : {}),
  };
}

/**
 * `POST /auth/forgot-password` (no auth) — body ForgotPasswordDto `{ email }` (`phone`
 * is the mobile alternative, not used here) → 200 `{ success, message?, messages?, error? }`.
 * Observed on DEV 2026-09-21: an unknown email answers 404 "User is not found" — the API
 * does enumerate accounts, unlike SRS FR-AUTH-FP-05/08. This helper reports that as a
 * thrown error with the body; whether the UI hides it is a question for the module.
 */
export async function requestPasswordReset(request: APIRequestContext, email: string): Promise<SuccessResponse> {
  const what = 'POST /auth/forgot-password';
  const body = await expectStatus(await request.post(`${apiBaseUrl()}/auth/forgot-password`, { data: { email } }), 200, what);
  return { success: field(body, 'success', isBoolean, what), ...(body as Omit<SuccessResponse, 'success'>) };
}

/**
 * Seed: `POST /user` (bearer, "Admin only") — body: the spec's optional fields
 * (email, phone, password ≥ 12 chars, firstName, lastName, role, status, settings); it
 * marks none as required, so the caller decides and the server validates → 201 with
 * `id`, `role`, `status` (required in the spec). Returns those plus `email` if present.
 * Root creates Root/Manager users in the admin flow (SRS 3.1.1.1) — a created user is
 * `pending` until the set-password link is used, unless `status`/`password` are set.
 */
export async function createUser(api: APIRequestContext, input: CreateUserInput): Promise<CreatedUser> {
  const what = 'POST /user';
  const body = await expectStatus(await api.post('/user', { data: input }), 201, what);
  const email = (body as { email?: unknown }).email;
  return {
    id: field(body, 'id', isString, what),
    role: field(body, 'role', isRole, what),
    status: field(body, 'status', isStatus, what),
    ...(isString(email) ? { email } : {}),
  };
}

/**
 * Cleanup: `DELETE /user/{id}` (bearer, "Manager+") → 200 `{ success }`. The spec says
 * "permanently removes a user OR marks them as deleted"; `DELETE /user/full-delete/{id}`
 * exists with the same contract for the hard variant — `full: true` uses it.
 */
export async function deleteUser(api: APIRequestContext, id: string, options: { full?: boolean } = {}): Promise<SuccessResponse> {
  const path = options.full ? `/user/full-delete/${encodeURIComponent(id)}` : `/user/${encodeURIComponent(id)}`;
  const what = `DELETE ${path}`;
  const body = await expectStatus(await api.delete(path), 200, what);
  return { success: field(body, 'success', isBoolean, what), ...(body as Omit<SuccessResponse, 'success'>) };
}

/**
 * `POST /user/{id}/resend-link` (bearer) → 200 `{ success }` — re-sends the activation /
 * verification email for a pending user. The way to (re)trigger a set-password email
 * for a seeded user without the UI (feeds utils/mailbox.ts → SetPasswordPage.openFromLink).
 */
export async function resendActivationLink(api: APIRequestContext, userId: string): Promise<SuccessResponse> {
  const what = `POST /user/${userId}/resend-link`;
  const body = await expectStatus(await api.post(`/user/${encodeURIComponent(userId)}/resend-link`), 200, what);
  return { success: field(body, 'success', isBoolean, what), ...(body as Omit<SuccessResponse, 'success'>) };
}

/**
 * Seed: `POST /tag` (bearer) — body `{ name }` (required, maxLength 255) → 201. The spec
 * marks `createdAt`, `updatedAt`, `user` required and `id` optional; cleanup needs `id`,
 * so a 201 without it throws rather than leaving an orphan tag behind.
 */
export async function createTag(api: APIRequestContext, name: string): Promise<CreatedTag> {
  const what = 'POST /tag';
  const body = await expectStatus(await api.post('/tag', { data: { name } }), 201, what);
  const tagName = (body as { name?: unknown }).name;
  return { id: field(body, 'id', isString, what), ...(isString(tagName) ? { name: tagName } : {}) };
}

/** Cleanup: `DELETE /tag/{id}` (bearer) → 200 `{ success }`. */
export async function deleteTag(api: APIRequestContext, id: string): Promise<SuccessResponse> {
  const what = `DELETE /tag/${id}`;
  const body = await expectStatus(await api.delete(`/tag/${encodeURIComponent(id)}`), 200, what);
  return { success: field(body, 'success', isBoolean, what), ...(body as Omit<SuccessResponse, 'success'>) };
}
