/** Redacted diagnostics only. QA_REDACT_FIELDS adds comma-separated field names.
 * Arbitrary non-JSON bodies are omitted; assertions always receive the original data.
 * Playwright traces and arbitrary test logs are outside this helper.
 */
const REDACTED = '[REDACTED]';
const FIELDS = [
  'authorization', 'proxy-authorization', 'cookie', 'set-cookie', 'password', 'passwd',
  'token', 'access_token', 'refresh_token', 'id_token', 'api_key', 'x-api-key',
  'secret', 'client_secret', 'session', 'session_id', 'csrf', 'x-csrf-token',
];
const normalise = (key: string) => key.toLowerCase().replace(/[^a-z0-9]/g, '');
const fields = () => [...FIELDS, ...(process.env.QA_REDACT_FIELDS || '').split(',')]
  .map((key) => key.trim()).filter(Boolean);

function sensitive(key: string): boolean {
  const name = normalise(key);
  return fields().some((key) => normalise(key) === name) ||
    /(?:token|secret|password|apikey)$/.test(name);
}

export function safeText(value: string): string {
  const keys = fields().sort((a, b) => b.length - a.length)
    .map((key) => key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  const pattern = new RegExp(
    `(["']?(?:${keys})["']?\\s*[:=]\\s*)("[^"]*"|'[^']*'|[^\\s,;&}]+)`, 'gi',
  );
  return value.replace(/\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+/gi, '$1 [REDACTED]')
    .replace(pattern, (_match, prefix: string) => prefix + REDACTED);
}

export function redact(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(redact);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) =>
      [key, sensitive(key) ? REDACTED : redact(item)]));
  }
  return typeof value === 'string' ? safeText(value) : value;
}

export function safeUrl(value: string): string {
  const method = value.match(/^([A-Z]+)\s+/)?.[0] || '';
  const target = value.slice(method.length);
  try {
    const absolute = /^[a-z][a-z\d+.-]*:\/\//i.test(target);
    const url = new URL(target, 'https://redaction.invalid');
    url.username = '';
    url.password = '';
    url.hash = '';
    for (const key of Array.from(url.searchParams.keys())) url.searchParams.set(key, REDACTED);
    return method + safeText(absolute ? url.toString() : url.pathname + url.search);
  } catch {
    return '[URL omitted]';
  }
}

export function safeBody(value: unknown): string {
  return value !== null && typeof value === 'object'
    ? JSON.stringify(redact(value)).slice(0, 2000)
    : '[non-structured body omitted]';
}
