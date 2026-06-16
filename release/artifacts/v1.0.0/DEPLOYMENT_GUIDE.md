# Deployment Guide

This guide covers deploying the Math Assistant MVP platform with Docker Compose, PostgreSQL, and production recommendations.

## Architecture

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | FastAPI backend |
| `web` | 5173 (dev) / 80 (prod) | React SPA |
| `postgres` | 5432 | PostgreSQL database |

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
# From repository root
docker compose up -d
```

Migrations run automatically on API container startup. The API is available at `http://localhost:8000` and the web UI at `http://localhost:5173`.

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
| `API_DATABASE_URL` | Yes (prod) | `postgresql+asyncpg://postgres:postgres@localhost:5432/math_assistant` | Async SQLAlchemy URL |
| `API_JWT_SECRET_KEY` | Yes (prod) | `dev-only-change-me-in-production` | JWT signing secret (≥32 bytes) |
| `API_SIMULATION_WORKER_COUNT` | No | `1` | In-process simulation workers |
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

- Increase `API_SIMULATION_WORKER_COUNT` for more parallel simulations
- Run multiple API instances behind a load balancer (shared PostgreSQL required)
- Replace the in-memory simulation queue with Redis/Celery for multi-node deployments

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
