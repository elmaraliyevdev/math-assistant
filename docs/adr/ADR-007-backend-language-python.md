# ADR-007: Backend Implementation Language — Python

**Status:** Accepted  
**Date:** 2026-06-14  
**Deciders:** Architecture, Engineering Lead  
**Supersedes:** Language selection aspects of [ADR-001](./ADR-001-simulation-core-language.md) (Rust vs Go)  
**Related:** [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §L, [CURSOR_RULES.md](../CURSOR_RULES.md) §17, ADR-002, ADR-003, ADR-004, ADR-006, [RUNTIME_CORE_DESIGN.md](../RUNTIME_CORE_DESIGN.md)

---

## Context

The AI Game Mathematics Assistant backend comprises several deterministic engines:

- **Validation Engine** — schema, graph, plugin, exposure, and limits validation
- **Runtime Core** — hierarchical state machine execution, built-in plugins, RNG, events
- **Simulation Engine** — Monte Carlo orchestration, sharding, worker coordination
- **Mathematical Engine** — RTP, volatility, exposure metrics from simulation artifacts

An initial implementation pass used **Go** (`packages/runtime-core/`) for the Validation Engine and Phase R1 of Runtime Core (RNG, events, session types). The team has decided to **standardize the entire backend on Python** for MVP and beyond.

This decision is a **technology migration only**. The following remain unchanged and authoritative:

- Architecture (modular monolith, bounded contexts)
- Canonical Game Schema v1.0.0 and frozen JSON schemas
- ADRs for execution model, RNG, money representation, and MVP deployment shape
- Golden fixtures and validation error codes
- Runtime Core design specification (frozen v1.0.0)
- Determinism, validation-first, and validation pipeline ordering requirements

The Go codebase serves as a **reference implementation** for behavioral intent during Python re-implementation. It is **not** a line-by-line translation source.

---

## Decision

**The backend implementation language for Validation Engine, Runtime Core, Simulation Engine, and Mathematical Engine SHALL be Python 3.13+.**

### Toolchain (Mandatory)

| Concern | Choice |
|---------|--------|
| Dependency management | `uv` |
| Linting | Ruff |
| Formatting | Black |
| Type checking | MyPy (strict) |
| Testing | Pytest + pytest-cov |
| DTOs / boundary validation | Pydantic v2 |
| Structured logging | structlog |

### Package Location

Primary Python package: `packages/runtime_core/` (see CURSOR_RULES §17.4).

The existing Go package `packages/runtime-core/` **SHOULD** be archived or removed after Python parity is achieved for each subsystem — not maintained in parallel long-term.

### Runtime Constraints (Non-Negotiable)

| Constraint | Policy |
|------------|--------|
| Determinism | Identical inputs → identical outcomes per ADR-002 and CURSOR_RULES §4 |
| Money | Integer minor units only in execution and aggregation paths (CURSOR_RULES §5) |
| Runtime Core purity | No I/O, no asyncio, no multiprocessing inside Runtime Core |
| Plugins | Built-in only; no I/O; deterministic |
| Validation first | Invalid `GameVersion` documents **MUST NOT** reach simulation |

---

## Rationale

### Why Python

1. **Team expertise** — The engineering team has extensive Python experience, reducing onboarding friction and review cycle time.
2. **Development velocity** — Faster iteration for MVP engines, golden test harnesses, and AI/mathematical integrations (notebooks, statistical tooling, DSL tooling).
3. **Ecosystem fit** — Strong libraries for JSON Schema, graph algorithms, statistics (NumPy), and test tooling align with platform needs without architectural change.
4. **AI integration** — Python is the natural host for explainability, analysis scripts, and future ML-adjacent workflows adjacent to the Mathematical Engine.
5. **MVP throughput is sufficient** — Monte Carlo targets for MVP (millions of spins, multi-core single-machine sharding) are achievable with `multiprocessing` / `ProcessPoolExecutor` without requiring Go or Rust for the first release.

### Why Not Continue with Go

- The Go implementation was early-stage (Validation Engine complete; Runtime Core at R1 only).
- Switching cost is lower now than after full Runtime Core and Simulation Engine completion.
- Team velocity and maintainability outweigh Go's raw throughput advantages for MVP scope.
- Architectural contracts are language-agnostic; re-implementation preserves behavior via golden fixtures.

### What Does Not Change

- Hierarchical stack FSM (ADR-004)
- PCG64 + `v1-hash-shard` HMAC seed derivation (ADR-002)
- Fixed minor-unit money (ADR-003 intent)
- Event contract and replay hashing semantics
- Validation pipeline order: Schema → Graph → Plugin → Exposure → Limits
- Golden fixtures as regression authority

---

## Consequences

### Positive

- Unified language across engines reduces context switching and hiring/training surface.
- Pydantic models align naturally with frozen JSON schemas and validation reports.
- `Protocol`-based plugin and RNG interfaces preserve ADR-004 execution model with idiomatic Python.
- NumPy-backed Mathematical Engine aggregations without leaving the primary codebase language.
- Easier integration with AI explainability and ad-hoc mathematical analysis.

### Negative

- **Rewrite cost** — Validation Engine and Runtime Core R1 Go code will be re-implemented; temporary dual-maintenance risk if both coexist.
- **Raw throughput** — Single-process spin throughput may be lower than Go/Rust; mitigated by multi-process Simulation Engine and MVP spin count targets.
- **GIL** — Python GIL limits single-process parallelism; Runtime Core is single-threaded by design; parallelism belongs in Simulation Engine only.
- **Type discipline overhead** — MyPy strict mode requires investment; pays off for mathematical correctness.

### Neutral

- API tier (e.g., NestJS/TypeScript) unchanged; Python engines exposed via subprocess, HTTP, or shared job queue per ADR-006.
- Frozen schemas remain JSON; Python consumes the same files under `packages/game-schema/`.
- Go reference code may remain in git history for behavioral comparison during migration.

---

## Alternatives Considered

| Alternative | Why Not (for MVP) |
|-------------|-------------------|
| **Go** (continue) | Strong performance and simplicity, but lower team velocity and weaker AI/stats ecosystem fit for MVP priorities |
| **Rust** (ADR-001 Option A) | Maximum performance and safety; steeper learning curve and slower MVP delivery |
| **Hybrid Go + Python** | Orchestration in Python, hot path in Go — operational and FFI complexity without proven MVP need |
| **TypeScript-only core** | Insufficient throughput and integer money discipline for simulation hot paths |
| **Keep Go Validation + Python Runtime** | Split language backend increases maintenance; no compelling benefit |

**Revisit Go or Rust** only if profiling on golden fixtures demonstrates Python cannot meet published MVP throughput SLOs after multi-process optimization — requires new ADR and explicit SLO breach evidence.

---

## Migration Strategy

### Phase M0 — Foundation

- Scaffold `packages/runtime_core/` with `uv`, Ruff, Black, MyPy strict, pytest.
- Define `domain` models from canonical schema (Pydantic + frozen dataclasses where appropriate).
- Port golden fixture test harness to pytest.

### Phase M1 — Validation Engine

- Re-implement validation pipeline in Python (see CURSOR_RULES §6).
- Achieve parity with Go validation against golden fixtures and error codes.
- Target **90%+** coverage.

### Phase M2 — Runtime Core (Phases R1–R7 per RUNTIME_CORE_DESIGN)

- Re-implement incrementally by design phases; **do not** bulk-translate Go files.
- R1 first: RNG, events, session types, request/result DTOs.
- Golden integration tests gate each phase.

### Phase M3 — Simulation + Mathematical Engines

- Simulation Engine with `ProcessPoolExecutor` / `multiprocessing` (MVP).
- Mathematical Engine with integer-safe aggregations; NumPy for vectorized stats where beneficial.

### Phase M4 — Decommission Go

- Remove or archive `packages/runtime-core/` after parity sign-off.
- Update CI to Python-only backend tests.

---

## Validation Plan

1. Validation Engine: all golden fixture validation tests pass with identical error codes and report structure.
2. Runtime Core: golden fixture spin chains produce matching events, wins, and replay hashes (where applicable).
3. Determinism: cross-run and cross-process reproducibility tests for fixed seeds.
4. Performance smoke: Fixture 1 at 1M spins meets MVP SLO on target hardware (define SLO in Technical Specification or follow-up ADR amendment).
5. Coverage gates: 80% overall, 90%+ Validation Engine and Runtime Core.

---

## References

- [CURSOR_RULES.md](../CURSOR_RULES.md) — §17 Python Engineering Standards
- [RUNTIME_CORE_DESIGN.md](../RUNTIME_CORE_DESIGN.md) — frozen Runtime Core contract
- [GOLDEN_FIXTURES_V1.md](../GOLDEN_FIXTURES_V1.md)
- Go reference: `packages/runtime-core/` (Validation Engine + Runtime Core R1)
