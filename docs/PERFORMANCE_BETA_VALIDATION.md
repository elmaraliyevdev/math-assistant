# Performance Beta Validation

Methodology and targets for internal beta load validation. **Simulation engine behavior is not modified** — benchmarks measure platform API and worker capacity only.

## Targets

| Scenario | Target |
|----------|--------|
| 100 concurrent users (API read load) | No sustained 5xx; p95 latency < 500ms on `/dashboard/summary` |
| 100 simultaneous simulation submissions | All accepted (202); queue drains without worker crash |
| Simulation throughput | Worker count scaled via `API_SIMULATION_WORKER_COUNT` |

## API load benchmark

Run against a running API (local or staging):

```bash
cd packages/api
uv run python ../../scripts/benchmark_api.py \
  --base-url http://127.0.0.1:8000 \
  --users 100 \
  --requests-per-user 10
```

Example output fields:

- Throughput (req/s)
- Mean / p95 / max latency (ms)

Record results in the table below after each beta environment validation.

| Date | Environment | Users | Req/user | Throughput | p95 ms | Notes |
|------|-------------|-------|----------|------------|--------|-------|
| | staging | 100 | 10 | | | |

## Concurrent simulations

1. Deploy with `API_SIMULATION_WORKER_COUNT=4` (or higher on multi-core hosts).
2. Use API or UI to submit 100 simulations (small spin count, e.g. 50, for faster drain).
3. Monitor Grafana panels:
   - Simulation throughput (`simulations_total`)
   - Worker queue size (`simulation_worker_queue_size`)
   - Simulation duration p95 (`simulation_duration_seconds`)

| Date | Workers | Simulations | Time to complete | Max queue | Failures |
|------|---------|-------------|------------------|-----------|----------|
| | 4 | 100 | | | |

## API latency (manual)

Measure authenticated endpoints with curl or `hey`:

```bash
# Health (unauthenticated)
curl -w "%{time_total}\n" -o /dev/null -s http://localhost:8000/health
```

Document baseline latencies on same network as production users.

## Findings & recommendations

### Initial assessment (pre-beta)

- API metrics exported at `GET /metrics` for Prometheus/Grafana.
- In-process simulation workers — scale vertically before horizontal multi-instance (requires shared queue in future phase).
- SQLite is not used in production; PostgreSQL connection pool defaults should be tuned under sustained load.
- Rate limiting and brute-force protection add negligible overhead on auth paths.

### Recommended production settings

```env
API_SIMULATION_WORKER_COUNT=4
API_RATE_LIMIT_AUTH_PER_MINUTE=20
API_MAX_REQUEST_BODY_BYTES=10485760
```

Re-run benchmarks after infrastructure changes and update this document.
