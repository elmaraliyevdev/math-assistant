"""Distributed worker monitoring router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_monitoring_service
from app.distributed.monitoring_service import MonitoringService
from app.schemas.distributed import WorkerHealthResponse, WorkerListResponse

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("", response_model=WorkerListResponse)
async def list_workers(
    auth: AuthContext = Depends(get_auth_context),
    monitoring: MonitoringService = Depends(get_monitoring_service),
) -> WorkerListResponse:
    return monitoring.list_workers()


@router.get("/health", response_model=WorkerHealthResponse)
async def worker_health(
    auth: AuthContext = Depends(get_auth_context),
    monitoring: MonitoringService = Depends(get_monitoring_service),
) -> WorkerHealthResponse:
    return monitoring.worker_health()
