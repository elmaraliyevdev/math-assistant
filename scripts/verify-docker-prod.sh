#!/usr/bin/env bash
# Verify Docker production stack builds and health endpoints respond.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export API_JWT_SECRET_KEY="${API_JWT_SECRET_KEY:-$(openssl rand -hex 32)}"
COMPOSE="docker compose -f docker-compose.prod.yml"

echo "Building production images..."
$COMPOSE build

echo "Starting stack..."
$COMPOSE up -d

cleanup() {
  $COMPOSE down -v 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for API health..."
for i in $(seq 1 60); do
  if curl -sf "http://localhost:${WEB_PORT:-8080}/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

curl -sf "http://localhost:${WEB_PORT:-8080}/api/health" | grep -q '"status":"ok"'
curl -sf "http://localhost:${WEB_PORT:-8080}/api/health/ready" | grep -q '"status"'
curl -sf "http://localhost:${WEB_PORT:-8080}/" | head -1 | grep -qi doctype

echo "Production Docker verification passed"
