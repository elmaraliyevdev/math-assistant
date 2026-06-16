"""Export router."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.auth.dependencies import get_auth_context
from app.auth.context import AuthContext
from app.dependencies import get_export_service
from app.services.export_service import ExportService

router = APIRouter(tags=["exports"])


@router.get("/simulations/compare/export")
async def export_simulation_comparison(
    ids: str = Query(..., description="Comma-separated simulation UUIDs"),
    format: str = Query(default="pdf", pattern="^(json|pdf)$"),
    auth: AuthContext = Depends(get_auth_context),
    export_service: ExportService = Depends(get_export_service),
) -> Response:
    simulation_ids = [uuid.UUID(part.strip()) for part in ids.split(",") if part.strip()]
    content, media_type, filename = await export_service.export_simulation_comparison(
        auth,
        simulation_ids,
        format,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/simulations/{simulation_id}/export")
async def export_simulation(
    simulation_id: uuid.UUID,
    format: str = Query(default="json", pattern="^(json|csv|pdf)$"),
    auth: AuthContext = Depends(get_auth_context),
    export_service: ExportService = Depends(get_export_service),
) -> Response:
    content, media_type, filename = await export_service.export_simulation_results(
        auth,
        simulation_id,
        format,
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/games/{game_id}/versions/{version_id}/export")
async def export_game_version(
    game_id: uuid.UUID,
    version_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    export_service: ExportService = Depends(get_export_service),
) -> Response:
    content, filename = await export_service.export_game_version_json(
        auth,
        game_id,
        version_id,
    )
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
