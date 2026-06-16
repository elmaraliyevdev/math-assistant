# Frontend Security Review

## XSS

| Area | Status | Notes |
|------|--------|-------|
| React rendering | **Good** — JSX escapes by default |
| `dangerouslySetInnerHTML` | **Not used** in platform UI |
| Canonical JSON display | Rendered via controlled `JsonViewer` / text — avoid injecting HTML from user JSON |
| URL handling | Router uses TanStack Router; no `javascript:` URLs in links |

**Recommendation:** Keep avoiding `dangerouslySetInnerHTML`. Sanitize any future rich-text features.

## Token storage

| Token | Storage | Risk |
|-------|---------|------|
| Access token | Zustand memory + axios header | Cleared on tab close; not persisted to disk |
| Refresh token | `localStorage` via `refresh-token-storage` | XSS can exfiltrate — mitigate with CSP + Sentry |

**Recommendation for hardened production:** Move refresh token to HttpOnly `Secure` `SameSite=Strict` cookie with CSRF protection (future phase). Current model is acceptable for internal beta with CSP rollout planned.

## Dependencies

- Run `npm audit` in `packages/web` before beta.
- Pin major versions in lockfile; CI should run audit on PRs.

## API errors

- Error messages displayed via `getErrorMessage` — do not render raw HTML from API.
- Sentry captures 5xx API failures without logging tokens (verify scrubbing in Sentry project settings).

## Third-party scripts

- Sentry SDK only (when `VITE_SENTRY_DSN` set).
- No analytics trackers in beta build.

## Checklist

- [ ] CSP documented and staged for enforcement
- [ ] Refresh token storage risk accepted or migrated
- [ ] Sentry PII scrubbing enabled
- [ ] Production build served over HTTPS only
