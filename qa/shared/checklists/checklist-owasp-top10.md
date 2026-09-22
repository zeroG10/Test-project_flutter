# Checklist — OWASP Top 10 (grey-box QA security)

> Optional module (`modules.security`). Companion to the automated checks in
> `automation/api/tests/security/`. Grey-box QA scope — NOT a pentest.
> Status vocabulary and severity tree: see [CLAUDE.md](../../../CLAUDE.md).

## Metadata

| Field | Value |
|---|---|
| Feature | Whole product (security pass) |
| Platform | shared |
| Scope confirmed by owner | ☐ yes — required before ANY active check |
| Active scanning authorized | ☐ yes / ☐ no (passive only) |
| Last reviewed | YYYY-MM-DD |

> **Before starting:** authorized dev/staging targets only, never production.
> Non-destructive by default (prove IDOR by reading, not deleting). Active scans
> need an explicit owner green light (doctrine rule 5).

## A01 Broken Access Control (highest priority)

- [ ] [CHK-SEC-001] IDOR: other user cannot read another user's object (403/404, never 200) — automated: `test_access_control.py`
- [ ] [CHK-SEC-002] Anonymous cannot reach protected resources (401/403)
- [ ] [CHK-SEC-003] Role boundaries: non-admin cannot call admin endpoints
- [ ] [CHK-SEC-004] Function-level: hidden/disabled UI actions are also blocked server-side

## A02 Cryptographic Failures

- [ ] [CHK-SEC-010] All traffic over HTTPS; no sensitive data in URLs
- [ ] [CHK-SEC-011] No secrets/PII/tokens in responses, logs, or error bodies

## A03 Injection

- [ ] [CHK-SEC-020] SQLi probes on inputs return no DB errors / data leakage
- [ ] [CHK-SEC-021] Stored/reflected XSS in user-controlled fields is escaped

## A04 Insecure Design

- [ ] [CHK-SEC-030] Rate limiting on expensive/paid endpoints (bounded-burst test)
- [ ] [CHK-SEC-031] Business-logic abuse (negative amounts, quantity overflow, replay)

## A05 Security Misconfiguration

- [ ] [CHK-SEC-040] Security headers present (HSTS, X-Content-Type-Options, CSP) — automated: `test_headers.py`
- [ ] [CHK-SEC-041] CORS does not reflect arbitrary Origin with credentials — automated: `test_headers.py`
- [ ] [CHK-SEC-042] Verbose errors / stack traces not exposed to clients
- [ ] [CHK-SEC-043] Cookie flags: Secure, HttpOnly, SameSite

## A06 Vulnerable & Outdated Components

- [ ] [CHK-SEC-050] Dependency scan run; known-vuln libs triaged (no proven exploit → Low/Info)

## A07 Identification & Authentication Failures

- [ ] [CHK-SEC-060] Token invalid after logout
- [ ] [CHK-SEC-061] Token/session expiry enforced
- [ ] [CHK-SEC-062] Password reset token is single-use and time-bound
- [ ] [CHK-SEC-063] Login rate limiting (bounded burst — do NOT lock real accounts)

## A08 Software & Data Integrity Failures

- [ ] [CHK-SEC-070] No insecure deserialization of user-supplied data
- [ ] [CHK-SEC-071] Update/upload paths validate integrity/type

## A09 Logging & Monitoring Failures

- [ ] [CHK-SEC-080] Auth failures and access-control denials are logged (no sensitive data in logs)

## A10 Server-Side Request Forgery (SSRF)

- [ ] [CHK-SEC-090] URL/host inputs are validated against an allowlist; internal ranges blocked

## Severity mapping (when a check fails)

- Auth bypass, IDOR/BOLA, injection, PII leak → **S1** (severity tree branch 1)
- Missing headers, weak rate-limit, verbose errors → **S3** (branch 3)
- Best-practice/outdated deps with no proven exploit → **S4 / Info**
