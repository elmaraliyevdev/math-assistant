# Game Schema Package (v1.0.0)

Machine-readable contracts for the AI Game Mathematics Assistant. These artifacts are **frozen at v1.0.0** and are the source of truth for validation and development.

**Human specification:** [docs/CANONICAL_GAME_SCHEMA_V1.md](../../docs/CANONICAL_GAME_SCHEMA_V1.md)  
**Golden fixtures framework:** [docs/GOLDEN_FIXTURES_V1.md](../../docs/GOLDEN_FIXTURES_V1.md)

## Folder Structure

```
packages/game-schema/
├── README.md
├── schemas/
│   ├── game-version-1.0.0.schema.json    # Canonical GameVersion document
│   └── plugins/
│       ├── base-game-1.0.0.schema.json
│       ├── free-spins-1.0.0.schema.json
│       ├── hold-and-win-1.0.0.schema.json
│       └── multiplier-1.0.0.schema.json
└── registries/
    ├── rtp-categories-v1.json
    ├── priority-tiers-v1.json
    └── validation-errors-v1.json
```

## Usage (Implementation Phase)

| Consumer | Artifacts |
|----------|-----------|
| Validation Engine | `game-version-1.0.0.schema.json`, plugin schemas, registries |
| DSL Compiler | Plugin schemas, priority tiers, RTP categories |
| Runtime Core | Plugin schemas (config shape), determinism block |
| Golden Runner | Fixture spec + pinned `contentHash` (future) |

## Versioning

All paths and `$id` values use semver **1.0.0**. Breaking changes require new files (e.g. `game-version-1.1.0.schema.json`).
