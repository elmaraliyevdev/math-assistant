# ADR-002: RNG Algorithm Selection and Deterministic Stream Splitting

**Status:** Proposed  
**Date:** 2026-06-14  
**Deciders:** [TBD — Architecture, Math Engineering]  
**Related:** [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §H, ADR-001, ADR-003

---

## Context

Reproducibility is a foundational requirement. Mathematicians and QA must be able to re-run a simulation with identical inputs and obtain identical aggregate metrics. Parallel simulation shards must not introduce non-determinism or correlated random streams.

Requirements:

- Deterministic given `(masterSeed, gameVersionHash, engineVersion, shardIndex)`
- Independent streams per shard (no overlap or correlation)
- Fast enough for inner spin loop (called thousands of times per spin)
- Well-documented algorithm for audit and golden test baselines
- Seed splitting strategy that survives parallel worker restarts

---

## Decision

**[TBD — select RNG algorithm and stream splitting scheme]**

### RNG Algorithm

- [ ] **PCG64** (Permuted Congruential Generator, 64-bit)
- [ ] **xoshiro256\*\***
- [ ] **ChaCha20-based counter mode** (cryptographic strength; slower)
- [ ] **Other:** _______________

### Stream Splitting

- [ ] **Option A:** `shardSeed = hash(masterSeed, shardIndex, runId)` — independent seeded RNG per shard
- [ ] **Option B:** Single counter-based RNG with partitioned sub-streams (e.g., SplitMix / jump-ahead)
- [ ] **Option C:** _______________

### Per-Spin / Per-Feature Derivation

Document how child RNG scopes are derived within a shard:

```
sessionRng   = derive(shardSeed, sessionIndex)
featureRng   = derive(sessionRng, stackDepth, frameId)
```

---

## Rationale

<!-- Fill in after decision -->

- Statistical quality requirements for Monte Carlo: [TBD]
- Performance benchmarks (RNG calls per spin): [TBD]
- Industry precedent in iGaming tooling: [TBD]
- Golden test reproducibility verified: [TBD]

---

## Consequences

### Positive

- [TBD]

### Negative

- [TBD]

---

## Invariants (Must Hold Regardless of Decision)

1. Same inputs → same aggregate metrics (within money representation policy — see ADR-003)
2. Shard merge order must not affect results (accumulators are commutative)
3. Every `SimulationRun` records: `rngAlgorithm`, `rngVersion`, `masterSeed`, `shardCount`
4. Golden tests pin exact RNG configuration

---

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| `Math.random()` / unseeded | Non-reproducible; unacceptable |
| Single global seed without splitting | Parallel shards would race or duplicate sequences |
| Cryptographic RNG only | Overkill for simulation; performance cost |

---

## Validation Plan

1. Run same 1M-spin job with 1 shard vs 8 shards → metrics must match within ε
2. Re-run with same seed after engine restart → bit-identical accumulators
3. Statistical tests on stream independence (optional chi-square on shard samples)
4. Document in simulation run metadata schema

---

## References

- [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) — §C.5 Reproducibility, §H.4 Parallelization
