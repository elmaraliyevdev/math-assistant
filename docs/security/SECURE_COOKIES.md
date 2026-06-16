# Secure Cookie Configuration

## Current authentication model

The platform uses **JWT bearer tokens**, not browser session cookies, for API authorization.

| Mechanism | Storage |
|-----------|---------|
| Access token | In-memory (Zustand) |
| Refresh token | `localStorage` |

No authentication cookies are set by the API in the current beta architecture.

## If cookie-based sessions are added

Apply these attributes on all auth cookies:

```
Set-Cookie: session=...; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=...
```

| Flag | Purpose |
|------|---------|
| `HttpOnly` | Prevents JavaScript access (mitigates XSS token theft) |
| `Secure` | HTTPS only |
| `SameSite=Strict` | CSRF mitigation for cross-site requests |
| `Path=/` | Limit cookie scope |

## nginx / reverse proxy

When TLS terminates at the proxy:

- Forward `X-Forwarded-Proto: https` to API if it needs to set cookies.
- Enable `API_ENABLE_HSTS=true` on API or set HSTS at load balancer.

## Logout

Ensure cookie clearing uses matching `Path` and `Domain` attributes.
