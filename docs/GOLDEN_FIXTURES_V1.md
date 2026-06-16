# Golden Mathematical Test Fixtures — Framework v1.0.0

**Status:** Frozen Candidate  
**Version:** 1.0.0  
**Related:** [CANONICAL_GAME_SCHEMA_V1.md](./CANONICAL_GAME_SCHEMA_V1.md), [TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md) §I-G, `packages/game-schema/`

---

## 1. Purpose

Golden fixtures are **spreadsheet-validated reference games** used to regression-test:

- Feature DSL compiler output (optional path)
- Validation Engine (schema + graph)
- Runtime Core (state machine + built-in plugins)
- Mathematical Engine (metric aggregation)
- Determinism (seed + hash reproducibility)

**No RTP numeric targets are defined in this document.** Expected metric values will be supplied in per-fixture `expected.yaml` files once spreadsheet baselines are finalized.

---

## 2. Repository Layout (Target)

```
tests/golden/
├── manifest.yaml
├── fixture-01-base-5x3/
│   ├── README.md
│   ├── game.canonical.json          # Canonical GameVersion (pinned)
│   ├── expected.yaml                # Spreadsheet-derived metrics (TBD)
│   └── simulation.profile.yaml      # SimulationProfile for CI
├── fixture-02-base-free-spins/
├── fixture-03-base-hold-win/
└── fixture-04-nested-fs-hold-win/
```

| Artifact | Frozen | Notes |
|----------|--------|-------|
| `game.canonical.json` | Yes | Must validate against `game-version-1.0.0.schema.json` |
| `expected.yaml` | Yes (when populated) | Tolerance bands documented per metric |
| `simulation.profile.yaml` | Yes | Pins seed, spin count, engine version |
| Spreadsheet source | External | Linked from fixture README |

---

## 3. Manifest Schema (Conceptual)

```yaml
version: "1.0.0"
fixtures:
  - id: fixture-01-base-5x3
    path: fixture-01-base-5x3
    flow: base
    ci:
      prSpinCount: 1000000
      nightlySpinCount: 10000000
      blockMergeOnFailure: true
```

---

## 4. Simulation Profile Requirements (All Fixtures)

Each fixture uses a **Simulation Profile** (non-canonical) per CANONICAL_GAME_SCHEMA_V1.md §17:

| Field | CI PR | CI Nightly |
|-------|-------|------------|
| `profileVersion` | `1.0.0` | `1.0.0` |
| `mode` | `golden` | `golden` |
| `gameVersionContentHash` | From fixture canonical JSON | Same |
| `masterSeed` | Fixed per fixture | Same |
| `spinCount` | `1_000_000` | `10_000_000` |
| `determinism.requireExactEngineMatch` | `true` | `true` |
| `eventLog.mode` | `transitions_only` | `none` |

Determinism: same `(contentHash, masterSeed, engineVersion, spinCount)` **must** produce identical aggregate metrics within fixture tolerance.

---

## 5. Metric Framework (All Fixtures)

Metrics collected for every fixture (values TBD in `expected.yaml`):

| Metric key | Description | Tolerance policy |
|------------|-------------|------------------|
| `rtp.overall` | Total win / total bet × 100 | ±0.05% absolute (default) |
| `hitFrequency.anyWin` | P(win > 0) per base spin chain | ±0.10% absolute |
| `volatility.sigmaPerSpin` | Std dev of win per spin (normalized) | Document per fixture |
| `exposure.maxWinObserved` | Max win in sim | Must be ≤ declared cap |
| `exposure.maxMultiplierObserved` | Max win / bet | Must be ≤ declared cap |

Additional metrics per fixture (see sections below) use the same tolerance table in `expected.yaml`.

---

## 6. Fixture 1 — Base Game (5×3)

**ID:** `fixture-01-base-5x3`  
**Flow:** Base Game only  
**Purpose:** Validate base grid spin, line evaluation, paytable, hit frequency, and overall RTP without features.

### 6.1 Canonical Graph Shape

| Element | Expected |
|---------|----------|
| Machines | `main` only |
| States | `BASE` |
| Plugins | `core.base-game` |
| Nesting | None (stack depth 1) |

### 6.2 Expected Event Flow (transitions_only)

```
SPIN_CHAIN_START
  STATE_ENTER (BASE)
  GRID_RESULT
  WIN_EVALUATED (optional — when win > 0)
  TRIGGER_EMITTED (optional — none for pure base fixture)
  TRANSITION_TAKEN (SPIN_COMPLETE → stay BASE)
SPIN_CHAIN_END
```

No `FRAME_PUSH` / `FRAME_POP` events.

### 6.3 Expected Metrics (Framework)

| Metric | Required in expected.yaml |
|--------|---------------------------|
| `rtp.overall` | Yes |
| `rtp.components.BASE` | Yes (equals overall for this fixture) |
| `hitFrequency.anyWin` | Yes |
| `volatility.sigmaPerSpin` | Optional Phase 1 |
| `featureFrequency.*` | Must be absent / zero |

### 6.4 Spreadsheet Validation Requirements

Spreadsheet MUST independently compute:

- Line paytable contributions for defined 5×3 grid and reel strips
- Total bet model (lines × coin value × scale)
- Hit frequency (any line win)
- Overall RTP

Fixture README MUST link to spreadsheet tab and version.

### 6.5 CI Acceptance Criteria

- [ ] `game.canonical.json` passes JSON Schema + graph validation (zero errors)
- [ ] Golden run at PR spin count completes without `RUNTIME_LIMIT_HIT`
- [ ] `rtp.overall` within ε of `expected.yaml` (once populated)
- [ ] `hitFrequency.anyWin` within ε of `expected.yaml`
- [ ] `contentHash` stable unless canonical definition intentionally changed
- [ ] Determinism: two consecutive CI runs → identical accumulators

---

## 7. Fixture 2 — Base → Free Spins

**ID:** `fixture-02-base-free-spins`  
**Flow:** Base Game → Free Spins → Base  
**Purpose:** Validate scatter trigger, FS award table, retrigger, FS RTP decomposition, and feature frequency.

### 7.1 Canonical Graph Shape

| Element | Expected |
|---------|----------|
| Machines | `main` |
| States | `BASE`, `FREE_SPINS` |
| Plugins | `core.base-game`, `core.free-spins`, optional `core.multiplier` |
| Nesting | Goto (same machine); stack depth 1 |

### 7.2 Expected Event Flow

Typical feature entry path:

```
SPIN_CHAIN_START
  STATE_ENTER (BASE)
  GRID_RESULT
  TRIGGER_EMITTED (FREE_SPINS)
  TRANSITION_TAKEN (FEATURE_ENTRY → goto FREE_SPINS)
  STATE_ENTER (FREE_SPINS)
  ... FS spins ...
  FEATURE_COUNTER_UPDATE (spinsRemaining)
  TRANSITION_TAKEN (FEATURE_EXIT → goto BASE)
SPIN_CHAIN_END
```

Retrigger path (subset of spins):

```
  TRIGGER_EMITTED (RETRIGGER or FREE_SPINS)
  FEATURE_COUNTER_UPDATE (spinsRemaining increase)
```

### 7.3 Expected Metrics (Framework)

| Metric | Required in expected.yaml |
|--------|---------------------------|
| `rtp.overall` | Yes |
| `rtp.components.BASE` | Yes |
| `rtp.components.FREE_SPINS` | Yes |
| `rtp.reconciliationDelta` | Yes (must be ≤ ε) |
| `hitFrequency.anyWin` | Yes |
| `featureFrequency.FREE_SPINS` | Yes (entries per base chain) |
| `featureStats.avgSpinsAwarded` | Yes |
| `featureStats.retriggerRate` | If retrigger enabled in fixture |

### 7.4 Spreadsheet Validation Requirements

Spreadsheet MUST model:

- Base game RTP component
- Free Spins entry frequency (scatter combinations)
- Award distribution (3/4/5 scatters → spins)
- Retrigger contribution (if enabled)
- FS segment RTP (conditional on entry)

### 7.5 CI Acceptance Criteria

- [ ] All Fixture 1 criteria on merged metrics where applicable
- [ ] `featureFrequency.FREE_SPINS` within ε
- [ ] `featureStats.avgSpinsAwarded` within ε
- [ ] RTP decomposition sum ≈ overall RTP (reconciliation report)
- [ ] Event flow includes at least one `FREE_SPINS` entry in transition log sample (smoke spin count)

---

## 8. Fixture 3 — Base → Hold & Win

**ID:** `fixture-03-base-hold-win`  
**Flow:** Base Game → Hold & Win (spawn) → pop → Base  
**Purpose:** Validate spawn/pop stack, respin progression, H&W frequency, average bonus win, jackpot tiers.

### 8.1 Canonical Graph Shape

| Element | Expected |
|---------|----------|
| Machines | `main`, `hold_and_win` |
| States | `BASE`; `HAW_RESPINS` (or equivalent) |
| Plugins | `core.base-game`, `core.hold-and-win` |
| Nesting | Spawn/pop; max stack depth 2 |

### 8.2 Expected Event Flow

```
SPIN_CHAIN_START
  STATE_ENTER (BASE)
  GRID_RESULT
  TRIGGER_EMITTED (HOLD_AND_WIN)
  TRANSITION_TAKEN (FEATURE_ENTRY_SPAWN)
  FRAME_PUSH (hold_and_win)
  STATE_ENTER (HAW_RESPINS)
  ... multi_step respins ...
  FEATURE_COUNTER_UPDATE (respinsRemaining)
  TRANSITION_TAKEN (FEATURE_EXIT → pop)
  FRAME_POP
  STATE_ENTER (BASE)  // resumed
SPIN_CHAIN_END
```

### 8.3 Expected Metrics (Framework)

| Metric | Required in expected.yaml |
|--------|---------------------------|
| `rtp.overall` | Yes |
| `rtp.components.BASE` | Yes |
| `rtp.components.HOLD_AND_WIN` | Yes |
| `featureFrequency.HOLD_AND_WIN` | Yes |
| `featureStats.avgBonusWin` | Yes (average H&W total win per trigger) |
| `featureStats.avgRespinsUsed` | Optional |
| `exposure.maxWinObserved` | Yes (validate against cap) |

### 8.4 Spreadsheet Validation Requirements

Spreadsheet MUST model:

- H&W trigger frequency (bonus symbol count)
- Respin mechanics and fill rules
- Symbol credit values / jackpot tiers
- Average bonus win per triggering event

### 8.5 CI Acceptance Criteria

- [ ] Spawn/pop event pairs balance (`FRAME_PUSH` count = `FRAME_POP` count per chain)
- [ ] No stack depth > 2 for this fixture
- [ ] `featureFrequency.HOLD_AND_WIN` within ε
- [ ] `featureStats.avgBonusWin` within ε
- [ ] Progression terminates (no `RUNTIME_LIMIT_HIT` on respins)

---

## 9. Fixture 4 — Base → Free Spins → Hold & Win

**ID:** `fixture-04-nested-fs-hold-win`  
**Flow:** Base → Free Spins → Hold & Win → pop → Free Spins → exit → Base  
**Purpose:** Validate nested stack behavior, context freeze/resume, combined RTP decomposition, transition correctness.

### 9.1 Canonical Graph Shape

| Element | Expected |
|---------|----------|
| Machines | `main`, `hold_and_win` |
| States | `BASE`, `FREE_SPINS`, `HAW_RESPINS` |
| Plugins | All four MVP plugins (multiplier optional but recommended) |
| Nesting | FS goto + H&W spawn; max stack depth 3 |

### 9.2 Expected Event Flow

Nested path:

```
SPIN_CHAIN_START
  ... BASE → FREE_SPINS (goto) ...
  ... FS spin triggers HOLD_AND_WIN ...
  FRAME_PUSH (hold_and_win)
  ... H&W completes ...
  FRAME_POP
  ... FS resumes (spinsRemaining decrements again) ...
  ... FS completes ...
  TRANSITION_TAKEN (FEATURE_EXIT → BASE)
SPIN_CHAIN_END
```

**Invariants (CI assertions on event log sample):**

| Invariant | Rule |
|-----------|------|
| FS freeze | No `FEATURE_COUNTER_UPDATE` on FS `spinsRemaining` while H&W frame active |
| Resume | After `FRAME_POP`, FS `spinsRemaining` decreases on subsequent FS spins |
| RTP tagging | H&W wins tagged `HOLD_AND_WIN`; FS wins tagged `FREE_SPINS` |
| Stack | Max depth ≤ 3 |

### 9.3 Expected Metrics (Framework)

| Metric | Required in expected.yaml |
|--------|---------------------------|
| `rtp.overall` | Yes |
| `rtp.components.BASE` | Yes |
| `rtp.components.FREE_SPINS` | Yes |
| `rtp.components.HOLD_AND_WIN` | Yes |
| `rtp.reconciliationDelta` | Yes |
| `featureFrequency.FREE_SPINS` | Yes |
| `featureFrequency.HOLD_AND_WIN` | Yes (conditional on FS segment documented) |
| `featureStats.avgSpinsAwarded` | Yes |
| `featureStats.nestedHwFromFsRate` | Optional — P(H&W triggered during FS) |

### 9.4 Spreadsheet Validation Requirements

Spreadsheet MUST model:

- All Fixture 2 and Fixture 3 components
- Conditional probability of H&W entry during FS
- FS counter freeze semantics (no FS consumption during H&W)
- Combined RTP decomposition (three components + reconciliation)

### 9.5 CI Acceptance Criteria

- [ ] All Fixture 2 and 3 criteria where applicable
- [ ] RTP decomposition: BASE + FREE_SPINS + HOLD_AND_WIN ≈ overall (ε)
- [ ] Nested event invariants pass on transition log sample
- [ ] `contentHash` matches Appendix A reference in CANONICAL_GAME_SCHEMA_V1.md (once fixture checked in)
- [ ] Golden PR run uses `masterSeed` from manifest; no drift across engine versions without bump

---

## 10. CI Pipeline Requirements

```yaml
# Conceptual — .github/workflows/golden-tests.yml
jobs:
  golden-validate:
    steps:
      - validate game.canonical.json against game-version-1.0.0.schema.json
      - run graph validation (all GV-* applicable to fixture)
  golden-simulate:
    matrix: [fixture-01, fixture-02, fixture-03, fixture-04]
    steps:
      - run golden runner with simulation.profile.yaml (PR spin count)
      - compare metrics to expected.yaml tolerances (when populated)
      - fail on RUNTIME_LIMIT_HIT or RV-* errors
  golden-nightly:
    schedule: nightly
    steps:
      - run all fixtures at nightlySpinCount
```

| Gate | When | Failure action |
|------|------|----------------|
| Schema + graph | Every PR | Block merge |
| Golden sim (1M spins) | Every PR | Block merge |
| Golden sim (10M spins) | Nightly | Alert + block release tag |
| Determinism double-run | Every PR | Block merge |
| Event invariant checks (Fixture 3, 4) | Every PR | Block merge |

---

## 11. Populating expected.yaml (Process)

1. Mathematician completes spreadsheet baseline for fixture  
2. Export metric values with documented methodology  
3. Add `expected.yaml` with values + tolerances  
4. Run 10M spin sim; confirm within ε  
5. Pin `contentHash` in manifest  
6. Mark fixture **baseline locked** in README  

Until step 6, CI runs **structure-only** mode: validation + sim completes without metric assertion failures (metrics comparison skipped if `expected.yaml` missing `locked: true`).

---

## 12. Document Control

| Version | Status | Date | Changes |
|---------|--------|------|---------|
| 1.0.0 | Frozen Candidate | 2026-06-14 | Initial golden fixture framework |

---

*Numeric RTP and frequency targets are intentionally omitted. They will be added only via spreadsheet-backed `expected.yaml` files per fixture.*
