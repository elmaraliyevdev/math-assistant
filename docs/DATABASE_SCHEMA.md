# Database Schema Design

**Phase:** 10.6 — Platform Architecture Design  
**Date:** 2026-06-14  
**Engine baseline:** `runtime-core@1.8.0`  
**Status:** Design only — no migrations implemented

---

## 1. Design principles

1. **Immutable game versions** — canonical JSON stored once, keyed by content hash; never updated in place
2. **Append-only simulation artifacts** — results and math reports are snapshots, not mutable aggregates
3. **Engine version on every run** — reproducibility requires pinned `engineVersion`
4. **Tenant isolation** — all game and simulation data scoped to `organization_id`
5. **Integer money in JSON** — `*MinorUnits` fields in stored engine DTOs; no floats in persisted win/bet amounts

---

## 2. Entity-relationship diagram

```mermaid
erDiagram
    organizations ||--o{ memberships : has
    users ||--o{ memberships : has
    organizations ||--o{ games : owns
    games ||--o{ game_versions : versions
    game_versions ||--o{ simulation_runs : uses
    simulation_runs ||--o{ simulation_shards : splits
    simulation_runs ||--o| simulation_results : produces
    simulation_runs ||--o| mathematics_reports : analyzes
    organizations ||--o{ audit_logs : logs
    users ||--o{ audit_logs : actor

    organizations {
        uuid id PK
        text name
        timestamptz created_at
    }

    users {
        uuid id PK
        text email UK
        text display_name
        timestamptz created_at
    }

    memberships {
        uuid id PK
        uuid organization_id FK
        uuid user_id FK
        text role
        timestamptz created_at
    }

    games {
        uuid id PK
        uuid organization_id FK
        text name
        text slug UK
        uuid current_version_id FK
        timestamptz created_at
        timestamptz updated_at
    }

    game_versions {
        uuid id PK
        uuid game_id FK
        text content_hash UK
        jsonb canonical_json
        text schema_version
        text engine_version
        timestamptz created_at
        uuid created_by FK
    }

    simulation_runs {
        uuid id PK
        uuid organization_id FK
        uuid game_version_id FK
        text simulation_run_id
        bytea master_seed_enc
        bigint spin_count
        int shard_count
        text engine_version
        text status
        jsonb profile_json
        timestamptz created_at
        timestamptz started_at
        timestamptz completed_at
        uuid created_by FK
    }

    simulation_shards {
        uuid id PK
        uuid simulation_run_id FK
        int shard_index
        int spin_start
        int spin_count
        bytea shard_seed
        text status
        jsonb partial_accumulator_json
        timestamptz completed_at
    }

    simulation_results {
        uuid id PK
        uuid simulation_run_id FK UK
        jsonb result_json
        timestamptz created_at
    }

    mathematics_reports {
        uuid id PK
        uuid simulation_run_id FK UK
        jsonb report_json
        jsonb spin_wins_sample_json
        int spin_wins_sample_size
        timestamptz created_at
    }

    audit_logs {
        uuid id PK
        uuid organization_id FK
        uuid user_id FK
        text action
        text resource_type
        uuid resource_id
        jsonb metadata_json
        timestamptz created_at
    }
```

---

## 3. Table definitions

### 3.1 `organizations`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` |
| `name` | `TEXT` | NOT NULL |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` |

**Indexes:** PK only (MVP).

---

### 3.2 `users`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `email` | `TEXT` | NOT NULL, UNIQUE |
| `display_name` | `TEXT` | NOT NULL |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `now()` |

**Indexes:** `UNIQUE (email)`

---

### 3.3 `memberships`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `organization_id` | `UUID` | FK → `organizations(id)` ON DELETE CASCADE |
| `user_id` | `UUID` | FK → `users(id)` ON DELETE CASCADE |
| `role` | `TEXT` | NOT NULL, CHECK IN (`owner`, `admin`, `analyst`, `viewer`) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |

**Indexes:**

- `UNIQUE (organization_id, user_id)`
- `INDEX memberships_user_id_idx ON (user_id)`

---

### 3.4 `games`

Logical game container; points to latest validated version for editing workflow.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `organization_id` | `UUID` | FK → `organizations`, NOT NULL |
| `name` | `TEXT` | NOT NULL |
| `slug` | `TEXT` | NOT NULL |
| `current_version_id` | `UUID` | FK → `game_versions(id)`, nullable |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL |

**Indexes:**

- `UNIQUE (organization_id, slug)`
- `INDEX games_organization_id_idx ON (organization_id)`

---

### 3.5 `game_versions` (immutable)

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `game_id` | `UUID` | FK → `games`, NOT NULL |
| `content_hash` | `TEXT` | NOT NULL, UNIQUE — SHA-256 hex of canonical JSON |
| `canonical_json` | `JSONB` | NOT NULL — full `GameVersion` document |
| `schema_version` | `TEXT` | NOT NULL — e.g. `1.0.0` |
| `engine_version` | `TEXT` | NOT NULL — validator pin at ingest |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |
| `created_by` | `UUID` | FK → `users`, nullable |

**Indexes:**

- `UNIQUE (content_hash)` — deduplication / content-addressing
- `INDEX game_versions_game_id_created_at_idx ON (game_id, created_at DESC)`

#### Immutable GameVersion strategy

```
                    ┌─────────────────┐
  POST /games ─────►│ Compute hash    │
  (canonical JSON)  │ SHA-256(canonical) │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     hash exists?                   hash new?
              │                             │
              ▼                             ▼
     Return existing               INSERT game_versions
     game_version_id               (no UPDATE ever)
```

**Rules:**

- `UPDATE` and `DELETE` on `game_versions` are **forbidden** at application level
- Corrections create a **new** version row with new hash
- Simulations FK to `game_version_id`, not mutable `games.current_version_id`
- `canonical_json` stored verbatim for audit replay
- Optional future: store canonical JSON in object storage; DB holds hash + pointer

---

### 3.6 `simulation_runs`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `organization_id` | `UUID` | FK, NOT NULL |
| `game_version_id` | `UUID` | FK → `game_versions`, NOT NULL |
| `simulation_run_id` | `TEXT` | NOT NULL — engine correlation ID |
| `master_seed_enc` | `BYTEA` | NOT NULL — encrypted seed bytes |
| `spin_count` | `BIGINT` | NOT NULL, CHECK `>= 0` |
| `shard_count` | `INT` | NOT NULL, CHECK `>= 1` |
| `engine_version` | `TEXT` | NOT NULL — e.g. `runtime-core@1.8.0` |
| `status` | `TEXT` | NOT NULL — `pending`, `running`, `aggregating`, `completed`, `failed` |
| `profile_json` | `JSONB` | NOT NULL — full `SimulationProfile` (sans raw seed in API responses) |
| `error_message` | `TEXT` | nullable |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |
| `started_at` | `TIMESTAMPTZ` | nullable |
| `completed_at` | `TIMESTAMPTZ` | nullable |
| `created_by` | `UUID` | FK → `users` |

**Indexes:**

- `INDEX simulation_runs_org_status_idx ON (organization_id, status)`
- `INDEX simulation_runs_game_version_idx ON (game_version_id)`
- `UNIQUE (organization_id, simulation_run_id)` — idempotent client run IDs per org

---

### 3.7 `simulation_shards`

Optional observability for multi-shard runs; not required for MVP correctness (engine aggregates internally).

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `simulation_run_id` | `UUID` | FK ON DELETE CASCADE |
| `shard_index` | `INT` | NOT NULL |
| `spin_start` | `INT` | NOT NULL |
| `spin_count` | `INT` | NOT NULL |
| `shard_seed` | `BYTEA` | NOT NULL — ADR-002 audit |
| `status` | `TEXT` | NOT NULL |
| `partial_accumulator_json` | `JSONB` | nullable |
| `completed_at` | `TIMESTAMPTZ` | nullable |

**Indexes:**

- `UNIQUE (simulation_run_id, shard_index)`

---

### 3.8 `simulation_results`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `simulation_run_id` | `UUID` | FK, UNIQUE — one result per run |
| `result_json` | `JSONB` | NOT NULL — `SimulationResult` schema |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |

**Indexes:**

- `UNIQUE (simulation_run_id)`
- GIN optional: `result_json` for feature trigger queries (Phase 15)

---

### 3.9 `mathematics_reports`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `simulation_run_id` | `UUID` | FK, UNIQUE |
| `report_json` | `JSONB` | NOT NULL — `MathematicsReport` |
| `spin_wins_sample_json` | `JSONB` | nullable — array of ints for CI replay |
| `spin_wins_sample_size` | `INT` | nullable |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |

**Indexes:** `UNIQUE (simulation_run_id)`

---

### 3.10 `audit_logs`

Append-only compliance trail.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | PK |
| `organization_id` | `UUID` | FK, NOT NULL |
| `user_id` | `UUID` | FK, nullable (system actions) |
| `action` | `TEXT` | NOT NULL — e.g. `game.validate`, `simulation.create` |
| `resource_type` | `TEXT` | NOT NULL |
| `resource_id` | `UUID` | NOT NULL |
| `metadata_json` | `JSONB` | NOT NULL — request correlation, engine version |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |

**Indexes:**

- `INDEX audit_logs_org_created_idx ON (organization_id, created_at DESC)`
- `INDEX audit_logs_resource_idx ON (resource_type, resource_id)`

**Retention:** MVP indefinite; enterprise tier may partition by month.

---

## 4. JSON document shapes (stored)

Engine Pydantic models serialize with camelCase aliases to match API and golden fixtures:

| Table | JSON column | Engine model |
|-------|-------------|--------------|
| `game_versions.canonical_json` | Full game | `GameVersion` |
| `simulation_runs.profile_json` | Profile sans secrets in API | `SimulationProfile` |
| `simulation_results.result_json` | Aggregates | `SimulationResult` |
| `mathematics_reports.report_json` | Metrics | `MathematicsReport` |

---

## 5. Migration strategy (Phase 12)

1. Alembic revision `001_initial_platform_schema`
2. Seed script for local dev org + user
3. No engine tables — engine remains stateless library
4. Foreign keys enforce referential integrity; no cascading deletes from `game_versions` while simulations reference them

---

## 6. Query patterns

| Use case | Query |
|----------|-------|
| List games for org | `games WHERE organization_id = ? ORDER BY updated_at DESC` |
| Resolve version by hash | `game_versions WHERE content_hash = ?` |
| Poll simulation status | `simulation_runs WHERE id = ? AND organization_id = ?` |
| Full result bundle | JOIN `simulation_runs` → `simulation_results` → `mathematics_reports` |
| Audit trail | `audit_logs WHERE organization_id = ? ORDER BY created_at DESC LIMIT 100` |

---

## References

- [PLATFORM_ARCHITECTURE.md](./PLATFORM_ARCHITECTURE.md)
- [API_SPECIFICATION.md](./API_SPECIFICATION.md)
- [CANONICAL_GAME_SCHEMA_V1.md](./CANONICAL_GAME_SCHEMA_V1.md)
