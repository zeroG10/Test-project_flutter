/**
 * Test-data helpers. No secrets, no literal emails in specs: a spec asks for
 * `testEmail()` and the mailbox domain comes from the environment.
 */

/** `prefix-<base36 time>-<4 random>` — unique per call, safe in emails, names and URLs. */
export function unique(prefix: string): string {
  const time = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 6).padEnd(4, '0');
  return `${prefix}-${time}-${rand}`;
}

/**
 * Domain whose inbox the mailbox provider (utils/mailbox.ts) can read. Plus-addressing
 * (`qa+<tag>@domain`) routes every generated address to one inbox. Throws when unset —
 * only at call time, so specs that never need an email are unaffected.
 */
export function testMailboxDomain(): string {
  const domain = process.env.TEST_MAILBOX_DOMAIN;
  if (!domain) {
    throw new Error(
      'TEST_MAILBOX_DOMAIN is not set — needed to build a test email address (qa+<unique>@<domain>). ' +
        'Set it in automation/web/.env (see .env.example). Blocked, not green.',
    );
  }
  return domain.replace(/^@/, '');
}

/** `qa+<unique>@<domain>` — a fresh, plus-addressed test email. */
export function testEmail(mailboxDomain: string = testMailboxDomain()): string {
  return `qa+${unique('t')}@${mailboxDomain.replace(/^@/, '')}`.toLowerCase();
}
