/**
 * Mailbox access for email-driven flows (set-password link after user creation,
 * forgot-password reset link). INTERFACE ONLY for now: no provider is implemented.
 * `MAILBOX_PROVIDER` selects the implementation; `none` (default) yields
 * NotConfiguredMailbox, whose every call is Blocked with a pointer to the setup note.
 *
 * Reserved provider names (not implemented yet): `mailosaur`, `mailslurp`, `imap`.
 * Adding one = a class implementing Mailbox + a case in mailbox() + its keys in
 * .env.example. Specs never import a provider class; they call mailbox().
 */

export type ReceivedEmail = {
  subject: string;
  text: string;
  html: string;
  /** Every absolute http(s) URL found in the message (html first, then text), de-duplicated. */
  links: string[];
};

export type WaitForEmailOptions = {
  /** Recipient address the message was sent to (as built by utils/data.ts → testEmail()). */
  to: string;
  /** Match on the subject; omit to accept the first message for `to`. */
  subjectMatches?: string | RegExp;
  /** How long to poll before giving up (Blocked). Provider default if omitted. */
  timeoutMs?: number;
};

export interface Mailbox {
  waitForEmail(options: WaitForEmailOptions): Promise<ReceivedEmail>;
}

export type MailboxProvider = 'none' | 'mailosaur' | 'mailslurp' | 'imap';
const RESERVED: ReadonlyArray<MailboxProvider> = ['mailosaur', 'mailslurp', 'imap'];

export const MAILBOX_NOT_CONFIGURED = 'Blocked: mailbox not configured (see docs/notes/email-automation-setup.md)';

/** Default implementation: every call is Blocked, loudly. */
export class NotConfiguredMailbox implements Mailbox {
  async waitForEmail(options: WaitForEmailOptions): Promise<ReceivedEmail> {
    throw new Error(`${MAILBOX_NOT_CONFIGURED} — waitForEmail(to=${options.to}) has no provider; MAILBOX_PROVIDER=none`);
  }
}

/** The mailbox selected by MAILBOX_PROVIDER (default `none`). */
export function mailbox(provider: string = process.env.MAILBOX_PROVIDER ?? 'none'): Mailbox {
  const name = provider.trim().toLowerCase();
  if (name === '' || name === 'none') return new NotConfiguredMailbox();
  if ((RESERVED as ReadonlyArray<string>).includes(name)) {
    throw new Error(
      `${MAILBOX_NOT_CONFIGURED} — MAILBOX_PROVIDER=${name} is reserved but not implemented yet in utils/mailbox.ts`,
    );
  }
  throw new Error(
    `MAILBOX_PROVIDER='${provider}' is unknown — allowed: none (default), ${RESERVED.join(', ')} (reserved, not implemented)`,
  );
}

/**
 * First link in the email whose URL matches `pattern` (e.g. /set-password|reset/).
 * Throws when none matches — a missing link is a failed precondition, never a skip.
 */
export function extractLink(email: ReceivedEmail, pattern: RegExp): string {
  const link = email.links.find((url) => pattern.test(url));
  if (!link) {
    throw new Error(
      `No link matching ${pattern} in email "${email.subject}" (${email.links.length} link(s): ${email.links.join(', ') || 'none'})`,
    );
  }
  return link;
}

/** Helper for providers: pull absolute http(s) URLs out of html + text, de-duplicated. */
export function collectLinks(html: string, text: string): string[] {
  const found = new Set<string>();
  for (const m of html.matchAll(/href=["']([^"']+)["']/gi)) found.add(m[1]);
  for (const m of `${html}\n${text}`.matchAll(/https?:\/\/[^\s"'<>)\]]+/g)) found.add(m[0]);
  return [...found].filter((u) => /^https?:\/\//.test(u));
}
