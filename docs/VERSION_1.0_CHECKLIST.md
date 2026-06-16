# Version 1.0 Freeze Checklist

Complete before tagging and distributing **Math Assistant v1.0.0**.

## Version alignment

- [x] Engine pinned at `runtime-core@1.8.0` (`packages/runtime_core/runtime_core/runtime/version.py` — unchanged)
- [x] API `pyproject.toml` and OpenAPI app version → `1.0.0`
- [x] Web `package.json` → `1.0.0`
- [x] Root `VERSION` file documents all component tags

## Git tags

Run after committing release prep (repository must be initialized):

```bash
chmod +x release/tag-v1.0.sh
./release/tag-v1.0.sh
```

Expected tags:

- `runtime-core@1.8.0`
- `api@1.0.0`
- `web@1.0.0`

## Release artifacts

```bash
chmod +x scripts/generate-release-artifacts.sh
./scripts/generate-release-artifacts.sh
```

Verify `release/artifacts/v1.0.0/` contains:

- [x] `docker-compose.prod.yml`
- [x] `.env.production.example`
- [x] `monitoring/`
- [x] `math-assistant-src-*.tar.gz`
- [x] `MANIFEST.txt`

## Documentation

- [x] `CHANGELOG.md`
- [x] `docs/RELEASE_NOTES_v1.0.md`
- [x] Internal doc links verified: `./scripts/verify-doc-links.sh`

## Tests

| Suite | Command | Status |
|-------|---------|--------|
| API integration | `cd packages/api && uv run pytest tests/api -q` | 69 passed |
| API security | `cd packages/api && uv run pytest tests/api/test_security_api.py -q` | 7 passed |
| Web unit | `cd packages/web && npm test -- --run` | 160 passed |
| Engine golden | CI / `packages/runtime_core` pytest | Engine frozen — no changes |

## Docker production verification

> **Note:** Requires Docker daemon running locally.

```bash
chmod +x scripts/verify-docker-prod.sh
./scripts/verify-docker-prod.sh
```

Manual verification:

- [ ] `curl -sf http://localhost:8080/` returns HTML *(requires Docker daemon — run `scripts/verify-docker-prod.sh`)*
- [ ] `curl -sf http://localhost:8080/api/health` returns `{"status":"ok",...}`
- [ ] `curl -sf http://localhost:8080/api/health/ready` shows `database: ok`
- [ ] Grafana at `:3000`, Prometheus at `:9090`
- [ ] Register → create game → upload version → run simulation (smoke)

Teardown: `docker compose -f docker-compose.prod.yml down`

## Constraints verified

- [ ] No `runtime_core` source changes in v1.0 release commit
- [ ] No simulation engine behavior changes
- [ ] No new business functionality — release prep only

## Sign-off

| Role | Name | Date |
|------|------|------|
| Engineering lead | | |
| QA | | |
| Operations | | |

**Freeze declared:** _______________
