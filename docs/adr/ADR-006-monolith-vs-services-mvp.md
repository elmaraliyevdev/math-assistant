# ADR-006: Monolith vs Service Architecture for MVP

**Status:** Proposed  
**Date:** 2026-06-14  
**Deciders:** [TBD — Architecture, Engineering Lead]  
**Related:** [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §D, §O, ADR-001

---

## Context

The MVP must validate the core value proposition with minimal operational overhead:

- Game Definition System + Feature DSL
- Validation Engine
- State Machine Runtime
- Simulation Engine
- Mathematical Engine
- Basic AI explainability

Future enterprise scope includes distributed billion-spin simulations, separate AI workers, SSO, billing, and multi-region deployment. The MVP architecture should not block that evolution but should not prematurely distribute the system.

---

## Decision

**[TBD — select MVP deployment shape]**

- [ ] **Option A: Modular Monolith** — single deployable API process; simulation runs in-process or as subprocess pool; shared codebase packages
- [ ] **Option B: Monolith + Separate Worker Process** — API monolith + single worker binary (same repo, two entrypoints); queue optional (Redis/BullMQ)
- [ ] **Option C: Two Services Minimum** — API service + simulation worker service from day one; message queue required

### Recommended Direction (Pending Confirmation)

**Option B: Modular Monolith + Worker Process**

| Component | MVP Deployment |
|-----------|----------------|
| Web SPA | Static hosting / bundled |
| API | Single NestJS or Go monolith (game CRUD, validation, orchestration, math metrics, AI) |
| Simulation | Separate worker binary (same `runtime-core` library) |
| Queue | Lightweight (BullMQ + Redis) OR in-process job queue for local dev |
| Database | PostgreSQL |
| Cache | Redis (optional for MVP local dev) |

---

## Rationale

<!-- Fill in after decision -->

- Team size and DevOps capacity: [TBD]
- Need for parallel simulation on single machine: [TBD]
- Time to first working demo: [TBD]
- Path to enterprise distribution: [TBD]

---

## MVP Explicitly Excluded

| Capability | Phase |
|------------|-------|
| Multi-region worker fleet | Enterprise |
| Separate AI microservice | Phase 2 (AI can live in API monolith for MVP) |
| Aggregator service split | Phase 3 |
| Kubernetes requirement | Enterprise (Docker Compose sufficient for MVP) |
| Billing / SSO services | Phase 2+ |

---

## Module Boundaries (Regardless of Deployment)

Logical packages remain separated within monorepo:

```
packages/domain
packages/game-schema
packages/feature-dsl          # DSL parser + compiler
packages/validation-engine
packages/runtime-core
packages/math-engine
packages/plugins/*            # built-in only (MVP)
apps/api
apps/simulation-worker
apps/web
```

This preserves clean extraction to services later.

---

## Consequences

### Positive

- [TBD]

### Negative

- [TBD]

---

## Migration Path to Enterprise

1. **Phase 2:** Extract AI to optional sidecar if load warrants
2. **Phase 3:** Horizontal worker pool + aggregator; Temporal for job durability
3. **Enterprise:** Multi-region queue, dedicated validation service if CPU-bound

---

## Validation Plan

1. Deploy MVP stack on single VM / Docker Compose
2. Run Golden Fixtures 1–4 via CI
3. Run 1M spin job with worker process; verify API remains responsive
4. Document operational runbook (single-page)

---

## References

- [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) — §D, §O, §M
- ADR-001 Simulation Core Language
