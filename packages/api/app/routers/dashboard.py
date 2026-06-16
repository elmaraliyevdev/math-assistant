"""Dashboard router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_dashboard_service
from app.schemas.platform import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    auth: AuthContext = Depends(get_auth_context),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummaryResponse:
    return await dashboard_service.get_summary(auth)
