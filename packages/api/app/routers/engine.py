"""Engine metadata router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, get_engine_service
from app.schemas.engine import EngineVersionResponse
from app.services.engine_service import EngineService

router = APIRouter(prefix="/engine", tags=["engine"])


@router.get("/version", response_model=EngineVersionResponse)
async def get_engine_version(
    engine_service: EngineService = Depends(get_engine_service),
    session: AsyncSession = Depends(get_db_session),
) -> EngineVersionResponse:
    return await engine_service.engine_version(session)
