# Release Notes — Math Assistant v1.0.0

**Release date:** 2026-06-15  
**Status:** Frozen

## Overview

Math Assistant v1.0 is the first frozen release of the full MVP platform: a web application for managing game mathematics models, running Monte Carlo simulations, and reviewing analytical reports — built on the certified **`runtime-core@1.8.0`** engine.

This release contains **no new features** and **no engine modifications** beyond the prior engine freeze.

## Component versions

| Component | Version | Git tag |
|-----------|---------|---------|
| Runtime Core | `runtime-core@1.8.0` | `runtime-core@1.8.0` |
| API | `1.0.0` | `api@1.0.0` |
| Web | `1.0.0` | `web@1.0.0` |

## What's included

### For mathematicians & game designers

- Upload and validate canonical game JSON
- Run simulations with configurable spin counts and seeds
- View RTP, volatility, exposure, feature/jackpot analytics
- Export results (CSV, JSON, PDF)

### For teams

- Multi-tenant organizations with role-based access
- Audit log of platform actions
- Notification center for simulation and org events
- User settings (profile, password, theme)

### For operators

- Docker Compose production stack (PostgreSQL, API, web, Prometheus, Grafana)
- Health and readiness endpoints (`/health`, `/health/ready`)
- Prometheus metrics and Grafana dashboard
- Optional Sentry error monitoring
- Security hardening (rate limits, brute-force protection, security headers)

## Upgrade / install

```bash
export API_JWT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose -f docker-compose.prod.yml up -d --build
```

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) and [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md).

## Breaking changes

None — initial v1.0 release.

## Known limitations

- AI assistant (Phase 14 roadmap) not included in v1.0
- In-process simulation workers (scale vertically via `API_SIMULATION_WORKER_COUNT`)
- Refresh tokens stored in browser `localStorage` (see security docs for hardening path)

## Verification

- API integration tests: `cd packages/api && uv run pytest tests/api`
- Web unit tests: `cd packages/web && npm test`
- E2E: `cd e2e && npm test`
- Engine golden suite: CI `golden-runtime.yml`

## Documentation index

| Document | Purpose |
|----------|---------|
| [USER_GUIDE.md](./USER_GUIDE.md) | End-user guide |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Install & configure |
| [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md) | Incidents & backups |
| [BETA_READINESS_CHECKLIST.md](./BETA_READINESS_CHECKLIST.md) | Pre-production checklist |
| [VERSION_1.0_CHECKLIST.md](./VERSION_1.0_CHECKLIST.md) | v1.0 freeze sign-off |
| [ENGINE_RELEASE_v1.0.md](./ENGINE_RELEASE_v1.0.md) | Engine freeze declaration |

## Support

Internal beta — refer to operations runbook for incident response.
