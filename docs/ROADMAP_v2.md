# Roadmap v2 — Post-Engine Platform

**Baseline:** Engine v1.0 frozen (M0–M9 complete)  
**Date:** 2026-06-14  
**Engine pin:** `runtime-core@1.8.0`

Phases 0–9 delivered the **deterministic mathematics core**. Phases 11–15 build the **product platform** on top of the frozen engine boundary. Phase 10 is reserved (intentionally skipped in numbering to align with engine milestone completion).

---

## Completed — Engine (M0–M9)

| Phase | Deliverable |
|-------|-------------|
| M0 | Foundation — `uv`, domain models, pytest |
| M1 | Validation Engine |
| M2–M5 | Runtime Core — RNG, events, plugins, stack FSM |
| M6 | SessionExecutor |
| M7 | Golden Runtime Validation |
| M8 | Simulation Engine |
| M9 | Mathematical Engine |

**Constraint for all subsequent phases:** Platform layers call engine public APIs; they **must not** modify runtime, simulation, or mathematical behavior without a new engine release.

---

## Phase 11 — FastAPI backend

**Goal:** Expose frozen engine capabilities via HTTP for internal tools and future UI.

### Scope

- FastAPI application (`packages/api/` or equivalent)
- REST endpoints:
  - `POST /games/validate` — Validation Engine
  - `POST /runtime/spin-chain` — single-chain execution (SessionExecutor)
  - `POST /simulation/run` — Monte Carlo orchestration
  - `POST /mathematics/analyze` — MathematicsReport from simulation results
  - `GET /engine/version` — engine pin and capabilities
- Async job model for long simulations (in-process queue MVP → Redis in Phase 12)
- OpenAPI schema generation
- Structured logging (structlog); correlation IDs
- Health checks and readiness probes

### Non-goals

- No game logic in API handlers
- No direct plugin invocation from routes
- No persistence (Phase 12)

### Exit criteria

- All four golden runtime fixtures executable via API with identical outcomes
- Simulation + math pipeline callable end-to-end
- Integration tests against running API

---

## Phase 12 — PostgreSQL persistence

**Goal:** Durable storage for game definitions, simulation runs, and analysis artifacts.

### Scope

- PostgreSQL schema:
  - Organizations / users (minimal MVP)
  - Game definitions and immutable `GameVersion` snapshots (content hash keyed)
  - Simulation runs (profile, seeds, shard config, engine version)
  - Simulation results and `MathematicsReport` JSON
  - Golden fixture registry (optional admin)
- Migrations (Alembic or equivalent)
- Repository layer — API routes read/write through repositories, not engine internals
- Job status tracking for long-running simulations

### Non-goals

- Multi-region replication
- Full audit trail / compliance archive (Enterprise)

### Exit criteria

- Re-run simulation from stored profile produces identical metrics
- GameVersion immutability enforced at DB layer

---

## Phase 13 — React frontend

**Goal:** Mathematician-facing UI for define → validate → simulate → analyze.

### Scope

- React SPA (TypeScript)
- Core views:
  - Game editor (canonical JSON / future DSL)
  - Validation report viewer
  - Simulation configuration (seeds, spin count, shards)
  - Mathematical report dashboard (RTP, volatility, distributions)
  - Golden fixture comparison (read-only admin)
- API client generated from OpenAPI
- Auth stub (session/JWT — full SSO in Enterprise)

### Non-goals

- Spreadsheet import/export (P2)
- Real-time collaborative editing

### Exit criteria

- End-to-end demo: upload fixture → validate → simulate → view MathematicsReport
- Parity with CLI golden-runner for single-chain validation

---

## Phase 14 — AI Assistant

**Goal:** Explain simulation results grounded in engine artifacts, not generic chat.

### Scope

- AI service integrated into API monolith (per ADR-006 MVP direction)
- Grounding sources:
  - `MathematicsReport`
  - Event samples (`eventLogMode: replay`)
  - Canonical game definition and validation issues
- Prompt templates for:
  - RTP / volatility interpretation
  - Feature frequency explanation
  - Exposure truncation analysis
  - Golden fixture diff explanation
- Safety: no fabricated metrics; cite artifact fields

### Non-goals

- Autonomous game design without human approval
- Training on customer data (Enterprise policy TBD)

### Exit criteria

- Explanations reference only retrieved artifacts
- Evaluation set against golden fixture Q&A pairs

---

## Phase 15 — Enterprise features

**Goal:** Production-grade deployment for studio and platform operators.

### Scope (indicative)

- SSO (SAML/OIDC), RBAC, org tenancy
- Distributed simulation worker fleet (multi-machine, multi-region)
- Billing and usage metering
- Plugin marketplace / signed WASM sandbox (extends ADR-005 Phase 2+)
- Certification report export (PDF, regulatory templates)
- Advanced mathematical analysis (RTP decomposition, analytic base game, bootstrap CI)
- Kubernetes deployment manifests, observability (metrics, tracing)
- SLA-backed performance benchmarks (1M–10M spin runs)

### Dependencies

- Phases 11–14 complete
- Formal ADR for deployment topology
- Performance SLO sign-off

---

## Cross-cutting principles (all phases)

1. **Engine boundary is sacred** — platform code imports `runtime_core`; never forks engine logic
2. **Golden tests gate regressions** — CI must include runtime, simulation, and mathematical suites
3. **Immutability** — `GameVersion` snapshots are write-once; simulations reference pinned hashes
4. **Determinism** — stored profiles must reproduce identical metrics with same engine version
5. **Incremental delivery** — each phase independently demoable

---

## Timeline guidance

| Phase | Relative priority | Depends on |
|-------|-------------------|------------|
| 11 — FastAPI | **Next** | Engine v1.0 |
| 12 — PostgreSQL | High | Phase 11 |
| 13 — React | High | Phase 11 (API stable) |
| 14 — AI Assistant | Medium | Phases 11–13 |
| 15 — Enterprise | Long-term | Phases 11–14 |

---

## References

- [ENGINE_RELEASE_v1.0.md](./ENGINE_RELEASE_v1.0.md)
- [ARCHITECTURE_DECISION_RECORD_FINAL.md](./ARCHITECTURE_DECISION_RECORD_FINAL.md)
- [ENGINE_METRICS.md](./ENGINE_METRICS.md)
- [TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md)
