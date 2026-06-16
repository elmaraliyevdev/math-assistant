# ADR-005: Feature Strategy (Built-in Plugins + DSL First)

**Status:** Accepted (Architectural Direction)  
**Date:** 2026-06-14  
**Deciders:** Architecture, Product  
**Related:** [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §Feature DSL, §G, §O

---

## Context

Game mathematicians and designers need to configure features without writing code. Custom plugin uploads, WASM sandboxing, and a plugin marketplace are valuable long-term but add significant MVP complexity and security surface.

MVP must prove: **define game → validate → simulate → analyze metrics → explain results**.

---

## Decision

### MVP Feature Strategy

1. **Built-in plugins only** — maintained internally by platform team:
   - Base Game
   - Free Spins
   - Hold & Win
   - Multipliers

2. **Feature DSL first** — designers configure features declaratively in YAML/JSON; DSL **compiles** to internal state machine definitions bound to built-in plugins.

3. **No custom plugin uploads in MVP** — studios cannot upload TypeScript, WASM, or other plugin artifacts.

4. **No plugin marketplace in MVP**.

### Phase 2+ (Future)

- Custom plugin SDK (TypeScript)
- Org-private plugin registry
- Signed WASM sandbox (Enterprise)
- Plugin marketplace (Platform phase)

---

## Feature DSL Role

```
Designer YAML/JSON  →  DSL Compiler  →  Canonical GameVersion (state graph)  →  Runtime
                              ↑
                    Validation Engine (schema + graph)
```

Example DSL surface (illustrative):

```yaml
free_spins:
  trigger:
    scatters:
      3: 10
      4: 15
      5: 20
  retrigger:
    enabled: true
    awards:
      3: 5
      4: 10
      5: 15
```

The compiler emits `StateNode` + `Transition` entries referencing `core.free-spins@1.x` built-in plugin.

---

## Rationale

- Maximizes MVP velocity: one internal plugin codebase
- Lowers barrier for mathematicians (DSL vs code)
- Validation Engine can validate DSL schema **before** compilation and graph **after** compilation
- Plugin architecture preserved for future extensibility without MVP scope
- Golden tests target built-in behavior with stable baselines

---

## Consequences

### Positive

- Simpler security model (no arbitrary code execution)
- Faster CI (golden tests + built-in contract tests only)
- DSL errors are human-readable at save time

### Negative

- Novel mechanics not expressible in DSL require internal plugin work in MVP
- Risk of DSL scope creep — mitigate with strict MVP schema

### Neutral

- Internal plugins still implement `IFeatureRuntime`; DSL is a configuration layer, not a replacement for plugin host

---

## DSL MVP Scope

| DSL Construct | MVP | Notes |
|---------------|-----|-------|
| Free Spins triggers / awards | Yes | |
| Retrigger config | Yes | |
| Multiplier (fixed, per-spin) | Yes | |
| Hold & Win (symbols, respins, jackpots tiers) | Yes | Simplified tier model |
| Simple bonus triggers (scatter count, symbol count) | Yes | |
| Wheel / Pick bonuses | No | Phase 2 built-in + DSL extension |
| Persistent collectors | No | Phase 3 — session context model required |

---

## Alternatives Considered

| Alternative | Why Not for MVP |
|-------------|-----------------|
| Custom plugins day one | Security, SDK docs, marketplace — too much scope |
| DSL-only (no plugin abstraction) | Blocks future custom plugins; poor extensibility |
| JSON-only (no DSL compiler) | Too low-level for designers; error-prone |

---

## References

- [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) — Feature DSL Layer, §G, §O
- ADR-004 State Machine Execution Model
