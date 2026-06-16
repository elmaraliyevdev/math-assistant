# CSRF Protection Strategy

## Current architecture

The Math Assistant SPA uses **Bearer JWT access tokens** in the `Authorization` header (via axios interceptors), not cookie-based session authentication for API calls.

Refresh tokens are stored in **localStorage** (`refresh-token-storage`) and sent in JSON body to `/auth/refresh` and `/auth/logout`.

## CSRF risk assessment

| Pattern | CSRF risk |
|---------|-----------|
| API calls with `Authorization: Bearer` | **Low** — browsers do not attach custom headers on cross-site form posts |
| Refresh token in JSON body | **Low** — requires attacker-controlled JS to read storage (XSS vector, not CSRF) |
| Cookie-based auth (not used) | N/A |

## Strategy

1. **Continue header-based API authentication** for all mutating platform routes.
2. **Do not** move access tokens to HttpOnly cookies without implementing double-submit or SameSite strict cookies + CSRF tokens.
3. If cookie sessions are introduced later:
   - Use `SameSite=Strict` or `Lax` for session cookies
   - Add CSRF token (synchronizer pattern) on state-changing requests
   - Validate `Origin` / `Referer` on API for browser requests
4. **CORS** — restrict allowed origins in production when enabling browser cross-origin access (currently same-origin via nginx proxy).

## Operational checks

- Ensure production serves API and web from same site (e.g. `app.example.com` with `/api` proxy).
- Reject unexpected `Origin` headers if CORS is enabled on API directly.
