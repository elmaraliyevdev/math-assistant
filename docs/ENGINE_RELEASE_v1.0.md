# Engine Release v1.0 — Freeze Declaration

**Status:** Frozen  
**Release date:** 2026-06-14  
**Engine version:** `runtime-core@1.8.0`  
**Package:** `packages/runtime_core/`  
**Scope:** M0–M9 (Validation → Runtime → Simulation → Mathematical)

---

## 1. Engine status

The **AI Game Mathematics Assistant — Core Engine v1.0** is declared **frozen** for platform work (API, persistence, frontend). All bounded-context deliverables through Phase M9 are complete, gated by pytest and golden regression suites.

| Attribute | Value |
|-----------|-------|
| Language | Python 3.13+ |
| Package manager | `uv` |
| Type checking | MyPy strict |
| Lint / format | Ruff, Black |
| Test runner | pytest |
| CI | GitHub Actions (`golden-runtime.yml`) |
| Total tests | **420** (all passing at freeze) |
| Overall statement coverage | **95%** (`runtime_core`) |

**Not in scope for v1.0:** HTTP API, database persistence, React UI, AI assistant, enterprise distribution, DSL compiler (design-only via canonical JSON fixtures).

---

## 2. Completed components

| Phase | Component | Location | Summary |
|-------|-----------|----------|---------|
| **M0** | Foundation | `packages/runtime_core/` | `uv` scaffold, domain models, pytest harness, repo conventions |
| **M1** | Validation Engine | `runtime_core/validation/` | Schema, graph, state-machine, plugin, transition validators; structured issue reports |
| **M2** | Runtime Core — R1 | `runtime_core/runtime/` | RNG (PCG64), events, session factory, spin-chain DTOs, stack frames |
| **M3** | Runtime Core — R2–R5 | `runtime_core/runtime/` | Lifecycle, transitions, plugin host, counters, exposure |
| **M4** | Built-in plugins | `runtime_core/plugins/` | Base game, free spins, hold & win, multiplier |
| **M5** | Runtime integration | `runtime_core/runtime/` | End-to-end stack execution, golden scenario tests |
| **M6** | SessionExecutor | `runtime_core/runtime/executor/` | Spin-chain loop, plugin manager, wins, termination, inheritance |
| **M7** | Golden Runtime | `runtime_core/golden/` | Fixture loader, comparator, CLI (`golden-runner`), CI gate |
| **M8** | Simulation Engine | `runtime_core/simulation/` | Deterministic sharding, `ProcessPoolExecutor`, commutative aggregation |
| **M9** | Mathematical Engine | `runtime_core/mathematical/` | RTP, volatility, frequencies, exposure, CI, distribution, report |

Supporting packages (unchanged at freeze):

| Package | Role |
|---------|------|
| `packages/game-schema/` | Frozen JSON schemas and registries |
| `packages/runtime-core/` | Legacy Go reference (archived path; Python is authoritative) |

---

## 3. Coverage summary

Measured with `pytest --cov=runtime_core` at freeze (2026-06-14).

| Subsystem | Tests (approx.) | Coverage |
|-----------|-----------------|----------|
| Validation Engine | 50 | **91%** |
| Runtime Core | 180 | **98%** |
| Built-in plugins | 86 | **97%** |
| Simulation Engine | 27 | **95%** |
| Mathematical Engine | 34 | **98%** |
| Golden Runtime harness | 36 | **96%** |
| Domain models | (shared) | **100%** |
| **Total** | **420** | **95%** |

Critical paths (RNG, money accumulation, session executor, golden compare) exceed **90%** branch-aware coverage.

---

## 4. Golden Runtime summary

**Manifest:** `tests/golden/manifest.yaml`  
**Engine pin:** `runtime-core@1.8.0`  
**CLI:** `uv run golden-runner --all [--determinism]`

| Fixture ID | Flow | Locked |
|------------|------|--------|
| `fixture-01-base-5x3` | Base game only | Yes |
| `fixture-02-base-free-spins` | Base → free spins | Yes |
| `fixture-03-base-hold-win` | Base → hold & win | Yes |
| `fixture-04-nested-fs-hold-win` | Base → FS → H&W (nested) | Yes |

Each fixture includes:

- `game.canonical.json` — immutable game definition
- `simulation.profile.yaml` — pinned single-chain execution profile
- `expected.yaml` — locked runtime outcome (wins, exposure, event log hash)

**Validation checks:**

- Field-level diff against `expected.yaml`
- Determinism: identical outcomes on repeated execution
- Engine version match

Fixtures 03 and 04 apply documented runtime overrides (H&W reachability) via profile, not canonical mutation.

---

## 5. Golden Mathematical summary

**Manifest:** `tests/golden/mathematical/manifest.yaml`

| Fixture ID | Purpose | Locked |
|------------|---------|--------|
| `analytic-4spin-bucketed` | Hand-computed RTP, volatility, CI, distribution buckets | Yes |

Each fixture includes:

- `input.yaml` — `SimulationResult` + `spinWinsMinorUnits`
- `expected.yaml` — pinned mathematical metrics

Mathematical golden tests validate analysis **without re-executing spins**. Per-spin win arrays are simulation output artifacts consumed read-only by the Mathematical Engine.

---

## 6. Determinism guarantees

The following invariants hold at v1.0 and **must not regress** without a major version bump and golden baseline update:

### 6.1 RNG and spin chains

- Algorithm: **PCG64** with HMAC-SHA256 seed derivation (`v1-hash-shard` policy)
- Chain scope: `derive(masterSeed, shardIndex, runId)` → `derive(shardSeed, spinChainIndex)`
- Monte Carlo sharding: **global `spinChainIndex`** drives per-chain RNG; physical shard index is work-partition only (1-shard ≡ N-shard aggregate equivalence)
- Child streams: frame → step → multiplier scopes derived deterministically from chain seed

### 6.2 Simulation

- Same `(gameVersion, masterSeed, simulationRunId, spinCount, shardCount)` → identical aggregate metrics
- Shard merge order does not affect totals (commutative accumulator)
- `ProcessPoolExecutor` workers receive immutable `GameVersion` snapshots; fresh `SessionExecutor` per worker
- No `asyncio`, no threading in simulation path

### 6.3 Runtime golden

- Same pinned profile → identical `eventLogHash`, wins, exposure deltas
- `elapsedTimeMs` excluded from determinism comparisons

### 6.4 Mathematical

- Pure functions over frozen inputs; no mutation of `SimulationResult`
- Identical inputs → identical `MathematicsReport`

### 6.5 Prohibited sources of nondeterminism

- Unseeded `random` / `Math.random()` equivalents
- Wall-clock timestamps in outcome paths
- Floating-point money in core accumulation (integer minor units only)

---

## 7. Breaking change policy

Effective from v1.0 freeze through the next major engine release:

### 7.1 Engine versioning

- Format: `runtime-core@MAJOR.MINOR.PATCH`
- **PATCH:** bug fixes that restore specified behavior; golden baselines unchanged
- **MINOR:** additive APIs, new events (backward compatible); golden baselines unchanged unless documented
- **MAJOR:** breaking changes to outcomes, RNG policy, money semantics, or golden contracts

Current pin: **`runtime-core@1.8.0`**

### 7.2 Golden fixture changes

1. Failing golden test → **stop**; investigate root cause
2. Expected values **must not** be updated without mathematical justification
3. Any baseline change requires:
   - Updated `expected.yaml` with rationale in PR description
   - Re-run `--determinism` and full 420-test suite
   - Explicit reviewer approval from math engineering

### 7.3 Schema and plugin contracts

- Canonical game schema changes require Validation Engine update + fixture re-validation
- Built-in plugin behavior changes are **breaking** if golden runtime outcomes shift
- Plugin IDs and supported versions are frozen: see `ENGINE_METRICS.md`

### 7.4 Simulation ↔ Mathematical boundary

- `SimulationResult` field semantics are frozen
- Mathematical Engine consumes simulation outputs only; no spin execution in math layer

---

## 8. Production readiness checklist

| Item | v1.0 status |
|------|-------------|
| Validation Engine MVP | ✅ Complete |
| Runtime Core MVP | ✅ Complete |
| Built-in plugins (4) | ✅ Complete |
| SessionExecutor | ✅ Complete |
| Simulation Engine MVP | ✅ Complete |
| Mathematical Engine MVP | ✅ Complete |
| Golden runtime CI gate | ✅ Complete |
| Golden mathematical tests | ✅ Complete |
| Determinism verification | ✅ Complete |
| Coverage ≥ 90% critical paths | ✅ Complete (95% overall) |
| ADR formal acceptance (002, 003, 006) | ⚠️ Proposed — implemented de facto; formal ADR update recommended |
| Performance SLO sign-off (1M spins) | ⬜ Not benchmarked at freeze |
| FastAPI backend | ⬜ Phase 11 |
| PostgreSQL persistence | ⬜ Phase 12 |
| React frontend | ⬜ Phase 13 |
| AI assistant | ⬜ Phase 14 |
| Enterprise features | ⬜ Phase 15 |
| Go runtime decommission (M4) | ⬜ Archive pending sign-off |

**Freeze confirmation:** Core engine behavior is **locked**. Platform layers may proceed against this release baseline.

---

## References

- [ENGINE_METRICS.md](./ENGINE_METRICS.md)
- [ARCHITECTURE_DECISION_RECORD_FINAL.md](./ARCHITECTURE_DECISION_RECORD_FINAL.md)
- [ROADMAP_v2.md](./ROADMAP_v2.md)
- [GOLDEN_FIXTURES_V1.md](./GOLDEN_FIXTURES_V1.md)
- [RUNTIME_CORE_DESIGN.md](./RUNTIME_CORE_DESIGN.md)
- [CURSOR_RULES.md](./CURSOR_RULES.md)
