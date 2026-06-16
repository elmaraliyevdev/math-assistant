# Engine Metrics — v1.0 Freeze Snapshot

**Captured:** 2026-06-14  
**Engine version:** `runtime-core@1.8.0`  
**Command:** `cd packages/runtime_core && uv run pytest -q`

---

## 1. Total tests

| Metric | Value |
|--------|-------|
| **Total tests** | **420** |
| **Pass rate** | 100% at freeze |
| **Test files** | 65 under `packages/runtime_core/tests/` |

### Tests by subsystem

| Subsystem | Directory | Tests |
|-----------|-----------|-------|
| Validation Engine | `tests/validation/` | 50 |
| Runtime Core | `tests/runtime/` | 180 |
| Built-in plugins | `tests/plugins/` | 86 |
| Simulation Engine | `tests/simulation/` | 27 |
| Mathematical Engine | `tests/mathematical/` | 34 |
| Golden Runtime | `tests/golden/` | 36 |
| Cross-cutting | `tests/test_*.py`, conftest | 7 |
| **Total** | | **420** |

---

## 2. Coverage by subsystem

Measured with `pytest --cov=runtime_core/<subsystem>`. Branch coverage enabled.

| Subsystem | Package path | Coverage |
|-----------|--------------|----------|
| **Overall** | `runtime_core/` | **95%** |
| Domain models | `runtime_core/domain/` | **100%** |
| Validation Engine | `runtime_core/validation/` | **91%** |
| Runtime Core | `runtime_core/runtime/` | **98%** |
| Built-in plugins | `runtime_core/plugins/` | **97%** |
| Simulation Engine | `runtime_core/simulation/` | **95%** |
| Mathematical Engine | `runtime_core/mathematical/` | **98%** |
| Golden Runtime harness | `runtime_core/golden/` | **96%** |

### CI coverage gates

| Suite | Minimum |
|-------|---------|
| Simulation Engine | 90% |
| Mathematical Engine | 95% |
| Overall (informational) | 95% actual |

---

## 3. Golden fixtures implemented

### 3.1 Runtime golden (`tests/golden/`)

| Fixture ID | Flow | Artifacts | CI |
|------------|------|-----------|-----|
| `fixture-01-base-5x3` | Base 5×3 only | canonical JSON, profile, expected | ✅ |
| `fixture-02-base-free-spins` | Base → free spins | canonical JSON, profile, expected | ✅ |
| `fixture-03-base-hold-win` | Base → hold & win | canonical JSON, profile, expected (+ overrides) | ✅ |
| `fixture-04-nested-fs-hold-win` | Base → FS → H&W | canonical JSON, profile, expected (+ overrides) | ✅ |

**Runner:** `uv run golden-runner --all --determinism`  
**Workflow:** `.github/workflows/golden-runtime.yml`

### 3.2 Mathematical golden (`tests/golden/mathematical/`)

| Fixture ID | Purpose | CI |
|------------|---------|-----|
| `analytic-4spin-bucketed` | Hand-verified RTP, volatility, CI, buckets | ✅ |

**Runner:** `pytest tests/mathematical/test_golden_mathematical.py -m golden_mathematical`

### 3.3 Validation golden

Validation tests run against canonical fixture JSON under `tests/golden/*/game.canonical.json` via `tests/validation/` and `tests/test_golden_fixtures.py`.

---

## 4. Supported plugins

Built-in plugins registered in `runtime_core/plugins/manifest.py`:

| Plugin ID | Version | Package path | Capabilities |
|-----------|---------|--------------|--------------|
| `core.base-game` | `1.0.0` | `plugins/base_game/` | Grid generation, line pays, scatter detection |
| `core.free-spins` | `1.0.0` | `plugins/free_spins/` | FS lifecycle, retrigger, spin counters |
| `core.hold-and-win` | `1.0.0` | `plugins/hold_and_win/` | Respins, held symbols, jackpot wins |
| `core.multiplier` | `1.0.0` | `plugins/multiplier/` | Weighted multiplier application |

**Policy:** MVP built-in only — no custom plugin uploads (ADR-005).

---

## 5. Supported feature flows

Validated by golden runtime fixtures and plugin integration tests:

| Flow ID | Description | Stack depth | Golden fixture |
|---------|-------------|-------------|----------------|
| `base` | Single base-game spin chain | 1 | fixture-01 |
| `base-free-spins` | Scatter trigger → free spins → return to base | 2 | fixture-02 |
| `base-hold-win` | H&W trigger from base → respins → complete | 2 | fixture-03 |
| `nested-fs-hold-win` | Base → FS → nested H&W → unwind stack | 3+ | fixture-04 |

### Execution capabilities

| Capability | Module | Status |
|------------|--------|--------|
| Single spin chain | `SessionExecutor` | ✅ |
| Monte Carlo simulation | `SimulationRunner` | ✅ |
| Deterministic sharding | `assign_shards()` + `ProcessPoolExecutor` | ✅ |
| Statistical analysis | `build_mathematics_report()` | ✅ |
| Pre-sim validation | Validation Engine | ✅ |
| Event logging modes | `none`, `replay`, `transitions_only` | ✅ |
| Exposure capping | Session wins + exposure state | ✅ |

### Not yet supported (post-v1.0)

| Capability | Target phase |
|------------|--------------|
| HTTP API | Phase 11 |
| Persistent simulation history | Phase 12 |
| UI workflow | Phase 13 |
| AI explanations | Phase 14 |
| Custom plugins / marketplace | Phase 15 |
| Feature DSL compiler | Platform |
| Long-run (1M+) performance certification | Pre-production |

---

## 6. Package structure

```
math-assistant/
├── docs/                          # Specifications, ADRs, freeze docs
│   ├── ENGINE_RELEASE_v1.0.md
│   ├── ENGINE_METRICS.md          # (this file)
│   ├── ARCHITECTURE_DECISION_RECORD_FINAL.md
│   ├── ROADMAP_v2.md
│   └── adr/
├── packages/
│   ├── game-schema/               # Frozen JSON schemas
│   ├── runtime_core/              # Authoritative Python engine (M0–M9)
│   └── runtime-core/              # Legacy Go reference
└── tests/golden/                  # Golden fixture contracts
    ├── manifest.yaml
    ├── fixture-01-base-5x3/
    ├── fixture-02-base-free-spins/
    ├── fixture-03-base-hold-win/
    ├── fixture-04-nested-fs-hold-win/
    └── mathematical/
        └── analytic-4spin-bucketed/
```

---

## 7. Reproduction commands

```bash
# Full test suite
cd packages/runtime_core && uv sync --group dev && uv run pytest -q

# Coverage report
uv run pytest -q --cov=runtime_core --cov-report=term-missing

# Golden runtime
uv run golden-runner --all --determinism

# Subsystem coverage
uv run pytest tests/simulation/ --cov=runtime_core/simulation --cov-fail-under=90
uv run pytest tests/mathematical/ --cov=runtime_core/mathematical --cov-fail-under=95
```

---

## References

- [ENGINE_RELEASE_v1.0.md](./ENGINE_RELEASE_v1.0.md)
- [GOLDEN_FIXTURES_V1.md](./GOLDEN_FIXTURES_V1.md)
