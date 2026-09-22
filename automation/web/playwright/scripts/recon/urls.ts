/** URL normalisation, route patterns and scope filters for the crawler. */

const VOLATILE_PARAMS = new Set([
  '_',
  'ts',
  'timestamp',
  'nonce',
  'cb',
  'cachebust',
  'rand',
  'random',
  'fbclid',
  'gclid',
  'msclkid',
  '_ga',
  '_gl',
]);

const ID_SEGMENT: readonly RegExp[] = [
  /^\d+$/,
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
  /^[0-9a-f]{16,}$/i,
  /^(?=.*\d)[A-Za-z0-9_-]{20,}$/,
];

const AUTH_ROUTE = /(^|\/)(login|log-in|signin|sign-in|auth|authenticate|sso)(\/|$|\?)/i;
const BUILTIN_DENY = /(^|\/)(logout|log-out|signout|sign-out)(\/|$|\?)/i;

export function isIdLike(segment: string): boolean {
  return ID_SEGMENT.some((r) => r.test(segment));
}

/**
 * Same-origin http(s) URL with volatile query params stripped and params sorted.
 * Hash kept only when the app is hash-routed (`#/…`). Returns null for anything
 * off-origin or non-http.
 */
export function normaliseUrl(raw: string, base: URL, hashRouted: boolean): URL | null {
  let u: URL;
  try {
    u = new URL(raw, base);
  } catch {
    return null;
  }
  if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
  if (u.origin !== base.origin) return null;
  const params = [...u.searchParams.entries()]
    .filter(([k]) => !VOLATILE_PARAMS.has(k.toLowerCase()) && !k.toLowerCase().startsWith('utm_'))
    .sort(([a], [b]) => a.localeCompare(b));
  u.search = '';
  for (const [k, val] of params) u.searchParams.append(k, val);
  if (!(hashRouted && u.hash.startsWith('#/'))) u.hash = '';
  if (u.pathname === '') u.pathname = '/';
  u.username = '';
  u.password = '';
  return u;
}

/** `/items/123?page=2#/x/9` → `/items/:id?page=:id#/x/:id` — the inventory key. */
export function routePattern(u: URL): string {
  const seg = (s: string) => (isIdLike(s) ? ':id' : s);
  const p = u.pathname.split('/').map(seg).join('/');
  const q = [...u.searchParams.entries()].map(([k, v]) => `${k}=${isIdLike(v) ? ':id' : v}`).join('&');
  const h = u.hash ? '#' + u.hash.slice(1).split('/').map(seg).join('/') : '';
  return p + (q ? `?${q}` : '') + h;
}

/** Path + search + hash — what `--allow` / `--deny` are matched against. */
export function routePath(u: URL): string {
  return u.pathname + u.search + u.hash;
}

export function isAuthRoute(pathLike: string): boolean {
  return AUTH_ROUTE.test(pathLike);
}

export function isBuiltinDenied(pathLike: string): boolean {
  return BUILTIN_DENY.test(pathLike);
}

export type FilterVerdict = 'ok' | 'deny' | 'not-allowed';

export function matchesFilters(pathLike: string, allow: RegExp | undefined, deny: RegExp | undefined): FilterVerdict {
  if (deny && deny.test(pathLike)) return 'deny';
  if (allow && !allow.test(pathLike)) return 'not-allowed';
  return 'ok';
}
