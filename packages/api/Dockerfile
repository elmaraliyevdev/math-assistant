FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

COPY packages/runtime_core /app/packages/runtime_core
COPY packages/game-schema /app/packages/game-schema
COPY packages/api /app/packages/api

WORKDIR /app/packages/api
RUN uv sync --frozen 2>/dev/null || uv sync

EXPOSE 8000

RUN chmod +x /app/packages/api/scripts/entrypoint.sh

CMD ["/app/packages/api/scripts/entrypoint.sh"]
