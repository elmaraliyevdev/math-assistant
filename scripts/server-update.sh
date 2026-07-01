#!/usr/bin/env bash
# Pull latest code and rebuild the production stack on Hetzner.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-deploy/mvp.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  echo "Copy deploy/mvp.env and set API_JWT_SECRET_KEY + POSTGRES_PASSWORD" >&2
  exit 1
fi

echo "==> Pulling latest code"
git pull --ff-only

echo "==> Rebuilding and restarting containers"
docker compose \
  -f docker-compose.prod.yml \
  --env-file "$ENV_FILE" \
  --profile mvp \
  up -d --build

echo "==> Service status"
docker compose \
  -f docker-compose.prod.yml \
  --env-file "$ENV_FILE" \
  --profile mvp \
  ps

echo "==> Health check"
curl -sf "http://localhost:${WEB_PORT:-8080}/api/health" | head -c 200
echo ""
echo "Update complete."
