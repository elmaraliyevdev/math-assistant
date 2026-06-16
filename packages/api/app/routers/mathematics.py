"""Theoretical mathematics and calibration router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from app.auth.context import AuthContext
from app.auth.dependencies import get_auth_context
from app.dependencies import get_mathematics_service
from app.schemas.mathematics import (
    CalibrateRequest,
    CalibrateResponse,
    CertificationReportRequest,
    CertificationReportResponse,
    MathematicsBaseRequest,
    TheoreticalAnalysisResponse,
)
from app.services.mathematics_service import MathematicsService

router = APIRouter(prefix="/mathematics", tags=["mathematics"])


@router.post("/theoretical", response_model=TheoreticalAnalysisResponse)
async def theoretical_analysis(
    body: MathematicsBaseRequest,
    auth: AuthContext = Depends(get_auth_context),
    mathematics_service: MathematicsService = Depends(get_mathematics_service),
) -> TheoreticalAnalysisResponse:
    return await mathematics_service.theoretical_analysis(
        auth,
        body.game_version_id,
        reel_set_id=body.reel_set_id,
        total_bet_minor_units=body.total_bet_minor_units,
    )


@router.post("/calibrate", response_model=CalibrateResponse)
async def calibrate_mathematics(
    body: CalibrateRequest,
    auth: AuthContext = Depends(get_auth_context),
    mathematics_service: MathematicsService = Depends(get_mathematics_service),
) -> CalibrateResponse:
    return await mathematics_service.calibrate(auth, body)


@router.post("/certification-report", response_model=None)
async def certification_report(
    body: CertificationReportRequest,
    auth: AuthContext = Depends(get_auth_context),
    mathematics_service: MathematicsService = Depends(get_mathematics_service),
) -> CertificationReportResponse | Response:
    result, media_type, filename = await mathematics_service.certification_report(
        auth,
        body,
    )
    if body.export_format in ("json", "pdf"):
        return Response(
            content=result,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    return result