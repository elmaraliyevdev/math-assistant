# Deployment Guide

This guide covers deploying the Math Assistant platform with Docker Compose, PostgreSQL, and production recommendations.

## Deployment profiles

Two Compose profiles tailor the stack to your scale. Application safeguards are controlled by `API_DEPLOYMENT_MODE`.

| Profile | Use case | Workers | Active simulation cap | Max spins |
|---------|----------|---------|----------------------|-----------|
| **mvp** | Single-server (Hetzner CX33, etc.) | 1 Celery worker | 2 | 10M |
| **enterprise** | Multi-worker, monitoring | Scalable (`--scale simulation-worker=N`) | Unlimited | Configurable (default 100M) |

### MVP (single server)

```bash
export API_JWT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose --env-file deploy/mvp.env --profile mvp up -d --build
```

Production with restart policies and no exposed DB ports:

```bash
docker compose -f docker-compose.prod.yml --env-file deploy/mvp.env --profile mvp up -d --build
```

### Enterprise

```bash
docker compose -f docker-compose.prod.yml \
  --env-file deploy/enterprise.env \
  --profile enterprise \
  up -d --build --scale simulation-worker=4
```

Includes Prometheus and Grafana (enterprise profile only).

### Local development (no profile)

```bash
docker compose up -d
```

Runs PostgreSQL, API (in-process simulation backend), and web. Redis and Celery workers are **not** started unless you activate `mvp` or `enterprise`.

### Hetzner

Step-by-step instructions for Hetzner Cloud: **[docs/deployment/HETZNER.md](deployment/HETZNER.md)**.

## Architecture

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | FastAPI backend |
| `web` | 5173 (dev) / 80 (prod) | React SPA |
| `postgres` | 5432 | PostgreSQL database |
| `redis` | 6379 | Celery broker (mvp/enterprise profiles) |
| `simulation-worker` | — | Celery worker (mvp/enterprise profiles) |

## Prerequisites

- Docker 24+ and Docker Compose v2
- Node.js 20+ (for local web builds)
- Python 3.13+ with `uv` (for local API development)

## Production release (v1.0)

- **Version file:** `VERSION`
- **Changelog:** `CHANGELOG.md`
- **Release notes:** `docs/RELEASE_NOTES_v1.0.md`
- **Freeze checklist:** `docs/VERSION_1.0_CHECKLIST.md`
- **Tags:** `./release/tag-v1.0.sh` (requires git)
- **Artifacts:** `./scripts/generate-release-artifacts.sh`

## Production Docker Compose

For beta/production with Prometheus and Grafana:

```bash
export API_JWT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose -f docker-compose.prod.yml up -d --build
```

Grafana: `http://localhost:3000` (default admin/admin — change immediately).  
Prometheus: `http://localhost:9090`.

See `docs/OPERATIONS_RUNBOOK.md` and `docs/BETA_READINESS_CHECKLIST.md`.

## Security settings (API)

| Variable | Default | Description |
|----------|---------|-------------|
| `API_SECURITY_HEADERS_ENABLED` | `true` | Security response headers |
| `API_ENABLE_HSTS` | `false` | HSTS (enable behind HTTPS) |
| `API_MAX_REQUEST_BODY_BYTES` | `10485760` | Max request body (10 MiB) |
| `API_RATE_LIMIT_AUTH_PER_MINUTE` | `20` | Per-IP auth endpoint rate limit |
| `API_BRUTE_FORCE_MAX_ATTEMPTS` | `5` | Failed logins before lockout |
| `API_BRUTE_FORCE_LOCKOUT_MINUTES` | `15` | Lockout duration |
| `API_METRICS_BEARER_TOKEN` | unset | Protect `GET /metrics` |

Security documentation: `docs/security/`.

## Quick Start with Docker Compose

```bash
# From repository root — local dev (in-process simulations)
docker compose up -d
```

Migrations run automatically on API container startup. The API is available at `http://localhost:8000` and the web UI at `http://localhost:5173`.

For distributed simulations on a single server:

```bash
docker compose --env-file deploy/mvp.env --profile mvp up -d --build
```

## PostgreSQL Setup

### Production database

1. Create a dedicated database and user:

```sql
CREATE USER math_assistant WITH PASSWORD 'your-secure-password';
CREATE DATABASE math_assistant OWNER math_assistant;
GRANT ALL PRIVILEGES ON DATABASE math_assistant TO math_assistant;
```

2. Set the connection URL:

```bash
API_DATABASE_URL=postgresql+asyncpg://math_assistant:your-secure-password@postgres:5432/math_assistant
```

### Migrations

```bash
cd packages/api
uv run alembic upgrade head
```

## Environment Variables

### API (`packages/api`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_DEPLOYMENT_MODE` | No | `mvp` | `mvp` or `enterprise` — controls safeguard defaults |
| `API_DATABASE_URL` | Yes (prod) | `postgresql+asyncpg://postgres:postgres@localhost:5432/math_assistant` | Async SQLAlchemy URL |
| `API_JWT_SECRET_KEY` | Yes (prod) | `dev-only-change-me-in-production` | JWT signing secret (≥32 bytes) |
| `API_SIMULATION_WORKER_COUNT` | No | `1` | In-process simulation workers |
| `API_MAX_SIMULATION_SPIN_COUNT` | No | `10000000` (mvp) | Hard cap on spins per simulation |
| `API_MAX_ACTIVE_SIMULATIONS` | No | `2` (mvp) | Max concurrent pending/running simulations (`0` = unlimited) |
| `API_SIMULATION_EXECUTION_BACKEND` | No | `inprocess` | `inprocess` or `distributed` |
| `API_REDIS_URL` | No | `redis://localhost:6379/0` | Redis URL (required for distributed backend) |
| `API_LOG_LEVEL` | No | `INFO` | Structlog level |
| `API_SENTRY_DSN` | No | — | Sentry error monitoring DSN |
| `API_SENTRY_ENVIRONMENT` | No | `development` | Sentry environment tag |
| `API_SENTRY_TRACES_SAMPLE_RATE` | No | `0.1` | Sentry performance sampling |

### Web (`packages/web`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `/api` | API base URL |
| `VITE_SENTRY_DSN` | No | — | Sentry DSN for frontend |
| `VITE_SENTRY_ENVIRONMENT` | No | `development` | Sentry environment |

## Production Recommendations

### Security

- Rotate `API_JWT_SECRET_KEY` and use a secrets manager
- Enable HTTPS via a reverse proxy (nginx, Caddy, or cloud load balancer)
- Restrict `GET /metrics` to internal networks only
- Use PostgreSQL SSL (`?ssl=require` in connection URL)

### Observability

- Configure `API_SENTRY_DSN` and `VITE_SENTRY_DSN` for error tracking
- Scrape `GET /metrics` with Prometheus for API request and simulation metrics
- Monitor simulation worker queue depth via `simulation_worker_queue_size`

### Scaling

- **MVP:** keep `simulation-worker` at 1 replica; limits are enforced in the API
- **Enterprise:** `docker compose ... --scale simulation-worker=4`
- Increase `API_SIMULATION_WORKER_COUNT` for more parallel in-process simulations (non-distributed mode)
- Run multiple API instances behind a load balancer (shared PostgreSQL required)
- Use `--profile mvp` or `--profile enterprise` with Redis/Celery for distributed execution

**Operational guide:** [docs/operations/CELERY_WORKER_SCALING.md](operations/CELERY_WORKER_SCALING.md) — worker counts, Hetzner sizing, Redis memory, stuck simulations, queue monitoring.

### Backups

- Enable automated PostgreSQL backups (daily snapshots minimum)
- Export game version canonical JSON periodically for disaster recovery

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness probe |
| `GET /metrics` | Prometheus metrics |
| `GET /engine/version` | Runtime engine version verification |

## Local Development (without Docker)

```bash
# API
cd packages/api
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Web
cd packages/web
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.
