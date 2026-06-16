# Architecture Decision Record — Final Summary (Engine v1.0 Freeze)

**Date:** 2026-06-14  
**Status:** Consolidated summary at M0–M9 completion  
**Related:** `docs/adr/ADR-001` through `ADR-007`

This document consolidates architectural decisions governing the frozen core engine. Individual ADR files remain authoritative for full rationale; this summary records **accepted direction** and **implementation reality** at freeze.

---

## Accepted decisions

### 1. DSL-first architecture

**ADR:** [ADR-005 — Feature Strategy (Built-in Plugins + DSL First)](./adr/ADR-005-feature-strategy-dsl-first.md)  
**Status:** Accepted (Architectural Direction)

**Decision:**

- MVP uses **built-in plugins only** (`core.base-game`, `core.free-spins`, `core.hold-and-win`, `core.multiplier`)
- Game designers configure features via **declarative DSL / canonical JSON**, not custom code uploads
- Pipeline: `Game Definition → Validation Engine → Runtime → Simulation → Mathematical Engine`
- DSL compiler is a **future platform component**; v1.0 golden fixtures use hand-authored canonical JSON

**Implementation at freeze:** Four built-in plugins in `runtime_core/plugins/`; validation against frozen JSON schemas in `packages/game-schema/`.

---

### 2. Stack-based FSM execution

**ADR:** [ADR-004 — State Machine Execution Model](./adr/ADR-004-state-machine-execution-model.md)  
**Status:** Accepted (Architectural Direction)

**Decision:**

- **Hierarchical stack-based FSM** (pushdown automaton) for nested bonus execution
- `spawnChildMachine` → push frame; terminal → pop; retrigger → mutate frame context
- MVP max stack depth: **4**
- Session-level context (bet, cumulative wins) at root; feature-local counters per frame

**Implementation at freeze:** `SessionExecutor`, plugin host, lifecycle/termination in `runtime_core/runtime/executor/` and `runtime_core/runtime/lifecycle.py`. All four golden fixture flows validated.

---

### 3. Python backend

**ADR:** [ADR-007 — Backend Language: Python 3.13+](./adr/ADR-007-backend-language-python.md)  
**Status:** Accepted

**Decision:**

- Validation Engine, Runtime Core, Simulation Engine, and Mathematical Engine implemented in **Python 3.13+**
- Tooling: `uv`, Ruff, Black, MyPy strict, pytest, hypothesis (where used)
- Go reference (`packages/runtime-core/`) superseded for new development

**Supersedes:** [ADR-001 — Simulation Core Language](./adr/ADR-001-simulation-core-language.md) (Rust vs Go — not pursued; Python chosen via ADR-007)

**Implementation at freeze:** Single authoritative package `packages/runtime_core/` with 420 tests and 95% coverage.

---

### 4. Deterministic RNG policy

**ADR:** [ADR-002 — RNG Algorithm and Stream Splitting](./adr/ADR-002-rng-algorithm-and-stream-splitting.md)  
**Status:** Proposed (formal) → **Accepted by implementation at v1.0 freeze**

**De facto decision (implemented):**

| Element | Choice |
|---------|--------|
| Algorithm | **PCG64** |
| Seed derivation policy | **`v1-hash-shard`** — HMAC-SHA256 |
| Shard seed | `HMAC(masterSeed, shardIndex, runId)` |
| Chain seed | `HMAC(shardSeed, spinChainIndex)` |
| Monte Carlo equivalence | Global `spinChainIndex` drives chain RNG; physical shard is partition-only |
| Child scopes | Frame → step → multiplier streams derived from chain seed |

**Invariants (ADR-002 §Invariants):**

1. Same inputs → same aggregate metrics
2. Shard merge order does not affect results
3. Every simulation run records algorithm, version, master seed, shard count
4. Golden tests pin exact RNG configuration

**Recommendation:** Update ADR-002 status to **Accepted** with implemented options checked.

---

### 5. Integer money representation

**ADR:** [ADR-003 — Money Representation Strategy](./adr/ADR-003-money-representation-strategy.md)  
**Status:** Proposed (formal) → **Accepted by implementation at v1.0 freeze**

**De facto decision (implemented):**

| Element | Choice |
|---------|--------|
| Representation | **`int64` minor units** (`*MinorUnits` fields) |
| Float in core paths | **Forbidden** for bet/win accumulation |
| Exposure | Capped vs uncapped wins tracked separately |
| RTP | Ratio of integer totals; display formatting deferred to reporting layers |

All runtime, simulation, and mathematical engines use integer minor units per [CURSOR_RULES.md](./CURSOR_RULES.md) §7.

**Recommendation:** Update ADR-003 status to **Accepted** — Option A (fixed-point integers / minor units).

---

### 6. Monolith MVP architecture

**ADR:** [ADR-006 — Monolith vs Service Architecture](./adr/ADR-006-monolith-vs-services-mvp.md)  
**Status:** Proposed (formal) → **Accepted direction at v1.0 freeze**

**Decision (recommended Option B — adopted for roadmap):**

| Component | MVP shape |
|-----------|-----------|
| Core engines | **Modular monolith** — `packages/runtime_core/` Python package |
| Simulation workers | **Subprocess pool** (`ProcessPoolExecutor`) in-process to library; separate worker entrypoint in Phase 11 |
| API | **Not yet implemented** — FastAPI monolith planned (Phase 11) |
| Database | PostgreSQL planned (Phase 12) |
| Queue | Lightweight / in-process until API layer (Phase 11+) |

Logical package boundaries enforced within monorepo regardless of deployment shape.

**Explicitly excluded from MVP:** multi-region worker fleet, separate AI microservice, Kubernetes requirement, billing/SSO.

---

## Decision matrix (quick reference)

| Topic | ADR | Formal status | v1.0 implementation |
|-------|-----|---------------|---------------------|
| DSL-first + built-in plugins | ADR-005 | Accepted | ✅ |
| Stack FSM | ADR-004 | Accepted | ✅ |
| Python backend | ADR-007 | Accepted | ✅ |
| Core language (Rust/Go) | ADR-001 | Proposed | Superseded by ADR-007 |
| RNG (PCG64 + HMAC) | ADR-002 | Proposed | ✅ Implemented |
| Integer money | ADR-003 | Proposed | ✅ Implemented |
| Monolith MVP | ADR-006 | Proposed | ✅ Direction locked |

---

## Unresolved future ADRs

The following decisions are **deferred** to post-v1.0 platform phases. New ADRs required before implementation.

| Topic | Notes | Likely phase |
|-------|-------|--------------|
| **API framework details** | FastAPI chosen in roadmap; OpenAPI, auth middleware, job orchestration TBD | Phase 11 |
| **Persistence schema** | PostgreSQL entity model for games, versions, simulation runs, reports | Phase 12 |
| **Job queue technology** | Redis/BullMQ vs in-process vs cloud-native | Phase 11–12 |
| **Performance SLO / throughput** | 1M-spin benchmark, hardware targets | Pre-production |
| **RTP decomposition (analytic)** | Hybrid analytic + simulation RTP reconciliation | Post-M9 |
| **Custom plugin SDK** | TypeScript/WASM sandbox, marketplace | Enterprise / Phase 15 |
| **Multi-region simulation** | Distributed worker fleet, shard coordination | Enterprise |
| **AI grounding strategy** | RAG over simulation artifacts vs inline explainability | Phase 14 |
| **Megaways / dynamic grids** | GridSpec extensions | P3 mechanics |
| **ADR-002 formal acceptance** | Check boxes, audit documentation | Housekeeping |
| **ADR-003 formal acceptance** | Display precision, Kahan summation policy | Housekeeping |
| **Go runtime decommission** | Archive `packages/runtime-core/` after parity sign-off | M4 completion |
| **Feature DSL compiler** | YAML → canonical `GameVersion` | Platform |
| **Bootstrap / RTP confidence methods** | Alternative CI methods for certification reports | Mathematical Engine v2 |

---

## Governance

- New architectural decisions affecting engine outcomes require a new or amended ADR
- Engine freeze (v1.0) changes require major version bump per [ENGINE_RELEASE_v1.0.md](./ENGINE_RELEASE_v1.0.md) §7
- Conflict resolution precedence: Canonical Schema → Technical Specification → ADRs → implementation

---

## References

- [ENGINE_RELEASE_v1.0.md](./ENGINE_RELEASE_v1.0.md)
- [ROADMAP_v2.md](./ROADMAP_v2.md)
- [TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md)
- Individual ADRs: `docs/adr/`
