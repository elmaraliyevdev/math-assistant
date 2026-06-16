# Alerting Documentation

## Sentry alerts

Configure in Sentry project settings:

| Alert | Trigger | Action |
|-------|---------|--------|
| New issue in production | First seen, `environment=production` | Email / Slack |
| Error spike | > 50 events in 1h | On-call channel |
| Simulation job failure | Message contains `simulation` + unhandled exception | Engineering channel |

**API:** `API_SENTRY_DSN`, `API_SENTRY_ENVIRONMENT=production`  
**Web:** `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT=production`

Scrub `Authorization` headers and tokens in Sentry before beta.

## Queue failures

Monitor Prometheus metrics:

- `simulation_worker_queue_size` — in-process dispatcher depth (stays **0** in distributed/Celery mode)
- `simulations_total{status="failed"}` — rate increase vs completed

**Distributed deployments:** use `GET /simulations/queue` and `GET /workers/health` as primary queue signals. See [CELERY_WORKER_SCALING.md](../operations/CELERY_WORKER_SCALING.md).

**Suggested Grafana alert (in-process):**

```
simulation_worker_queue_size > 50
```

**Suggested alert (distributed):** synthetic check on `/simulations/queue` where `pendingTasks > 50` for 10 minutes, or `/workers/health` returns `healthy: false`.

**Response:** See `docs/OPERATIONS_RUNBOOK.md` → Queue recovery.

## Database availability

- `GET /health/ready` — alert if `status != ready` or `checks.database != ok`
- Postgres container healthcheck failures in orchestrator

**Suggested check interval:** 30s from synthetic monitoring or k8s probe.

## API error rate

```
sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.01
```

## Notification channels

Document owner contacts and escalation path in your team wiki; link Grafana contact points to the same channels.
