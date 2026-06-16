# Beta Readiness Checklist

Use this checklist before inviting internal beta users or first customers.

## Functional validation

- [ ] User can register, login, logout, refresh session
- [ ] User can create/switch organizations
- [ ] User can create games and upload validated versions
- [ ] Validation failures surface clearly in UI
- [ ] User can create simulations and monitor progress
- [ ] Completed simulations show RTP, volatility, exposure, feature/jackpot analytics
- [ ] Notifications appear for simulation complete/fail
- [ ] Settings (profile, password, theme, notification prefs) work
- [ ] Audit log records key actions
- [ ] Exports: simulation CSV/JSON/PDF, version canonical JSON
- [ ] Playwright E2E suite passes: `cd e2e && npm test`

## Security validation

- [ ] `API_JWT_SECRET_KEY` is strong (≥32 bytes) and not committed
- [ ] Security headers present on API and nginx (`X-Frame-Options`, `nosniff`, etc.)
- [ ] Auth rate limiting active (`API_RATE_LIMIT_AUTH_PER_MINUTE`)
- [ ] Brute-force lockout verified (`API_BRUTE_FORCE_MAX_ATTEMPTS`)
- [ ] Refresh token rotation + reuse detection tested
- [ ] Request body size limit enforced (`API_MAX_REQUEST_BODY_BYTES`)
- [ ] `/metrics` protected with bearer token in production
- [ ] CSRF strategy documented (`docs/security/CSRF_STRATEGY.md`)
- [ ] CSP documented (`docs/security/CSP.md`)
- [ ] Frontend storage review complete (`docs/security/FRONTEND_SECURITY_REVIEW.md`)
- [ ] Sentry configured for API and web (optional but recommended)

## Performance validation

- [ ] API benchmark run: `python scripts/benchmark_api.py --users 100`
- [ ] 100 concurrent dashboard requests complete without 5xx
- [ ] 100 simultaneous simulations queued (adjust workers as needed)
- [ ] p95 API latency documented in `docs/PERFORMANCE_BETA_VALIDATION.md`
- [ ] Simulation duration p95 acceptable for beta spin counts

## Operational readiness

- [ ] `docker-compose.prod.yml` deploys successfully
- [ ] Migrations run on API startup (`alembic upgrade head`)
- [ ] `/health/ready` returns `database: ok`
- [ ] Prometheus scrapes API metrics
- [ ] Grafana dashboard imported and visible
- [ ] Backup procedure tested (dump + restore on staging)
- [ ] Operations runbook reviewed (`docs/OPERATIONS_RUNBOOK.md`)
- [ ] On-call / incident channel defined

## Deployment validation

- [ ] TLS/HTTPS in front of web (reverse proxy or load balancer)
- [ ] Environment variables documented in `docs/DEPLOYMENT_GUIDE.md`
- [ ] Database connection string uses production credentials
- [ ] `runtime_core` unchanged (frozen engine)
- [ ] Smoke test on production URL after deploy

## Sign-off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Engineering | | | |
| Operations | | | |
| Product | | | |
