# Canonical Game Schema v1.0 — Design Specification

**Document ID:** `CANONICAL_GAME_SCHEMA_V1`  
**Schema Version:** `1.0.0`  
**Status:** **Frozen Candidate**  
**Audience:** Engineering, Game Mathematics, Validation, Runtime, QA  
**Last Updated:** 2026-06-14  
**Related:** [TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md), [ADR-004](./adr/ADR-004-state-machine-execution-model.md), [ADR-005](./adr/ADR-005-feature-strategy-dsl-first.md)

> **Frozen Candidate (v1.0.0):** This specification is feature-complete for MVP implementation. Only clarifications, errata, and non-semantic editorial fixes are permitted without bumping to `schemaVersion` 1.1.0. Semantic changes require a new minor/major schema version and migration plan.

---

## Table of Contents

1. [Goals](#1-goals)
2. [MVP Supported Flows](#2-mvp-supported-flows)
3. [Top-Level Structure](#3-top-level-structure)
4. [State Machine Representation](#4-state-machine-representation)
5. [Plugin Binding Strategy](#5-plugin-binding-strategy)
6. [Transition Model](#6-transition-model)
7. [Session Context Model](#7-session-context-model)
8. [Validation Rules](#8-validation-rules)
9. [Versioning Strategy](#9-versioning-strategy)
10. [JSON Schema Deliverables](#10-json-schema-deliverables)
11. [Future-Proofing](#11-future-proofing)
12. [Runtime Event Contract](#12-runtime-event-contract)
13. [RTP Category Registry](#13-rtp-category-registry)
14. [Transition Priority Conventions](#14-transition-priority-conventions)
15. [Exposure Validation Strategies](#15-exposure-validation-strategies)
16. [Context Inheritance Policies](#16-context-inheritance-policies)
17. [Simulation Profile (Non-Canonical)](#17-simulation-profile-non-canonical)
18. [Runtime Safety Limits](#18-runtime-safety-limits)

---

## 1. Goals

The **Canonical Game Schema** is the **single source of truth** for a frozen game mathematics definition. It is consumed directly by the Runtime Core and all downstream systems. The Feature DSL compiles **into** this schema; the schema is **not** a projection of the DSL syntax.

### 1.1 Primary Goals

| Goal | How the schema achieves it |
|------|----------------------------|
| **Represent all MVP game types** | Root + nested state machines, four built-in plugins, line-base 5×3 grid |
| **Deterministic simulations** | Explicit RNG policy references, integer money, pinned plugin versions, content hash |
| **Hierarchical stack-based FSM** | Multiple `stateMachines`, `spawnMachine` transitions, `pop` effects |
| **Independent from Feature DSL** | DSL-agnostic field names; no DSL-only sugar in canonical JSON |
| **Immutable when published** | `status`, `contentHash`, write-once publish semantics |
| **JSON serializable** | UTF-8 JSON document; canonical serialization rules for hashing |
| **Forward-compatible expansion** | `schemaVersion`, namespaced extensions, optional blocks, plugin config openness |

### 1.2 Consumers

| Consumer | Usage |
|----------|-------|
| **Feature DSL Compiler** | Emits / updates `GameVersion` documents |
| **Validation Engine** | Schema validation + graph validation |
| **Runtime Core** | Loads snapshot; executes state machines |
| **Simulation Engine** | Loads snapshot; configures session factory |
| **Mathematical Engine** | Reads paytable, exposure, RTP categories |
| **Golden Test Framework** | Pins fixture documents by `contentHash`; uses Simulation Profile §17 |
| **Runtime / Debug** | Emits events per §12; enforces limits per §18 |
| **Future UI Editor** | Reads/writes canonical JSON (or compiles from forms) |

### 1.3 Non-Goals (v1.0.0)

- Custom plugin manifests (P3)
- Persistent feature **configuration** beyond placeholder store (P3)
- Cascading / cluster / Megaways **configuration** blocks (P2 — extension points only)
- Certification report templates
- Operator client presentation metadata

### 1.4 Canonical Document Identity

A serialized document is identified by:

```
contentHash = SHA-256( canonicalJsonBytes )
```

**Canonical JSON rules** (for hashing):

1. JSON object keys sorted lexicographically at every level  
2. No insignificant whitespace  
3. Numbers: integers without decimal point; decimals as JSON numbers with fixed scale policy documented per field  
4. UTF-8 encoding, no BOM  
5. Field `contentHash` **excluded** from hash input  

---

## 2. MVP Supported Flows

The schema MUST fully express these four MVP paths using the same structural model:

| # | Flow | State machine pattern |
|---|------|------------------------|
| 1 | **Base Game** | `main` machine: `BASE` only (terminal returns to idle between spins) |
| 2 | **Base → Free Spins** | `BASE` → `FREE_SPINS` → pop/`COMPLETE` → `BASE` |
| 3 | **Base → Hold & Win** | `BASE` → spawn `hold_and_win` machine → pop → `BASE` |
| 4 | **Base → Free Spins → Hold & Win** | `BASE` → `FREE_SPINS` → spawn `hold_and_win` → pop → `FREE_SPINS` → `COMPLETE` → `BASE` |

Future flows reuse the same primitives:

| Future flow | Extension mechanism |
|-------------|---------------------|
| Wheel Bonus | New built-in plugin + states + `spawnMachine` or inline multistep state |
| Pick Bonus | `ChoiceState` + plugin `core.pick-bonus` |
| Cascading | `core.base-game` config extension `cascade: { ... }` |
| Cluster Pays | `winModel.type: "cluster"` in `gameConfig` |
| Megaways | `gridModel.type: "megaways"` + dynamic ways in plugin config |
| Persistent collectors | `sessionContext.persistentStore` schema + plugin config |

---

## 3. Top-Level Structure

### 3.1 Root Document: `GameVersion`

The root type is **`GameVersion`**. One document = one versioned math definition snapshot.

```json
{
  "schemaVersion": "1.0.0",
  "gameVersion": { },
  "metadata": { },
  "gameConfig": { },
  "symbols": { },
  "reelSets": { },
  "paytable": { },
  "winModel": { },
  "betModel": { },
  "plugins": { },
  "stateMachines": { },
  "session": { },
  "exposure": { },
  "determinism": { },
  "precedence": { },
  "extensions": { },
  "rtpCategoryRegistry": { }
}
```

Optional at root (present after validation / publish):

```json
{
  "validationMetadata": { },
  "contentHash": "sha256:..."
}
```

---

### 3.2 Section Reference

#### 3.2.1 `schemaVersion`

| Property | Value |
|----------|-------|
| **Purpose** | Identifies the **document schema** format, not the game content version |
| **Type** | `string` (semver) |
| **Required** | Yes |
| **MVP value** | `"1.0.0"` |
| **Constraints** | Must match supported schema registry entry |
| **Validation** | Schema validator rejects unknown major version |

---

#### 3.2.2 `gameVersion`

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `id` | `string` (UUID) | Yes | Unique version identifier |
| `projectId` | `string` (UUID) | Yes | Parent game project |
| `versionNumber` | `integer` ≥ 1 | Yes | Monotonic per project |
| `status` | enum | Yes | `draft` \| `published` \| `archived` |
| `createdAt` | ISO 8601 | Yes | Creation timestamp |
| `publishedAt` | ISO 8601 | No | Set once on publish |
| `createdBy` | `string` | No | Author identifier |
| `label` | `string` | No | Human label ("v3 — FS RTP tune") |
| `source` | enum | No | `canonical` \| `dsl-compiler` \| `import` |

**Constraints:**

- `published` documents are **immutable** — any change requires new `id` + incremented `versionNumber`
- `publishedAt` required when `status === "published"`

---

#### 3.2.3 `metadata`

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `title` | `string` | Yes | Game title |
| `description` | `string` | No | Internal description |
| `tags` | `string[]` | No | Search / organization |
| `rtpTarget` | `RtpTarget` | No | Design target for comparison (not enforced math) |
| `volatilityTarget` | `string` | No | e.g. `"medium"`, `"high"` |

**`RtpTarget`:**

| Field | Type | Constraints |
|-------|------|-------------|
| `percent` | number | 0–100, e.g. 96.5 |
| `tolerance` | number | e.g. 0.1 (±0.1%) |

---

#### 3.2.4 `gameConfig`

Core mechanical configuration shared across plugins.

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `grid` | `GridSpec` | Yes | Reels × rows |
| `defaultReelSetId` | `string` | Yes | Reference into `reelSets` |

**`GridSpec` (MVP):**

| Field | Type | Constraints |
|-------|------|-------------|
| `reels` | integer | 1–10 (MVP: typically 5) |
| `rows` | integer | 1–10 (MVP: typically 3) |
| `indexOrigin` | enum | `"top-left"` \| `"bottom-left"` — default `"top-left"` |

**Future `gridModel` (extension, P2+):**

```json
"gridModel": {
  "type": "fixed | megaways | cluster",
  "megaways": { "reelHeightsTableId": "..." }
}
```

MVP uses implicit `type: "fixed"`.

---

#### 3.2.5 `symbols`

Map of symbol definitions keyed by **symbol ID** (stable string).

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `[symbolId].id` | `string` | Yes | Same as key |
| `[symbolId].displayName` | `string` | No | UI / docs |
| `[symbolId].type` | enum | Yes | `regular` \| `wild` \| `scatter` \| `bonus` |
| `[symbolId].pays` | boolean | No | Default true for regular; false for decorative |
| `[symbolId].substitutes` | `string[]` | No | Wild substitution rules |
| `[symbolId].properties` | object | No | Extensible flags |

**Constraints:**

- At least one `regular` symbol
- `wild` symbols must declare `substitutes` or global wild rule in base plugin config
- `scatter` / `bonus` used by feature triggers — must exist if triggers reference them
- Symbol IDs: `^[A-Za-z][A-Za-z0-9_]{0,31}$`

---

#### 3.2.6 `reelSets`

Named reel strip collections.

| Field | Type | Purpose |
|-------|------|---------|
| `[reelSetId].id` | `string` | Reel set identifier |
| `[reelSetId].reels` | `ReelStrip[]` | Length MUST equal `gameConfig.grid.reels` |

**`ReelStrip`:**

| Field | Type | Constraints |
|-------|------|-------------|
| `reelIndex` | integer | 0-based, unique per set |
| `symbols` | `string[]` | Symbol IDs; length ≥ rows |
| `weights` | `integer[]` | Optional; same length as symbols if present |

If `weights` omitted, uniform random position on strip.

---

#### 3.2.7 `paytable`

Line / way pays for symbol combinations.

**MVP `winModel` companion:** see §3.2.8.

| Field | Type | Purpose |
|-------|------|---------|
| `lines` | `PaylineDefinition[]` | Required when `betModel.type === "lines"` |
| `pays` | `PaytableEntry[]` | Symbol combination payouts |

**`PaylineDefinition`:**

| Field | Type | Constraints |
|-------|------|-------------|
| `index` | integer | 1-based line number |
| `path` | `integer[]` | Length = reels; each value row index 0..rows-1 |

**`PaytableEntry`:**

| Field | Type | Constraints |
|-------|------|-------------|
| `symbolId` | `string` | Must exist in `symbols` |
| `count` | integer | ≥ 3 typically (OAK count) |
| `multiplier` | `MoneyMultiplier` | Pay × bet-per-line or × total bet per `winModel` |

**`MoneyMultiplier`:** integer or rational object `{ "num": 10, "den": 1 }` — see §3.2.16.

---

#### 3.2.8 `winModel`

| Field | Type | MVP | Purpose |
|-------|------|-----|---------|
| `type` | enum | `"lines"` | `lines` \| `ways` \| `cluster` (future) |
| `direction` | enum | `"left-to-right"` | Win evaluation direction |
| `scatterPaysOnReels` | boolean | true | Scatter evaluated anywhere on grid |
| `highestWinOnlyPerLine` | boolean | true | Standard line rule |

---

#### 3.2.9 `betModel`

| Field | Type | MVP | Constraints |
|-------|------|-----|-------------|
| `type` | enum | `"lines"` | `lines` \| `ways` \| `totalBet` |
| `lineCount` | integer | 20 | Required for `lines` |
| `coinValueScale` | integer | 100 | Minor units per coin (see money) |
| `defaultCoinValue` | integer | 1 | |
| `minCoinValue` | integer | 1 | |
| `maxCoinValue` | integer | 1 | MVP often fixed |
| `totalBetMinorUnits` | integer | computed | Optional explicit total bet |

**Total bet (MVP lines):**

```
totalBetMinorUnits = lineCount × defaultCoinValue × coinValueScale
```

(or explicit override if allowed by validation policy)

---

#### 3.2.10 `plugins`

Registry of **plugin references** used in this game version.

| Field | Type | Purpose |
|-------|------|---------|
| `[refId].refId` | `string` | Local alias used by states |
| `[refId].pluginId` | `string` | Global plugin id e.g. `core.base-game` |
| `[refId].pluginVersion` | semver string | Pinned version e.g. `"1.0.0"` |
| `[refId].configSchemaVersion` | string | Plugin config schema semver |
| `[refId].capabilities` | `string[]` | Declared at compile time for validation |

**Constraints:**

- Every `state.pluginRefId` must resolve to an entry here
- MVP: only `core.base-game`, `core.free-spins`, `core.hold-and-win`, `core.multiplier`
- Duplicate `(pluginId, pluginVersion)` allowed with different `refId` if configs differ

Example:

```json
"plugins": {
  "base_main": {
    "refId": "base_main",
    "pluginId": "core.base-game",
    "pluginVersion": "1.0.0",
    "configSchemaVersion": "1.0.0",
    "capabilities": ["spin.grid", "win.lines", "win.scatter"]
  }
}
```

---

#### 3.2.11 `stateMachines`

Map of state machine definitions — see [§4](#4-state-machine-representation).

| Field | Type | Required |
|-------|------|----------|
| `[machineId]` | `StateMachine` | Yes for each referenced machine |

**Constraints:**

- Must include `session.rootMachineId` key
- Machine IDs: `^[a-z][a-z0-9_]{0,63}$`

---

#### 3.2.12 `session`

Session-level execution configuration.

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `rootMachineId` | `string` | Yes | Entry state machine |
| `rootStateId` | `string` | No | Override initial state (default: machine's `initialStateId`) |
| `maxStackDepth` | integer | Yes | MVP default: `4` |
| `spinLoopMode` | enum | Yes | MVP: `"single_chain"` |
| `persistentStore` | object | No | Placeholder for P3 — MUST be `{}` or omitted in MVP |
| `runtimeLimits` | object | No | Override platform defaults — see [§18](#18-runtime-safety-limits) |
| `contextInheritancePolicy` | string | No | Policy set id — default `"mvp-v1"` — see [§16](#16-context-inheritance-policies) |

**`spinLoopMode` values:**

| Value | Meaning |
|-------|---------|
| `single_chain` | MVP: one base-spin execution chain per simulated spin |
| `multi_base_session` | P3: multiple base spins share session persistent store |

---

#### 3.2.13 `exposure`

Maximum win governance.

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `maxWinMinorUnits` | integer | Yes | Absolute cap |
| `maxWinMultiplier` | integer | No | Cap as × total bet |
| `capScope` | enum | Yes | `session_spin_chain` \| `single_spin` \| `feature` |
| `enforceCap` | boolean | Yes | Runtime truncates wins if true |
| `validationMode` | enum | Yes | See [§15](#15-exposure-validation-strategies) — default `strict` |

**Validation:** Strategy depends on `validationMode`. See §15 for `strict`, `simulation_assisted`, and `manual` modes.

---

#### 3.2.14 `determinism`

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `rngAlgorithm` | string | Yes | e.g. `"PCG64"` (ADR-002) |
| `rngAlgorithmVersion` | string | Yes | e.g. `"1.0"` |
| `seedDerivationPolicy` | string | Yes | e.g. `"v1-hash-shard"` |
| `moneyRepresentation` | enum | Yes | `"fixed_minor_units"` |
| `moneyScale` | integer | Yes | e.g. `10000` |

Simulation runs record these fields plus external `masterSeed`.

---

#### 3.2.15 `precedence`

Global trigger conflict resolution when multiple trigger tokens match transitions on the same step.

| Field | Type | Purpose |
|-------|------|---------|
| `triggerOrder` | `string[]` | Ordered trigger token names (first = highest precedence) |

MVP example:

```json
"precedence": {
  "triggerOrder": ["HOLD_AND_WIN", "FREE_SPINS", "COMPLETE"]
}
```

---

#### 3.2.16 Money Representation

All monetary amounts in canonical schema use **integer minor units**:

| Concept | Representation |
|---------|----------------|
| Paytable multiplier | Integer × `betModel` unit OR rational `{ num, den }` |
| Wins / caps | `integer` minor units |
| Scale | Documented in `determinism.moneyScale` |

**No floating point** in canonical documents.

---

#### 3.2.17 `extensions`

Namespaced extension bag for forward-compatible metadata.

| Field | Type | Purpose |
|-------|------|---------|
| `[namespace].*` | any | e.g. `"studio.acme": { "internalId": "42" }` |

**Rules:**

- Unknown extension namespaces MUST be preserved by tooling  
- Validation Engine ignores unknown namespaces unless registered  
- MVP: may be empty `{}`

---

#### 3.2.18 `validationMetadata`

Populated after successful validation (optional on drafts, recommended on publish).

| Field | Type | Purpose |
|-------|------|---------|
| `validatedAt` | ISO 8601 | Timestamp |
| `validatorVersion` | string | Validation Engine version |
| `reportId` | UUID | Link to full report |
| `checksPassed` | `string[]` | Check codes |
| `warnings` | `ValidationIssue[]` | Non-blocking issues |

---

#### 3.2.19 `rtpCategoryRegistry`

Optional document-level extension of the platform RTP category registry — see [§13](#13-rtp-category-registry).

| Field | Type | Required |
|-------|------|----------|
| `extends` | string | Yes if block present |
| `categories` | map | Yes if block present |

Omit entirely when all states use platform MVP categories.

---

#### 3.2.20 `contentHash`

| Field | Type | Purpose |
|-------|------|---------|
| `contentHash` | `string` | `sha256:` + hex digest of canonical JSON (excluding this field) |

Set on publish. Simulation snapshots MUST match hash.

---

## 4. State Machine Representation

### 4.1 Concepts

| Concept | Description |
|---------|-------------|
| **StateMachine** | Named graph of states with one initial state |
| **State** | Node bound to one plugin reference + config |
| **Transition** | Edge triggered by plugin output token |
| **Spawn** | Push child machine onto execution stack |
| **Pop** | Pop current machine frame; resume parent |
| **Terminal state** | State with `terminal: true`; triggers stack pop when entered or completed |

### 4.2 `StateMachine` Object

```json
{
  "id": "main",
  "label": "Main Game Flow",
  "initialStateId": "BASE",
  "states": {
    "BASE": { },
    "FREE_SPINS": { }
  }
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique within `stateMachines` |
| `label` | string | No | Human-readable |
| `initialStateId` | string | Yes | Must exist in `states` |
| `states` | map | Yes | Non-empty; keys are state IDs |

**Graph validation rules:**

- Exactly one `initialStateId` per machine  
- All states reachable from initial (unless explicitly marked `deprecated: true`)  
- No orphan states  

---

### 4.3 `State` Object

```json
{
  "id": "FREE_SPINS",
  "label": "Free Spins Feature",
  "pluginRefId": "fs_main",
  "stateType": "atomic_spin",
  "terminal": false,
  "rtpCategory": "FREE_SPINS",
  "pluginConfig": { },
  "transitions": [ ],
  "progression": { }
}
```

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `id` | string | Yes | Unique within parent machine |
| `label` | string | No | Display / reports |
| `pluginRefId` | string | Yes | Key into `plugins` |
| `stateType` | enum | Yes | See §4.4 |
| `terminal` | boolean | Yes | Terminal / exit semantics |
| `rtpCategory` | string | Yes | Must be registered — see [§13](#13-rtp-category-registry) |
| `pluginConfig` | object | Yes | Validated against plugin schema |
| `transitions` | `Transition[]` | Yes | May be empty only if `terminal: true` |
| `progression` | object | No | Loop guard metadata for validation |

**State ID constraints:** `^[A-Z][A-Z0-9_]{0,63}$` (convention: SCREAMING_SNAKE)

---

### 4.4 `stateType` Enum

| Value | MVP | Runtime behavior |
|-------|-----|------------------|
| `atomic_spin` | Yes | One grid spin + win eval per step |
| `multi_step` | Yes | Hold & Win respins; multiple steps before transition |
| `choice` | No (P2) | Pick bonus |
| `composite_entry` | No | Wrapper / spawn-only (use spawn transitions instead in MVP) |

---

### 4.5 `progression` (Validation Hints)

Used by Validation Engine to detect infinite loops.

```json
"progression": {
  "counterField": "respinsRemaining",
  "decrementsOn": "each_step",
  "minValue": 0,
  "terminatesWhen": "counterField == 0"
}
```

Hold & Win example: respins decrement → guaranteed termination.

---

### 4.6 Nested State Machines (Stack Model)

Nested features use **separate machines** + **spawn transitions**.

**MVP nested pattern (Base → FS → H&W):**

```
stateMachines:
  main:
    BASE ──FREE_SPINS──► FREE_SPINS ──COMPLETE──► BASE
    FREE_SPINS ──HOLD_AND_WIN (spawn)──► [push hold_and_win]

  hold_and_win:
    HAW_RESPINS ──COMPLETE (pop)──► (resume FREE_SPINS)
```

**Child spawn:** transition with `"effect": "spawn"` + `targetMachineId`  
**Child exit:** transition with `"effect": "pop"` from terminal or COMPLETE trigger  

Runtime pushes `hold_and_win` initial state; on pop, resumes `FREE_SPINS` frame unchanged.

---

### 4.7 JSON Example: Minimal Base Game

```json
{
  "session": { "rootMachineId": "main", "maxStackDepth": 4, "spinLoopMode": "single_chain" },
  "stateMachines": {
    "main": {
      "id": "main",
      "initialStateId": "BASE",
      "states": {
        "BASE": {
          "id": "BASE",
          "pluginRefId": "base_main",
          "stateType": "atomic_spin",
          "terminal": false,
          "rtpCategory": "BASE",
          "pluginConfig": {
            "reelSetId": "base_game",
            "scatterTriggers": []
          },
          "transitions": [
            {
              "id": "t_base_complete",
              "trigger": "SPIN_COMPLETE",
              "priority": 100,
              "effect": "stay",
              "targetStateId": "BASE"
            }
          ]
        }
      }
    }
  }
}
```

Note: MVP simulates one spin chain; `SPIN_COMPLETE` returns to idle/base for next simulated spin.

---

### 4.8 JSON Example: Base → Free Spins

Additional state + transition on `BASE`:

```json
{
  "id": "FREE_SPINS",
  "pluginRefId": "fs_main",
  "stateType": "atomic_spin",
  "terminal": false,
  "rtpCategory": "FREE_SPINS",
  "pluginConfig": {
    "reelSetId": "free_spins",
    "awardsByScatterCount": { "3": 10, "4": 15, "5": 20 },
    "retrigger": {
      "enabled": true,
      "awardsByScatterCount": { "3": 5, "4": 10, "5": 15 }
    },
    "multiplierRefId": "mult_fs"
  },
  "transitions": [
    {
      "id": "t_fs_complete",
      "trigger": "FEATURE_COMPLETE",
      "priority": 100,
      "effect": "goto",
      "targetStateId": "BASE"
    }
  ]
}
```

On `BASE`:

```json
{
  "id": "t_base_to_fs",
  "trigger": "FREE_SPINS",
  "priority": 10,
  "effect": "goto",
  "targetStateId": "FREE_SPINS"
}
```

---

### 4.9 JSON Example: Spawn Hold & Win from Free Spins

Separate machine:

```json
"hold_and_win": {
  "id": "hold_and_win",
  "initialStateId": "HAW_RESPINS",
  "states": {
    "HAW_RESPINS": {
      "id": "HAW_RESPINS",
      "pluginRefId": "haw_main",
      "stateType": "multi_step",
      "terminal": false,
      "rtpCategory": "HOLD_AND_WIN",
      "pluginConfig": {
        "reelSetId": "hold_and_win",
        "triggerSymbolId": "BONUS",
        "triggerSymbolCount": 6,
        "initialRespins": 3,
        "gridCapacity": 15,
        "jackpotTiers": {
          "mini": 20,
          "major": 100,
          "grand": 500
        },
        "multiplierRefId": "mult_haw"
      },
      "progression": {
        "counterField": "respinsRemaining",
        "decrementsOn": "each_step",
        "minValue": 0
      },
      "transitions": [
        {
          "id": "t_haw_pop",
          "trigger": "FEATURE_COMPLETE",
          "priority": 100,
          "effect": "pop"
        }
      ]
    }
  }
}
```

Spawn transition on `FREE_SPINS`:

```json
{
  "id": "t_fs_to_haw",
  "trigger": "HOLD_AND_WIN",
  "priority": 10,
  "effect": "spawn",
  "targetMachineId": "hold_and_win"
}
```

---

## 5. Plugin Binding Strategy

### 5.1 Plugin Reference Format

States never embed bare plugin IDs inline. They reference **`plugins` map entries** by `pluginRefId`.

Fully qualified plugin identity:

```
{pluginId}@{pluginVersion}
```

Examples:

| pluginId | pluginVersion | Purpose |
|----------|---------------|---------|
| `core.base-game` | `1.0.0` | Base grid spin |
| `core.free-spins` | `1.0.0` | Free spins feature |
| `core.hold-and-win` | `1.0.0` | Hold & Win respins |
| `core.multiplier` | `1.0.0` | Multiplier application |

### 5.2 Multiplier Binding (Cross-Cutting Plugin)

Multipliers are referenced from feature configs via **`multiplierRefId`** pointing to entries in `plugins` with `pluginId: "core.multiplier"`.

```json
"mult_fs": {
  "refId": "mult_fs",
  "pluginId": "core.multiplier",
  "pluginVersion": "1.0.0",
  "configSchemaVersion": "1.0.0",
  "capabilities": ["multiplier.apply"]
}
```

Referenced from FS `pluginConfig.multiplierRefId`. Runtime resolves multiplier plugin when applying wins in that frame.

### 5.3 `pluginConfig` Validation

Each state's `pluginConfig` MUST validate against the JSON Schema registered for:

```
{pluginId}@{configSchemaVersion}
```

Validation Engine responsibilities:

1. Resolve `pluginRefId` → plugin entry  
2. Load plugin config schema from platform registry  
3. Validate `pluginConfig` instance  
4. Verify declared `capabilities` satisfy `stateType` requirements  

**MVP capability requirements:**

| stateType | Required capabilities |
|-----------|----------------------|
| `atomic_spin` | `spin.grid`, at least one of `win.lines` / `win.scatter` |
| `multi_step` | `state.multistep`, `spin.grid` |

### 5.4 Versioning Strategy (Plugins)

| Rule | Description |
|------|-------------|
| **Pin exact version** | Canonical document pins `pluginVersion` semver (not ranges) |
| **Platform registry** | Runtime loads exact version or rejects snapshot |
| **Schema evolution** | `configSchemaVersion` independent patch/minor within same pluginVersion |
| **Breaking changes** | Major plugin version bump → new `pluginId` suffix or major semver |
| **Golden tests** | Pin full plugin versions in fixture `contentHash` |

**Compatibility matrix (maintained by platform):**

```
runtimeEngine 1.x → supports core.*@1.0.x
```

Published games never auto-migrate plugin versions.

### 5.5 MVP Plugin Config Sketches

**`core.base-game@1.0.0`:**

```json
{
  "reelSetId": "base_game",
  "scatterTriggers": [
    { "symbolId": "SCATTER", "minCount": 3, "emitTrigger": "FREE_SPINS" }
  ],
  "bonusTriggers": [
    { "symbolId": "BONUS", "minCount": 6, "emitTrigger": "HOLD_AND_WIN" }
  ]
}
```

**`core.free-spins@1.0.0`:** (see §4.8)

**`core.hold-and-win@1.0.0`:** (see §4.9)

**`core.multiplier@1.0.0`:**

```json
{
  "mode": "fixed",
  "value": 2,
  "scope": "feature_frame",
  "applyTo": "all_wins_in_frame"
}
```

---

## 6. Transition Model

### 6.1 `Transition` Object Structure

```json
{
  "id": "t_fs_to_haw",
  "label": "Enter Hold & Win from Free Spins",
  "trigger": "HOLD_AND_WIN",
  "priority": 10,
  "guard": null,
  "effect": "spawn",
  "targetStateId": null,
  "targetMachineId": "hold_and_win",
  "actions": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique within parent state |
| `label` | string | No | Documentation |
| `trigger` | string | Yes | Trigger token from plugin |
| `priority` | integer | Yes | Must use registered tier from [§14](#14-transition-priority-conventions) |
| `priorityTier` | enum | Recommended | Semantic tier; compiler MUST emit both tier and numeric value |
| `guard` | `GuardExpression` | No | Additional condition |
| `effect` | enum | Yes | `goto` \| `spawn` \| `pop` \| `stay` |
| `targetStateId` | string | Conditional | Required for `goto`, `stay` |
| `targetMachineId` | string | Conditional | Required for `spawn` |
| `actions` | `TransitionAction[]` | No | Side effects (counter resets) |

---

### 6.2 Standard Trigger Tokens (MVP)

| Token | Typical source |
|-------|----------------|
| `FREE_SPINS` | Base game scatter trigger |
| `HOLD_AND_WIN` | Base or FS bonus symbol trigger |
| `FEATURE_COMPLETE` | Feature exhausted (FS spins = 0, H&W filled) |
| `SPIN_COMPLETE` | Single spin resolved, no feature entry |
| `RETRIGGER` | Internal FS handling (may not need transition) |

Plugins MAY emit custom tokens; all must have matching transitions or explicit drop policy.

---

### 6.3 `GuardExpression`

```json
{
  "op": "and",
  "args": [
    { "op": "eq", "path": "frame.spinsRemaining", "value": 0 },
    { "op": "eq", "path": "session.stackDepth", "value": 1 }
  ]
}
```

| Op | Meaning |
|----|---------|
| `eq`, `neq`, `gt`, `gte`, `lt`, `lte` | Comparison |
| `and`, `or`, `not` | Logic |
| `path` | Context path (see §7) |

MVP: guards optional; most flows use plugin-emitted tokens only.

---

### 6.4 `TransitionAction`

```json
{
  "type": "set_context",
  "path": "frame.spinsRemaining",
  "value": 10
}
```

MVP: prefer plugin-managed counters; actions reserved for compiler-generated setup.

---

### 6.5 Conflict Resolution Algorithm

When plugin emits multiple trigger tokens `{T1, T2, ...}` on one step:

```
1. Collect all transitions on current state where trigger ∈ emitted tokens
2. Filter by guard evaluation (if present)
3. Sort by:
   a. precedence.triggerOrder index (lower index = wins)
   b. transition.priority (lower = wins)
   c. transition.id lexicographic (stable tie-break)
4. Execute FIRST matching transition only (exclusive choice)
5. If spawn effect: push before any goto in same step
6. Log warning if multiple equally-ranked matches (validation should prevent)
```

**Validation Engine** must flag `AMBIGUOUS_TRANSITION` when step 5 would be nondeterministic without precedence.

---

### 6.6 Effect Semantics

| Effect | Behavior |
|--------|----------|
| `goto` | Change current state within same machine frame |
| `spawn` | Push `targetMachineId` initial state onto stack; parent frame frozen |
| `pop` | Pop current machine frame; resume parent state |
| `stay` | Re-enter same state (multi-step loops) |

---

### 6.7 Transition Examples

**Base → Hold & Win (direct spawn from BASE):**

```json
{
  "id": "t_base_to_haw",
  "trigger": "HOLD_AND_WIN",
  "priorityTier": "FEATURE_ENTRY_SPAWN",
  "priority": 100,
  "effect": "spawn",
  "targetMachineId": "hold_and_win"
}
```

**Free Spins complete → Base:**

```json
{
  "id": "t_fs_complete",
  "trigger": "FEATURE_COMPLETE",
  "priorityTier": "FEATURE_EXIT",
  "priority": 900,
  "effect": "goto",
  "targetStateId": "BASE"
}
```

**Hold & Win complete → pop to parent (FS or BASE):**

```json
{
  "id": "t_haw_pop",
  "trigger": "FEATURE_COMPLETE",
  "priorityTier": "FEATURE_EXIT",
  "priority": 900,
  "effect": "pop"
}
```

### 6.8 Priority Tiers

Transitions MUST conform to [§14 Transition Priority Conventions](#14-transition-priority-conventions). The DSL compiler emits `priorityTier` alongside numeric `priority`. Hand-authored graphs without tiers receive validation warning `GV-028`.

---

## 7. Session Context Model

The canonical schema **defines static structure**; **runtime** materializes mutable context. This section specifies the **context contract** referenced by guards, validation, and plugins.

### 7.1 Ownership Overview

```
SessionContext (1 per simulated spin chain)
├── identifiers: sessionId, spinIndex, masterSeed
├── bet: BetContext (immutable for chain)
├── totals: totalWinMinorUnits, totalBetMinorUnits
├── rng: RngContext (derived streams)
├── persistentStore: PersistentStore (placeholder MVP)
└── executionStack: FrameContext[]
      └── FrameContext (1 per stack depth)
            ├── machineId, stateId, frameId
            ├── pluginRefId, rtpCategory
            ├── frameLocal: object (plugin-owned schema)
            └── multiplierContext: optional
```

---

### 7.2 Session Context Fields

| Field | Owner | Mutable | Lifetime |
|-------|-------|---------|----------|
| `sessionId` | Runtime | No | Full chain |
| `spinIndex` | Runtime | Yes | Incremented per base spin in multi-base mode |
| `masterSeed` | Simulation config | No | Full chain |
| `totalWinMinorUnits` | Runtime | Yes | Accumulates all wins |
| `totalBetMinorUnits` | Canonical `betModel` | No | Fixed per chain (MVP) |
| `betContext` | Canonical | No | lineCount, coinValue, scale |
| `rngContext` | Runtime | Yes | Derived sub-streams per frame/step |
| `persistentStore` | Runtime | Yes (P3) | Empty object MVP |
| `stackDepth` | Runtime | Yes | `executionStack.length` |

---

### 7.3 Frame Context Fields

| Field | Owner | Mutable | Lifetime |
|-------|-------|---------|----------|
| `frameId` | Runtime | No | Created on push |
| `machineId` | Canonical | No | From spawn / root |
| `stateId` | Runtime | Yes | Transitions update |
| `pluginRefId` | Canonical state | No | |
| `rtpCategory` | Canonical state | No | Win tagging |
| `spinsRemaining` | FS plugin | Yes | FS frame only |
| `respinsRemaining` | H&W plugin | Yes | H&W frame only |
| `heldSymbols` | H&W plugin | Yes | Array of grid positions |
| `activeMultiplier` | Multiplier plugin | Yes | Resolved at frame entry |
| `frameLocalState` | Plugin | Yes | opaque object; validated by plugin schema |

---

### 7.4 Context Path Reference (for Guards)

| Path | Description |
|------|-------------|
| `session.stackDepth` | Current stack depth |
| `session.totalWinMinorUnits` | Cumulative win |
| `frame.stateId` | Active state |
| `frame.spinsRemaining` | FS counter |
| `frame.respinsRemaining` | H&W counter |
| `frame.heldSymbols.length` | Held symbol count |

---

### 7.5 Inheritance Rules (Summary)

See [§16 Context Inheritance Policies](#16-context-inheritance-policies) for the authoritative policy tables, spawn/pop matrices, and nested-feature worked examples.

| Data | Scope | On spawn | On pop |
|------|-------|----------|--------|
| Bet / coin value | Session | Inherited | Unchanged |
| Total win | Session | Inherited | Unchanged |
| FS spins remaining | FS frame | Frozen when child pushed | Resumed |
| H&W held grid | H&W frame | N/A | Destroyed |
| Multiplier | Frame | Child may override | Parent unchanged |
| Persistent store | Session | Visible to all frames (P3) | Unchanged |

---

### 7.6 `persistentStore` Placeholder (Future P3)

Canonical schema allows:

```json
"session": {
  "persistentStoreSchema": {
    "collectorCount": { "type": "integer", "min": 0, "max": 12, "default": 0 }
  }
}
```

MVP: field **absent** or `"persistentStore": {}` with no schema. Runtime MUST NOT persist across spin chains in MVP.

---

### 7.7 RNG Context

Not stored in canonical JSON. Runtime derives:

```
sessionRng  = Derive(masterSeed, gameVersionId, spinChainIndex)
frameRng    = Derive(sessionRng, frameId, stepIndex)
```

Documented in `determinism.seedDerivationPolicy`.

---

## 8. Validation Rules

Validation is split into three layers with distinct responsibilities.

### 8.1 Layer Overview

| Layer | When | Input | Failure blocks |
|-------|------|-------|----------------|
| **Schema Validation** | Parse / load | JSON vs JSON Schema | Save |
| **Graph Validation** | Post-compile | Canonical object | Save, publish, sim |
| **Runtime Validation** | Pre-step / pre-sim | Snapshot + registry | Simulation start |

---

### 8.2 Schema Validation

Structural JSON Schema checks:

| Rule ID | Description |
|---------|-------------|
| `SV-001` | Required root fields present |
| `SV-002` | Field types match schema |
| `SV-003` | Enum values valid |
| `SV-004` | String patterns (IDs) |
| `SV-005` | Integer min/max (grid size, counts) |
| `SV-006` | No unknown root keys (unless in `extensions`) |
| `SV-007` | `schemaVersion` major supported |
| `SV-008` | `contentHash` format valid if present |

**Does NOT check:** reachability, RTP correctness, plugin semantic rules.

---

### 8.3 Graph Validation

Validation Engine graph analyzer:

| Rule ID | Severity | Description |
|---------|----------|-------------|
| `GV-001` | Error | Exactly one `initialStateId` per machine |
| `GV-002` | Error | `session.rootMachineId` exists |
| `GV-003` | Error | All `targetStateId` references exist in same machine (for `goto`) |
| `GV-004` | Error | All `targetMachineId` references exist (for `spawn`) |
| `GV-005` | Error | No orphan states (unreachable from initial) |
| `GV-006` | Error | All non-terminal states have ≥1 outgoing path or progression to terminal |
| `GV-007` | Error | Terminal states have no `goto` to non-terminal without exit |
| `GV-008` | Error | Every `spawn` has matching `pop` path from child machine |
| `GV-009` | Error | Max stack depth ≥ longest spawn path (see `GV-012`) |
| `GV-010` | Error | `maxStackDepth` ≥ computed worst-case depth |
| `GV-011` | Error | No infinite loops without `progression` metadata |
| `GV-012` | Error | Worst-case spawn depth ≤ `session.maxStackDepth` |
| `GV-013` | Error | Transition `id` unique within state |
| `GV-014` | Error | State `id` unique within machine |
| `GV-015` | Error | Machine `id` unique |
| `GV-016` | Warning | Ambiguous transition priority (same trigger + priority) |
| `GV-017` | Error | `AMBIGUOUS_TRANSITION` without resolving precedence |
| `GV-018` | Error | Plugin ref resolution fails |
| `GV-019` | Error | Plugin config schema validation fails |
| `GV-020` | Error | Capability requirements not met for `stateType` |
| `GV-021` | Error | Symbol references in paytable / reels / triggers exist |
| `GV-022` | Error | Reel set strip count matches `grid.reels` |
| `GV-023` | Error / Warning | Exposure check per `validationMode` (§15) |
| `GV-025` | Error | `rtpCategory` not registered in platform or document registry |
| `GV-026` | Error | Duplicate `rtpCategory` mapping to conflicting decomposition rules |
| `GV-027` | Error | `priority` not in registered tier mapping (§14) |
| `GV-028` | Warning | `priorityTier` absent on transition (hand-authored graph) |
| `GV-024` | Error | Published document modified without version bump |

---

### 8.4 Runtime Validation

Executed immediately before simulation batch:

| Rule ID | Description |
|---------|-------------|
| `RV-001` | `contentHash` matches document bytes |
| `RV-002` | All pinned plugin versions exist in runtime registry |
| `RV-003` | `determinism` fields supported by engine version |
| `RV-004` | `status === "published"` OR sim mode allows draft (dev only) |
| `RV-005` | Validation report exists and `valid === true` (publish/sim) |
| `RV-006` | Golden fixture hash match when running golden mode |

Runtime does **not** re-run full graph analysis if hash + validator version unchanged (configurable cache).

---

### 8.5 Stack Depth Calculation

```
depth(machine) = 1 + max(spawn transition into M': depth(M'))
```

For MVP paths:

| Flow | Worst-case depth |
|------|------------------|
| Base only | 1 |
| Base → FS | 1 (FS in same machine) or 2 if FS separate |
| Base → H&W spawn | 2 |
| Base → FS → H&W | 3 |

MVP `maxStackDepth: 4` provides headroom.

---

## 9. Versioning Strategy

### 9.1 Three Version Dimensions

| Dimension | Field | Scope | Example |
|-----------|-------|-------|---------|
| **Schema version** | `schemaVersion` | Document format | `1.0.0` |
| **Game version** | `gameVersion.versionNumber` | Content iteration | `3` |
| **Plugin version** | `plugins.*.pluginVersion` | Behavior of mechanics | `1.0.0` |

These are **independent**. Changing plugin patch version does not change `schemaVersion`.

---

### 9.2 Schema Semver Policy

| Bump | Meaning | Migration |
|------|---------|-----------|
| **Major** | Breaking field removal / restructure | Explicit migration tool required |
| **Minor** | Additive optional fields | Old documents valid |
| **Patch** | Documentation / constraint clarification | No migration |

**v1.0.0 guarantee:** all future `1.x.x` schemas accept v1.0.0 documents without mutation.

---

### 9.3 Backward Compatibility Rules

1. **Readers MUST ignore unknown fields** outside `extensions` (tolerant reader)  
2. **Writers MUST NOT emit unknown root fields** without namespace  
3. **New state types / effects** added as enum extensions with defaults  
4. **Plugin configs** evolve via `configSchemaVersion`; old configs valid if schema declares defaults  

---

### 9.4 Migration Strategy

| Transition | Strategy |
|------------|----------|
| `schemaVersion` 1.0 → 1.1 | Automated migrator adds default optional fields |
| Plugin `1.0.0` → `1.1.0` | New game version; re-compile; re-validate; re-run golden tests |
| DSL output drift | Re-compile from DSL source; canonical hash change expected |

**Published immutability:**

```
IF gameVersion.status == "published":
  reject UPDATE except status → archived
  reject in-place plugin version change
  reject contentHash mismatch
```

New math → new `gameVersion.id`, increment `versionNumber`, `status: draft` → validate → publish.

---

### 9.5 Snapshot Storage

Stored artifact:

```json
{
  "snapshot": { /* full GameVersion */ },
  "contentHash": "sha256:...",
  "frozenAt": "2026-06-14T12:00:00Z",
  "compilerVersion": "dsl-compiler@1.0.0",
  "validatorVersion": "validation-engine@1.0.0"
}
```

Simulation runs reference `contentHash` + `masterSeed` + engine version.

---

## 10. JSON Schema Deliverables

### 10.A Human-Readable Specification

This document (`CANONICAL_GAME_SCHEMA_V1.md`) is the authoritative human-readable specification for v1.0.0.

Supporting artifacts (to be created at implementation):

| Artifact | Path |
|----------|------|
| Machine-readable JSON Schema | `packages/game-schema/schemas/game-version-1.0.0.schema.json` |
| Plugin config schemas | `packages/game-schema/schemas/plugins/` |
| RTP category registry | `packages/game-schema/registries/rtp-categories-v1.json` |
| Priority tier registry | `packages/game-schema/registries/priority-tiers-v1.json` |
| Validation error registry | `packages/game-schema/registries/validation-errors-v1.json` |
| Golden fixtures framework | [GOLDEN_FIXTURES_V1.md](./GOLDEN_FIXTURES_V1.md) |

---

### 10.B JSON Schema v1.0 Draft Structure

Top-level JSON Schema skeleton (draft 2020-12):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://math-assistant.io/schemas/game-version-1.0.0.schema.json",
  "title": "GameVersion",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schemaVersion",
    "gameVersion",
    "metadata",
    "gameConfig",
    "symbols",
    "reelSets",
    "paytable",
    "winModel",
    "betModel",
    "plugins",
    "stateMachines",
    "session",
    "exposure",
    "determinism",
    "precedence"
  ],
  "properties": {
    "schemaVersion": {
      "type": "string",
      "const": "1.0.0"
    },
    "gameVersion": { "$ref": "#/$defs/GameVersionMeta" },
    "metadata": { "$ref": "#/$defs/Metadata" },
    "gameConfig": { "$ref": "#/$defs/GameConfig" },
    "symbols": {
      "type": "object",
      "additionalProperties": { "$ref": "#/$defs/Symbol" },
      "minProperties": 1
    },
    "reelSets": {
      "type": "object",
      "additionalProperties": { "$ref": "#/$defs/ReelSet" },
      "minProperties": 1
    },
    "paytable": { "$ref": "#/$defs/Paytable" },
    "winModel": { "$ref": "#/$defs/WinModel" },
    "betModel": { "$ref": "#/$defs/BetModel" },
    "plugins": {
      "type": "object",
      "additionalProperties": { "$ref": "#/$defs/PluginRef" },
      "minProperties": 1
    },
    "stateMachines": {
      "type": "object",
      "additionalProperties": { "$ref": "#/$defs/StateMachine" },
      "minProperties": 1
    },
    "session": { "$ref": "#/$defs/SessionConfig" },
    "exposure": { "$ref": "#/$defs/Exposure" },
    "determinism": { "$ref": "#/$defs/Determinism" },
    "precedence": { "$ref": "#/$defs/Precedence" },
    "rtpCategoryRegistry": { "$ref": "#/$defs/RtpCategoryRegistry" },
    "extensions": {
      "type": "object",
      "additionalProperties": true
    },
    "validationMetadata": { "$ref": "#/$defs/ValidationMetadata" },
    "contentHash": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$"
    }
  },
  "$defs": {
    "GameVersionMeta": {
      "type": "object",
      "required": ["id", "projectId", "versionNumber", "status", "createdAt"],
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "projectId": { "type": "string", "format": "uuid" },
        "versionNumber": { "type": "integer", "minimum": 1 },
        "status": { "enum": ["draft", "published", "archived"] },
        "createdAt": { "type": "string", "format": "date-time" },
        "publishedAt": { "type": "string", "format": "date-time" },
        "createdBy": { "type": "string" },
        "label": { "type": "string" },
        "source": { "enum": ["canonical", "dsl-compiler", "import"] }
      },
      "additionalProperties": false
    },
    "StateMachine": {
      "type": "object",
      "required": ["id", "initialStateId", "states"],
      "properties": {
        "id": { "type": "string", "pattern": "^[a-z][a-z0-9_]{0,63}$" },
        "label": { "type": "string" },
        "initialStateId": { "type": "string" },
        "states": {
          "type": "object",
          "additionalProperties": { "$ref": "#/$defs/State" },
          "minProperties": 1
        }
      },
      "additionalProperties": false
    },
    "State": {
      "type": "object",
      "required": [
        "id", "pluginRefId", "stateType", "terminal",
        "rtpCategory", "pluginConfig", "transitions"
      ],
      "properties": {
        "id": { "type": "string", "pattern": "^[A-Z][A-Z0-9_]{0,63}$" },
        "label": { "type": "string" },
        "pluginRefId": { "type": "string" },
        "stateType": { "enum": ["atomic_spin", "multi_step", "choice", "composite_entry"] },
        "terminal": { "type": "boolean" },
        "rtpCategory": { "type": "string" },
        "pluginConfig": { "type": "object" },
        "transitions": {
          "type": "array",
          "items": { "$ref": "#/$defs/Transition" }
        },
        "progression": { "type": "object" }
      },
      "additionalProperties": false
    },
    "Transition": {
      "type": "object",
      "required": ["id", "trigger", "priority", "effect"],
      "properties": {
        "id": { "type": "string" },
        "label": { "type": "string" },
        "trigger": { "type": "string" },
        "priority": { "type": "integer", "minimum": 0, "maximum": 9999 },
        "priorityTier": {
          "type": "string",
          "enum": [
            "FEATURE_ENTRY_SPAWN",
            "FEATURE_ENTRY_GOTO",
            "FEATURE_RETRIGGER",
            "FEATURE_PROGRESS",
            "FEATURE_EXIT",
            "SPIN_IDLE",
            "CUSTOM"
          ]
        },
        "guard": { "type": ["object", "null"] },
        "effect": { "enum": ["goto", "spawn", "pop", "stay"] },
        "targetStateId": { "type": ["string", "null"] },
        "targetMachineId": { "type": ["string", "null"] },
        "actions": { "type": "array", "items": { "type": "object" } }
      },
      "additionalProperties": false,
      "allOf": [
        {
          "if": { "properties": { "effect": { "const": "goto" } } },
          "then": { "required": ["targetStateId"] }
        },
        {
          "if": { "properties": { "effect": { "const": "spawn" } } },
          "then": { "required": ["targetMachineId"] }
        }
      ]
    },
    "PluginRef": {
      "type": "object",
      "required": ["refId", "pluginId", "pluginVersion", "configSchemaVersion", "capabilities"],
      "properties": {
        "refId": { "type": "string" },
        "pluginId": { "type": "string" },
        "pluginVersion": { "type": "string" },
        "configSchemaVersion": { "type": "string" },
        "capabilities": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    }
  }
}
```

**Note:** Full `$defs` for `Paytable`, `ReelSet`, `Symbol`, `BetModel`, etc. follow the same patterns documented in §3. Complete machine-readable schema file to be generated at implementation without changing v1.0.0 semantics.

---

### 10.C Complete Example: Base → Free Spins → Hold & Win

See [Appendix A](#appendix-a-complete-gameversion-example) for the full document (~350 lines JSON).

Summary of structure:

| Component | Value |
|-----------|-------|
| Machines | `main`, `hold_and_win` |
| Main states | `BASE`, `FREE_SPINS` |
| H&W states | `HAW_RESPINS` |
| Plugins | `base_main`, `fs_main`, `haw_main`, `mult_fs`, `mult_haw` |
| Spawn | `FREE_SPINS` → `hold_and_win` |
| Pop | `HAW_RESPINS` → parent |
| RTP categories | `BASE`, `FREE_SPINS`, `HOLD_AND_WIN` |

---

### 10.D Example Validation Failures

#### Failure 1: Orphan State

```json
{
  "code": "GV-005",
  "severity": "error",
  "path": "/stateMachines/main/states/ORPHAN",
  "message": "State ORPHAN is not reachable from initial state BASE",
  "suggestion": "Remove unused state or add incoming transition"
}
```

**Cause:** State defined but no path from `initialStateId`.

---

#### Failure 2: Invalid Transition Target

```json
{
  "code": "GV-003",
  "severity": "error",
  "path": "/stateMachines/main/states/BASE/transitions/0/targetStateId",
  "message": "Target state FREE_SPIN does not exist (did you mean FREE_SPINS?)",
  "suggestion": "Fix typo in targetStateId"
}
```

---

#### Failure 3: Missing Pop Path for Spawned Machine

```json
{
  "code": "GV-008",
  "severity": "error",
  "path": "/stateMachines/hold_and_win",
  "message": "Machine hold_and_win is spawnable but has no transition with effect pop",
  "suggestion": "Add FEATURE_COMPLETE → pop transition in HAW_RESPINS"
}
```

---

#### Failure 4: Stack Depth Exceeded

```json
{
  "code": "GV-012",
  "severity": "error",
  "path": "/session/maxStackDepth",
  "message": "Worst-case spawn depth 5 exceeds maxStackDepth 4",
  "suggestion": "Increase maxStackDepth or reduce nesting"
}
```

---

#### Failure 5: Exposure Infeasible (Strict Mode)

```json
{
  "code": "GV-023",
  "severity": "error",
  "path": "/exposure",
  "message": "Theoretical max win 1200000 minor units exceeds effective cap 500000 (validationMode: strict)",
  "suggestion": "Raise maxWinMinorUnits / maxWinMultiplier or reduce paytable / jackpot tiers"
}
```

---

#### Failure 6: Schema Validation — Invalid Enum

```json
{
  "code": "SV-003",
  "severity": "error",
  "path": "/gameVersion/status",
  "message": "Value 'live' is not valid enum (draft|published|archived)"
}
```

---

#### Failure 7: Plugin Config Schema Failure

```json
{
  "code": "GV-019",
  "severity": "error",
  "path": "/stateMachines/main/states/FREE_SPINS/pluginConfig",
  "message": "awardsByScatterCount.2 must be >= 3 for core.free-spins@1.0.0",
  "suggestion": "Remove award for 2 scatters or adjust trigger rules"
}
```

---

#### Failure 8: Published Immutability

```json
{
  "code": "GV-024",
  "severity": "error",
  "path": "/contentHash",
  "message": "Published game version contentHash mismatch — mutation detected",
  "suggestion": "Create new draft version instead of modifying published snapshot"
}
```

---

#### Failure 9: Unregistered RTP Category

```json
{
  "code": "GV-025",
  "severity": "error",
  "path": "/stateMachines/main/states/BONUS_WHEEL/rtpCategory",
  "message": "rtpCategory WHEEL_BONUS is not registered in platform:v1 or document registry",
  "suggestion": "Use FREE_SPINS, HOLD_AND_WIN, BASE, or add to rtpCategoryRegistry"
}
```

---

#### Failure 10: Invalid Priority Tier

```json
{
  "code": "GV-027",
  "severity": "error",
  "path": "/stateMachines/main/states/BASE/transitions/0",
  "message": "priority 10 does not match any registered tier (expected FEATURE_ENTRY_SPAWN=100)",
  "suggestion": "Set priorityTier FEATURE_ENTRY_SPAWN and priority 100"
}
```

---

## 11. Future-Proofing

### 11.1 Extension Principles

| Principle | Application |
|-----------|-------------|
| **Open plugin configs** | `pluginConfig` validated per plugin schema; unknown keys allowed on minor schema bumps |
| **Closed root document** | Root uses `additionalProperties: false`; extensions only via `extensions` map |
| **Additive enums** | New `stateType`, `effect`, `winModel.type` values added in minor schema releases |
| **Spawn/pop unchanged** | All future features use same stack model |
| **RTP categories** | Free-form string; math engine aggregates dynamically |

---

### 11.2 Wheel Bonuses (P2)

**Extension approach:**

```json
"plugins": {
  "wheel_main": {
    "pluginId": "core.wheel-bonus",
    "pluginVersion": "1.0.0",
    "capabilities": ["feature.nested", "jackpot.local"]
  }
}
```

New state machine or inline `multi_step` state with `pluginConfig.segments[]`.

Transition: `trigger: "WHEEL_BONUS"`, `effect: "spawn"`, `targetMachineId: "wheel"`.

**MVP compatibility:** MVP runtime ignores unknown plugin IDs in registry only if not referenced — no impact on MVP documents.

---

### 11.3 Pick Bonuses (P2)

```json
{
  "stateType": "choice",
  "pluginRefId": "pick_main",
  "pluginConfig": {
    "pickCount": 3,
    "pool": [ { "weight": 10, "award": { "type": "multiplier", "value": 5 } } ]
  }
}
```

New `stateType: "choice"` added in schema **1.1.0** (minor) with default handling.

---

### 11.4 Persistent Features (P3)

**Session block extension:**

```json
"session": {
  "spinLoopMode": "multi_base_session",
  "persistentStoreSchema": {
    "meterFill": { "type": "integer", "min": 0, "max": 100 }
  }
}
```

Plugins declare `feature.persistent` capability; read/write `session.persistentStore`.

Validation ensures caps prevent unbounded accumulation.

---

### 11.5 Cascading Slots (P2)

**No schema root change.** Extend `core.base-game` config:

```json
"pluginConfig": {
  "reelSetId": "base_game",
  "cascade": {
    "enabled": true,
    "maxChainLength": 20,
    "multiplierLadder": [1, 2, 3, 5]
  }
}
```

`winModel.type` remains `"lines"` for MVP; cascade wins tagged `rtpCategory: "BASE_CASCADE"`.

---

### 11.6 Cluster Pays (P2)

```json
"winModel": {
  "type": "cluster",
  "minClusterSize": 5,
  "adjacency": "orthogonal"
}
```

Requires `core.base-game@1.x` with `win.cluster` capability.

---

### 11.7 Megaways (P3)

```json
"gameConfig": {
  "gridModel": {
    "type": "megaways",
    "reels": 6,
    "rowsMax": 7,
    "reelHeightWeightsRef": "megaways_heights"
  }
}
```

Dynamic ways calculation in plugin; exposure validation uses max ways scenario.

---

### 11.8 Custom Plugins (P3 Enterprise)

**`plugins` entry extension:**

```json
"plugins": {
  "custom_haw": {
    "refId": "custom_haw",
    "pluginId": "studio.acme.mega-hold-win",
    "pluginVersion": "2.0.0",
    "origin": "custom",
    "artifactDigest": "sha256:...",
    "signature": "base64...",
    "configSchemaVersion": "2.0.0",
    "capabilities": ["spin.grid", "state.multistep", "feature.nested"]
  }
}
```

MVP schema: `origin` field **absent** or `"built-in"` only. Validation rejects `origin: "custom"` in MVP mode.

---

### 11.9 Marketplace Plugins (P4)

Additional fields on custom plugin refs:

```json
{
  "marketplaceId": "mp-uuid",
  "publisherId": "publisher-uuid",
  "licenseId": "license-token-ref"
}
```

Stored outside canonical document in platform registry; canonical stores only digest + version pin.

Stored outside canonical document in platform registry; canonical stores only digest + version pin.

---

## 12. Runtime Event Contract

The Runtime Event Contract defines **structured events emitted during execution** for debugging, audit trails, and deterministic replay verification. Events are **not part of the canonical `GameVersion` document** and do not affect `contentHash`.

### 12.1 Purpose

| Use case | Description |
|----------|-------------|
| **Debug** | Step-through feature entry, transitions, win application |
| **Replay verification** | Re-execute with same seed; compare event sequence hash |
| **Golden test diagnostics** | Identify divergence point when metrics differ |
| **AI explainability (P2)** | Ground explanations in factual event traces |

### 12.2 Event Envelope

Every event shares a common envelope:

```json
{
  "eventVersion": "1.0.0",
  "sequence": 1042,
  "eventType": "TRANSITION_TAKEN",
  "timestampUs": 0,
  "correlation": {
    "simulationRunId": "uuid",
    "spinChainIndex": 58123,
    "gameVersionContentHash": "sha256:...",
    "engineVersion": "runtime-core@1.0.0"
  },
  "context": {
    "stackDepth": 2,
    "machineId": "hold_and_win",
    "stateId": "HAW_RESPINS",
    "frameId": "f-2-0"
  },
  "payload": { }
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `eventVersion` | string | Yes | Event schema semver |
| `sequence` | integer | Yes | Monotonic per spin chain; starts at 0 |
| `eventType` | enum | Yes | See §12.3 |
| `timestampUs` | integer | No | Microseconds offset from chain start; 0 if unused |
| `correlation` | object | Yes | Links to sim run and canonical snapshot |
| `context` | object | Yes | Stack frame snapshot at event time |
| `payload` | object | Yes | Type-specific body |

**Determinism rule:** For replay comparison, **`sequence` + `eventType` + canonical payload fields** MUST be identical given identical `(gameVersionContentHash, masterSeed, spinChainIndex, engineVersion)`. `timestampUs` is excluded from replay hash.

### 12.3 Event Types (MVP)

| eventType | When emitted | Payload highlights |
|-----------|--------------|-------------------|
| `SPIN_CHAIN_START` | Start of simulated spin chain | `masterSeed`, `betMinorUnits` |
| `SPIN_CHAIN_END` | Chain complete | `totalWinMinorUnits`, `stepCount` |
| `FRAME_PUSH` | `spawn` effect | `targetMachineId`, `parentFrameId`, `newFrameId` |
| `FRAME_POP` | `pop` effect | `frameId`, `resumedFrameId`, `machineId` |
| `STATE_ENTER` | State becomes active | `stateId`, `pluginRefId`, `rtpCategory` |
| `GRID_RESULT` | After reel stop | `reelSetId`, `symbols[][]`, `rngDrawIds[]` |
| `WIN_EVALUATED` | Wins computed | `lines[]`, `winMinorUnits`, `rtpCategory` |
| `TRIGGER_EMITTED` | Plugin emits token(s) | `tokens[]` |
| `TRANSITION_TAKEN` | Transition selected | `transitionId`, `trigger`, `effect`, `priority`, `priorityTier` |
| `MULTIPLIER_APPLIED` | Multiplier plugin runs | `multiplierRefId`, `factor`, `winMinorUnitsBefore`, `winMinorUnitsAfter` |
| `EXPOSURE_CAP_APPLIED` | Win truncated | `capMinorUnits`, `uncappedWinMinorUnits` |
| `FEATURE_COUNTER_UPDATE` | FS/H&W counter change | `field`, `before`, `after` |
| `RUNTIME_LIMIT_HIT` | Safety limit triggered | `limitCode`, `action` — see §18 |

**Debug-only events (Simulation Profile enables):**

| eventType | Notes |
|-----------|-------|
| `RNG_DRAW` | Records draw index + stream id; verbose; off in production sims |
| `GUARD_EVALUATED` | Guard expression result |

### 12.4 Payload Examples

**`TRANSITION_TAKEN`:**

```json
{
  "transitionId": "t_fs_to_haw_spawn",
  "trigger": "HOLD_AND_WIN",
  "effect": "spawn",
  "targetMachineId": "hold_and_win",
  "priority": 100,
  "priorityTier": "FEATURE_ENTRY_SPAWN",
  "candidatesRejected": ["t_fs_complete"]
}
```

**`WIN_EVALUATED`:**

```json
{
  "rtpCategory": "FREE_SPINS",
  "components": [
    { "source": "lines", "symbolId": "H1", "count": 4, "winMinorUnits": 5000 }
  ],
  "totalWinMinorUnits": 5000
}
```

### 12.5 Event Log Modes

Controlled by **Simulation Profile** (§17), not canonical schema:

| Mode | Events emitted |
|------|----------------|
| `none` | No event log (metrics only) |
| `transitions_only` | `FRAME_*`, `STATE_ENTER`, `TRANSITION_TAKEN`, chain start/end |
| `full` | All MVP event types |
| `replay` | All MVP + `RNG_DRAW` |

### 12.6 Replay Contract

**Full deterministic replay** (verify bit-identical metrics):

```
Input:
  gameVersionContentHash
  masterSeed
  spinChainIndex
  engineVersion
  simulationProfile.profileVersion

Process:
  Re-execute spin chain with event logging disabled
  Compare aggregate accumulators to original run

Optional verification:
  eventLogHash = SHA-256( canonicalJsonLines(event[]) excluding timestampUs )
  Compare to stored hash when profile.eventLog.mode != none
```

**Partial replay** (debug single chain): load event log; seek to `sequence` N; re-execute from checkpoint (P2 runtime feature).

### 12.7 Storage Format

Event logs stored outside canonical document:

```
{simulationRunId}/events.jsonl     — one event per line
{simulationRunId}/events.meta.json — eventVersion, mode, eventCount, eventLogHash
```

---

## 13. RTP Category Registry

RTP categories tag wins for **decomposition** (`RTP_base + RTP_feature + … ≈ RTP_total`). Unregistered or inconsistent categories break reporting and golden tests.

### 13.1 Registry Layers

| Layer | Location | Authority |
|-------|----------|-----------|
| **Platform registry** | Shipped with runtime (`rtp-categories-v1.json`) | Built-in categories for MVP |
| **Document registry** | Optional `rtpCategoryRegistry` on `GameVersion` | Extends platform set for game-specific labels |
| **State binding** | `state.rtpCategory` on each state | Must resolve to registered id |

### 13.2 Optional Canonical Field: `rtpCategoryRegistry`

```json
"rtpCategoryRegistry": {
  "extends": "platform:v1",
  "categories": {
    "BASE_LINES": {
      "label": "Base Game Line Wins",
      "parent": "BASE",
      "decompositionGroup": "base"
    },
    "FREE_SPINS": {
      "label": "Free Spins Feature",
      "parent": null,
      "decompositionGroup": "feature"
    }
  }
}
```

| Field | Type | Purpose |
|-------|------|---------|
| `extends` | string | Platform registry baseline |
| `categories[id].label` | string | Human-readable |
| `categories[id].parent` | string \| null | Optional rollup for reports |
| `categories[id].decompositionGroup` | enum | `base` \| `feature` \| `jackpot` \| `adjustment` |

MVP: field **may be omitted** if all states use platform MVP categories only.

### 13.3 Platform MVP Categories (v1)

| Category ID | decompositionGroup | Used by |
|-------------|-------------------|---------|
| `BASE` | base | `BASE` state default |
| `BASE_LINES` | base | Optional split from BASE |
| `BASE_SCATTER` | base | Scatter pays in base |
| `FREE_SPINS` | feature | Free Spins state |
| `HOLD_AND_WIN` | feature | Hold & Win state |
| `MULTIPLIER_ADJUSTMENT` | adjustment | Cross-cutting multiplier wins (if split) |

Plugins tag wins with state's `rtpCategory` unless plugin config specifies sub-tag (must still map to registered id).

### 13.4 Validation Strategy

| Check | Code | Severity | Rule |
|-------|------|----------|------|
| State category registered | `GV-025` | Error | Every `state.rtpCategory` ∈ platform ∪ document registry |
| No unknown win tags | post-sim | Warning | Runtime wins with unregistered tag |
| Decomposition closure | `GV-026` | Error | No two categories same group + overlapping win rules |
| Required MVP categories | `GV-029` | Warning | Published games should declare categories matching active features |
| Parent rollup acyclic | `GV-030` | Error | `parent` links must not cycle |

**Mathematical Engine rule:**

```
RTP_total = sum(RTP_c for c in decompositionGroups) ± ε
```

Each win event MUST carry exactly one primary `rtpCategory`. Validation Engine cannot prove RTP equality pre-sim; Mathematical Engine flags mismatch post-sim.

### 13.5 Compiler / DSL Rules

- Feature DSL compiler **MUST** assign `rtpCategory` from platform registry defaults:
  - Base → `BASE`
  - Free Spins → `FREE_SPINS`
  - Hold & Win → `HOLD_AND_WIN`
- Hand-edited canonical JSON must pass `GV-025`
- New categories in `rtpCategoryRegistry` require `decompositionGroup` and validator approval in CI

---

## 14. Transition Priority Conventions

Raw priority integers (`10`, `100`) are **implementation details**. Authors and compilers MUST use **registered priority tiers** to avoid magic numbers and ambiguous ordering.

### 14.1 Priority Tier Registry (v1)

| `priorityTier` | Numeric `priority` | Semantics | Typical triggers |
|----------------|---------------------|-----------|------------------|
| `FEATURE_ENTRY_SPAWN` | 100 | Enter nested machine (spawn) | `HOLD_AND_WIN` |
| `FEATURE_ENTRY_GOTO` | 200 | Enter feature in same machine | `FREE_SPINS` |
| `FEATURE_RETRIGGER` | 300 | Extend current feature | `RETRIGGER` (internal) |
| `FEATURE_PROGRESS` | 400 | Continue multi-step loop | internal step tokens |
| `FEATURE_EXIT` | 900 | Exit feature to parent or base | `FEATURE_COMPLETE` |
| `SPIN_IDLE` | 1000 | Default / stay on base | `SPIN_COMPLETE` |

**Ordering rule:** Lower numeric `priority` value = **higher precedence** (evaluated first).

Tiers are spaced by 100 to allow future insertion (e.g., `850` for `FEATURE_EXIT_FORCED`).

### 14.2 Canonical Transition Fields

```json
{
  "id": "t_fs_to_haw_spawn",
  "trigger": "HOLD_AND_WIN",
  "priorityTier": "FEATURE_ENTRY_SPAWN",
  "priority": 100,
  "effect": "spawn",
  "targetMachineId": "hold_and_win"
}
```

| Rule | Description |
|------|-------------|
| **RC-001** | If `priorityTier` present, `priority` MUST equal registry numeric value |
| **RC-002** | DSL compiler MUST emit both fields |
| **RC-003** | Hand-authored graphs without `priorityTier` → `GV-028` warning |
| **RC-004** | Unknown tier → `GV-027` error |
| **RC-005** | Custom numeric priority only allowed with `priorityTier: "CUSTOM"` and validation review flag (discouraged) |

### 14.3 Recommended Tier Usage by MVP Flow

| Transition | priorityTier | priority |
|------------|--------------|----------|
| Base → spawn H&W | `FEATURE_ENTRY_SPAWN` | 100 |
| Base → goto FS | `FEATURE_ENTRY_GOTO` | 200 |
| FS → spawn H&W | `FEATURE_ENTRY_SPAWN` | 100 |
| FS → complete → Base | `FEATURE_EXIT` | 900 |
| H&W → pop | `FEATURE_EXIT` | 900 |
| Base spin complete (stay) | `SPIN_IDLE` | 1000 |

### 14.4 Relationship to `precedence.triggerOrder`

Two-layer resolution:

1. **`precedence.triggerOrder`** — filters which **trigger token** wins when multiple tokens emitted  
2. **`priority` / `priorityTier`** — selects which **transition** wins for the chosen token  

Validation must ensure no ambiguous `(state, triggerToken)` pair has equal `(tier, priority)` without distinct `transition.id` tie-break.

### 14.5 Migration from Magic Numbers

Legacy drafts using raw `10` / `100` MUST be normalized at compile time:

```
10  → FEATURE_ENTRY_SPAWN (100)   // remapped — not equal
100 → FEATURE_EXIT (900)          // remapped — not equal
```

Validation rejects unmapped raw values outside tier registry.

---

## 15. Exposure Validation Strategies

Maximum exposure (`exposure.*`) defines win caps. **Validation strictness** is explicit via `exposure.validationMode`.

### 15.1 Canonical Field

```json
"exposure": {
  "maxWinMinorUnits": 1200000,
  "maxWinMultiplier": 5000,
  "capScope": "session_spin_chain",
  "enforceCap": true,
  "validationMode": "strict",
  "manualAttestation": null
}
```

| `validationMode` | Phase | Description |
|------------------|-------|-------------|
| `strict` | MVP default | Analytic max win MUST be ≤ declared cap before publish |
| `simulation_assisted` | P2 | Analytic OR Monte Carlo max-observed with sufficient spins |
| `manual` | Exception path | Human attestation with documented rationale |

### 15.2 Strict Mode (MVP Default)

**Validation Engine checks:**

1. Compute **theoretical max win** from:
   - Max paytable payout × line/w bet model
   - Max multiplier chain from registered multiplier plugins
   - Max jackpot tier values from H&W config (if applicable)
   - Nested path: worst-case stack composition (Base → FS mult → H&W grand)

2. Compare to `min(maxWinMinorUnits, maxWinMultiplier × totalBet)` if both set — **effective cap** is the lower bound

3. Fail `GV-023` if theoretical max **>** effective cap by any amount

4. Fail `GV-031` if cap is unreachable but `enforceCap: true` and paytable implies higher (configuration incoherence)

**No simulation required** for publish in strict mode.

### 15.3 Simulation-Assisted Mode (P2)

Used when analytic bound is conservative or infeasible (future complex mechanics).

```json
"exposure": {
  "validationMode": "simulation_assisted",
  "simulationAssisted": {
    "minSpinCount": 100000000,
    "confidenceLevel": 0.999,
    "maxObservedMustReachPercentOfCap": 95
  }
}
```

**Validation Engine:**

- Runs or references attached simulation report
- Verifies `maxWinObserved >= cap × 0.95` (configurable)
- Verifies no uncapped wins when `enforceCap: true`
- Emits warning if theoretical max unknown

MVP: **`simulation_assisted` rejected at publish** unless platform flag enabled.

### 15.4 Manual Mode (Exception)

```json
"exposure": {
  "validationMode": "manual",
  "manualAttestation": {
    "attestedBy": "user-id",
    "attestedAt": "2026-06-14T12:00:00Z",
    "effectiveCapMinorUnits": 1200000,
    "rationale": "Analytic bound exceeds cap; product caps at 5000× bet by jurisdiction.",
    "reviewTicket": "MATH-1234"
  }
}
```

**Validation Engine:**

- Skips `GV-023` analytic comparison
- Requires all attestation fields
- Emits `GV-032` warning on publish
- Runtime still enforces `enforceCap: true` if set

MVP: **manual mode disallowed** for golden fixtures and CI publish gates.

### 15.5 Runtime Enforcement

Independent of validation mode:

| `enforceCap` | Runtime behavior |
|--------------|------------------|
| `true` | Truncate wins; emit `EXPOSURE_CAP_APPLIED` event |
| `false` | Record overflow in metrics; warn in sim report |

Mathematical Engine reports both **raw** and **capped** RTP when truncation occurs.

---

## 16. Context Inheritance Policies

Nested features require explicit **ownership and mutation rules** when pushing/popping stack frames. Policy id: **`mvp-v1`** (default).

### 16.1 Policy Declaration

```json
"session": {
  "rootMachineId": "main",
  "maxStackDepth": 4,
  "spinLoopMode": "single_chain",
  "contextInheritancePolicy": "mvp-v1"
}
```

Future policies (e.g., `persistent-v1`) add fields without breaking v1.0.0 documents.

### 16.2 Ownership Classes

| Class | Mutable by | Visible to child frames | Survives pop |
|-------|--------------|-------------------------|--------------|
| **Session-scoped** | Runtime session root | Yes (read-only for plugins) | Yes |
| **Frame-scoped** | Active frame plugin only | No (parent frozen) | No |
| **Child-scoped** | Child frame plugin | No upward writes | Destroyed on pop |
| **Inherited-snapshot** | Parent at spawn time | Child read-only copy | N/A |

### 16.3 Session-Scoped Fields (mvp-v1)

| Field | Plugins may read | Plugins may write | Notes |
|-------|------------------|-------------------|-------|
| `totalWinMinorUnits` | Yes | Via runtime win API only | Never direct plugin mutation |
| `totalBetMinorUnits` | Yes | No | Immutable |
| `betContext` | Yes | No | Immutable |
| `masterSeed` / RNG streams | Via API | No | Derived draws only |
| `persistentStore` | No (MVP) | No (MVP) | P3 policy extension |

### 16.4 Frame-Scoped Fields (mvp-v1)

| Field | Feature | On spawn child | On pop child |
|-------|---------|----------------|--------------|
| `spinsRemaining` | Free Spins | **Frozen** — not decremented while child active | **Resume** decrement |
| `respinsRemaining` | Hold & Win | N/A in parent | Destroyed with frame |
| `heldSymbols` | Hold & Win | N/A in parent | Destroyed |
| `activeMultiplier` | Multiplier | Parent unchanged; child resolves own `multiplierRefId` | Parent multiplier unchanged |
| `frameLocalState` | Any | Parent frozen | Parent resumed |

### 16.5 Spawn Matrix (Base → FS → H&W)

| Step | Stack | Active frame | Parent state |
|------|-------|--------------|--------------|
| 1 | `[BASE]` | BASE | — |
| 2 | `[BASE, FREE_SPINS]` | FREE_SPINS | BASE frozen (not executing) |
| 3 | `[BASE, FREE_SPINS, HAW]` | HAW_RESPINS | FS frozen (`spinsRemaining` paused) |
| 4 pop | `[BASE, FREE_SPINS]` | FREE_SPINS | FS resumes; HAW destroyed |
| 5 pop/exit | `[BASE]` | BASE | FS complete or continuing |

**Rules:**

- **SI-001:** Child MUST NOT mutate parent `frameLocalState`  
- **SI-002:** Child wins add to `session.totalWinMinorUnits` with child's `rtpCategory`  
- **SI-003:** Multipliers apply within frame only unless plugin declares `scope: session` (no MVP plugin does)  
- **SI-004:** Bet amount for win calculation always from session root  

### 16.6 Retrigger vs Spawn

| Mechanism | Stack | Context |
|-----------|-------|---------|
| **Retrigger** (FS) | No push | Mutates `spinsRemaining` in current frame |
| **Spawn** (H&W) | Push | New frame; parent frozen |

Validation ensures retriggers do not use `spawn` effect.

### 16.7 Validation Rules

| Code | Rule |
|------|------|
| `GV-033` | Spawn from state requires resolvable return `pop` in child machine |
| `GV-034` | Policy `mvp-v1` disallows `persistentStore` writes if store non-empty schema |
| `GV-035` | Multiplier plugin `scope: session` forbidden in MVP |

---

## 17. Simulation Profile (Non-Canonical)

The **Simulation Profile** configures a Monte Carlo run. It is **NOT part of `GameVersion`**, does **NOT** affect `contentHash`, and is stored alongside simulation run metadata.

### 17.1 Purpose

Separates **what the game is** (canonical) from **how to simulate it** (operational parameters).

### 17.2 SimulationProfile Structure

```json
{
  "profileVersion": "1.0.0",
  "gameVersionContentHash": "sha256:...",
  "spinCount": 1000000,
  "masterSeed": "golden-fixture-4-seed-v1",
  "shardPolicy": {
    "shardCount": 8,
    "minSpinsPerShard": 100000
  },
  "mode": "metrics_only",
  "warmup": {
    "discardSpins": 0
  },
  "eventLog": {
    "mode": "none",
    "includeRngDraws": false,
    "maxEventsPerChain": 10000
  },
  "exposureCheck": {
    "runtimeEnforce": true,
    "recordUncapped": false
  },
  "accumulators": {
    "rtpDecomposition": true,
    "featureFrequencies": true,
    "histograms": false
  },
  "determinism": {
    "engineVersion": "runtime-core@1.0.0",
    "requireExactEngineMatch": true
  },
  "labels": {
    "purpose": "golden-fixture-4",
    "environment": "ci"
  }
}
```

### 17.3 Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profileVersion` | semver | Yes | Simulation profile schema version |
| `gameVersionContentHash` | string | Yes | Pins canonical snapshot |
| `spinCount` | integer | Yes | Total spins across all shards |
| `masterSeed` | string | Yes | Root RNG seed |
| `shardPolicy` | object | No | Parallelism; default auto |
| `mode` | enum | Yes | `metrics_only` \| `debug` \| `golden` |
| `warmup.discardSpins` | integer | No | P2 variance stabilization |
| `eventLog` | object | No | See §12.5 |
| `exposureCheck` | object | No | Runtime cap enforcement overrides |
| `accumulators` | object | No | Which metrics to collect |
| `determinism` | object | Yes | Engine version pinning |
| `labels` | object | No | Arbitrary metadata |

### 17.4 Mode Presets

| mode | spinCount (typical) | eventLog | Use |
|------|---------------------|----------|-----|
| `metrics_only` | 1M+ | `none` | Production sims |
| `debug` | 1K | `full` | Feature debugging |
| `golden` | fixture-defined | `transitions_only` or `none` | CI golden tests |

### 17.5 Relationship to Canonical Schema

| Aspect | Canonical | Simulation Profile |
|--------|-----------|-------------------|
| Affects math definition | Yes | No |
| Hashed for game identity | Yes | No |
| References other | — | References `gameVersionContentHash` |
| Validated by Validation Engine | Yes (graph/schema) | Separate profile validator |
| Stored with SimulationRun | Snapshot copy | Full profile JSON |

### 17.6 Profile Validation

| Rule | Description |
|------|-------------|
| `SP-001` | `gameVersionContentHash` must exist and be published (or draft in dev) |
| `SP-002` | `spinCount` ≥ 1 |
| `SP-003` | `golden` mode must match fixture manifest spin count |
| `SP-004` | `eventLog.maxEventsPerChain` ≤ platform `runtimeLimits.maxEventsPerChain` |
| `SP-005` | `determinism.engineVersion` must match worker or fail |

---

## 18. Runtime Safety Limits

Safety limits prevent runaway execution from misconfigured graphs or plugin bugs. Defaults are **platform-defined**; canonical schema may override via `session.runtimeLimits`.

### 18.1 Canonical Override: `session.runtimeLimits`

```json
"runtimeLimits": {
  "maxStepsPerSpinChain": 500,
  "maxFramesPerChain": 4,
  "maxTransitionsPerStep": 8,
  "maxRespinsPerFeature": 100,
  "maxEventsPerChain": 10000,
  "maxWallClockMsPerChain": 5000
}
```

All fields optional — unset fields use platform defaults below.

### 18.2 Platform Defaults (MVP)

| Limit | Default | Enforced by | On breach |
|-------|---------|-------------|-----------|
| `maxStepsPerSpinChain` | 500 | Runtime loop guard | Fail chain; `RUNTIME_LIMIT_HIT` |
| `maxFramesPerChain` | `session.maxStackDepth` | Stack push | Fail chain |
| `maxTransitionsPerStep` | 8 | Transition resolver | Fail chain |
| `maxRespinsPerFeature` | 100 | H&W plugin + validator | Fail chain |
| `maxEventsPerChain` | 10000 | Event logger | Stop logging; continue metrics |
| `maxWallClockMsPerChain` | 5000 (debug sims) | Worker watchdog | Fail shard (dev only) |

Production `metrics_only` sims: `maxWallClockMsPerChain` disabled (0 = unlimited).

### 18.3 Validation Engine Cross-Checks

| Code | Rule |
|------|------|
| `GV-036` | `runtimeLimits.maxFramesPerChain` ≤ `session.maxStackDepth` |
| `GV-037` | H&W `initialRespins` + grid fill progression cannot exceed `maxRespinsPerFeature` under worst case |
| `GV-012` | Worst-case spawn depth ≤ `maxStackDepth` (existing) |

Graph validation uses **static analysis**; runtime limits catch dynamic edge cases.

### 18.4 Interaction with Simulation Profile

```
effectiveMaxEventsPerChain = min(
  profile.eventLog.maxEventsPerChain,
  game.session.runtimeLimits.maxEventsPerChain,
  platform.default.maxEventsPerChain
)
```

### 18.5 Golden Test Requirements

Golden fixtures MUST execute without hitting any runtime limit. Limit breach fails CI with `RUNTIME_LIMIT_HIT` in event log.

---

## Appendix A: Complete GameVersion Example

**Flow:** Base → Free Spins → Hold & Win  
**Schema:** 1.0.0  
**Status:** Frozen Candidate example (draft status shown for illustration)

```json
{
  "schemaVersion": "1.0.0",
  "gameVersion": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "projectId": "f0e1d2c3-b4a5-9678-9012-3456789abcde",
    "versionNumber": 1,
    "status": "draft",
    "createdAt": "2026-06-14T10:00:00Z",
    "source": "dsl-compiler",
    "label": "Golden Fixture 4 — Nested FS + H&W"
  },
  "metadata": {
    "title": "Example Nested Slot",
    "description": "Reference canonical document for Base → FS → H&W",
    "rtpTarget": { "percent": 96.0, "tolerance": 0.1 }
  },
  "gameConfig": {
    "grid": { "reels": 5, "rows": 3, "indexOrigin": "top-left" },
    "defaultReelSetId": "base_game"
  },
  "symbols": {
    "H1": { "id": "H1", "type": "regular", "displayName": "High 1" },
    "H2": { "id": "H2", "type": "regular", "displayName": "High 2" },
    "L1": { "id": "L1", "type": "regular", "displayName": "Low 1" },
    "L2": { "id": "L2", "type": "regular", "displayName": "Low 2" },
    "WILD": {
      "id": "WILD",
      "type": "wild",
      "substitutes": ["H1", "H2", "L1", "L2"]
    },
    "SCATTER": { "id": "SCATTER", "type": "scatter", "pays": false },
    "BONUS": { "id": "BONUS", "type": "bonus", "pays": false }
  },
  "reelSets": {
    "base_game": {
      "id": "base_game",
      "reels": [
        { "reelIndex": 0, "symbols": ["L1", "H1", "L2", "SCATTER", "L1", "H2", "L2", "BONUS"] },
        { "reelIndex": 1, "symbols": ["L2", "H1", "L1", "WILD", "L2", "H2", "SCATTER", "L1"] },
        { "reelIndex": 2, "symbols": ["L1", "L2", "H2", "L1", "SCATTER", "H1", "L2", "BONUS"] },
        { "reelIndex": 3, "symbols": ["H2", "L1", "L2", "L1", "WILD", "H1", "L2", "SCATTER"] },
        { "reelIndex": 4, "symbols": ["L2", "H1", "L1", "BONUS", "L2", "SCATTER", "H2", "L1"] }
      ]
    },
    "free_spins": {
      "id": "free_spins",
      "reels": [
        { "reelIndex": 0, "symbols": ["L1", "H1", "L2", "SCATTER", "H2", "L1", "BONUS", "L2"] },
        { "reelIndex": 1, "symbols": ["L2", "H1", "SCATTER", "WILD", "L1", "H2", "L2", "BONUS"] },
        { "reelIndex": 2, "symbols": ["L1", "SCATTER", "H2", "L1", "H1", "L2", "BONUS", "L2"] },
        { "reelIndex": 3, "symbols": ["H2", "L1", "SCATTER", "WILD", "L2", "H1", "L1", "BONUS"] },
        { "reelIndex": 4, "symbols": ["L2", "H1", "L1", "SCATTER", "BONUS", "H2", "L2", "L1"] }
      ]
    },
    "hold_and_win": {
      "id": "hold_and_win",
      "reels": [
        { "reelIndex": 0, "symbols": ["BONUS", "L1", "BONUS", "L2", "BONUS"] },
        { "reelIndex": 1, "symbols": ["L2", "BONUS", "L1", "BONUS", "L2"] },
        { "reelIndex": 2, "symbols": ["BONUS", "BONUS", "L1", "L2", "BONUS"] },
        { "reelIndex": 3, "symbols": ["L1", "BONUS", "L2", "BONUS", "BONUS"] },
        { "reelIndex": 4, "symbols": ["BONUS", "L1", "BONUS", "BONUS", "L2"] }
      ]
    }
  },
  "paytable": {
    "lines": [
      { "index": 1, "path": [1, 1, 1, 1, 1] },
      { "index": 2, "path": [0, 0, 0, 0, 0] },
      { "index": 3, "path": [2, 2, 2, 2, 2] }
    ],
    "pays": [
      { "symbolId": "H1", "count": 3, "multiplier": 10 },
      { "symbolId": "H1", "count": 4, "multiplier": 50 },
      { "symbolId": "H1", "count": 5, "multiplier": 200 },
      { "symbolId": "H2", "count": 3, "multiplier": 8 },
      { "symbolId": "H2", "count": 4, "multiplier": 40 },
      { "symbolId": "H2", "count": 5, "multiplier": 150 },
      { "symbolId": "L1", "count": 3, "multiplier": 5 },
      { "symbolId": "L1", "count": 4, "multiplier": 20 },
      { "symbolId": "L1", "count": 5, "multiplier": 80 },
      { "symbolId": "L2", "count": 3, "multiplier": 4 },
      { "symbolId": "L2", "count": 4, "multiplier": 15 },
      { "symbolId": "L2", "count": 5, "multiplier": 60 }
    ]
  },
  "winModel": {
    "type": "lines",
    "direction": "left-to-right",
    "scatterPaysOnReels": true,
    "highestWinOnlyPerLine": true
  },
  "betModel": {
    "type": "lines",
    "lineCount": 20,
    "coinValueScale": 100,
    "defaultCoinValue": 1,
    "minCoinValue": 1,
    "maxCoinValue": 1
  },
  "plugins": {
    "base_main": {
      "refId": "base_main",
      "pluginId": "core.base-game",
      "pluginVersion": "1.0.0",
      "configSchemaVersion": "1.0.0",
      "capabilities": ["spin.grid", "win.lines", "win.scatter"]
    },
    "fs_main": {
      "refId": "fs_main",
      "pluginId": "core.free-spins",
      "pluginVersion": "1.0.0",
      "configSchemaVersion": "1.0.0",
      "capabilities": ["spin.grid", "win.lines", "win.scatter", "feature.retrigger", "feature.nested"]
    },
    "haw_main": {
      "refId": "haw_main",
      "pluginId": "core.hold-and-win",
      "pluginVersion": "1.0.0",
      "configSchemaVersion": "1.0.0",
      "capabilities": ["spin.grid", "state.multistep", "jackpot.local"]
    },
    "mult_fs": {
      "refId": "mult_fs",
      "pluginId": "core.multiplier",
      "pluginVersion": "1.0.0",
      "configSchemaVersion": "1.0.0",
      "capabilities": ["multiplier.apply"]
    },
    "mult_haw": {
      "refId": "mult_haw",
      "pluginId": "core.multiplier",
      "pluginVersion": "1.0.0",
      "configSchemaVersion": "1.0.0",
      "capabilities": ["multiplier.apply"]
    }
  },
  "stateMachines": {
    "main": {
      "id": "main",
      "label": "Main Game",
      "initialStateId": "BASE",
      "states": {
        "BASE": {
          "id": "BASE",
          "label": "Base Game",
          "pluginRefId": "base_main",
          "stateType": "atomic_spin",
          "terminal": false,
          "rtpCategory": "BASE",
          "pluginConfig": {
            "reelSetId": "base_game",
            "scatterTriggers": [
              { "symbolId": "SCATTER", "minCount": 3, "emitTrigger": "FREE_SPINS" }
            ],
            "bonusTriggers": [
              { "symbolId": "BONUS", "minCount": 6, "emitTrigger": "HOLD_AND_WIN" }
            ]
          },
          "transitions": [
            {
              "id": "t_base_to_fs",
              "trigger": "FREE_SPINS",
              "priorityTier": "FEATURE_ENTRY_GOTO",
              "priority": 200,
              "effect": "goto",
              "targetStateId": "FREE_SPINS"
            },
            {
              "id": "t_base_to_haw_spawn",
              "trigger": "HOLD_AND_WIN",
              "priorityTier": "FEATURE_ENTRY_SPAWN",
              "priority": 100,
              "effect": "spawn",
              "targetMachineId": "hold_and_win"
            },
            {
              "id": "t_base_spin_complete",
              "trigger": "SPIN_COMPLETE",
              "priorityTier": "SPIN_IDLE",
              "priority": 1000,
              "effect": "stay",
              "targetStateId": "BASE"
            }
          ]
        },
        "FREE_SPINS": {
          "id": "FREE_SPINS",
          "label": "Free Spins",
          "pluginRefId": "fs_main",
          "stateType": "atomic_spin",
          "terminal": false,
          "rtpCategory": "FREE_SPINS",
          "pluginConfig": {
            "reelSetId": "free_spins",
            "awardsByScatterCount": { "3": 10, "4": 15, "5": 20 },
            "retrigger": {
              "enabled": true,
              "awardsByScatterCount": { "3": 5, "4": 10, "5": 15 }
            },
            "multiplierRefId": "mult_fs",
            "bonusTriggers": [
              { "symbolId": "BONUS", "minCount": 6, "emitTrigger": "HOLD_AND_WIN" }
            ]
          },
          "transitions": [
            {
              "id": "t_fs_to_haw_spawn",
              "trigger": "HOLD_AND_WIN",
              "priorityTier": "FEATURE_ENTRY_SPAWN",
              "priority": 100,
              "effect": "spawn",
              "targetMachineId": "hold_and_win"
            },
            {
              "id": "t_fs_complete",
              "trigger": "FEATURE_COMPLETE",
              "priorityTier": "FEATURE_EXIT",
              "priority": 900,
              "effect": "goto",
              "targetStateId": "BASE"
            }
          ]
        }
      }
    },
    "hold_and_win": {
      "id": "hold_and_win",
      "label": "Hold and Win",
      "initialStateId": "HAW_RESPINS",
      "states": {
        "HAW_RESPINS": {
          "id": "HAW_RESPINS",
          "label": "Hold & Win Respins",
          "pluginRefId": "haw_main",
          "stateType": "multi_step",
          "terminal": false,
          "rtpCategory": "HOLD_AND_WIN",
          "pluginConfig": {
            "reelSetId": "hold_and_win",
            "triggerSymbolId": "BONUS",
            "triggerSymbolCount": 6,
            "initialRespins": 3,
            "gridCapacity": 15,
            "jackpotTiers": {
              "mini": 20,
              "major": 100,
              "grand": 500
            },
            "multiplierRefId": "mult_haw"
          },
          "progression": {
            "counterField": "respinsRemaining",
            "decrementsOn": "each_step",
            "minValue": 0,
            "terminatesWhen": "respinsRemaining == 0 OR gridFull == true"
          },
          "transitions": [
            {
              "id": "t_haw_complete_pop",
              "trigger": "FEATURE_COMPLETE",
              "priorityTier": "FEATURE_EXIT",
              "priority": 900,
              "effect": "pop"
            }
          ]
        }
      }
    }
  },
  "session": {
    "rootMachineId": "main",
    "maxStackDepth": 4,
    "spinLoopMode": "single_chain",
    "contextInheritancePolicy": "mvp-v1",
    "runtimeLimits": {
      "maxStepsPerSpinChain": 500,
      "maxRespinsPerFeature": 100
    }
  },
  "exposure": {
    "maxWinMinorUnits": 1200000,
    "maxWinMultiplier": 5000,
    "capScope": "session_spin_chain",
    "enforceCap": true,
    "validationMode": "strict"
  },
  "determinism": {
    "rngAlgorithm": "PCG64",
    "rngAlgorithmVersion": "1.0",
    "seedDerivationPolicy": "v1-hash-shard",
    "moneyRepresentation": "fixed_minor_units",
    "moneyScale": 10000
  },
  "precedence": {
    "triggerOrder": ["HOLD_AND_WIN", "FREE_SPINS", "FEATURE_COMPLETE", "SPIN_COMPLETE"]
  },
  "rtpCategoryRegistry": {
    "extends": "platform:v1",
    "categories": {
      "BASE": { "label": "Base Game", "parent": null, "decompositionGroup": "base" },
      "FREE_SPINS": { "label": "Free Spins", "parent": null, "decompositionGroup": "feature" },
      "HOLD_AND_WIN": { "label": "Hold and Win", "parent": null, "decompositionGroup": "feature" }
    }
  },
  "extensions": {}
}
```

---

## Appendix B: Document Control

| Version | Status | Date | Changes |
|---------|--------|------|---------|
| 1.0.0 | Draft | 2026-06-14 | Initial canonical game schema specification |
| 1.0.0 | **Frozen Candidate** | 2026-06-14 | Added §12–§18: event contract, RTP registry, priority tiers, exposure modes, inheritance policies, simulation profile, runtime limits |

### Freeze Criteria (Met)

- [x] MVP flows fully specified with Appendix A example  
- [x] Validation layers complete (schema, graph, runtime)  
- [x] Plugin binding and versioning defined  
- [x] Determinism and money representation referenced  
- [x] Extension points documented without MVP scope creep  
- [x] Operational contracts (events, sim profile, safety limits) defined  

**Next implementation artifacts (non-blocking for freeze):** ~~machine-readable JSON Schema file~~ **Done** — see `packages/game-schema/`. Golden fixture canonical JSON files under `tests/golden/` (see [GOLDEN_FIXTURES_V1.md](./GOLDEN_FIXTURES_V1.md)).

---

## Appendix C: Cross-Reference Index

| Topic | Section |
|-------|---------|
| State machine stack | §4, [ADR-004](./adr/ADR-004-state-machine-execution-model.md) |
| DSL → canonical | [TECHNICAL_SPEC §F-DSL](./TECHNICAL_SPECIFICATION.md#f-dsl-feature-dsl-layer-design) |
| Validation Engine | [TECHNICAL_SPEC §D-V](./TECHNICAL_SPECIFICATION.md#dv-validation-engine-design) |
| Golden fixtures | [TECHNICAL_SPEC §I-G](./TECHNICAL_SPECIFICATION.md#ig-golden-mathematical-test-framework) |
| Money / RNG ADRs | [ADR-002](./adr/ADR-002-rng-algorithm-and-stream-splitting.md), [ADR-003](./adr/ADR-003-money-representation-strategy.md) |
| Runtime events & replay | §12 |
| RTP decomposition | §13 |
| Transition priorities | §14 |
| Exposure validation | §15 |
| Context inheritance | §16 |
| Simulation runs | §17 |
| Safety limits | §18 |

---

*This document is the **Frozen Candidate** authoritative definition of Canonical Game Schema v1.0.0. Implementation artifacts (JSON Schema files, registries, migrators, validators) MUST conform to this specification without altering semantics.*
