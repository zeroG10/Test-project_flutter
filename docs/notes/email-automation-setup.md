# Email automation setup — flows that continue in an inbox

Written for: the project QA owner choosing a mailbox provider, and the dev team if option C or E is chosen.

## Why a mailbox is needed

Flows that leave the app and continue in an email (typical: password recovery, account
activation / invitation, email change, magic-link login) can only be automated end to end if
the test can **read the email**. List the product's flows here once known:

| Flow | Trigger | Email | Continues at |
|---|---|---|---|
| `<Password recovery>` | `<Forgot password → email submitted>` | `<reset link>` | `<route the link opens>` |
| `<Account activation>` | `<admin creates a user>` | `<invitation link>` | `<set-password route>` |

Test cases that need the inbox carry `Needs: mailbox` in their structured format. Without a
provider they stay **Blocked** — never faked (CLAUDE.md doctrine rule 3). Record what you learn
about the link (token in path or query, single-use, lifetime, sender, subject) here after the
first real email is observed.

## What the harness already expects (no code change needed to switch provider)

`automation/web/playwright/utils/mailbox.ts` defines the contract:

```ts
waitForEmail({ to, subjectMatches?, timeoutMs? }) → { subject, text, html, links }
extractLink(email, /reset-password/)
```

Selected by `.env`: `MAILBOX_PROVIDER=none|mailosaur|mailslurp|imap|mailpit` and
`TEST_MAILBOX_DOMAIN=<domain the target env delivers to>`. Tests build unique recipients as
`qa+<unique>@<TEST_MAILBOX_DOMAIN>` (`utils/data.ts → testEmail()`), so every run uses fresh
addresses and never collides with another run or a human tester. `none` (default) makes every
mailbox call fail as Blocked with a pointer to this note.

## Options, best first

| # | Option | Determinism | Setup effort | Cost | When to choose |
|---|---|---|---|---|---|
| **A** | **Mailosaur** — test-mail SaaS with a wildcard domain `<serverId>.mailosaur.net`, REST + Node SDK | high | 30 min | paid, trial available | Default choice; works from CI with one API key |
| B | MailSlurp — inboxes created via API, Node SDK | high | 30 min | small free tier, paid above | Same idea as A if the team already has it |
| C | Env mail catcher (Mailpit / MailHog) — the backend on the test env routes ALL outgoing mail into a catcher with an HTTP API | high | 1–2 h for devs, 15 min for QA | free | If devs agree; no real emails leave the env, no third party |
| D | Dedicated Google Workspace / Gmail mailbox + plus-addressing + IMAP (app password) | medium | 1 h | free | Fallback only: polling, rate limits, 2FA / app-password upkeep |
| E | Dev-only backend hook that returns the last token for an address | highest | dev work | free | Fastest tests; must be impossible outside the test env |

Recommendation: **A now**, **C in parallel** if the dev team is willing — it removes the
external dependency and the cost. D only if A/B/C are impossible.

## Option A — Mailosaur, step by step

1. Create an account at mailosaur.com, create a **Server** (e.g. `<project>-dev`). Note its
   **Server ID** and generate an **API key**.
2. Every address `<anything>@<serverId>.mailosaur.net` is delivered to that server —
   no inbox creation needed.
3. In `automation/web/.env` (never committed):
   ```
   MAILBOX_PROVIDER=mailosaur
   MAILOSAUR_API_KEY=<key>
   MAILOSAUR_SERVER_ID=<serverId>
   TEST_MAILBOX_DOMAIN=<serverId>.mailosaur.net
   ```
4. `npm install --save-dev mailosaur` and implement the provider class in `utils/mailbox.ts`
   (one class + one `case` in `mailbox()`; specs never import a provider).
5. Standing recovery account: create a user with email `qa-recovery@<serverId>.mailosaur.net`,
   complete its activation once through the emailed link, set `APP_RECOVERY_EMAIL` in `.env`.
   Recovery tests reset THIS account's password every run and restore it at the end.
6. Confirm with the backend team that the test env really sends email to external domains
   (which provider: SES / SendGrid / …) and that the sender is not sandboxed to a whitelist —
   otherwise option C.
7. CI: add `MAILOSAUR_API_KEY`, `MAILOSAUR_SERVER_ID` as repository secrets and
   `TEST_MAILBOX_DOMAIN` as a variable; the workflow passes them to the test step.

## Option C — env mail catcher (for the dev team)

1. Point the env's SMTP settings at Mailpit (`docker run -p 8025:8025 -p 1025:1025 axllent/mailpit`)
   or MailHog. All outgoing mail is captured; nothing is delivered externally.
2. Expose the HTTP API to the QA runner (VPN or basic auth): Mailpit `GET /api/v1/search?query=to:<address>`.
3. `.env`: `MAILBOX_PROVIDER=mailpit`, `MAILPIT_URL=https://<host>:8025`, `TEST_MAILBOX_DOMAIN=<any domain — the catcher accepts everything>`.
4. Same standing recovery account as A.5.

## Option D — IMAP fallback (only if A/B/C are impossible)

1. Dedicated mailbox, e.g. `qa.automation@<company domain>`, 2-step verification on, an
   **app password** generated for IMAP.
2. Plus-addressing gives unique recipients: `qa.automation+<unique>@<domain>`.
3. `.env`: `MAILBOX_PROVIDER=imap`, `IMAP_HOST=imap.gmail.com`, `IMAP_PORT=993`,
   `IMAP_USER=…`, `IMAP_PASSWORD=<app password>`, `TEST_MAILBOX_DOMAIN=<domain>`.
4. Expect slower tests (polling every 5 s, 90 s timeout) and occasional throttling.

## Rules baked into the tests (do not weaken)

- One fresh link per test case; mailbox-dependent tests run **serial** (`test.describe.configure({ mode: 'serial' })`).
- `waitForEmail` timeout 90 s → the test fails as **Blocked** with the recipient and the time waited; it never passes on a missing email.
- The link is opened exactly as received (no rewriting), and the test asserts the landing page by its own landmark, not by URL alone.
- Cleanup: users created for activation tests are deleted through the API at the end of the test; the recovery account's password is restored.
- Secrets only in `.env` / CI secrets; email bodies captured on failure are attached to the Playwright report, so never use a mailbox that receives real customer mail.

## Decision record

| Date | Provider chosen | Why | Owner |
|---|---|---|---|
| | | | |
