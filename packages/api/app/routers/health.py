"""Health check router."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, get_engine_service
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.engine_service import EngineService

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def get_health(
    engine_service: EngineService = Depends(get_engine_service),
) -> HealthResponse:
    return engine_service.health()


@router.get("/health/ready", response_model=ReadinessResponse)
async def get_readiness(
    session: AsyncSession = Depends(get_db_session),
) -> ReadinessResponse:
    checks: dict[str, str] = {}
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
        status = "ready"
    except Exception as exc:
        checks["database"] = f"error: {exc.__class__.__name__}"
        status = "degraded"

    return ReadinessResponse(
        status=status,
        timestamp=datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        checks=checks,
    )
