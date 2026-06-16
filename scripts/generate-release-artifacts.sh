#!/usr/bin/env bash
# Generate production deployment artifact bundle for v1.0.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/release/artifacts/v1.0.0"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

rm -rf "$OUT"
mkdir -p "$OUT"

ARCHIVE_NAME="math-assistant-src-${STAMP}.tar.gz"
ARCHIVE_TMP="$(mktemp /tmp/math-assistant-src-XXXXXX.tar.gz)"

tar -czf "$ARCHIVE_TMP" \
  --exclude='node_modules' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='coverage' \
  --exclude='dist' \
  --exclude='release/artifacts' \
  -C "$ROOT" \
  packages/api packages/web packages/runtime_core \
  docker-compose.yml docker-compose.prod.yml \
  monitoring scripts release \
  docs/DEPLOYMENT_GUIDE.md docs/OPERATIONS_RUNBOOK.md \
  docs/RELEASE_NOTES_v1.0.md docs/VERSION_1.0_CHECKLIST.md \
  docs/USER_GUIDE.md docs/BETA_READINESS_CHECKLIST.md \
  CHANGELOG.md VERSION

cp "$ARCHIVE_TMP" "$OUT/$ARCHIVE_NAME"
cp "$ROOT/docker-compose.prod.yml" "$OUT/"
cp "$ROOT/VERSION" "$OUT/"
cp "$ROOT/docs/DEPLOYMENT_GUIDE.md" "$OUT/"
cp "$ROOT/docs/OPERATIONS_RUNBOOK.md" "$OUT/"
cp "$ROOT/docs/RELEASE_NOTES_v1.0.md" "$OUT/"
cp "$ROOT/docs/VERSION_1.0_CHECKLIST.md" "$OUT/"
cp -R "$ROOT/monitoring" "$OUT/monitoring"
cp "$ROOT/release/env.production.example" "$OUT/.env.production.example"

cat > "$OUT/MANIFEST.txt" <<EOF
Math Assistant v1.0.0 deployment artifacts
Generated: ${STAMP}
Commit: $(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo 'unknown')

Contents:
  docker-compose.prod.yml
  .env.production.example
  monitoring/
  DEPLOYMENT_GUIDE.md
  OPERATIONS_RUNBOOK.md
  RELEASE_NOTES_v1.0.md
  VERSION_1.0_CHECKLIST.md
  ${ARCHIVE_NAME}
EOF

rm -f "$ARCHIVE_TMP"

echo "Artifacts written to $OUT"
