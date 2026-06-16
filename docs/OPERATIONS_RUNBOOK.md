# Operations Runbook

Operational procedures for the Math Assistant platform during internal beta and early production.

## Service map

| Service | Port (prod compose) | Health |
|---------|---------------------|--------|
| Web (nginx) | 8080 | `GET /` |
| API | internal 8000 | `GET /health`, `GET /health/ready` |
| PostgreSQL | internal 5432 | `pg_isready` |
| Prometheus | 9090 | `GET /-/healthy` |
| Grafana | 3000 | UI login |

Start production stack:

```bash
export API_JWT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose -f docker-compose.prod.yml up -d --build
```

## Incident response

### Severity levels

1. **SEV-1** — Platform unavailable, data loss risk, auth bypass
2. **SEV-2** — Simulations failing broadly, elevated 5xx, queue stalled
3. **SEV-3** — Degraded latency, single-tenant issues, non-critical UI defects

### Response steps

1. Acknowledge alert (Sentry, Grafana, or on-call channel).
2. Check `GET /health/ready` and Grafana **Math Assistant Platform** dashboard.
3. Inspect API logs (structured JSON) filtered by `request_id` when available.
4. Check PostgreSQL connectivity and disk usage.
5. Check simulation worker queue metric `simulation_worker_queue_size`.
6. Mitigate: scale workers (`API_SIMULATION_WORKER_COUNT`), restart API, or fail over DB.
7. Document timeline, root cause, and follow-up in incident notes.

### Common failures

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| 503/timeout on API | DB down or pool exhausted | Verify Postgres, restart API |
| Simulations stuck pending | Worker crash / queue backlog | Restart API, review worker logs |
| 401 spikes | Token expiry / clock skew | Verify JWT secret unchanged, NTP |
| 429 on login | Brute-force or rate limit | Expected under attack; tune limits if false positive |

## Backup procedures

### PostgreSQL logical backup

```bash
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres -Fc math_assistant > backups/math_assistant-$(date +%Y%m%d-%H%M).dump
```

Schedule daily via cron or managed backup service. Retain 30 days minimum for beta.

### What to back up

- PostgreSQL (`games`, `simulations`, `users`, `organizations`, audit/notifications)
- Environment secrets (JWT key, metrics token, Sentry DSN) in secret manager
- Grafana dashboards (provisioned from `monitoring/grafana/dashboards/`)

## Restore procedures

1. Stop API to prevent writes: `docker compose -f docker-compose.prod.yml stop api`
2. Restore database:

```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_restore -U postgres -d math_assistant --clean --if-exists < backups/your.dump
```

3. Run migrations if restoring to empty DB: `docker compose exec api uv run alembic upgrade head`
4. Start API: `docker compose -f docker-compose.prod.yml start api`
5. Verify `/health/ready` and run smoke E2E tests.

## Queue recovery procedures

Simulation jobs use either **in-process workers** (`API_SIMULATION_EXECUTION_BACKEND=inprocess`) or **Celery** (`distributed`). See [CELERY_WORKER_SCALING.md](operations/CELERY_WORKER_SCALING.md) for distributed troubleshooting.

### In-process mode

1. Check queue depth: `simulation_worker_queue_size` in Prometheus/Grafana.
2. List stuck simulations via API (`status=pending|running`).
3. Restart API container to reinitialize dispatcher and workers.
4. If simulations remain `running` after restart, mark failed manually only after confirming no active worker (DB inspection).
5. Re-submit failed simulations from UI after root cause is fixed.

### Distributed (Celery) mode

1. `GET /simulations/queue` — pending and running counts.
2. `GET /workers/health` — verify `activeWorkers > 0`.
3. `GET /simulations/{id}/shards` — per-shard status.
4. Restart workers: `docker compose ... restart simulation-worker` or scale with `--force-recreate`.
5. Retry failed shards: `POST /simulations/{id}/retry`.
6. Cancel stuck runs: `POST /simulations/{id}/cancel`.

**Do not** modify `runtime_core` or simulation execution logic during recovery.

## Database health checks

- **Liveness:** `GET /health` — process up
- **Readiness:** `GET /health/ready` — includes `database: ok`
- **Postgres:** `pg_isready` in compose healthcheck

## Migration rollback

1. Identify target revision: `uv run alembic history`
2. Roll back one revision: `uv run alembic downgrade -1`
3. Roll back to revision: `uv run alembic downgrade <revision>`
4. Restore from backup if downgrade is unsafe or data migration is irreversible.

Always test downgrade on staging before production.

## Monitoring & alerting

See `docs/DEPLOYMENT_GUIDE.md` and Grafana dashboard **Math Assistant Platform**.

### Alerting (recommended)

| Alert | Condition | Channel |
|-------|-----------|---------|
| API 5xx rate | > 1% for 5m | Pager / Slack |
| Readiness degraded | `database != ok` | Pager |
| Queue backlog | `simulation_worker_queue_size > 50` for 10m | Slack |
| Sentry new issue | Production environment | Email / Slack |

## Security operations

- Rotate `API_JWT_SECRET_KEY` only with planned session invalidation (all users re-login).
- Set `API_METRICS_BEARER_TOKEN` in production; scrape with Authorization header.
- Enable `API_ENABLE_HSTS=true` when TLS terminates in front of API.
- Review audit log (`/audit`) for suspicious `auth.login` patterns.
