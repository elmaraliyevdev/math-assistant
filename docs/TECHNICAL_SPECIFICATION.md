# AI Game Mathematics Assistant — Technical Specification

**Version:** 1.1  
**Status:** Architecture & Design (Pre-Implementation)  
**Audience:** Engineering, Game Mathematics, Product, Architecture  
**Last Updated:** 2026-06-14

---

## Table of Contents

1. [Product Vision (A)](#a-product-vision)
2. [Functional Requirements (B)](#b-functional-requirements)
3. [Non-Functional Requirements (C)](#c-non-functional-requirements)
4. [High-Level System Architecture (D)](#d-high-level-system-architecture)
5. [Validation Engine Design (D-V)](#dv-validation-engine-design)
6. [Domain-Driven Design Analysis (E)](#e-domain-driven-design-ddd-analysis)
7. [State Machine Architecture (F)](#f-state-machine-architecture)
8. [Feature DSL Layer Design (F-DSL)](#f-dsl-feature-dsl-layer-design)
9. [Feature Plugin System Design (G)](#g-feature-plugin-system-design)
10. [Simulation Engine Design (H)](#h-simulation-engine-design)
11. [Mathematical Engine Design (I)](#i-mathematical-engine-design)
12. [Golden Mathematical Test Framework (I-G)](#ig-golden-mathematical-test-framework)
13. [AI Assistant Architecture (J)](#j-ai-assistant-architecture)
14. [Database Design (K)](#k-database-design)
15. [Recommended Technology Stack (L)](#l-recommended-technology-stack)
16. [Project Folder Structure (M)](#m-suggested-project-folder-structure)
17. [Risks and Challenges (N)](#n-risks-and-challenges-specific-to-igaming-mathematical-systems)
18. [MVP vs Future Scope (O)](#o-mvp-scope-versus-future-enterprise-scope)

---

## A. Product Vision

### A.1 Mission

**AI Game Mathematics Assistant** is a B2B SaaS platform for slot game studios, mathematicians, and compliance teams to **design, simulate, analyze, optimize, and validate** casino game mathematics during development.

This is **not** a casino operator, game aggregator, or real-money gaming platform. It is an **internal development tool** used before games ship to operators.

### A.2 Problem Statement

Modern slot games combine base games with deeply nested bonus structures (Free Spins → Hold & Win → Wheel Bonus → nested pick games). Studios face:

- Long iteration cycles tuning RTP, volatility, and hit frequency
- Fragile spreadsheets and ad-hoc scripts that do not scale to nested mechanics
- Difficulty explaining RTP deviation from targets to stakeholders
- Lack of reproducible simulation artifacts for certification prep
- Siloed knowledge between mathematicians, engineers, and producers

### A.3 Product Goals

| Goal | Description |
|------|-------------|
| **Model complexity** | Represent arbitrary feature nesting without architectural rewrites |
| **Simulate reliably** | Monte Carlo runs from smoke tests (MVP) to large-scale batches (future) |
| **Quantify mathematics** | RTP, volatility, hit frequency, feature frequency, max exposure (MVP core metrics) |
| **Validate before simulating** | Catch broken graphs and invalid configs at save time via Validation Engine |
| **Explain mathematics** | AI-assisted explainability of RTP, volatility, and version diffs (MVP) |
| **Ensure reproducibility** | Versioned game definitions, golden test baselines, deterministic runs |

### A.4 Target Users

| Persona | Primary Needs |
|---------|---------------|
| **Game Mathematician** | Define paytables, features, weights; run simulations; tune targets |
| **Math Engineer** | Extend built-in plugins and DSL compiler; optimize simulation performance |
| **Game Designer / Producer** | Configure features via DSL; understand metrics; compare variants |
| **QA** | Validate simulated math against spreadsheet baselines; run golden tests |

### A.5 Core Value Proposition

A **unified mathematical modeling environment** where game structure is expressed via a **declarative Feature DSL** that compiles to a **stack-based state machine of built-in plugins**, validated by a **first-class Validation Engine**, simulated by a **deterministic engine**, analyzed by a **mathematical metrics layer**, and explained by an **AI assistant** grounded in simulation artifacts—not generic chat.

### A.6 Product Boundaries (Explicit Non-Goals)

- No player wallet, KYC, or real-money transactions
- No game client rendering or operator integration (export only)
- No guarantee of regulatory certification (certification reports are post-MVP)
- No replacement for human mathematician sign-off on shipped math
- No custom plugin uploads, WASM sandboxing, or plugin marketplace in MVP

---

## B. Functional Requirements

Requirements are tagged by phase: **MVP**, **P2** (Phase 2), **P3** (Enterprise), **P4** (Platform).

### B.1 Game Definition System (MVP)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-001 | MVP | Create and version slot game projects with metadata (title, reels, rows, bet model) |
| FR-002 | MVP | Define base game: reel strips, symbol sets, paylines, wild/scatter behavior |
| FR-003 | MVP | Configure features via **Feature DSL** (YAML/JSON); compiler emits state graph |
| FR-004 | MVP | Support feature paths: Base; Base → FS; Base → H&W; Base → FS → H&W |
| FR-005 | MVP | Import/export canonical game definitions (JSON/YAML) |
| FR-006 | P2 | Clone games and branches for A/B math variants |
| FR-007 | P2 | Diff two game versions and highlight mathematical-relevant changes |

### B.2 Validation Engine (MVP)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-008 | MVP | Run validation on **game save**, **before publish**, and **before simulation** |
| FR-009 | MVP | Detect unreachable states |
| FR-010 | MVP | Detect orphan states |
| FR-011 | MVP | Detect invalid transitions (missing targets, broken references) |
| FR-012 | MVP | Detect infinite loops without progression |
| FR-013 | MVP | Detect conflicting transition priorities |
| FR-014 | MVP | Detect impossible maximum exposure configurations |
| FR-015 | MVP | Detect invalid plugin / DSL configurations |
| FR-016 | MVP | Detect missing built-in plugin dependencies |
| FR-017 | MVP | Validate state graph integrity (single initial state, terminal reachability) |
| FR-018 | MVP | Detect circular dependencies exceeding configured stack depth limit |
| FR-019 | P2 | Cross-check analytic vs simulated RTP tolerance (post-sim validation) |

### B.3 Built-in Feature Plugins (MVP — Internal Only)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-020 | MVP | Built-in plugins only: **Base Game**, **Free Spins**, **Hold & Win**, **Multipliers** |
| FR-021 | MVP | Each plugin: triggers, execution logic, outcomes, transitions, RTP contribution hooks |
| FR-022 | MVP | Nested features via child state machines (stack push/pop) |
| FR-023 | MVP | Feature-level config validated by Validation Engine against plugin schema |
| FR-024 | P2 | Additional built-ins: Wheel, Pick, Sticky/Expanding Wilds, Respins |
| FR-025 | P3 | Custom plugin SDK and signed WASM upload (Enterprise) |
| FR-026 | P4 | Plugin marketplace |

### B.4 State Machine Runtime (MVP)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-030 | MVP | Execute spins through hierarchical stack-based state machine |
| FR-031 | MVP | Deterministic execution given seed + game version + engine version |
| FR-032 | MVP | Transition rules evaluated in documented priority order |
| FR-033 | MVP | Conflict resolution via transition priority + game-level precedence table |
| FR-034 | P2 | Structured event log per spin (debug mode) |
| FR-035 | MVP | Multi-step feature semantics (Hold & Win respin chains) |

### B.5 Simulation Engine (MVP)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-040 | MVP | Monte Carlo simulation with configurable spin count |
| FR-041 | MVP | Single-threaded (debug) and parallel sharded modes |
| FR-042 | MVP | Reject simulation start if Validation Engine reports errors |
| FR-043 | MVP | Aggregate results into run-level and feature-level statistics |
| FR-044 | P2 | Real-time progress streaming |
| FR-045 | P2 | Checkpoint and resume long-running jobs |
| FR-046 | P2 | Compare multiple simulation runs side-by-side |
| FR-047 | P3 | Distributed billion-spin cluster; importance sampling |

### B.6 Mathematical Engine (MVP)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-050 | MVP | Overall RTP |
| FR-051 | MVP | Volatility (σ per spin, normalized by bet) |
| FR-052 | MVP | Hit frequency |
| FR-053 | MVP | Feature / bonus frequency |
| FR-054 | MVP | Maximum exposure (theoretical cap + simulated max observed) |
| FR-055 | MVP | RTP decomposition (base + feature components) for nested paths |
| FR-056 | P2 | Win distribution histograms and percentiles |
| FR-057 | P2 | Feature-specific stat descriptors |
| FR-058 | P3 | Certification-oriented PDF reports |

### B.7 AI Assistant — Explainability (MVP)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-060 | MVP | Explain RTP calculations from simulation results |
| FR-061 | MVP | Explain volatility |
| FR-062 | MVP | Explain simulation outcomes (metrics, feature rates) |
| FR-063 | MVP | Explain differences between game versions |
| FR-064 | MVP | Identify possible reasons for RTP deviation from target |
| FR-065 | P2 | Compare simulation results across runs with narrative summary |
| FR-066 | P2 | Suggest RTP adjustments (MathPatch proposals) |
| FR-067 | P2 | Detect mathematical inconsistencies in concert with Validation Engine |
| FR-068 | P3 | Automatic RTP / volatility optimization loops |
| FR-069 | P3 | Automatic feature generation and game design |
| FR-070 | P3 | Autonomous simulation loops (agent-driven tuning) |

### B.8 Collaboration & Governance (Post-MVP)

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-080 | P2 | Multi-tenant organizations with RBAC |
| FR-081 | P2 | Project-level permissions |
| FR-082 | P3 | Approval workflow for published game math versions |
| FR-083 | P3 | Activity audit log |
| FR-084 | P2 | SSO / SAML |
| FR-085 | P2 | Billing and usage quotas |

### B.9 Integration & Export

| ID | Phase | Requirement |
|----|-------|-------------|
| FR-090 | MVP | REST API for game CRUD, validation, simulation, results |
| FR-091 | P2 | Webhook notifications on simulation completion |
| FR-092 | P2 | Export machine-readable math packages |
| FR-093 | P2 | CI/CD golden test gate |
| FR-094 | P2 | GraphQL API |
| FR-095 | P3 | Visual state graph editor |

---

## C. Non-Functional Requirements

### C.1 Performance

| ID | Requirement | Target (MVP) | Target (Enterprise) |
|----|-------------|--------------|---------------------|
| NFR-001 | Single-spin execution (base game, 5×3) | < 1 ms | < 0.1 ms (native worker) |
| NFR-002 | 1M spin simulation (MVP game set) | < 120 s (8 cores) | < 10 s (distributed) |
| NFR-003 | 100M spin batch | P3 | < 30 min cluster |
| NFR-004 | UI dashboard update latency | < 2 s | < 500 ms streaming |
| NFR-005 | Game definition load | < 500 ms | < 100 ms cached |

### C.2 Scalability

- MVP: single-machine parallel sharding sufficient
- P3+: horizontally scale simulation workers independently of API tier
- P3+: support 100+ concurrent simulation jobs per tenant (enterprise)

### C.3 Reliability & Availability

- MVP: simulation jobs fail fast with clear validation errors
- P2+: checkpoint resume for long jobs
- P3: API availability target 99.9% (enterprise SLA)
- P2+: idempotent job submission via client-supplied idempotency keys

### C.4 Security

- Encryption at rest/in transit for production deployments
- MVP: single-tenant or simplified auth acceptable for internal studio pilot
- No storage of operator or player PII (development tool scope)
- P3: signed custom plugin packages (Enterprise — not MVP)

### C.5 Reproducibility

- Every simulation run records: game version hash, engine version, RNG algorithm, seed strategy, worker count
- Identical inputs MUST produce identical aggregate metrics (within floating-point policy)
- Event-level logs optional for debug runs (storage-intensive)

### C.6 Maintainability & Extensibility

- New **built-in** feature types added without modifying core state machine engine
- Feature DSL schema versioned with forward-compatible migrations
- Plugin API semver with deprecation policy (relevant from P3 custom plugins)
- Golden test suite gates all engine changes (MVP)

### C.7 Observability

- Structured logging, distributed tracing across API → queue → worker
- Metrics: spins/sec, queue depth, job failure rate, p99 spin latency
- Simulation cost attribution per org/project

### C.8 Compliance & Audit

- MVP: immutable game version snapshots; reproducible simulation metadata
- P3: exportable audit trail; certification report templates
- Disclaimer: tool assists development; does not replace lab certification

---

## D. High-Level System Architecture

### D.1 Architectural Style

**Modular monolith (MVP)** evolving to **services + worker fleet (Enterprise)** with clear bounded contexts and async boundaries at simulation workloads.

### D.2 System Context Diagram (MVP)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GAME STUDIO USERS                                    │
│              (Mathematicians, Engineers, Producers, QA)                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI GAME MATHEMATICS ASSISTANT (MVP)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │   Web App    │  │   API        │  │  AI Assistant│                       │
│  │  (Frontend)  │──│  (Monolith)  │──│  (Explain)   │                       │
│  └──────────────┘  └──────┬───────┘  └──────────────┘                       │
│                           │                                                  │
│         ┌─────────────────┼─────────────────┬─────────────────┐               │
│         ▼                 ▼                 ▼                 ▼               │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │   Game      │   │ Validation  │   │ Simulation  │   │ Mathematical│    │
│  │ Definition  │──▶│   Engine    │──▶│ Orchestrator│──▶│   Engine    │    │
│  │ + Feature   │   │             │   │             │   │             │    │
│  │    DSL      │   └─────────────┘   └──────┬──────┘   └─────────────┘    │
│  └─────────────┘                            │                              │
│                           ┌─────────────────┴─────────────────┐            │
│                           ▼                                   ▼            │
│                    ┌─────────────┐                     ┌─────────────┐       │
│                    │  Runtime    │                     │  Golden Test│       │
│                    │  Core +     │                     │  Framework  │       │
│                    │  Built-in   │                     │  (CI)       │       │
│                    │  Plugins    │                     └─────────────┘       │
│                    └─────────────┘                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  PostgreSQL (+ optional │
                    │  Redis for job queue)   │
                    └─────────────────────────┘
```

**Pipeline order:** Game Definition → **Validation Engine** → Simulation Engine → Mathematical Engine

### D.3 Core Subsystems

| Subsystem | MVP | Responsibility |
|-----------|-----|----------------|
| **Presentation Layer** | Yes | Game/DSL editor, simulation dashboard, AI explainability chat |
| **API (Modular Monolith)** | Yes | REST, game CRUD, orchestration, basic auth |
| **Game Definition + Feature DSL** | Yes | CRUD, DSL compile, canonical schema, versioning |
| **Validation Engine** | Yes | Graph integrity, config validation, exposure checks — **gates save, publish, sim** |
| **Runtime Core** | Yes | Stack-based state machine, built-in plugin host, RNG |
| **Simulation Orchestrator** | Yes | Job lifecycle, sharding, aggregation |
| **Mathematical Engine** | Yes | RTP, volatility, hit/feature frequency, exposure, decomposition |
| **AI Assistant** | Yes | Explainability only (RTP, volatility, diffs, deviation reasons) |
| **Golden Test Framework** | Yes | Spreadsheet-validated reference games; CI gate |
| **Plugin Registry** | Built-in only | Four internal plugins; no custom upload |
| **Auth / Billing / SSO** | No (P2+) | Deferred |
| **Graph Editor** | No (P3) | List/DSL editor in MVP |
| **Plugin Marketplace** | No (P4) | Deferred |

### D.4 Key Architectural Principles

1. **DSL + built-in plugins, not custom code in MVP** — designers configure; platform team maintains plugins.
2. **Validate before simulate** — Validation Engine is a first-class gate on save, publish, and simulation start.
3. **Simulation is embarrassingly parallel** — spins are independent; aggregation is commutative.
4. **Determinism is sacred** — golden tests and reproducible runs underpin mathematician trust.
5. **Separation of execution vs analysis** — runtime produces counters; math engine computes derived metrics.
6. **AI explains, does not optimize in MVP** — no auto-tuning or autonomous design loops until P3.
7. **Golden tests gate engine changes** — every runtime/math change must pass spreadsheet-validated fixtures.

### D.5 Request Flow: Save Game Definition

```
User → API: PUT /games/{id}/versions/{vid} { dsl + paytable + reels }
  → Parse Feature DSL
  → DSL Compiler → canonical GameVersion (state graph)
  → Validation Engine.run(draft):
       - DSL schema validation
       - Graph integrity (reachability, orphans, transitions)
       - Plugin config validation (built-in schemas)
       - Exposure feasibility
       - Stack depth / cycle checks
  → IF errors: return 422 with structured ValidationReport
  → ELSE: persist draft version
```

### D.6 Request Flow: Run Simulation

```
User → API: POST /simulations { gameVersionId, spinCount, seed }
  → Validation Engine.run(version, context=PUBLISH_OR_SIM):
       - Re-validate frozen snapshot (plugins unchanged, hash match)
  → IF errors: reject with ValidationReport
  → Create SimulationRun (status: QUEUED)
  → Dispatch to worker (in-process or worker process)
Worker:
  → Load game snapshot + built-in plugin registry
  → Execute N spins via Runtime Core
  → Local accumulator merge
Aggregator:
  → Mathematical Engine: RTP, volatility, hit rate, feature frequency, exposure
  → Persist SimulationResult
  → AI context updated (for explainability queries)
```

### D.7 Deployment Topology (Enterprise Target — Post-MVP)

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────────────┐
│  CDN + SPA  │────▶│  API (K8s)  │────▶│  PostgreSQL (RDS/Aurora) │
└─────────────┘     └──────┬──────┘     └──────────────────────────┘
                           │
                    ┌──────▼──────┐     ┌──────────────────────────┐
                    │    Redis    │     │  S3-compatible storage   │
                    │ cache/locks │     │  (results, checkpoints)  │
                    └──────┬──────┘     └──────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  RabbitMQ / │
                    │  SQS / NATS │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
     ┌─────────────────┐      ┌─────────────────┐
     │ Simulation      │      │ AI Worker       │
     │ Worker Pool     │      │ (GPU optional)  │
     │ (CPU-optimized) │      └─────────────────┘
     └─────────────────┘
```

---

## D-V. Validation Engine Design

The **Validation Engine** is a first-class subsystem positioned **between Game Definition and Simulation**. Invalid games must never reach a Monte Carlo run.

### D-V.1 Responsibilities

| Category | Checks |
|----------|--------|
| **Graph integrity** | Single initial state; no orphan nodes; all transition targets exist; terminal states reachable |
| **Reachability** | All non-terminal states reachable from initial state |
| **Transition validity** | Valid trigger tokens; no dangling edges; return paths exist for nested entries |
| **Progression** | No infinite loops without decrementing counters (respins, spin counts) |
| **Priority conflicts** | Ambiguous transitions flagged when multiple rules match without precedence |
| **Exposure** | Theoretical max win computable and consistent with paytable × multiplier caps |
| **Plugin / DSL config** | JSON Schema validation against built-in plugin schemas |
| **Dependencies** | All referenced built-in plugins exist at pinned versions |
| **Stack depth** | Worst-case nesting path ≤ `maxStackDepth` (MVP default: 4) |
| **Circular dependencies** | Cycles without explicit loop features rejected |

### D-V.2 Execution Triggers

| Trigger | Scope | Behavior |
|---------|-------|----------|
| **Game save** | Draft version | Full validation; block save on **errors**; allow **warnings** with acknowledgment (optional) |
| **Before publish** | Draft → published | Full validation; block publish on any error |
| **Before simulation** | Frozen snapshot | Re-run validation; block sim on any error |

### D-V.3 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Validation Engine                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ DSL Schema   │  │ Graph        │  │ Plugin Config    │  │
│  │ Validator    │  │ Analyzer     │  │ Validator        │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         └─────────────────┼───────────────────┘            │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │ ValidationReport │                        │
│                  │ errors[]         │                        │
│                  │ warnings[]       │                        │
│                  │ checksPassed[]   │                        │
│                  └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
         ▲                              ▲
         │                              │
   Game Definition              Built-in Plugin
   (post-compile graph)         JSON Schemas
```

### D-V.4 ValidationReport (Value Object)

```
ValidationReport {
  valid: boolean                    // true iff errors.length === 0
  errors: ValidationIssue[]         // block save/publish/sim
  warnings: ValidationIssue[]       // informational
  metadata: { gameVersionHash, engineVersion, timestamp }
}

ValidationIssue {
  code: string                      // e.g. UNREACHABLE_STATE
  severity: 'error' | 'warning'
  path: string                      // JSON pointer into definition
  message: string                   // human-readable
  suggestion?: string
}
```

### D-V.5 Relationship to Mathematical Engine

| Concern | Owner |
|---------|-------|
| Structural validity (graph, config, exposure feasibility) | **Validation Engine** (pre-sim) |
| Numeric consistency (RTP sum mismatch, sim vs analytic) | **Mathematical Engine** (post-sim, P2+) |
| Spreadsheet baseline conformance | **Golden Test Framework** (CI) |

### D-V.6 MVP Validation Codes (Illustrative)

| Code | Severity | Description |
|------|----------|-------------|
| `ORPHAN_STATE` | Error | State not reachable from initial |
| `UNREACHABLE_TERMINAL` | Error | Terminal state unreachable |
| `INVALID_TRANSITION_TARGET` | Error | Target state ID missing |
| `INFINITE_LOOP` | Error | Cycle detected without progression counter |
| `AMBIGUOUS_TRANSITION` | Error / Warning | Conflicting priorities |
| `STACK_DEPTH_EXCEEDED` | Error | Nesting path exceeds limit |
| `EXPOSURE_INFEASIBLE` | Error | Configured cap unreachable given paytable |
| `MISSING_PLUGIN` | Error | Referenced built-in plugin not found |
| `INVALID_DSL` | Error | DSL fails schema compilation |

---

## E. Domain-Driven Design (DDD) Analysis

### E.1 Strategic Design — Bounded Contexts

```
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│  Game Design   │   │  Validation    │   │   Simulation   │
│    Context     │   │    Context     │   │    Context     │
│                │   │                │   │                │
│ Game projects  │   │ ValidationRun  │   │ Sim runs       │
│ Feature DSL    │   │ Reports        │   │ Workers        │
│ State graphs   │   │ Graph rules    │   │ Accumulators   │
└───────┬────────┘   └───────┬────────┘   └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │      Shared Kernel          │
              │  (GameVersionSnapshot,      │
              │   RNG spec, Money types)    │
              └──────────────┬──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   Analytics    │  │  AI Assistant  │  │  Identity &    │
│    Context     │  │    Context     │  │  Access (P2+)  │
└────────────────┘  └────────────────┘  └────────────────┘
                             │
                    ┌────────┴────────┐
                    │ Plugin Registry │
                    │ (built-in MVP)  │
                    │ (custom P3+)    │
                    └─────────────────┘
```

| Bounded Context | Ubiquitous Language Highlights |
|-----------------|--------------------------------|
| **Game Design** | Reel strip, paytable, Feature DSL, state graph node, compile |
| **Validation** | ValidationReport, orphan state, reachability, exposure feasibility |
| **Simulation** | Spin, session, shard, seed, accumulator |
| **Analytics** | RTP, contribution, volatility, hit rate, feature frequency, exposure |
| **AI Assistant** | Explanation, deviation reason, version diff narrative |
| **Identity & Access (P2+)** | Organization, project, role |
| **Plugin Registry** | Built-in plugin, capability token (custom plugins P3+) |

**Context Relationships:**

- Game Design → Validation: **Customer-Supplier** (definition must pass validation)
- Validation → Simulation: **Conformist** (simulation refuses invalid snapshots)
- Game Design → Simulation: **Customer-Supplier** (immutable version snapshots)
- Simulation → Analytics: **Customer-Supplier**
- AI Assistant → Analytics + Game Design: **Conformist** with ACL for LLM I/O

### E.2 Aggregates

#### Game Design Context

| Aggregate | Root Entity | Invariants |
|-----------|-------------|------------|
| **GameProject** | `GameProject` | Unique slug per org; must have ≥1 version |
| **GameVersion** | `GameVersion` | Must pass Validation Engine before publish; immutable once published |
| **FeatureDefinition** | `FeatureDefinition` | Valid DSL compile output; built-in plugin reference |
| **StateGraph** | `StateGraph` | Passes Validation Engine graph analyzer |
| **ValidationRun** | `ValidationReport` | Immutable report tied to version hash + validator version |
| **BuiltInPlugin** | `BuiltInPlugin` | Platform-maintained; MVP: four plugins only |

#### Simulation Context

| Aggregate | Root Entity | Invariants |
|-----------|-------------|------------|
| **SimulationRun** | `SimulationRun` | References frozen game snapshot; spinCount > 0 |
| **SimulationShard** | `SimulationShard` | Shard index unique per run; idempotent completion |
| **Checkpoint** | `Checkpoint` | Monotonic spin offset per shard |

#### Analytics Context

| Aggregate | Root Entity | Invariants |
|-----------|-------------|------------|
| **SimulationResult** | `SimulationResult` | 1:1 with completed run; metrics computed from engine version |
| **Report** | `Report` | Generated from result; template version tracked |

#### Identity Context

| Aggregate | Root Entity | Invariants |
|-----------|-------------|------------|
| **Organization** | `Organization` | P2+: optional quota gates |
| **Membership** | `Membership` | User has one role per org |

### E.3 Entities

| Entity | Context | Identity | Mutable |
|--------|---------|----------|---------|
| `GameProject` | Game Design | `projectId` | Yes (draft) |
| `GameVersion` | Game Design | `versionId` | Draft yes; published no |
| `StateNode` | Game Design | `nodeId` within version | Via draft only |
| `FeatureInstance` | Game Design | `featureInstanceId` | Via draft only |
| `SimulationRun` | Simulation | `runId` | Status transitions |
| `User` | Identity | `userId` | Profile |
| `Organization` | Identity | `orgId` | Settings |
| `PluginPackage` | Plugin (P3+) | `pluginId` + version | New versions only |
| `ValidationReport` | Validation | `reportId` | Immutable |

### E.4 Value Objects

| Value Object | Description |
|--------------|-------------|
| `Money` | Decimal + scale policy; no float for monetary amounts |
| `RtpTarget` | Percentage with tolerance band |
| `PaytableEntry` | Symbol combination → payout multiplier |
| `ReelStrip` | Ordered symbol IDs with weights |
| `GridSpec` | Reels × rows × indexing convention |
| `TriggerCondition` | Predicate AST (symbol count, scatter pay, random test) |
| `TransitionRule` | Target state + priority + guard |
| `RngSpec` | Algorithm (e.g., PCG64), seed derivation rules |
| `SpinOutcome` | Grid result, line wins, scatter wins, feature triggers |
| `WinBreakdown` | Base vs feature contributions |
| `MetricSnapshot` | RTP, SD, hit rates at a point in time |
| `GameVersionHash` | Content-addressed hash of canonical definition |
| `SimulationConfig` | Spin count, bet, seed mode, logging level |
| `ValidationIssue` | Structured error/warning from Validation Engine |
| `FeatureDslDocument` | Source YAML/JSON before compilation |
| `Accumulator` | Commutative partial metrics struct |

**Value Object Rules:**

- All value objects immutable after construction
- Equality by value, not reference
- Validation at construction (parse, don't validate twice)

### E.5 Domain Events

| Event | Producer | Consumers |
|-------|----------|-----------|
| `GameVersionPublished` | Game Design | Simulation, Validation cache |
| `ValidationFailed` | Validation | UI, API (422 responses) |
| `SimulationRunCompleted` | Simulation | Analytics, AI |
| `SimulationRunFailed` | Simulation | Notifications |
| `GoldenTestFailed` | CI | Block merge |

### E.6 Anti-Corruption Layers

- **AI Layer ACL**: Natural language ↔ structured explanation context; read-only on game definitions in MVP
- **Feature DSL ACL**: DSL AST ↔ canonical `GameVersion` state graph
- **Import Adapters ACL (P2+)**: Legacy formats → canonical schema

---

## F. State Machine Architecture

### F.1 Conceptual Model

A slot game session is a **hierarchical state machine**:

- **Session** — outermost container (player session abstraction for simulation)
- **StateMachineInstance** — one per active feature layer (base or bonus)
- **State** — node in the graph (e.g., `BASE`, `FREE_SPINS`, `HOLD_AND_WIN`)
- **Transition** — guarded edge triggered by feature plugin output

Nested features are **child state machines** pushed onto a **execution stack** (not a single flat enum).

```
Session
 └── Stack[0]: BaseGameStateMachine (current: BASE)
       └── spin → trigger FS
 └── Stack[1]: FreeSpinsStateMachine (current: SPINNING)  ← pushed
       └── spin → trigger H&W
 └── Stack[2]: HoldAndWinStateMachine (current: RESPINS)   ← pushed
       └── completed → pop → return to FS
       └── FS exhausted → pop → return to BASE
```

### F.2 State Types

| State Type | Behavior |
|------------|----------|
| **AtomicSpinState** | Single spin resolves grid + wins + triggers (most common) |
| **MultiStepState** | Feature spans multiple steps without leaving state (respins) |
| **ChoiceState** | Player pick simulation (RNG-driven pick for math sim) |
| **TerminalState** | Absorbs execution; pop stack or end session |
| **CompositeEntryState** | Wrapper that initializes child machine on entry |

### F.3 State Node Schema (Conceptual)

Each state node carries:

- `id`, `name`, `pluginId`
- `config` (plugin-specific JSON validated by plugin schema)
- `transitions[]` (ordered by priority)
- `childMachineRef` (optional — for embedded sub-graphs)
- `rtpContributionCategory` (for reporting decomposition)

### F.4 Transition Model

```
Transition {
  targetStateId: string
  priority: number          // lower = evaluated first
  guard: GuardExpression    // optional
  trigger: TriggerToken     // emitted by plugin
  actions: Action[]         // optional side effects (increment counters)
}
```

**Evaluation algorithm (per step):**

1. Active plugin executes current step → produces `FeatureStepResult`
2. Result includes: `win`, `events[]`, `triggerTokens[]`, `requestedTransition`, `childMachineSpawn?`
3. If `childMachineSpawn` present → push new machine, enter its initial state ( **before** sibling transitions)
4. Else evaluate transitions on current state matching `triggerTokens` + guards
5. If transition to terminal → run exit hooks, pop stack if nested
6. If stack empty and terminal → session spin complete

### F.5 Handling Nested Features

**Pattern: Pushdown Automaton (State Machine Stack)**

| Scenario | Stack Behavior |
|----------|----------------|
| Base → Free Spins | Push FS machine; base suspended |
| FS → Hold & Win | Push H&W; FS frozen (resume counter preserved) |
| H&W complete | Pop H&W; resume FS |
| FS complete | Pop FS; return to base |
| Retrigger in FS | Mutate FS context (add spins); no push |

**Context inheritance:**

| Data | Inheritance Policy |
|------|-------------------|
| Bet / ante | Inherited from session root |
| Accumulated session win | Shared mutable session context |
| Feature-local counters (spins remaining) | Isolated per stack frame |
| Persistent collection state (hold symbols) | Frame-local with optional export to parent on complete |
| Multipliers | Plugin-defined: frame-local or session-global |

### F.6 Recursive Bonus Structures

**Unbounded nesting** is supported via:

1. **Graph composition** — any state may reference a sub-graph template
2. **Stack depth limit** — configurable safety cap (default 32) prevents infinite loops
3. **Cycle detection** — validate at design time: no zero-cost transition cycles unless explicit loop feature
4. **Template reuse** — same `HoldAndWin` sub-graph template instanced multiple times with different configs

Example: `Base → FS → Bonus → Mini Bonus → Super Bonus`

```
Stack depth 0: BASE
Stack depth 1: FREE_SPINS (10 spins)
Stack depth 2: BONUS (pick game)
Stack depth 3: MINI_BONUS (nested wheel)
Stack depth 4: SUPER_BONUS (final pick)
```

Each level is a **FeaturePlugin** hosting its own states or delegating to a **SubGraphFeature**.

### F.7 Conflict Resolution

When multiple triggers fire on one step:

1. Plugin declares **exclusive triggers** (only highest priority applies)
2. Global policy: `priority` on transition rules
3. Configurable **feature precedence table** at game level (e.g., Jackpot > FS > H&W)
4. Validation warning if ambiguous without precedence

### F.8 Session Lifecycle (Single Simulated Spin)

```
BEGIN_SPIN
  WHILE stack not empty AND not session_terminal:
    frame = stack.top
    result = frame.plugin.execute(frame.context, rng)
    emit events
    apply wins to session
    handle spawn / transition / pop
END_SPIN → record metrics
```

### F.9 Design-Time Validation

Design-time structural validation is owned by the **Validation Engine** (§D-V), not the runtime. The runtime assumes a pre-validated snapshot.

F.9 rules are implemented as Validation Engine checks:

- Reachability analysis from initial state
- Dead states (no outgoing transitions, non-terminal)
- Infinite loops without progress (respins that never decrement)
- Every `Transition.targetStateId` exists
- Built-in plugin capabilities match state type
- Stack depth and cycle limits

### F.10 Persistent State Features (Future — Phase 3)

Persistent features carry state **across spins or bonus sessions** within a simulated player session. They are **not in MVP** but the context model must accommodate them without architectural rewrites.

**Examples:**

- **Collector systems** (e.g., Big Bass-style fisherman collection)
- **Progress meters** filling toward a feature trigger
- **Level systems** unlocking enhanced bonus modes
- **Meter-based jackpots** accumulating until award

**Context hierarchy:**

```
SessionContext (simulated player session)
  ├── betModel, totalSessionWin, sessionSeed
  ├── persistentStore: Map<PersistentKey, PersistentValue>   ← session-level
  └── executionStack[]
        └── FrameContext
              ├── spinsRemaining, localMultipliers             ← feature-level
              └── frameLocalState                              ← feature-level
```

| State Type | Lifetime | Examples |
|------------|----------|----------|
| **Session-level persistent** | Survives base spins until session ends or reset rule | Collection count, meter fill % |
| **Feature-level** | Created on feature entry; destroyed on pop | FS spins remaining, H&W held symbols |
| **Cross-session persistent** | Out of scope MVP; requires explicit multi-session sim config | Account-wide jackpots (P4) |

**Simulation implications:**

- Monte Carlo must define **session boundary** (N base spins per session, or until quit condition)
- Persistent state introduces **path dependence** — seed and session length affect RTP
- Validation Engine must verify persistent rules cannot create unbounded accumulation without cap
- Golden tests for persistent features require multi-spin session fixtures (Phase 3)

**MVP note:** MVP uses stateless sessions (one base spin chain per simulated spin): persistent store exists in domain model but is unused until Phase 3.

---

## F-DSL. Feature DSL Layer Design

Not all game designers should write plugins. The **Feature DSL** is the primary MVP interface for configuring common mechanics. It compiles into canonical state machine definitions that bind to **built-in plugins**.

### F-DSL.1 Design Goals

- **Accessibility** — mathematicians and designers configure features in YAML/JSON
- **Safety** — DSL schema validated before compilation; output validated by Validation Engine
- **Transparency** — compiler output inspectable (canonical JSON state graph)
- **Extensibility** — new DSL constructs added alongside new built-in plugins (Phase 2+)
- **No custom code in MVP** — DSL replaces plugin authoring for all MVP feature paths

### F-DSL.2 Pipeline

```
FeatureDslDocument (YAML/JSON)
        │
        ▼
┌───────────────────┐
│  DSL Parser       │  ← schema version, syntax errors
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  DSL Compiler     │  ← emits StateGraph + paytable bindings
└─────────┬─────────┘
          ▼
   Canonical GameVersion
          │
          ▼
┌───────────────────┐
│ Validation Engine │
└───────────────────┘
```

### F-DSL.3 MVP DSL Constructs

| Construct | Maps To | MVP |
|-----------|---------|-----|
| `base_game` | `core.base-game` plugin | Yes |
| `free_spins` | `core.free-spins` plugin | Yes |
| `hold_and_win` | `core.hold-and-win` plugin | Yes |
| `multipliers` | `core.multiplier` plugin | Yes |
| `retrigger` | FS config block | Yes |
| `transitions` | State graph edges | Yes (limited templates) |
| `wheel_bonus`, `pick_bonus` | — | P2 |
| `persistent_collector` | — | P3 |

### F-DSL.4 Example: Free Spins with Retrigger

```yaml
schemaVersion: "1.0"

base_game:
  grid: { reels: 5, rows: 3 }
  lines: 20

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

  # Optional: multiplier applied during FS
  multiplier:
    value: 2
    scope: feature   # feature-local for FS frame

  # Nested feature entry from within FS
  hold_and_win:
    trigger:
      bonus_symbols: 6
    respins: 3
```

The compiler emits:

- `BASE` state node → `core.base-game@1.x`
- Transition `FREE_SPINS` on scatter trigger
- `FREE_SPINS` state node with compiled award table
- Nested `HOLD_AND_WIN` child graph with return transition to `FREE_SPINS`

### F-DSL.5 Example: Simple Multiplier on Base Wins

```yaml
multipliers:
  base:
    type: fixed
    value: 1
  free_spins:
    type: fixed
    value: 3
```

### F-DSL.6 Compiler Responsibilities

| Task | Description |
|------|-------------|
| **Normalize** | Expand sugar syntax to canonical plugin config |
| **Bind plugins** | Pin `core.*@semver` for each state |
| **Emit transitions** | Generate priority-ordered edges + precedence table |
| **Emit RTP categories** | Tag states with contribution categories for decomposition |
| **Reject** | Unknown constructs, unsupported nesting beyond MVP depth |

### F-DSL.7 Error Handling

- DSL parse errors → `INVALID_DSL` with line/column
- Semantic errors (e.g., FS inside H&W without template) → `DSL_SEMANTIC_ERROR`
- Post-compile errors delegated to Validation Engine

### F-DSL.8 Relationship to Plugins

The DSL is **not** a replacement for the plugin host. Built-in plugins implement execution logic; the DSL is declarative configuration that **selects and parameterizes** those plugins. Custom plugin SDK (P3) may accept lower-level state graph editing or extended DSL blocks.

---

## G. Feature Plugin System Design

### G.0 MVP Scope: Built-in Plugins Only

**MVP supports only four internally maintained built-in plugins.** Game studios do not upload, register, or author plugins in MVP. All designer-facing configuration flows through the Feature DSL.

| Plugin ID | Purpose | MVP |
|-----------|---------|-----|
| `core.base-game` | Reel spin, line wins, scatter triggers | Yes |
| `core.free-spins` | FS awards, retriggers, nested entry | Yes |
| `core.hold-and-win` | Respins, symbol hold, tier awards | Yes |
| `core.multiplier` | Win multipliers (base / feature scope) | Yes |

Custom plugins, SDK, WASM sandbox, and marketplace → **Phase 2 / Enterprise** (see §O, ADR-005).

### G.1 Design Goals

- **Discoverability** — plugins declare capabilities and config JSON Schema
- **Composability** — plugins spawn children via standard stack API
- **Testability** — contract tests + golden fixtures per built-in plugin
- **Versioning** — platform pins plugin versions; games reference via compiled graph
- **Isolation (P3+)** — sandbox / timeout for custom plugins only

### G.2 Plugin Host Architecture

```
┌─────────────────────────────────────────┐
│            Plugin Host (Core)           │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  Registry   │  │  Lifecycle Mgr   │  │
│  └─────────────┘  └──────────────────┘  │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │ Schema Val. │  │  Lifecycle Mgr   │  │
│  └─────────────┘  └──────────────────┘  │
└───────────────────┬─────────────────────┘
                    │ MVP: static registry
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   BaseGame    FreeSpins   HoldAndWin   Multiplier
   (built-in)  (built-in)  (built-in)   (built-in)
```

### G.3 Base Interfaces (Conceptual — Not Implementation Code)

#### `IFeaturePlugin` (Metadata)

| Method / Property | Purpose |
|-------------------|---------|
| `id`, `version`, `apiVersion` | Identity |
| `displayName`, `description` | UI |
| `configSchema` | JSON Schema for validation |
| `capabilities` | Capability tokens (see G.4) |
| `getRtpEstimator(config)` | Optional analytic RTP contribution estimate |

#### `IFeatureRuntime` (Execution)

| Operation | Input | Output |
|-----------|-------|--------|
| `initialize(context, config)` | Parent context, config | Frame context |
| `onEnter()` | — | Side effects |
| `executeStep(rng, input)` | RNG, step input | `FeatureStepResult` |
| `onExit()` | — | Merge persistent state upward |
| `getTriggerDefinitions()` | — | Declarative triggers for editor |
| `getTransitionContributions()` | — | Edges this plugin may emit |

#### `FeatureStepResult` (Value Object)

```
FeatureStepResult {
  gridOutcome?: GridOutcome
  wins: WinLine[]
  triggerTokens: string[]
  nextStepHint?: 'CONTINUE' | 'WAIT_FOR_TRANSITION'
  spawnChildMachine?: ChildMachineSpec
  consumeSpin: boolean
  metadata: Record<string, unknown>  // feature stats
}
```

#### `IRtpContributionProvider`

| Operation | Purpose |
|-----------|---------|
| `estimate(config, parentContext)` | Closed-form or sampled estimate for design-time |
| `decompose(actualSimResults)` | Map simulation counters → RTP line items |

### G.4 Capability Tokens

Plugins declare capabilities for editor and validator:

| Token | Meaning |
|-------|---------|
| `spin.grid` | Produces reel grid outcomes |
| `spin.nudge` | May nudge reels |
| `win.lines` | Evaluates line wins |
| `win.ways` | Evaluates ways wins |
| `win.scatter` | Scatter pays |
| `feature.nested` | Can spawn child machines |
| `feature.retrigger` | Can extend own counter |
| `feature.persistent` | Survives across spins/sessions (sim config) |
| `multiplier.apply` | Applies multipliers to wins |
| `jackpot.local` | Contributes to local jackpot logic |
| `state.multistep` | Occupies multiple steps in one state |

### G.5 Extension Mechanisms

| Mechanism | Phase | Use Case |
|-----------|-------|----------|
| **Feature DSL** | MVP | Designer configuration → compiled state graph |
| **Built-in plugins** | MVP | Platform-maintained execution logic |
| **Sub-graph templates** | P2 | Compose built-ins without new code |
| **Custom plugin SDK** | P3 | Studio-implemented plugins |
| **WASM sandbox** | P3 (Enterprise) | Signed custom plugins |
| **Plugin marketplace** | P4 | Cross-studio distribution |

### G.6 Registration Mechanisms

**MVP — static registration only:**

Built-in plugins are registered at host startup from an internal manifest index. No dynamic upload.

```text
BuiltInManifest {
  plugins: [
    { id: "core.base-game", version: "1.0.0", ... },
    { id: "core.free-spins", version: "1.0.0", ... },
    { id: "core.hold-and-win", version: "1.0.0", ... },
    { id: "core.multiplier", version: "1.0.0", ... }
  ]
}
```

**Phase 3+ — dynamic registration (Enterprise):**

Custom `PluginManifest` upload with signature verification, API compatibility checks, and contract test suite. See ADR-005.

### G.7 Built-in Plugin Reference (MVP + Roadmap)

| Plugin | Trigger Examples | Transitions | Phase |
|--------|------------------|-------------|-------|
| **BaseGame** | — | → FS, → H&W | MVP |
| **FreeSpins** | 3+ scatters | retrigger; → H&W; → BASE | MVP |
| **HoldAndWin** | 6+ bonus symbols | respin loop → parent | MVP |
| **Multiplier** | config | win adjustment | MVP |
| **StickyWilds** | wild lands | modifies subsequent spins | P2 |
| **ExpandingWilds** | wild on reel | grid mutation | P2 |
| **WheelBonus** | bonus / meter fill | → wheel → award | P2 |
| **PickBonus** | trigger token | → choice state | P2 |
| **Cascade** | any win | tumble loop | P2 (see §O.6) |
| **ClusterPay** | cluster size | grid evaluation | P2 (see §O.6) |
| **Megaways** | dynamic ways | variable reel heights | P3 (see §O.6) |

### G.8 Error Handling

| Failure | Behavior |
|---------|----------|
| Invalid config | Block at Validation Engine (save/publish/sim) |
| RNG misuse | Host wraps RNG; plugins receive scoped stream |
| Uncaught exception in built-in | Fail run; log plugin id; golden test regression |
| Plugin timeout | P3+ custom plugins only |

---

## H. Simulation Engine Design

### H.1 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  Simulation Orchestrator                      │
│  Job scheduler │ Shard planner │ Aggregator │ Status tracker │
└────────────────────────────┬─────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │  Worker   │       │  Worker   │       │  Worker   │
   │           │       │           │       │           │
   │ Runtime   │       │ Runtime   │       │ Runtime   │
   │ Core      │       │ Core      │       │ Core      │
   │           │       │           │       │           │
   │ Local     │       │ Local     │       │ Local     │
   │ Accumulator│      │ Accumulator│      │ Accumulator│
   └───────────┘       └───────────┘       └───────────┘
```

**Components:**

| Component | Role |
|-----------|------|
| **Orchestrator** | Splits work, tracks progress, merges results |
| **Worker** | Stateless process; loads snapshot once per job/shard |
| **Runtime Core** | State machine + plugins (shared library) |
| **Accumulator** | O(1) commutative stats update per spin |
| **Aggregator** | Tree or sequential merge of partial accumulators |

### H.2 Simulation Workflow

```
1. PRE-FLIGHT
   - Validation Engine.run(snapshot, context=SIMULATION)
   - Abort if invalid

2. INIT
   - Load GameVersionSnapshot (immutable)
   - Load built-in plugin registry (static)
   - Derive shard seeds: seed_i = hash(masterSeed, shardIndex)

3. SPIN LOOP (per shard)
   FOR spin in 1..shardSpinCount:
     - Execute session spin via Runtime Core (stack-based FSM)
     - Update local accumulator

4. FINALIZE SHARD
   - Serialize accumulator
   - Merge via aggregator

5. AGGREGATE
   - Mathematical Engine: RTP, volatility, hit rate, feature frequency, exposure
   - Persist SimulationResult

6. POST-PROCESS (MVP)
   - Update AI explainability context
   - (P2: webhooks, streaming progress, checkpoints)
```

### H.3 Accumulator Design (Commutative)

Partial metrics must be **associative** for parallel merge:

| Field | Merge Strategy |
|-------|----------------|
| `totalBet` | Sum |
| `totalWin` | Sum |
| `spinCount` | Sum |
| `winSumSquares` | Sum (for variance) |
| `hitCount` (win > 0) | Sum |
| `featureEntryCounts` | Map merge by key |
| `histogramBuckets` | Bucket-wise sum |
| `maxWinObserved` | Max |
| `featureRtpComponents` | Sum |

Optional **Kahan summation** or **fixed-point** for numerical stability at 1B+ spins.

### H.4 Parallelization Strategy

| Level | Strategy |
|-------|----------|
| **Job level** | Multiple simulation runs across workers |
| **Shard level** | Single run split into N shards by spin ranges |
| **Intra-shard** | Single-threaded (RNG sequential integrity) |

**Shard sizing:**

```
shardCount = min(maxShards, ceil(totalSpins / minSpinsPerShard))
```

Default `minSpinsPerShard` = 100,000 for merge efficiency.

**Seed strategy:**

- `masterSeed` + `shardIndex` → deterministic, independent streams
- Document RNG algorithm and stream splitting (e.g., counter-based RNG)

### H.5 Performance Considerations

| Technique | Benefit |
|-----------|---------|
| Snapshot caching on worker | Avoid repeated deserialization |
| Plugin hot path in native code (Rust/Go) or WASM | 10–100× spin throughput |
| Avoid per-spin heap allocation | Object pools for grids |
| Tiered logging | `METRICS_ONLY` vs `FULL_EVENT_LOG` |
| Approximate histograms | Fixed buckets vs exact win lists |
| JIT paytable lookup | Precomputed win tables for line games |
| Batch aggregation | Merge shards in tree reduction |

**Throughput targets:**

| Game Complexity | Expected spins/sec/core |
|-----------------|-------------------------|
| Simple base game | 50,000 – 200,000 |
| FS + H&W nested | 5,000 – 20,000 |
| Full event logging | 100 – 1,000 |

### H.6 Checkpoint & Resume

Checkpoint payload:

- `shardIndex`, `lastSpinOffset`, `rngState`, `accumulatorSnapshot`
- Optional: stack frames for features with cross-spin persistence (expensive)

Default: **checkpoint without session state** — restart shard from scratch on failure (acceptable if shards are short).

Enterprise: **full session checkpoint** for rare long-running Markov chain features.

### H.7 Simulation Modes

| Mode | Spins | Logging | Use |
|------|-------|---------|-----|
| **Smoke** | 10K | Metrics | Dev iteration |
| **Standard** | 1M – 10M | Metrics + feature stats | Tuning |
| **Certification** | 100M – 1B | Metrics + audit metadata | P3 |
| **Debug** | 1K | Full event log | Feature debugging |

---

## I. Mathematical Engine Design

### I.1 Separation of Concerns

| Layer | Responsibility |
|-------|----------------|
| **Runtime** | Produce raw outcomes and counters |
| **Accumulator** | O(1) spin-level aggregation |
| **Mathematical Engine** | Derived metrics: RTP, volatility, hit/feature frequency, exposure, decomposition |
| **Validation Engine** | Pre-sim structural validation (§D-V) |
| **Golden Test Framework** | Spreadsheet baseline conformance (CI) |

### I.2 RTP Calculations

**Overall RTP:**

```
RTP = (Total Win / Total Bet) × 100%
```

**Component RTP (decomposition):**

```
RTP_total ≈ RTP_base + Σ RTP_feature_i + RTP_jackpot
```

**Methods:**

| Method | When Used |
|--------|-----------|
| **Simulation RTP** | Primary; from aggregated wins/bets |
| **Analytic RTP** | Base game line pays via exhaustive enumeration (small grids) |
| **Plugin estimator** | Design-time quick feedback before long sim |
| **Hybrid** | Analytic base + simulated features |

**Weighted contribution tracking:**

Each win tagged at runtime with `contributionCategory`:

- `BASE_LINES`, `BASE_SCATTER`, `FS`, `HOLD_WIN`, `WHEEL`, etc.

**RTP reconciliation report** flags when sum of components deviates from total beyond ε.

### I.3 Volatility Calculations

**Per-spin win variance:**

```
μ = totalWin / spinCount
σ² = (winSumSquares / spinCount) - μ²
σ = sqrt(σ²)
```

**Volatility index (industry common):**

- Report σ normalized by bet size
- Optional: simulation of bonus-only conditional volatility

**Confidence intervals:**

- For RTP at N spins: use normal approximation or bootstrap on bucketed samples
- Report 95% CI in certification reports

### I.4 Hit Frequency

| Metric | Definition |
|--------|------------|
| **Hit Rate (any win)** | P(win > 0) |
| **Win ≥ X bet** | P(win ≥ X × bet) |
| **Feature Hit Rate** | P(enter feature) per base spin |
| **Retrigger Rate** | P(retrigger \| in feature) |

Tracked via counters in accumulator; conditional rates computed post-sim.

### I.5 Bonus Frequency

- `featureEntryCounts[featureId] / baseSpinCount`
- Average spins per feature entry: inverse of frequency
- Nested feature: report frequency **conditional on parent state**

### I.6 Maximum Exposure

Track during simulation:

- `maxWinObserved` (absolute win amount)
- `maxMultiplierObserved` (win / bet)
- Theoretical cap from game rules (static analysis):

```
exposureCap = maxPaytablePayout × maxMultiplierChain × maxBet
```

**Validation:** simulated max ≤ theoretical cap; alert if cap unreachable but rules claim it is.

### I.7 Win Distribution Analysis (P2)

- Histogram buckets and percentiles deferred to Phase 2
- MVP focuses on core metrics listed in §O.1

### I.8 Feature-Specific Statistics

MVP tracks via built-in counters:

- Average FS awarded (Fixture 2)
- H&W trigger frequency and average bonus win (Fixture 3)
- Nested path decomposition (Fixture 4)

P2: plugins register formal **stat descriptors**.

### I.9 Post-Simulation Consistency Checks (P2)

| Check | Owner | Phase |
|-------|-------|-------|
| RTP sum mismatch (components ≠ total) | Mathematical Engine | MVP (decomposition) |
| Unreachable max win in long sim | Mathematical Engine | P2 warning |
| Zero-hit feature | Mathematical Engine | MVP warning |
| Sim vs analytic delta (base game) | Mathematical Engine | P2 |
| Orphan states, invalid graph | Validation Engine | MVP (pre-sim) |

---

## I-G. Golden Mathematical Test Framework

The platform MUST include **reference games with spreadsheet-validated expected outcomes**. Golden tests are the primary regression gate for Runtime Core, Validation Engine, DSL Compiler, and Mathematical Engine changes.

### I-G.1 Principles

1. **Spreadsheet is source of truth** for expected metrics (within documented tolerance ε)
2. **Deterministic seeds** — golden runs use pinned `masterSeed`, `spinCount`, engine version
3. **CI blocking** — failing golden test blocks merge to main
4. **Every engine change** runs full golden suite

### I-G.2 Tolerance Policy

| Metric | Default ε (MVP) |
|--------|-----------------|
| RTP | ±0.05% absolute |
| Hit frequency | ±0.10% absolute |
| Feature frequency | ±0.05% absolute |
| Average FS awarded | ±0.5 spins |
| Max exposure (observed) | Must match theoretical cap |

Exact tolerances documented per fixture in `tests/golden/manifest.yaml`.

### I-G.3 Golden Fixtures

#### Fixture 1: Simple 5×3 Base Game

**Path:** `tests/golden/fixture-01-base-5x3/`

| Validate | Expected source |
|----------|-----------------|
| RTP | Spreadsheet |
| Hit frequency | Spreadsheet |

**Spin count:** 10M (CI may use 1M with widened ε for PR checks; nightly full run)

---

#### Fixture 2: Base → Free Spins

**Path:** `tests/golden/fixture-02-base-free-spins/`

| Validate | Expected source |
|----------|-----------------|
| RTP | Spreadsheet |
| Bonus (FS) frequency | Spreadsheet |
| Average free spins awarded | Spreadsheet |

---

#### Fixture 3: Base → Hold & Win

**Path:** `tests/golden/fixture-03-base-hold-win/`

| Validate | Expected source |
|----------|-----------------|
| RTP | Spreadsheet |
| Hold & Win frequency | Spreadsheet |
| Average bonus win (H&W) | Spreadsheet |

---

#### Fixture 4: Base → Free Spins → Hold & Win

**Path:** `tests/golden/fixture-04-nested-fs-hold-win/`

| Validate | Expected source |
|----------|-----------------|
| Nested feature behavior | Transition event counts |
| RTP decomposition | Spreadsheet (base / FS / H&W components) |
| Transition correctness | Stack push/pop invariants; return to FS after H&W |

---

### I-G.4 CI Requirements

```yaml
# .github/workflows/golden-tests.yml (conceptual)
on: [push, pull_request]

jobs:
  golden:
    steps:
      - run: validation-engine validate tests/golden/*/game.dsl.yaml
      - run: golden-runner --all --spin-count=1000000  # PR
      - run: golden-runner --all --spin-count=10000000  # nightly / main
    fail-fast: true
```

| Gate | When | Action on failure |
|------|------|-------------------|
| DSL + validation | Every PR | Block merge |
| Golden metrics (1M spins) | Every PR | Block merge |
| Golden metrics (10M spins) | Nightly / main | Alert + block release |
| Determinism check | Every PR | Same seed → identical accumulators |

### I-G.5 Golden Runner Architecture

```
GoldenRunner
  → Load fixture DSL + expected metrics (expected.yaml)
  → Compile DSL → validate
  → Run simulation (pinned seed, spin count)
  → Mathematical Engine → actual metrics
  → Assert |actual - expected| ≤ ε per metric
  → Emit GoldenTestReport
```

### I-G.6 Repository Layout

```
tests/golden/
├── manifest.yaml
├── fixture-01-base-5x3/
│   ├── game.dsl.yaml
│   ├── expected.yaml          # spreadsheet-derived
│   └── README.md              # spreadsheet link / methodology
├── fixture-02-base-free-spins/
├── fixture-03-base-hold-win/
└── fixture-04-nested-fs-hold-win/
```

---

## J. AI Assistant Architecture

### J.1 Design Philosophy (MVP: Explainability Only)

The MVP AI layer is a **domain-aware explainer**, not an optimizer or designer. It:

- Grounds responses in **current game definition + simulation results + version diffs**
- Explains RTP, volatility, feature frequencies, and exposure in **auditable terms**
- Identifies **possible reasons** for RTP deviation from target (hypotheses, not prescriptions)
- Does **not** auto-generate game designs, RTP patches, or autonomous simulation loops in MVP

**MVP capabilities:**

| Capability | Description |
|------------|-------------|
| Explain RTP | How total and component RTP were computed from sim counters |
| Explain volatility | What σ means for this game; drivers of variance |
| Explain simulation outcomes | Hit rate, feature frequency, max win observed |
| Explain version differences | What changed in DSL/paytable and likely metric impact |
| Explain RTP deviation | Hypotheses tied to specific config paths (not auto-fix) |
| Compare simulation results | Narrative comparison of two completed runs |

**Deferred to P2+:** MathPatch suggestions, inconsistency auto-fix, feature design, optimization loops (see §O).

### J.2 Components (MVP)

```
┌─────────────────────────────────────────────────────────────┐
│              AI Assistant (Explainability — MVP)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Chat API     │  │ Context      │  │ Explanation      │  │
│  │              │  │ Builder      │  │ Composer         │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         └─────────────────┼───────────────────┘            │
│                           ▼                                 │
│              ┌────────────────────────┐                     │
│              │ Structured Retrieval    │                     │
│              │ (game JSON, metrics,    │                     │
│              │  validation, diffs)     │                     │
│              └────────────┬───────────┘                     │
└───────────────────────────┼─────────────────────────────────┘
                            ▼
                 ┌────────────────────┐
                 │  LLM Provider      │
                 └────────────────────┘
```

MVP may colocate AI in API monolith (ADR-006). Separate AI service is optional P2 extraction.

### J.3 Responsibilities by Sub-Component

| Component | MVP | Responsibility |
|-----------|-----|----------------|
| **Context Builder** | Yes | Game summary, metrics, version diff, validation warnings |
| **Structured Retrieval** | Yes | Paytable rows, DSL blocks, simulation result fields |
| **Explanation Composer** | Yes | Natural language with citations to config paths |
| **RAG (vector)** | Optional | MVP can use structured JSON context only |
| **Suggestion Engine** | No (P2) | MathPatch generation |
| **Design Agent** | No (P3) | Feature generation |
| **Optimization Agent** | No (P3) | Autonomous sim loops |
| **Guardrails** | Yes | No legal/regulatory guarantees; no auto-mutation |

### J.4 Context Packaging (MVP)

Always included when available:

- Compiled game version summary (grid, bet, feature list from DSL)
- Latest `SimulationResult` metrics (RTP, σ, hit rate, feature frequency, exposure)
- RTP decomposition table (if nested features)
- `ValidationReport` warnings from last save
- Diff vs previous version (paytable + DSL semantic diff)

Not in MVP context:

- Similar historical games RAG corpus
- Certification notes
- MathPatch history

### J.5 Output Constraints (MVP)

- **Read-only** — AI cannot modify game definitions
- Responses cite `path` references (e.g., `free_spins.trigger.scatters.3`)
- Deviation explanations list **hypotheses ranked by likelihood**, not automated changes
- P2 introduces structured **MathPatch** output format

### J.6 Future Expansion

| Capability | Phase |
|------------|-------|
| Compare runs with structured diff tables | MVP (basic narrative) |
| MathPatch RTP / volatility suggestions | P2 |
| Validation + math inconsistency co-pilot | P2 |
| Multi-objective optimization | P3 |
| Automatic feature generation | P3 |
| Autonomous simulation loops | P3 |
| Fine-tuned math LLM | P4 |

### J.7 Evaluation & Safety

- Golden Q&A test set for explainability (expected topics cited, no forbidden auto-edit claims)
- Log prompts/responses (configurable retention)
- P2+: rate limits per org tier when billing exists

---

## K. Database Design

### K.1 Storage Strategy Overview

| Data Type | Store | Rationale |
|-----------|-------|-----------|
| Relational metadata | PostgreSQL | ACID, joins, tenancy |
| Game definition snapshots | PostgreSQL JSONB + S3 | Large blobs offloaded |
| Simulation results (aggregates) | PostgreSQL | Queryable metrics |
| Large histograms / event logs | S3 / object storage | Size, cost |
| Cache / locks | Redis | Job status, rate limits |
| Vector embeddings (AI) | pgvector | P2 optional; MVP uses structured context |

### K.2 Core Entities & Relationships

```
Organization 1──* GameProject          (P2+: multi-tenant)
GameProject 1──* GameVersion
GameVersion 1──0..* ValidationReport
GameVersion 1──1 StateGraph (compiled)
GameVersion 1──* SimulationRun
SimulationRun 1──0..1 SimulationResult

BuiltInPlugin (static catalog — not per-org in MVP)
GameVersion *──* MathPatch             (P2+ AI suggestions)
User, AuditLog                         (P2+)
```

### K.3 Key Tables (Logical Schema)

#### `organizations`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | TEXT | |
| slug | TEXT UNIQUE | |
| plan_tier | ENUM | free, pro, enterprise |
| simulation_quota | JSONB | limits |

#### `game_projects`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| org_id | UUID FK | |
| name | TEXT | |
| slug | TEXT | UNIQUE per org |
| created_at | TIMESTAMPTZ | |

#### `game_versions`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK | |
| version_number | INT | monotonic |
| status | ENUM | draft, published, archived |
| definition_hash | TEXT | content-addressed |
| definition_blob_ref | TEXT | S3 key or inline JSONB |
| rtp_target | DECIMAL | optional |
| created_by | UUID FK | |
| published_at | TIMESTAMPTZ | nullable |

#### `state_nodes`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| version_id | UUID FK | |
| node_key | TEXT | stable id in graph |
| plugin_id | TEXT | |
| plugin_version | TEXT | |
| config | JSONB | |
| is_initial | BOOL | |
| is_terminal | BOOL | |

#### `state_transitions`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| version_id | UUID FK | |
| from_node_id | UUID FK | |
| to_node_id | UUID FK | |
| priority | INT | |
| trigger_token | TEXT | |
| guard | JSONB | nullable |

#### `simulation_runs`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| version_id | UUID FK | snapshot frozen |
| status | ENUM | queued, running, completed, failed |
| config | JSONB | spins, seed, mode |
| master_seed | TEXT | |
| engine_version | TEXT | |
| started_at / completed_at | TIMESTAMPTZ | |

#### `simulation_results`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| run_id | UUID FK UNIQUE | |
| metrics | JSONB | RTP, σ, hits, etc. |
| feature_metrics | JSONB | per-feature |
| histogram_ref | TEXT | S3 optional |
| created_at | TIMESTAMPTZ | |

#### `validation_reports` (MVP)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| version_id | UUID FK | |
| valid | BOOL | |
| report | JSONB | errors, warnings |
| validator_version | TEXT | |
| created_at | TIMESTAMPTZ | |

#### `plugin_packages` (P3+ — custom plugins)

Deferred in MVP. Built-in plugins are code-defined, not stored per tenant.

#### `math_patches` (P2+)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| version_id | UUID FK | |
| patch | JSONB | MathPatch DSL |
| status | ENUM | proposed, accepted, rejected |
| created_by_ai | BOOL | |

#### `audit_log` (P3+)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| org_id | UUID FK | |
| actor_id | UUID FK | |
| action | TEXT | |
| resource_type | TEXT | |
| resource_id | UUID | |
| metadata | JSONB | |
| created_at | TIMESTAMPTZ | |

### K.4 Indexing Strategy

- `(org_id, slug)` on projects
- `(project_id, version_number DESC)` on versions
- `(version_id, status)` on simulation_runs
- `(run_id)` on shards
- GIN index on `definition JSONB` for feature search (optional)

### K.5 Multi-Tenancy

- MVP: single-tenant or lightweight `org_id` column without RLS complexity
- P2+: row-level `org_id` with PostgreSQL RLS policies

---

## L. Recommended Technology Stack

### L.1 Selection Criteria

- Strong typing for complex domain models
- High-performance simulation workers
- Mature ecosystem for SaaS (auth, billing, observability)
- Team familiarity and hiring market

### L.2 Recommended Stack

| Layer | Technology | MVP | Rationale |
|-------|------------|-----|-----------|
| **Frontend** | React + TypeScript | Yes | DSL editor, sim dashboard, AI chat |
| **UI Framework** | Tailwind + shadcn/ui | Yes | SaaS UI velocity |
| **State management** | TanStack Query + Zustand | Yes | Server vs editor state |
| **Backend API** | NestJS or Go monolith | Yes | ADR-006 |
| **Shared domain types** | TypeScript or Protobuf | Yes | API ↔ worker contract |
| **Simulation core** | Rust or Go | Yes | ADR-001; golden test throughput |
| **Feature DSL** | YAML/JSON + compiler pkg | Yes | Designer-facing config |
| **Validation Engine** | Same language as core or TS | Yes | Shared graph analyzer |
| **Simulation worker** | Same binary as core | Yes | Optional separate process |
| **Background jobs** | In-process or BullMQ | Yes | Lightweight queue |
| **Primary database** | PostgreSQL 16+ | Yes | JSONB for definitions + results |
| **Cache** | Redis | Optional | Job progress P2 |
| **Object storage** | Local / S3 | Optional MVP | Large histograms P2+ |
| **AI** | LLM API + structured context | Yes | Explainability only |
| **Auth** | Simple JWT / local | MVP | SSO P2 (Auth0/Clerk) |
| **Billing** | — | No | Stripe P2 |
| **Graph visualizer** | — | No | React Flow P3 |
| **Plugin SDK / WASM** | — | No | P3 Enterprise |
| **Observability** | OpenTelemetry + Sentry | P2 | Basic logging MVP |
| **Infrastructure** | Docker Compose | MVP | K8s P3 |
| **CI/CD** | GitHub Actions | Yes | **Golden tests required** |

### L.3 Alternative Considerations

| Choice | Alternative | Trade-off |
|--------|-------------|-----------|
| Rust workers | C++ | C++ faster hire difficulty |
| NestJS API | Pure Go monolith | Go if team is Go-native throughout |
| Temporal | BullMQ only | Temporal adds durability complexity |
| Dedicated ClickHouse | PostgreSQL only | ClickHouse for billion-spin analytics at enterprise |

### L.4 Shared Runtime Library

Critical: **one simulation core** compiled to:

- Native binary (workers)
- WASM (browser smoke tests — optional)
- Bound to Node (API integration tests)

Avoid duplicating math logic in frontend and backend.

---

## M. Suggested Project Folder Structure

```
math-assistant/
├── docs/
│   ├── TECHNICAL_SPECIFICATION.md
│   ├── CANONICAL_GAME_SCHEMA_V1.md     # Canonical GameVersion schema v1.0.0 (Frozen Candidate)
│   ├── GOLDEN_FIXTURES_V1.md           # Golden test framework v1.0.0
│   └── adr/                            # ADR-001 … ADR-006
├── packages/
│   ├── domain/
│   ├── game-schema/
│   ├── feature-dsl/                    # Parser, compiler, schema
│   ├── validation-engine/              # Graph analyzer, config validator
│   ├── runtime-core/                   # State machine + built-in plugin host
│   ├── math-engine/
│   └── plugins/                        # Built-in only (MVP)
│       ├── base-game/
│       ├── free-spins/
│       ├── hold-and-win/
│       └── multiplier/
├── apps/
│   ├── web/
│   ├── api/                            # Modular monolith (MVP)
│   └── simulation-worker/              # Optional separate entrypoint
├── tests/
│   ├── golden/                         # Spreadsheet-validated fixtures (CI gate)
│   ├── validation/
│   └── integration/
├── examples/
│   └── games/
├── .github/workflows/
│   └── golden-tests.yml
├── package.json
└── README.md
```

**Post-MVP additions (do not build initially):** `plugin-sdk/`, `apps/ai-service/` (split), `apps/aggregator/`, `infra/kubernetes/`

### M.1 Package Dependency Rules

```
web → api (HTTP only)
api → domain, game-schema, feature-dsl, validation-engine, math-engine
simulation-worker → runtime-core, plugins, math-engine, validation-engine, domain
runtime-core → domain, game-schema, plugins (built-in)
feature-dsl → game-schema, validation-engine (post-compile)
validation-engine → game-schema, domain
```

**Forbidden:** web → runtime-core (simulation server-side only)

**MVP forbidden packages:** `plugin-sdk`, custom plugin loaders, WASM runtime

---

## N. Risks and Challenges Specific to iGaming Mathematical Systems

### N.1 Mathematical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Floating-point drift** | RTP off by 0.01%+ at scale | Fixed-point or decimal library; Kahan summation |
| **RTP decomposition mismatch** | False confidence in components | Mandatory reconciliation report |
| **Rare event undersampling** | Miss max win / jackpot behavior | Long runs; importance sampling; explicit max-win hunt mode |
| **Conditional probability errors** | Nested feature RTP wrong | Stack-based context; peer review; golden tests |
| **Non-ergodic features** | Persistent state skews results | Configurable session count; multiple session seeds |

### N.2 Engineering Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Plugin API breaking changes** | Studio plugins break | Strict semver; compatibility matrix; deprecation window |
| **Simulation non-determinism** | Cannot reproduce certification runs | Pin engine version; document RNG; CI determinism tests |
| **Performance cliff on nested games** | 100× slower sims | Profiling; native workers; feature complexity budget |
| **Unbounded nesting / loops** | Worker hang | Depth limits; cycle validation; step timeouts |
| **Schema evolution** | Old games fail to load | Migration pipeline; versioned schema |

### N.3 Product & Organizational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Over-reliance on AI suggestions** | Shipped math errors | MVP: explain-only AI; P2: human approval on patches |
| **Misalignment with real game client** | Sim doesn't match production | Export adapters; client parity test harness |
| **Certification gap** | Studio assumes tool = certified | Clear positioning; export for labs; no false claims |
| **Feature scope creep** | Never ship MVP | Strict MVP boundary (Section O) |

### N.4 Security Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Malicious custom plugins** | RCE on workers | MVP: no custom plugins; P3: WASM + signatures |
| **Cross-tenant data leak** | Critical | RLS; job context isolation; penetration testing |
| **Prompt injection via game configs** | AI misbehavior | Sanitize retrieved content; structured prompts |

### N.5 Industry-Specific Nuances

- **Regulatory variation** by jurisdiction (RTP display, max win caps) — model as configurable constraints, not hardcoded rules
- **Buy feature / ante bet** math — separate bet models in domain
- **Cluster pays, cascading, Megaways** — roadmap only (§O.6); not MVP
- **Social casino vs real-money** — bet model abstraction from day one

---

## O. MVP Scope Versus Future Enterprise Scope

### O.1 MVP Scope — Core Value Proposition

**Goal:** Validate the core loop: **define (DSL) → validate → simulate → measure → explain**.

**Timeline:** ~3–4 months focused delivery.

#### MVP Includes

| Area | Scope |
|------|-------|
| **Game Definition System** | Projects, versions, paytable, reel strips, YAML/JSON Feature DSL |
| **Feature DSL** | Compiles to state graph; built-in plugin binding |
| **Validation Engine** | Full pre-save / pre-publish / pre-sim validation (§D-V) |
| **State Machine Runtime** | Hierarchical stack-based FSM (ADR-004) |
| **Simulation Engine** | Monte Carlo; local parallel sharding; deterministic seeds |
| **Mathematical Engine** | RTP, volatility, hit frequency, feature frequency, max exposure, RTP decomposition |
| **Built-in plugins** | Base Game, Free Spins, Hold & Win, Multipliers — **internal only** |
| **Supported paths** | Base; Base → FS; Base → H&W; Base → FS → H&W |
| **Golden Test Framework** | Four spreadsheet-validated fixtures; CI gate (§I-G) |
| **AI Assistant** | Explainability only: RTP, volatility, outcomes, version diffs, deviation hypotheses |
| **API** | REST for games, validation, simulation, results |
| **UI** | DSL editor (form/text), simulation dashboard, metrics view, AI chat |

#### MVP Explicitly Excludes

| Excluded | Moved To |
|----------|----------|
| Billing | P2 |
| SSO / SAML | P2 |
| Audit workflows | P3 |
| Visual graph editor | P3 |
| Plugin marketplace | P4 |
| Custom plugin uploads | P3 (Enterprise) |
| WASM sandboxing | P3 (Enterprise) |
| Certification PDF reports | P3 |
| AI-generated game designs | P3 |
| AI auto-optimization loops | P3 |
| Autonomous simulation loops | P3 |
| Distributed billion-spin simulations | P3 |
| Win distribution histograms / percentiles | P2 |
| Multi-tenant RBAC | P2 |
| Webhooks / GraphQL | P2 |
| Cascading / cluster / Megaways | P2–P3 (§O.6) |
| Persistent collector / meter features | P3 (§F.10) |

#### MVP Success Criteria

1. Golden Fixtures 1–4 pass at documented tolerances (10M spins nightly)
2. Mathematician models Base → FS → H&W via DSL; RTP within ε of spreadsheet
3. Validation Engine blocks invalid graph before any simulation runs
4. 1M spins on Fixture 1 completes in acceptable time on 8 cores (ADR-001 benchmark)
5. AI correctly explains RTP decomposition and version diff for Fixture 4 scenario

---

### O.2 Phase 2 — Studio Product (6–12 months)

- Multi-tenant RBAC, SSO, billing
- Visual simulation comparison; webhooks; CI RTP gates
- Expanded built-ins + DSL: Wheel, Pick, Sticky/Expanding Wilds, Respins
- AI MathPatch suggestions (human accept/reject)
- Win distribution histograms
- **Grid mechanics foundation:** cascading slots, cluster pays (see O.6)
- Optional AI service split from monolith

---

### O.3 Phase 3 — Enterprise (12–24 months)

- Custom plugin SDK + signed WASM upload
- Distributed simulation (100M+ spins)
- Certification-oriented report templates
- Persistent state features (collectors, meters, levels — §F.10)
- SAML, audit exports, approval workflows
- Bayesian / autonomous optimization agents
- Visual state graph editor
- Megaways mechanic support (§O.6)
- Optional on-prem deployment

---

### O.4 Phase 4 — Platform (24+ months)

- Plugin marketplace
- Industry benchmark datasets (opt-in)
- Fine-tuned math LLM
- Progressive jackpot simulation adapters
- Regulatory constraint packs by jurisdiction
- White-label deployment

---

### O.5 MVP vs Enterprise Summary Matrix

| Capability | MVP | Enterprise |
|------------|-----|------------|
| Feature configuration | Feature DSL | DSL + custom plugins |
| Feature nesting | 4 paths (max depth 3 bonuses) | Validated arbitrary depth |
| Plugins | 4 built-in internal | Built-in + signed WASM |
| Validation Engine | Yes (full) | Yes + analytic cross-checks |
| Max spins per run | 10M practical | 1B+ distributed |
| AI | Explain only | Explain + optimize + design |
| Golden tests | 4 fixtures, CI required | Extended suite + client parity |
| Compliance exports | JSON metrics | Certification PDF packages |
| Billing / SSO | No | Yes |

---

### O.6 Future Roadmap: Advanced Grid Mechanics

These mechanics are **not in MVP** but the architecture (stack FSM + built-in plugins + DSL extension) anticipates them.

| Mechanic | Description | Architectural Notes | Target Phase |
|----------|-------------|---------------------|--------------|
| **Cascading slots** | Winning symbols removed; new symbols fall; chain until no win | Multi-step `AtomicSpinState` or dedicated `CascadeLoop` built-in; DSL `cascade:` block | P2 |
| **Cluster pays** | Wins on adjacent symbol clusters, not lines | Replace/e extend `win.lines` with `win.cluster` capability; grid evaluator plugin | P2 |
| **Megaways** | Variable reel heights; dynamic ways count | `GridSpec` becomes dynamic per spin; ways calculation in base plugin extension | P3 |

**Validation considerations (future):**

- Cascade loops must pass **progression validation** (max chain depth cap)
- Cluster games require exposure analysis over max cluster size × max multiplier
- Megaways requires validation of reel height weight tables and max ways cap

**Golden tests (future):** add Fixture 5+ when each mechanic ships.

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **RTP** | Return to Player — long-run ratio of wins to bets |
| **Volatility** | Dispersion of win outcomes (often σ per spin) |
| **Hit Frequency** | Probability of a winning outcome |
| **Exposure** | Maximum possible win (absolute or as multiplier) |
| **Feature** | Bonus mechanic entered via triggers from base or another feature |
| **State Graph** | Directed graph of game states and transitions |
| **Feature DSL** | Declarative YAML/JSON configuring built-in plugins |
| **Validation Engine** | Pre-sim subsystem enforcing graph and config integrity |
| **Golden Test** | Spreadsheet-validated reference simulation fixture |
| **Built-in Plugin** | Platform-maintained module implementing feature behavior |
| **Plugin** | General term; MVP = built-in only; P3+ = custom allowed |
| **Shard** | Partition of spins within a simulation run |
| **Accumulator** | Commutative partial result structure for parallel merge |

---

## Appendix B: Reference Game Definition (DSL Shape — MVP)

MVP authoring surface is **Feature DSL** (see §F-DSL). Canonical compiled JSON retained for runtime and API.

```yaml
schemaVersion: "1.0"

base_game:
  grid: { reels: 5, rows: 3 }
  lines: 20
  paytable: { }     # symbol pays
  reel_sets: { }    # strip definitions

free_spins:
  trigger:
    scatters: { 3: 10, 4: 15, 5: 20 }
  retrigger:
    enabled: true
    awards: { 3: 5, 4: 10, 5: 15 }
  hold_and_win:
    trigger:
      bonus_symbols: 6
    respins: 3

multipliers:
  free_spins:
    value: 2
    scope: feature
```

Compiled state graph (excerpt):

```json
{
  "schemaVersion": "1.0.0",
  "stateGraph": {
    "initialState": "BASE",
    "states": [
      { "id": "BASE", "plugin": "core.base-game@1.0.0" },
      { "id": "FREE_SPINS", "plugin": "core.free-spins@1.0.0" },
      { "id": "HOLD_AND_WIN", "plugin": "core.hold-and-win@1.0.0" }
    ]
  }
}
```

---

## Appendix C: Architecture Decision Records

ADR templates are maintained in `docs/adr/`:

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](adr/ADR-001-simulation-core-language.md) | Simulation Core Language (Rust vs Go) | Proposed |
| [ADR-002](adr/ADR-002-rng-algorithm-and-stream-splitting.md) | RNG Algorithm and Deterministic Stream Splitting | Proposed |
| [ADR-003](adr/ADR-003-money-representation-strategy.md) | Money Representation (Fixed Point vs Decimal) | Proposed |
| [ADR-004](adr/ADR-004-state-machine-execution-model.md) | State Machine Execution Model (Hierarchical Stack FSM) | Accepted |
| [ADR-005](adr/ADR-005-feature-strategy-dsl-first.md) | Feature Strategy (Built-in Plugins + DSL First) | Accepted |
| [ADR-006](adr/ADR-006-monolith-vs-services-mvp.md) | Monolith vs Service Architecture for MVP | Proposed |

**Next step before implementation:** Resolve ADR-001, ADR-002, ADR-003, and ADR-006 via benchmarks and team review. Implement canonical schema per [CANONICAL_GAME_SCHEMA_V1.md](./CANONICAL_GAME_SCHEMA_V1.md).

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-14 | Architecture | Initial technical specification |
| 1.1 | 2026-06-14 | Architecture | MVP scope reduction; Validation Engine; Feature DSL; golden tests; ADR templates; AI explainability-only MVP |

---

*This document is the authoritative pre-implementation reference for the AI Game Mathematics Assistant platform. Implementation code, API contracts, and plugin SDK details should trace back to sections defined herein.*
