# Release v1.0.0

## Tags

| Tag | Component |
|-----|-----------|
| `runtime-core@1.8.0` | Frozen simulation engine (`runtime-core@1.8.0`) |
| `api@1.0.0` | FastAPI platform (`packages/api`) |
| `web@1.0.0` | React SPA (`packages/web`) |

Create tags (requires git repository with clean working tree):

```bash
./release/tag-v1.0.sh
```

## Artifacts

```bash
./scripts/generate-release-artifacts.sh
```

Output: `release/artifacts/v1.0.0/`

## Verification scripts

| Script | Purpose |
|--------|---------|
| `scripts/verify-doc-links.sh` | Validate `docs/` markdown links |
| `scripts/verify-docker-prod.sh` | Build & smoke-test production compose |
