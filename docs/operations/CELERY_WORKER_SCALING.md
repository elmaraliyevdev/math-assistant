# Celery Worker Scaling Guide

Operational reference for scaling distributed simulation workers (Redis + Celery) on Docker Compose deployments.

**Related docs:** [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) · [HETZNER.md](../deployment/HETZNER.md) · [OPERATIONS_RUNBOOK.md](../OPERATIONS_RUNBOOK.md) · [ALERTING.md](../monitoring/ALERTING.md)

---

## Architecture recap

```
POST /simulations
  → API enqueues orchestrate_simulation (Celery)
  → orchestrator splits into shard tasks (run_simulation_shard)
  → N simulation-worker containers consume from Redis queue "simulations"
  → aggregator finalizes when all shards complete
```

Each `simulation-worker` container runs:

```text
celery -A app.distributed.celery_app worker --loglevel=info -Q simulations --concurrency=1
```

**Scaling model:** increase **container replicas** (`--scale simulation-worker=N`). Per-container concurrency stays at **1** so each worker runs one CPU-bound shard at a time. Total parallel shard capacity = `N` containers × `1` concurrency.

---

## Increasing workers in Docker Compose

### Development (`docker-compose.yml`)

```bash
# Start distributed stack with MVP settings
docker compose --env-file deploy/mvp.env --profile mvp up -d --build

# Scale to 4 worker containers
docker compose --env-file deploy/mvp.env --profile mvp up -d --scale simulation-worker=4
```

### Production (`docker-compose.prod.yml`)

```bash
docker compose -f docker-compose.prod.yml \
  --env-file deploy/enterprise.env \
  --profile enterprise \
  up -d --build --scale simulation-worker=4
```

### Verify scale

```bash
docker compose -f docker-compose.prod.yml --profile enterprise ps simulation-worker
```

You should see multiple `simulation-worker` containers (e.g. `project-simulation-worker-1` … `project-simulation-worker-4`).

### Confirm workers are registered

```bash
# Requires auth — use a developer JWT
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/workers | jq

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/workers/health | jq
```

Expected: `activeWorkers` matches the number of running worker containers (when Redis is healthy).

### Scale down

```bash
docker compose -f docker-compose.prod.yml \
  --env-file deploy/enterprise.env \
  --profile enterprise \
  up -d --scale simulation-worker=2
```

Running shard tasks on removed containers will fail and can be retried via `POST /simulations/{id}/retry` after workers stabilize.

### Important constraints

| Constraint | MVP (`deploy/mvp.env`) | Enterprise (`deploy/enterprise.env`) |
|------------|------------------------|-------------------------------------|
| Active simulations | Max **2** concurrent (`API_MAX_ACTIVE_SIMULATIONS=2`) | Unlimited (`API_MAX_ACTIVE_SIMULATIONS=0`) |
| Spins per simulation | Max **10M** | Configurable (default **100M**) |
| Default worker replicas | **1** | **4** (via `--scale`) |

Adding workers does not raise MVP concurrency limits — upgrade to enterprise when you need more than two simultaneous simulations.

### Environment variables (reference)

| Variable | Purpose |
|----------|---------|
| `API_SIMULATION_EXECUTION_BACKEND=distributed` | Required for Celery workers |
| `API_REDIS_URL` | Celery broker and result backend |
| `API_DEPLOYMENT_MODE` | `mvp` or `enterprise` — controls API safeguards |
| `API_SIMULATION_WORKER_COUNT` | In-process workers only (ignored when `distributed`) |

---

## Recommended worker counts by CPU

Simulation shards are **CPU-bound** (`runtime_core`). Reserve cores for PostgreSQL, Redis, the API, and the OS.

| Server vCPUs | Reserved for platform | Recommended `simulation-worker` replicas |
|--------------|----------------------|------------------------------------------|
| 2 | 1 | **1** |
| 4 | 1–2 | **1–2** |
| 8 | 2 | **4–6** |
| 16 | 2–4 | **8–12** |
| 32+ | 4 | **16–24** (measure before going higher) |

**Rule of thumb:** `workers ≈ vCPUs − 2`, then tune from observed CPU and queue latency.

Signs you need more workers:

- `GET /simulations/queue` shows rising `pendingTasks` while `runningTasks` stays at worker count
- Shard progress stalls with all workers showing `activeTasks: 1`
- Host CPU is not saturated but queue depth grows

Signs you have too many workers:

- CPU pegged at 100% with context-switch overhead
- PostgreSQL connection pressure or OOM kills
- Diminishing throughput (shard contention on DB writes)

---

## Hetzner sizing recommendations

Hetzner Cloud **CX** (shared vCPU) is sufficient for most workloads. Use **CCX** (dedicated vCPU) when running continuous 10M+ spin batches or many concurrent enterprise simulations.

| Profile | Hetzner type | vCPU | RAM | Worker replicas | Typical use |
|---------|--------------|------|-----|-----------------|-------------|
| MVP | **CX33** | 4 | 8 GB | **1** | ≤2 concurrent sims, ≤10M spins |
| Light enterprise | **CX43** | 8 | 16 GB | **4** | Small team, moderate throughput |
| Production | **CX53** | 16 | 32 GB | **8–12** | Multiple large simulations |
| Heavy / certification | **CCX33+** | 8+ dedicated | 32+ GB | **6–8+** | Sustained CPU load, predictable latency |

### Single-server vs split

On a **single** Hetzner server, run the full Compose stack (postgres, redis, api, workers, web). Do not expose Redis or PostgreSQL on the public interface.

When simulations routinely exceed ~70% CPU for hours, consider:

1. Upgrading instance type (vertical scale)
2. Moving PostgreSQL to [Hetzner Managed Database](https://www.hetzner.com/cloud/managed-databases)
3. Running workers on a second CX/CCX node sharing the same Redis/Postgres endpoints (advanced)

See [HETZNER.md](../deployment/HETZNER.md) for initial MVP provisioning.

---

## Redis memory sizing

Redis serves as **Celery broker** and **result backend** (`API_REDIS_URL`). Task payloads are small JSON (`simulation_id`, `shard_index`); results are short status strings.

### Baseline estimates

| Component | Approximate size |
|-----------|------------------|
| Queued orchestration task | ~0.5–2 KB |
| Queued shard task | ~0.5–2 KB |
| Celery result entry (TTL) | ~0.5–1 KB |
| Redis overhead | ~20–30% |

**Example:** 500 shard tasks in flight ≈ 500 × 2 KB ≈ **1 MB** payload + overhead. Redis memory pressure usually comes from **result accumulation** or **unbounded queues**, not individual message size.

### Recommended allocations

| Deployment | Worker replicas | Suggested Redis memory |
|------------|-----------------|----------------------|
| MVP | 1 | **256 MB** (default Alpine image is fine) |
| Small enterprise | 2–4 | **512 MB** |
| Medium enterprise | 4–8 | **1 GB** |
| Large / high queue depth | 8+ | **2 GB+** |

### Production Redis settings

For persistent production deployments, consider a `redis.conf` override or managed Redis with:

```conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

Monitor:

```bash
docker compose -f docker-compose.prod.yml exec redis redis-cli INFO memory
docker compose -f docker-compose.prod.yml exec redis redis-cli DBSIZE
```

**Warning signs:** `used_memory` near `maxmemory`, rising `evicted_keys`, or Celery `ConnectionError` / timeout in worker logs.

### Queue inspection (debugging)

```bash
# List keys (broker uses db 0 by default)
docker compose exec redis redis-cli KEYS 'celery*'

# Check list length for the simulations queue (name may vary by Celery version)
docker compose exec redis redis-cli LLEN simulations
```

---

## Troubleshooting stuck simulations

Use this flowchart when a simulation remains `pending` or `running` without progress.

### 1. Check deployment mode and limits

```bash
curl -s http://localhost:8080/api/engine/version | jq '.maxRecommendedSpinCount'
```

| API error / symptom | Cause | Action |
|---------------------|-------|--------|
| `429 ACTIVE_SIMULATION_LIMIT_EXCEEDED` | MVP allows 2 active sims | Wait, cancel a run, or switch to enterprise |
| `400 SIMULATION_SPIN_COUNT_EXCEEDED` | MVP 10M spin cap | Reduce spins or use enterprise |
| API won't start | Redis down in distributed mode | Start Redis; check `API_REDIS_URL` |

### 2. Simulation-level status

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/simulations/$SIMULATION_ID | jq \
  '{status, progressPercentage, completedShards, totalShards, distributedExecution}'

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/simulations/$SIMULATION_ID/shards | jq
```

| Shard pattern | Likely cause |
|---------------|--------------|
| All shards `pending` | Workers not running, Redis unreachable, or orchestration never dispatched |
| Some shards `running`, rest `pending` | Not enough workers; normal if workers < shard count |
| Shards `failed` | Check `errorMessage`; use retry endpoint |
| Shards `completed` but simulation not `completed` | Aggregation issue — check API logs |

### 3. Queue and worker health

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/simulations/queue | jq

curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/workers/health | jq
```

| Observation | Action |
|-------------|--------|
| `healthy: false`, `activeWorkers: 0` | Restart workers; verify Redis |
| `pendingTasks` high, `runningTasks` low | Scale workers (`--scale simulation-worker=N`) |
| `pendingTasks` zero, simulation still `pending` | Check API logs for orchestration errors |

### 4. Container logs

```bash
docker compose -f docker-compose.prod.yml logs --tail=200 simulation-worker
docker compose -f docker-compose.prod.yml logs --tail=100 api
```

Look for: `Redis is unavailable`, `Connection refused`, task tracebacks, or OOM kills.

### 5. Recovery actions

| Action | Endpoint / command |
|--------|-------------------|
| Retry failed shards | `POST /simulations/{id}/retry` |
| Cancel and revoke tasks | `POST /simulations/{id}/cancel` |
| Restart workers | `docker compose ... restart simulation-worker` |
| Full worker recycle | `docker compose ... up -d --scale simulation-worker=N --force-recreate` |

**Do not** modify `runtime_core` or shard seed logic during recovery. Fix infrastructure, then retry.

### 6. Database inspection (last resort)

```sql
SELECT id, status, total_shards, completed_shards, failed_shards, progress_percentage
FROM simulations WHERE status IN ('pending', 'running') ORDER BY created_at;

SELECT shard_index, status, worker_id, error_message
FROM simulation_shards WHERE simulation_id = '<uuid>' ORDER BY shard_index;
```

---

## Monitoring queue depth (Prometheus / Grafana)

Enterprise profile includes Prometheus and Grafana:

```bash
docker compose -f docker-compose.prod.yml \
  --env-file deploy/enterprise.env \
  --profile enterprise \
  up -d
```

- **Grafana:** `http://localhost:3000` (dashboard: **Math Assistant Platform**)
- **Prometheus:** `http://localhost:9090`

### Grafana panels (provisioned)

| Panel | PromQL | Use |
|-------|--------|-----|
| Worker queue size | `simulation_worker_queue_size` | In-process dispatcher depth |
| Simulation throughput | `sum(rate(simulations_total[5m])) by (status)` | Completed vs failed rate |
| Simulation duration p95 | `histogram_quantile(0.95, sum(rate(simulation_duration_seconds_bucket[5m])) by (le))` | End-to-end latency |
| API error rate | `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m]))` | Platform health |

### Distributed mode caveat

When `API_SIMULATION_EXECUTION_BACKEND=distributed`, the Prometheus gauge `simulation_worker_queue_size` reflects the **in-process** dispatcher only and stays at **0**. For Celery deployments, use these sources instead:

#### API queue summary (primary)

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/simulations/queue | jq
```

| Field | Meaning |
|-------|---------|
| `pendingTasks` | DB `pending` simulations + Celery reserved tasks |
| `runningTasks` | Simulations in `running` status |
| `failedTasks` | Failed simulations (platform-wide count) |
| `averageSimulationDurationSeconds` | Rolling 24h average |

Poll this endpoint from synthetic monitoring or export to Prometheus via a blackbox/json exporter if you need historical charts.

#### Worker metrics

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/workers | jq
```

Track `activeWorkers` and per-worker `activeTasks` on the dashboard UI (Simulation detail → Distributed panel) or via API.

#### Prometheus metrics still useful in distributed mode

| Metric | Alert idea |
|--------|------------|
| `simulations_total{status="failed"}` rate | Failure spike |
| `simulation_duration_seconds` p95 | Slow runs |
| `api_requests_total{status=~"5.."}` rate | API errors affecting enqueue |

Suggested alert (from [ALERTING.md](../monitoring/ALERTING.md)):

```promql
# In-process mode only
simulation_worker_queue_size > 50
```

For **distributed** mode, alert on API queue instead (external check):

```text
GET /simulations/queue → pendingTasks > 50 for 10 minutes
```

Or monitor worker health:

```text
GET /workers/health → healthy == false for 2 minutes
```

### Scraping `/metrics`

Production should set `API_METRICS_BEARER_TOKEN` and configure Prometheus with an Authorization header. See `monitoring/prometheus/prometheus.yml` (targets `api:8000`).

```bash
curl -s -H "Authorization: Bearer $METRICS_TOKEN" \
  http://localhost:8000/metrics | grep simulation
```

### Recommended Grafana additions (manual)

Until a dedicated Celery queue metric is exported, create Grafana panels using **Infinity** or **JSON API** datasource pointing at `/simulations/queue`, or run a small cron script that pushes `pendingTasks` to Prometheus via Pushgateway.

---

## Quick reference commands

```bash
# Scale workers to 6
docker compose -f docker-compose.prod.yml \
  --env-file deploy/enterprise.env \
  --profile enterprise \
  up -d --scale simulation-worker=6

# Queue snapshot
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/simulations/queue | jq

# Worker health
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/workers/health | jq

# Redis memory
docker compose -f docker-compose.prod.yml exec redis redis-cli INFO memory | grep used_memory_human

# Worker logs
docker compose -f docker-compose.prod.yml logs -f simulation-worker
```
