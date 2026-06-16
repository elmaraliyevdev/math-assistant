# AI Game Mathematics Assistant — Engineering Constitution (Cursor Rules)

**Version:** 1.1.0  
**Status:** Mandatory  
**Audience:** Engineering, AI Agents (Cursor), Architecture  
**Last Updated:** 2026-06-14

---

## Purpose

This document is the **Engineering Constitution** for the AI Game Mathematics Assistant project. It defines mandatory rules that govern all implementation work performed by engineers and AI coding agents (including Cursor).

Its purpose is to ensure that every change remains consistent with:

- The approved architecture
- Architecture Decision Records (ADRs)
- Frozen schemas and contracts
- MVP scope boundaries
- Determinism, validation, and golden-test requirements

**All implementation prompts MUST assume these rules are active unless explicitly overridden by the user.**

---

## RFC 2119 Key Words

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

When this document uses **MUST**, the requirement is absolute. When it uses **SHOULD**, deviation requires explicit justification documented as an assumption (see §15).

---

## Table of Contents

1. [Source of Truth](#1-source-of-truth)
2. [MVP Scope Protection](#2-mvp-scope-protection)
3. [Architectural Integrity](#3-architectural-integrity)
4. [Determinism Rules](#4-determinism-rules)
5. [Money Representation](#5-money-representation)
6. [Validation First](#6-validation-first)
7. [Runtime Core Responsibilities](#7-runtime-core-responsibilities)
8. [Mathematical Engine Responsibilities](#8-mathematical-engine-responsibilities)
9. [Plugin Rules](#9-plugin-rules)
10. [Event Rules](#10-event-rules)
11. [Golden Fixture Rules](#11-golden-fixture-rules)
12. [Testing Requirements](#12-testing-requirements)
13. [Incremental Development](#13-incremental-development)
14. [Simplicity Rules](#14-simplicity-rules)
15. [Explicit Assumptions](#15-explicit-assumptions)
16. [Versioning Rules](#16-versioning-rules)
17. [Python Engineering Standards](#17-python-engineering-standards)
18. [Completion Checklist](#18-completion-checklist)

---

## 1. Source of Truth

The following artifacts are authoritative. Implementation **MUST** conform to them.

| Artifact | Location |
|----------|----------|
| Technical Specification | `docs/TECHNICAL_SPECIFICATION.md` |
| Canonical Game Schema | `docs/CANONICAL_GAME_SCHEMA_V1.md` |
| Architecture Decision Records | `docs/adr/` |
| Frozen JSON Schemas | `packages/game-schema/schemas/` |
| Plugin Schemas | `packages/game-schema/schemas/plugins/` |
| Registries | `packages/game-schema/registries/` |
| Golden Fixture Specifications | `docs/GOLDEN_FIXTURES_V1.md`, `tests/golden/` |

### 1.1 Conflict Resolution

If implementation conflicts with any authoritative document:

1. **STOP** implementation immediately.
2. **Request clarification** from the user or architecture owner.
3. **NEVER** make silent architectural decisions.

Agents **MUST NOT** reinterpret, simplify, or override frozen contracts without explicit approval.

### 1.2 Precedence

When documents overlap, precedence **SHOULD** be applied in this order:

1. ADRs (accepted decisions)
2. Canonical Game Schema and machine-readable schemas
3. Technical Specification
4. Golden Fixture specifications
5. Implementation code comments or informal notes

Code **MUST NOT** contradict a higher-precedence artifact.

---

## 2. MVP Scope Protection

Cursor and all implementers **MUST** implement only features defined within the MVP scope of the Technical Specification.

### 2.1 Prohibited Features (MVP)

Cursor **MUST NOT** implement the following unless the user explicitly requests them and scope is formally expanded:

| Category | Prohibited (Non-MVP) |
|----------|----------------------|
| Platform | Billing, SSO, audit workflows |
| Authoring UI | Graph editor |
| Plugins | Plugin marketplace, WASM plugins, custom plugin uploads |
| AI | Optimization loops, autonomous game generation |
| Simulation | Distributed billion-spin simulations |
| General | Any feature outside Technical Specification MVP scope (§O) |

### 2.2 Scope Discipline

When a task appears to require a non-MVP feature:

- **STOP** and surface the scope conflict.
- Propose a minimal MVP-compliant alternative.
- **MUST NOT** implement the non-MVP feature speculatively.

---

## 3. Architectural Integrity

The following artifacts **MUST NOT** be modified without explicit approval:

- Canonical Game Schema v1.0
- ADR decisions (especially Accepted ADRs)
- Validation error codes (`SV-*`, `GV-*`, `RV-*`, `SP-*`)
- Plugin contracts and capability declarations
- Registry formats (`priority-tiers`, `rtp-categories`, etc.)
- Golden Fixture structures and manifest conventions

### 3.1 Breaking Changes

Breaking changes to any frozen artifact **MUST** follow this process:

1. Author a **new ADR** explaining the decision.
2. Introduce a **new schema version** (never mutate a frozen version in place).
3. Provide **migration documentation** for consumers.
4. Obtain **explicit approval** before merge.

Silent refactors of contracts, error codes, or schema semantics **MUST NOT** occur.

### 3.2 Modular Monolith

The MVP architecture is a **modular monolith**. Implementers **MUST** preserve bounded contexts and dependency direction defined in the Technical Specification. Extracting services **MUST NOT** occur without an ADR and explicit request.

---

## 4. Determinism Rules

The system **MUST** be deterministic.

Given identical inputs:

- `GameVersion` (canonical content hash)
- `EngineVersion`
- RNG algorithm and version
- Seed / seed derivation policy
- `SimulationProfile`

Results **MUST** be reproducible bit-for-bit where the specification requires exact reproducibility, and within documented tolerance bands where statistical aggregation applies.

### 4.1 Prohibited Non-Determinism

Implementers **MUST NOT** introduce:

- Unseeded randomness in runtime, simulation, or mathematical aggregation paths
- `time.Now()` or wall-clock time inside runtime execution logic
- Non-deterministic map iteration affecting execution order or emitted events
- Hidden side effects (global mutation, implicit I/O, ambient configuration)

### 4.2 Allowed Exceptions

Wall-clock timestamps **MAY** appear in:

- Validation report metadata
- API audit fields
- Logging and observability (outside execution hot paths)

Such timestamps **MUST NOT** influence game outcomes, RNG streams, or mathematical results.

---

## 5. Money Representation

All money calculations in runtime, validation (where numeric), simulation, and mathematical engines **MUST** use:

- **Fixed-point integers in minor units** (`int` in Python; bounded `int64` where interoperability requires it)
- Explicit scale factors as defined in `GameVersion.determinism` and schema

### 5.1 Prohibited Representations

Money calculations **MUST NOT** use:

- `float32`
- `float64`

Floating-point **MUST NOT** appear in win calculation, exposure enforcement, RTP aggregation, or payout paths.

### 5.2 Presentation Layer

Decimal or arbitrary-precision libraries **MAY** be used **only** for human-readable presentation (UI, reports, exports). Presentation conversions **MUST NOT** feed back into execution or measurement logic.

---

## 6. Validation First

The **Validation Engine** is the single source of truth for structural and static mathematical correctness of a `GameVersion`.

### 6.1 Separation of Concerns

- **Runtime Core MUST** assume inputs have already passed validation.
- Validation logic **MUST NOT** be duplicated inside Runtime Core.
- Defensive checks in Runtime Core **MAY** exist only for safety against internal bugs and **MUST** emit explicit runtime fault events—not re-implement graph or schema rules.

### 6.2 Validation Gates

Validation **MUST** occur:

| Gate | Requirement |
|------|-------------|
| Save | Invalid documents **MUST NOT** be persisted as canonical drafts without explicit warn-only mode (if ever introduced—currently **MUST NOT** be assumed) |
| Publish | Published versions **MUST** pass full validation pipeline |
| Simulation | Simulation **MUST NOT** start against invalid `GameVersion` documents |

Validation pipeline order **MUST** remain: **Schema → Graph → Plugin → Exposure → Limits**, as defined in the Technical Specification and Canonical Schema.

---

## 7. Runtime Core Responsibilities

Runtime Core **MUST** only:

- Execute hierarchical state machines
- Manage the state stack (`spawn` / `pop`)
- Evaluate and apply transitions
- Invoke built-in plugins through defined contracts
- Emit runtime events per the event contract

### 7.1 Prohibited Runtime Core Behavior

Runtime Core **MUST NOT**:

- Calculate RTP, volatility, or hit frequency
- Persist game or session data (MVP)
- Call AI services
- Perform validation (schema, graph, or plugin)
- Mutate canonical `GameVersion` documents

Runtime Core **SHOULD** remain free of business analytics and remain a pure execution engine.

---

## 8. Mathematical Engine Responsibilities

The Mathematical Engine **MUST** only:

- Calculate RTP (total and decomposed by RTP category)
- Calculate volatility and related statistical measures
- Calculate hit frequency and feature frequencies
- Calculate exposure metrics from simulation artifacts
- Aggregate simulation statistics

### 8.1 Prohibited Mathematical Engine Behavior

The Mathematical Engine **MUST NOT**:

- Execute game logic or drive state transitions
- Modify runtime state or plugin context
- Validate game definitions (that is Validation Engine scope)
- Invoke plugins directly for spin outcomes

Measurement **MUST** be derived from emitted events and deterministic simulation outputs—not re-simulation of ad-hoc logic.

---

## 9. Plugin Rules

MVP plugins are **built-in only** (`core.base-game`, `core.free-spins`, `core.hold-and-win`, `core.multiplier`, and future built-ins approved by ADR).

### 9.1 Plugin Properties

Built-in plugins **MUST** be:

- **Deterministic** — same inputs produce same outputs
- **Stateless** outside explicitly provided execution context
- **Pure functions** whenever possible (no hidden state)

### 9.2 Plugin Prohibitions

Plugins **MUST NOT**:

- Access databases
- Access the filesystem
- Make network requests
- Modify global or package-level mutable state
- Bypass the plugin contract or declare undeclared capabilities

Plugin configuration **MUST** validate against the corresponding plugin JSON Schema before runtime execution.

---

## 10. Event Rules

All meaningful runtime actions **MUST** emit events conforming to the Runtime Event Contract (Canonical Game Schema §12).

### 10.1 Transparency

- No hidden state transitions are permitted.
- Side effects that affect wins, features, or stack depth **MUST** be observable via events.
- Event ordering **MUST** be deterministic and documented.

### 10.2 Event Purposes

Events **MUST** support:

- **Debugging** — engineers can trace execution paths
- **Replay** — sessions can be reconstructed from event logs
- **Simulation analysis** — Mathematical Engine consumes event streams or derived artifacts

Implementers **MUST NOT** rely on undocumented internal state that is not recoverable from events and canonical inputs.

---

## 11. Golden Fixture Rules

Golden Fixtures are **authoritative regression tests** for validation, runtime, and mathematical correctness.

Reference: `docs/GOLDEN_FIXTURES_V1.md`, `tests/golden/`.

### 11.1 Failure Response

If Golden Fixtures fail:

1. **STOP** implementation.
2. **Investigate root cause** — do not mask failures.
3. **DO NOT** update expected results without mathematical justification and explicit approval.

Changing golden expected values to make CI pass without understanding **MUST NOT** occur.

### 11.2 Gating

Golden Fixtures **MUST** gate changes to:

- Runtime Core
- Validation Engine
- Mathematical Engine
- Plugin behavior affecting outcomes

A change that breaks golden fixtures **MUST NOT** be considered complete until fixtures pass or expectations are formally updated with documented mathematical rationale.

---

## 12. Testing Requirements

Every implementation **MUST** include appropriate tests.

| Test Type | Requirement |
|-----------|-------------|
| Unit tests | **MUST** be included for all new logic |
| Integration tests | **MUST** be included when components interact across boundaries |
| Golden Fixture tests | **MUST** be included when behavior affects fixture flows or metrics |

### 12.1 Coverage Targets

| Scope | Target |
|-------|--------|
| Minimum (all packages) | **80%** statement coverage |
| Critical components (Validation Engine, Runtime Core, RNG, money paths) | **SHOULD** exceed **90%** |

Coverage **MUST NOT** be achieved by trivial or assertion-free tests. Tests **SHOULD** validate real behavior and regression scenarios.

### 12.2 CI Discipline

Tests **MUST** pass before a task is marked complete. Skipping or disabling tests to merge **MUST NOT** occur without explicit approval.

---

## 13. Incremental Development

Each implementation task **MUST** focus on a **single bounded context**.

### 13.1 Allowed Focus Examples

| Task | Status |
|------|--------|
| Validation Engine | Allowed |
| Runtime Core | Allowed |
| Simulation Engine | Allowed |
| Mathematical Engine metrics module | Allowed |

### 13.2 Prohibited Multi-Subsystem Changes

Implementers **MUST NOT** combine major subsystems in a single task unless explicitly directed.

| Combined Task | Status |
|---------------|--------|
| Runtime Core + HTTP API + AI Assistant | **NOT** allowed |
| Validation Engine + Simulation Engine + UI | **NOT** allowed |
| Schema change + Runtime + Golden update without approval | **NOT** allowed |

Large tasks **SHOULD** be decomposed into reviewable, independently testable increments.

---

## 14. Simplicity Rules

Implementers **MUST** prioritize:

- **Simplicity** — smallest correct solution
- **Readability** — code readable by domain experts, not just authors
- **Maintainability** — clear boundaries and minimal coupling

### 14.1 Prohibited Premature Complexity

The following **MUST NOT** be introduced unless explicitly requested:

- Microservices architecture
- Message buses (e.g., Kafka)
- Kubernetes / complex orchestration
- Premature optimization (custom allocators, lock-free structures, etc.)
- Framework churn without ADR

When complexity is necessary, it **MUST** be justified in an ADR or explicit assumption block.

---

## 15. Explicit Assumptions

Whenever requirements are ambiguous and a decision must be made, implementers **MUST** document assumptions explicitly before proceeding.

### 15.1 Required Format

```
ASSUMPTION:
<R clear statement of what was assumed>

RATIONALE:
<Why this assumption was necessary>

ALTERNATIVES CONSIDERED:
<Other options and why they were rejected>
```

### 15.2 Rules

- Assumptions **MUST NOT** be hidden in code or commit messages alone.
- Assumptions that affect architecture, schemas, or MVP scope **MUST** be escalated to the user before implementation continues.
- Silent defaults that alter mathematical behavior **MUST NOT** be introduced.

---

## 16. Versioning Rules

Frozen artifacts **MUST NOT** change incompatibly in place.

### 16.1 Breaking Change Process

Breaking changes **MUST** include:

1. New schema version (e.g., `1.0.0` → `1.1.0` or `2.0.0` per semver policy)
2. Migration documentation
3. ADR update or new ADR

### 16.2 Compatibility

Backward compatibility **SHOULD** be preserved whenever possible. Deprecation **SHOULD** precede removal with documented timelines.

Implementers **MUST NOT** rename validation error codes, registry IDs, or plugin IDs without a version bump and migration path.

---

## 17. Python Engineering Standards

Python is the primary implementation language for core engines (see [ADR-007](./adr/ADR-007-backend-language-python.md) and Technical Specification §L).

### 17.1 Language and Toolchain

| Standard | Requirement |
|----------|-------------|
| Python version | **3.13+** |
| Dependency management | **`uv`** (`pyproject.toml`, lockfile committed) |
| Linting | **Ruff** (import order, style, common bugs) |
| Formatting | **Black** (line length per project config, default 88) |
| Type checking | **MyPy strict mode** (`strict = true` in pyproject) |
| Testing | **Pytest** with fixtures; **pytest-cov** for coverage |
| Logging | **structlog** (structured, JSON-capable; no print in library code) |

### 17.2 Typing and Data Modeling

Code **MUST**:

| Standard | Requirement |
|----------|-------------|
| Type hints | Mandatory on all public functions, methods, and module-level APIs |
| DTOs / validation models | **Pydantic v2** for JSON-boundary types, validation reports, API payloads |
| Immutable domain objects | **`@dataclass(frozen=True)`** or Pydantic frozen models where appropriate |
| Interfaces | **`typing.Protocol`** for plugin contracts, RNG, validators, and engine facades |
| Generics | Use where they clarify collections and result types without over-abstraction |

Code **SHOULD**:

- Prefer `TypedDict` or Pydantic models over untyped `dict[str, Any]` at boundaries
- Use `Final`, `Literal`, and `NewType` to encode invariants (error codes, event types, engine version strings)
- Keep `Any` out of core execution paths except at explicit JSON extension points (`extensions` fields)

### 17.3 Architecture and State

Code **MUST**:

| Standard | Requirement |
|----------|-------------|
| Global mutable state | **Avoid** — no module-level caches that affect determinism or outcomes |
| Composition | Prefer composition over inheritance; shallow class hierarchies |
| Context managers | Use for scoped resources (RNG streams, event log buffers, temporary execution state) |
| Dependency injection | Constructor/factory injection for engines, validators, plugin registries |
| Side effects | Runtime Core **MUST** remain pure and side-effect free (see §7, ADR-007) |
| Async in Runtime Core | **MUST NOT** use `asyncio` inside Runtime Core execution paths |
| Multiprocessing | Allowed **only** in Simulation Engine orchestration, not inside Runtime Core |

Code **MUST NOT**:

- Use `random` module defaults (unseeded) in runtime, simulation, or mathematical aggregation paths
- Rely on dict/set iteration order for execution semantics (use explicit sorted keys where order matters)
- Perform I/O inside plugins (filesystem, network, database)
- Use `eval`, dynamic imports, or runtime code generation for game logic

### 17.4 Package Layout

Packages **SHOULD** align with bounded contexts under `packages/runtime_core/`:

| Package | Responsibility |
|---------|----------------|
| `domain` | Canonical domain types (`GameVersion`, symbols, state machines) |
| `validation` | Validation Engine pipeline |
| `runtime` | Runtime Core public API and execution |
| `plugins` | Built-in plugin implementations |
| `simulation` | Simulation Engine orchestration |
| `mathematics` | RTP, volatility, statistical aggregation |
| `common` | Shared utilities (money helpers, determinism guards, error types) |

- Export intentional public APIs from package `__init__.py` or dedicated `api` modules.
- Keep internal modules prefixed with `_` or under `_internal/` subpackages when needed.
- Tests live in `tests/` mirroring package structure (not co-located in production packages unless small).

### 17.5 Errors and Logging

- Return explicit result types or raise domain-specific exceptions with stable error codes (`SV-*`, `GV-*`, `RV-*`, `SP-*`).
- Wrap third-party validation errors with context; **MUST NOT** swallow validation failures.
- structlog **SHOULD** bind correlation IDs (`simulationRunId`, `spinChainIndex`, `gameVersionContentHash`) at Simulation/API layers — **MUST NOT** bind wall-clock timestamps into Runtime Core outcome logic.

### 17.6 Testing and Coverage

| Scope | Target |
|-------|--------|
| Minimum (all packages) | **80%** line coverage |
| Validation Engine | **90%+** |
| Runtime Core (including RNG, events, money paths) | **90%+** |

- Use pytest parametrize for validation error codes and event log mode matrices.
- Golden fixture tests **MUST** remain authoritative regression gates.
- Coverage **MUST NOT** be achieved by trivial or assertion-free tests.

### 17.7 Prohibited Patterns

Code **MUST NOT**:

- Use `# type: ignore` without a comment explaining why and a ticket/ADR reference
- Disable Ruff or MyPy rules globally to merge — fix or narrow per-file overrides with justification
- Introduce heavyweight frameworks inside Runtime Core (ORM, HTTP clients, task queues)
- Commit secrets, `.env` values, or local machine paths into schema resolution defaults

---

## 18. Completion Checklist

Before considering **any** implementation task complete, implementers **MUST** verify:

| # | Check |
|---|-------|
| 1 | **Architecture compliance** — aligns with Technical Specification bounded contexts |
| 2 | **ADR compliance** — no contradiction with Accepted ADRs |
| 3 | **MVP scope compliance** — no non-MVP features introduced |
| 4 | **Tests passing** — unit, integration, and golden tests as applicable |
| 5 | **Golden Fixtures passing** — when touching validation, runtime, math, or plugins |
| 6 | **No breaking schema changes** — unless explicitly approved with version bump |
| 7 | **No undocumented assumptions** — all assumptions recorded per §15 |
| 8 | **Validation gates respected** — invalid documents cannot reach publish/sim paths |
| 9 | **Determinism preserved** — no unseeded randomness or float money paths introduced |
| 10 | **Coverage targets met** — minimum 80%; critical paths SHOULD exceed 90% |

If any item fails, the task **MUST NOT** be reported as complete.

---

## Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-06-14 | Replaced Go engineering standards with Python standards (ADR-007); money type wording updated for Python |
| 1.0.0 | 2026-06-14 | Initial Engineering Constitution for Cursor and engineering agents |

---

## Related Documents

- [TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md)
- [CANONICAL_GAME_SCHEMA_V1.md](./CANONICAL_GAME_SCHEMA_V1.md)
- [GOLDEN_FIXTURES_V1.md](./GOLDEN_FIXTURES_V1.md)
- [Architecture Decision Records](./adr/) — including [ADR-007 Backend Language: Python](./adr/ADR-007-backend-language-python.md)

**This document is mandatory reading before any implementation task.**
