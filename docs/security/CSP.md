# Content Security Policy (CSP)

## Current state

- API returns security headers via `SecurityHeadersMiddleware` (frame denial, nosniff, referrer policy).
- nginx serves the SPA with matching headers; **full CSP is not yet enforced** to avoid breaking Vite dev and inline hydration during beta.

## Recommended production CSP (nginx)

Add when serving built static assets only:

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://*.sentry.io; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
```

Adjust `connect-src` if API is on a different origin or Sentry DSN differs.

## Directives explained

| Directive | Purpose |
|-----------|---------|
| `default-src 'self'` | Default allowlist for assets |
| `script-src 'self'` | Block inline/eval scripts (use nonces if needed later) |
| `connect-src` | API, Sentry, WebSocket (if added) |
| `frame-ancestors 'none'` | Clickjacking protection (aligns with `X-Frame-Options`) |

## Rollout

1. Deploy in **Report-Only** mode first: `Content-Security-Policy-Report-Only`
2. Monitor browser console violations in staging
3. Enforce blocking CSP after zero critical violations

## Sentry

If using Sentry browser SDK, include `https://*.ingest.sentry.io` in `connect-src`.
