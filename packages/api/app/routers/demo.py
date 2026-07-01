"""Demo workspace router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_demo_service
from app.schemas.demo import DemoOverviewResponse, DuplicateDemoResponse
from app.services.demo_service import DemoService

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/overview", response_model=DemoOverviewResponse)
async def get_demo_overview(
    auth: AuthContext = Depends(get_auth_context),
    demo_service: DemoService = Depends(get_demo_service),
) -> DemoOverviewResponse:
    return await demo_service.get_overview(auth)


@router.post(
    "/duplicate",
    response_model=DuplicateDemoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def duplicate_demo(
    auth: AuthContext = Depends(get_auth_context),
    demo_service: DemoService = Depends(get_demo_service),
) -> DuplicateDemoResponse:
    return await demo_service.duplicate_to_workspace(auth)
