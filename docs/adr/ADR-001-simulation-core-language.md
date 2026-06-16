# ADR-001: Simulation Core Language (Rust vs Go)

**Status:** Proposed  
**Date:** 2026-06-14  
**Deciders:** [TBD — Architecture, Engineering Lead, Math Engineering]  
**Related:** [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §H, §O, ADR-002, ADR-006

---

## Context

The AI Game Mathematics Assistant requires a high-performance **simulation core** that executes hierarchical state machines, built-in feature plugins, and Monte Carlo spin loops. This core is the most performance-critical component in the platform.

The core must:

- Execute millions of spins with deterministic results
- Host built-in feature plugins (Base Game, Free Spins, Hold & Win, Multipliers)
- Support stack-based nested feature execution (MVP: up to Base → FS → H&W)
- Be callable from API integration tests and simulation workers
- Be maintainable by the internal team without requiring game studios to write native code in MVP

Candidates under consideration:

| Language | Strengths | Weaknesses |
|----------|-----------|------------|
| **Rust** | Maximum performance, memory safety, strong type system, excellent for numerical correctness | Steeper learning curve, longer initial development, FFI complexity |
| **Go** | Fast development, good concurrency, simpler FFI to Node, strong hiring pool | GC pauses (usually negligible), less strict memory model |

---

## Decision

**[TBD — select one]**

- [ ] **Option A: Rust** — simulation core implemented in Rust; exposed via FFI to workers and tests
- [ ] **Option B: Go** — simulation core implemented in Go; compiled as shared library or standalone worker binary
- [ ] **Option C: Hybrid** — Go orchestration layer + Rust hot path (defer unless profiling proves need)

---

## Rationale

<!-- Fill in after decision -->

- Performance benchmarks on golden fixtures (see Golden Test Framework):
  - Fixture 1 (Base 5×3): target ___ spins/sec/core
  - Fixture 4 (Base → FS → H&W): target ___ spins/sec/core
- Team expertise: [TBD]
- Time to MVP: [TBD]
- Long-term extensibility for persistent state and future mechanics: [TBD]

---

## Consequences

### Positive

- [TBD]

### Negative

- [TBD]

### Neutral

- Built-in plugins maintained internally in chosen language for MVP (no custom plugin upload)
- Feature DSL compiles to state machine definitions; does not change based on this ADR

---

## Alternatives Considered

| Alternative | Why Not (or When to Revisit) |
|-------------|------------------------------|
| TypeScript-only core | Insufficient throughput for 1M+ spin runs; acceptable only for smoke tests |
| C++ | Performance comparable to Rust; harder to hire and maintain safely |
| JVM (Kotlin) | GC and startup overhead; viable for API tier only |

---

## Validation Plan

1. Implement minimal base game spin loop in top 2 candidate languages
2. Run Golden Fixture 1 at 1M spins; compare throughput and determinism
3. Measure memory usage under 8-shard parallel load
4. Prototype FFI/bindings to NestJS integration test harness
5. Document build and CI requirements

---

## References

- [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) — §H Simulation Engine, §O MVP Scope
- Golden fixtures: `tests/golden/` (to be created)
