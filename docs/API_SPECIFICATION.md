# API Specification

**Phase:** 10.6 — Platform Architecture Design  
**Date:** 2026-06-14  
**Engine baseline:** `runtime-core@1.8.0`  
**Status:** Design only — OpenAPI to be generated in Phase 11  
**Base URL:** `/api/v1`  
**Auth:** `Authorization: Bearer <JWT>` (all routes except `/health`, `/engine/version`)

---

## 1. Conventions

| Topic | Rule |
|-------|------|
| JSON field names | camelCase (matches engine DTOs) |
| IDs | UUID v4 strings |
| Timestamps | ISO 8601 UTC |
| Money | Integer `*MinorUnits` in engine payloads |
| Errors | `{ "error": { "code", "message", "details" } }` |
| Pagination | `?limit=20&cursor=<uuid>` on list endpoints (future) |
| Correlation | Response header `X-Request-Id` |

---

## 2. System

### GET /health

Liveness probe — no auth.

**Response 200:**

```json
{
  "status": "ok",
  "timestamp": "2026-06-14T12:00:00Z"
}
```

### GET /engine/version

Engine pin and capability advertisement.

**Response 200:**

```json
{
  "engineVersion": "runtime-core@1.8.0",
  "validatorVersion": "1.0.0",
  "supportedPlugins": [
    { "pluginId": "core.base-game", "version": "1.0.0" },
    { "pluginId": "core.free-spins", "version": "1.0.0" },
    { "pluginId": "core.hold-and-win", "version": "1.0.0" },
    { "pluginId": "core.multiplier", "version": "1.0.0" }
  ],
  "rng": {
    "algorithm": "PCG64",
    "policy": "v1-hash-shard"
  },
  "maxRecommendedSpinCount": 10000000
}
```

---

## 3. Game management

### POST /games/validate

Validate canonical game JSON **without** persisting.

**Maps to:** `ValidationEngine.validate(...)`

**Request:**

```json
{
  "canonicalJson": { "...": "GameVersion document" },
  "engineVersion": "runtime-core@1.8.0"
}
```

**Response 200 (valid):**

```json
{
  "valid": true,
  "contentHash": "a1b2c3d4e5f6...",
  "engineVersion": "runtime-core@1.8.0",
  "report": {
    "passed": true,
    "findings": [],
    "metadata": {
      "validatorVersion": "1.0.0",
      "schemaVersion": "1.0.0"
    }
  }
}
```

**Response 422 (validation findings):**

```json
{
  "valid": false,
  "contentHash": "a1b2c3d4e5f6...",
  "report": {
    "passed": false,
    "findings": [
      {
        "code": "GRAPH_ORPHAN_STATE",
        "severity": "error",
        "message": "State HAW_IDLE is unreachable",
        "path": "/machines/main/states/HAW_IDLE"
      }
    ]
  }
}
```

---

### POST /games

Create or register a game and immutable version.

**Flow:** validate → compute hash → dedupe → insert `games` + `game_versions`

**Request:**

```json
{
  "name": "Golden Base 5x3",
  "slug": "golden-base-5x3",
  "canonicalJson": { "...": "GameVersion document" }
}
```

**Response 201:**

```json
{
  "gameId": "550e8400-e29b-41d4-a716-446655440000",
  "gameVersionId": "660e8400-e29b-41d4-a716-446655440001",
  "contentHash": "a1b2c3d4e5f6789...",
  "name": "Golden Base 5x3",
  "slug": "golden-base-5x3",
  "engineVersion": "runtime-core@1.8.0",
  "createdAt": "2026-06-14T12:00:00Z"
}
```

**Response 409:** Version with same `contentHash` already exists (returns existing IDs).

---

### GET /games

List games for current organization.

**Response 200:**

```json
{
  "items": [
    {
      "gameId": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Golden Base 5x3",
      "slug": "golden-base-5x3",
      "currentVersionId": "660e8400-e29b-41d4-a716-446655440001",
      "updatedAt": "2026-06-14T12:00:00Z"
    }
  ],
  "nextCursor": null
}
```

---

### GET /games/{id}

Game detail with version history summary.

**Response 200:**

```json
{
  "gameId": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Golden Base 5x3",
  "slug": "golden-base-5x3",
  "currentVersionId": "660e8400-e29b-41d4-a716-446655440001",
  "versions": [
    {
      "gameVersionId": "660e8400-e29b-41d4-a716-446655440001",
      "contentHash": "a1b2c3d4...",
      "engineVersion": "runtime-core@1.8.0",
      "createdAt": "2026-06-14T12:00:00Z"
    }
  ]
}
```

**Response 404:** Unknown game or wrong organization.

---

## 4. Simulation

### POST /simulations

Enqueue a Monte Carlo simulation job.

**Maps to:** `run_simulation(game_version, simulation_profile)` (async worker)

**Request:**

```json
{
  "gameVersionId": "660e8400-e29b-41d4-a716-446655440001",
  "simulationRunId": "studio-run-2026-06-14-001",
  "spinCount": 1000000,
  "shardCount": 4,
  "masterSeed": "0x636572742d62656e63686d61726b2d7631",
  "eventLogMode": "none",
  "sampleEvents": 0,
  "betMinorUnits": 0,
  "clientRequestId": "optional-idempotency-key"
}
```

**Response 202 Accepted:**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "simulationRunId": "studio-run-2026-06-14-001",
  "status": "pending",
  "engineVersion": "runtime-core@1.8.0",
  "spinCount": 1000000,
  "shardCount": 4,
  "createdAt": "2026-06-14T12:00:01Z",
  "pollUrl": "/api/v1/simulations/770e8400-e29b-41d4-a716-446655440002"
}
```

**Notes:**

- `masterSeed` accepted as hex (`0x...`) or UTF-8 string; stored encrypted; never returned on GET
- `spinCount` > 10M → 400 with recommended max from `/engine/version`

---

### GET /simulations/{id}

Poll job status.

**Response 200 (running):**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "simulationRunId": "studio-run-2026-06-14-001",
  "status": "running",
  "engineVersion": "runtime-core@1.8.0",
  "spinCount": 1000000,
  "shardCount": 4,
  "progress": {
    "shardsCompleted": 2,
    "shardsTotal": 4
  },
  "startedAt": "2026-06-14T12:00:02Z",
  "completedAt": null
}
```

**Response 200 (completed):**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "status": "completed",
  "elapsedTimeMs": 43614,
  "resultsUrl": "/api/v1/simulations/770e8400-e29b-41d4-a716-446655440002/results"
}
```

**Response 200 (failed):**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "status": "failed",
  "error": {
    "code": "SIMULATION_WORKER_ERROR",
    "message": "Process pool worker terminated unexpectedly"
  }
}
```

---

### GET /simulations/{id}/results

Fetch aggregated simulation outcome.

**Maps to:** stored `SimulationResult` JSON

**Response 200:**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "engineVersion": "runtime-core@1.8.0",
  "result": {
    "spinCount": 1000000,
    "shardCount": 4,
    "elapsedTimeMs": 43614,
    "totalBetMinorUnits": 2000000000,
    "totalWinMinorUnits": 103070000,
    "uncappedWinMinorUnits": 103070000,
    "exposureTruncationCount": 0,
    "exposureTruncatedMinorUnits": 0,
    "chainFaultCount": 671900,
    "limitHitCount": 0,
    "featureTriggerCounts": {},
    "jackpotCounts": {},
    "eventSampleCount": 0
  }
}
```

**Response 409:** Job not yet `completed`.

---

## 5. Mathematics

### POST /mathematics/analyze

Build statistical report from a completed simulation.

**Maps to:** `build_mathematics_report(simulation_result, spin_wins_minor_units=...)`

**Request:**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "spinWinsSampleSize": 100000
}
```

**Response 200:**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "report": {
    "spinCount": 1000000,
    "engineVersion": "runtime-core@1.8.0",
    "rtp": {
      "rtp": 0.051535,
      "uncappedRtp": 0.051535,
      "totalBetMinorUnits": 2000000000,
      "totalWinMinorUnits": 103070000,
      "uncappedWinMinorUnits": 103070000
    },
    "hitFrequency": {
      "hitFrequency": 0.01081,
      "winningSpinCount": 1081,
      "losingSpinCount": 98919
    },
    "volatility": {
      "meanWinMinorUnits": 1030.7,
      "variance": 1069300.0,
      "standardDeviation": 1034.08,
      "coefficientOfVariation": 1.002
    },
    "confidenceInterval": {
      "lowerBound": 0.050845,
      "upperBound": 0.057255,
      "confidenceLevel": 0.95
    },
    "featureFrequencies": [],
    "jackpotFrequencies": [],
    "exposure": {
      "truncationRate": 0.0,
      "totalTruncatedMinorUnits": 0,
      "cappedRtp": 0.051535,
      "uncappedRtp": 0.051535,
      "rtpDifference": 0.0
    },
    "winDistribution": {
      "totalSpins": 100000,
      "betMinorUnitsPerSpin": 2000,
      "buckets": [
        { "label": "0x", "count": 98919, "percentage": 0.98919 }
      ]
    }
  },
  "spinWinsSampleSize": 100000
}
```

**Notes:**

- Platform worker collects `spinWinsSampleSize` chains via benchmark-style collector (Phase 11); does not modify engine
- Full-spin CI deferred to engine export feature

---

## 6. AI assistant

### POST /assistant/explain

Grounded natural-language explanation of stored artifacts.

**Request:**

```json
{
  "simulationId": "770e8400-e29b-41d4-a716-446655440002",
  "question": "Why is RTP around 5% and is that expected for this game?",
  "context": {
    "includeValidationReport": false,
    "includeWinDistribution": true
  }
}
```

**Response 200:**

```json
{
  "answer": "The observed RTP of 5.15% is derived from totalWinMinorUnits (103,070,000) divided by totalBetMinorUnits (2,000,000,000) across 1,000,000 spins [simulation_results.result]. This fixture is a test harness with high chain-fault rate (671,900 faults) and is not a production RTP target.",
  "citations": [
    {
      "source": "simulation_results",
      "field": "result.totalWinMinorUnits",
      "value": "103070000"
    },
    {
      "source": "simulation_results",
      "field": "result.totalBetMinorUnits",
      "value": "2000000000"
    },
    {
      "source": "mathematics_reports",
      "field": "report.rtp.rtp",
      "value": "0.051535"
    }
  ],
  "engineVersion": "runtime-core@1.8.0",
  "grounded": true
}
```

**Response 400:** Missing simulation or math report when question requires metrics.

See [AI_ASSISTANT_ARCHITECTURE.md](./AI_ASSISTANT_ARCHITECTURE.md) for grounding rules.

---

## 7. Error catalog (representative)

| Code | HTTP | Description |
|------|------|-------------|
| `INVALID_JSON` | 400 | Malformed request body |
| `ENGINE_VERSION_MISMATCH` | 400 | Requested engine ≠ deployed pin |
| `GAME_NOT_FOUND` | 404 | Unknown `gameId` |
| `SIMULATION_NOT_FOUND` | 404 | Unknown `simulationId` |
| `SIMULATION_NOT_COMPLETE` | 409 | Results not ready |
| `VALIDATION_FAILED` | 422 | Structured validation report |
| `WORKER_QUEUE_FULL` | 503 | Backpressure |

---

## 8. Engine adapter mapping

| Endpoint | Engine call |
|----------|-------------|
| `POST /games/validate` | `ValidationEngine(...).validate(game_version)` |
| `POST /simulations` | Worker → `run_simulation(game, profile)` |
| `GET /simulations/{id}/results` | Read persisted `SimulationResult` |
| `POST /mathematics/analyze` | `build_mathematics_report(result, spin_wins=...)` |

No route calls plugins or RNG directly.

---

## References

- [PLATFORM_ARCHITECTURE.md](./PLATFORM_ARCHITECTURE.md)
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
- [AI_ASSISTANT_ARCHITECTURE.md](./AI_ASSISTANT_ARCHITECTURE.md)
