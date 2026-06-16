# ADR-004: State Machine Execution Model (Hierarchical Stack-Based FSM)

**Status:** Accepted (Architectural Direction)  
**Date:** 2026-06-14  
**Deciders:** Architecture  
**Related:** [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) §F, §O

---

## Context

Slot games require nested bonus structures (e.g., Base → Free Spins → Hold & Win). Flat state enums do not scale to arbitrary nesting without combinatorial explosion. The platform must support MVP paths:

- Base Game
- Base → Free Spins
- Base → Hold & Win
- Base → Free Spins → Hold & Win

While preserving extensibility for deeper nesting in future phases.

Alternatives considered:

| Model | Description |
|-------|-------------|
| **Flat FSM** | Single enum for all states | Fails at nested resume semantics |
| **Hierarchical FSM (stack)** | Push/pop child machines | Natural fit for bonus nesting |
| **Behavior trees** | Common in game AI | Awkward for paytable-driven math |
| **Coroutines / async generators** | Per-feature yield points | Harder to validate statically |

---

## Decision

Adopt a **hierarchical stack-based finite state machine (pushdown automaton)** as the sole execution model for game sessions.

### Core Structures

```
Session
  └── executionStack: StateMachineFrame[]
        └── each frame: { plugin, localContext, currentState, config }
```

### Transition Rules

1. Active frame plugin executes `executeStep()` → `FeatureStepResult`
2. `spawnChildMachine` → **push** new frame (before sibling transitions)
3. Terminal / COMPLETE → **pop** frame; resume parent
4. Retrigger → mutate current frame context (no push)

### MVP Depth Limit

- Maximum stack depth: **4** (Base + FS + H&W + headroom)
- Validation Engine rejects graphs exceeding configured `maxStackDepth` (default 4 for MVP, 32 enterprise)

---

## Rationale

- Matches industry mental model of "entering" and "exiting" bonuses
- Isolates feature-local counters (spins remaining) per frame
- Session-level context (bet, cumulative win) shared at session root
- Validation Engine can analyze graph independently of runtime
- Feature DSL compiles to state graph consumed by this model

---

## Consequences

### Positive

- Unified model for all MVP feature paths without special cases
- Clear RTP contribution tagging per stack frame / state
- Validation rules (orphan states, unreachable nodes) apply to declarative graph

### Negative

- Slightly higher runtime overhead than flat FSM (stack management)
- Persistent cross-session state requires explicit session context (see §F.10 in spec)

### Neutral

- Future mechanics (cascades, cluster pays) still use this model; grid evaluation differs, not stack model

---

## Validation Engine Integration

The Validation Engine MUST verify before simulation:

- Exactly one initial state per machine / sub-graph
- All transitions reference valid targets
- No infinite loops without progression counters
- Stack depth of worst-case path ≤ configured limit
- Return transitions exist for every nested entry (pop path)

---

## Alternatives Rejected

| Alternative | Reason |
|-------------|--------|
| Flat FSM | Cannot resume FS after H&W without state duplication |
| Separate simulators per feature | RTP decomposition and nesting breaks |
| Unlimited stack without validation | Risk of runaway worker loops |

---

## References

- [TECHNICAL_SPECIFICATION.md](../TECHNICAL_SPECIFICATION.md) — §F State Machine Architecture
- ADR-005 Feature Strategy (DSL compiles to this model)
