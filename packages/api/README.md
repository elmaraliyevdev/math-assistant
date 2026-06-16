# Math Assistant API

FastAPI platform layer for the frozen `runtime-core@1.8.0` engine.

## Phase 11A scope

- `GET /health` — liveness probe
- `GET /engine/version` — engine capability advertisement
- Request ID middleware (`X-Request-Id`)
- Structured logging (structlog)

No database, authentication, simulations, mathematics, or AI endpoints in this phase.

## Setup

```bash
cd packages/api
uv sync --group dev
```

## Run

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test

```bash
uv run pytest -v --cov=app --cov-report=term-missing
```

## Engine integration

The API reads metadata exclusively from **public** `runtime_core` exports:

| Field | Source |
|-------|--------|
| `engineVersion` | `runtime_core.runtime.ENGINE_VERSION` |
| `validatorVersion` | `runtime_core.validation.VALIDATOR_VERSION` |
| `supportedPlugins` | `runtime_core.plugins.BUILT_IN_PLUGINS` |
| `rng.*` | `runtime_core.runtime.default_rng_service_config()` |

`maxRecommendedSpinCount` is platform configuration (default `10_000_000`, certified in Phase 10.5).

## Endpoints

### `GET /health`

```json
{
  "status": "ok",
  "timestamp": "2026-06-14T12:00:00Z"
}
```

### `GET /engine/version`

See [API_SPECIFICATION.md](../../docs/API_SPECIFICATION.md) for the full response shape.
