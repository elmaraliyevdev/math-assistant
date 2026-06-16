#!/bin/sh
set -e

export PYTHONDONTWRITEBYTECODE=1

cd /app/packages/api
uv run alembic upgrade head
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
