# ADR-003: Money Representation Strategy (Fixed Point vs Decimal)

**Status:** Proposed  
**Date:** 2026-06-14  
**Deciders:** [TBD — Architecture, Math Engineering]  
**Related:** [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §E.4, §I, §N.1, ADR-001

---

## Context

RTP, volatility, and exposure calculations aggregate millions or billions of win and bet amounts. Floating-point (`float64`) arithmetic introduces rounding drift that can produce visible RTP errors (0.01%+ ) at scale — unacceptable for a mathematics platform.

The platform must represent:

- Bet amounts and line bets
- Paytable multipliers applied to bets
- Win amounts (potentially large for max exposure scenarios)
- Aggregated totals for RTP: `totalWin / totalBet`

MVP scope uses line-based 5×3 games with standard paytables; future phases add complex multiplier chains and persistent collection meters.

---

## Decision

**[TBD — select representation strategy]**

- [ ] **Option A: Fixed-point integers** — all amounts stored as `int64` in smallest currency unit (e.g., 1/10000 of bet unit); scale defined globally
- [ ] **Option B: Decimal library** — arbitrary-precision decimal (e.g., `rust_decimal`, `shopspring/decimal`)
- [ ] **Option C: Hybrid** — fixed-point in hot simulation path; decimal in API/reporting layer only
- [ ] **Option D: Other:** _______________

### Proposed Scale (if fixed-point)

```
BET_SCALE = 10_000   // 4 decimal places relative to bet unit
MAX_BET_UNITS = int64 max safe for paytable multiples × max exposure
```

---

## Rationale

<!-- Fill in after decision -->

- Performance impact in inner spin loop: [TBD]
- Alignment with spreadsheet baselines (golden tests): [TBD]
- Cross-language consistency (if API in TS, core in Rust/Go): [TBD]
- Overflow risk at max exposure: [TBD]

---

## Consequences

### Positive

- [TBD]

### Negative

- [TBD]

---

## Policy Decisions (Required with This ADR)

| Policy | Decision |
|--------|----------|
| RTP display precision | e.g., 4 decimal places (96.1234%) |
| Golden test tolerance ε | e.g., ±0.05% RTP vs spreadsheet |
| Summation strategy | Kahan summation / integer-only path |
| Float usage | Forbidden in core / allowed for display only |

---

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| `float64` throughout | Accumulation drift at 1M+ spins |
| String decimals | Too slow for simulation hot path |
| Rational numbers (fractions) | Complex for multiplier chains |

---

## Validation Plan

1. Golden Fixture 1: RTP matches spreadsheet within ε
2. Stress test: 100M spins synthetic always-win game — RTP stable vs float baseline
3. Max exposure edge case: verify no overflow at configured cap
4. Cross-shard merge: integer sums exact

---

## References

- [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) — §N.1 Mathematical Risks
- Golden fixtures spreadsheet baselines
