"""Prometheus metrics endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response

from app.config import Settings
from app.dependencies import get_settings
from app.observability.metrics import metrics_payload

router = APIRouter(tags=["metrics"])


def _verify_metrics_access(
    settings: Settings = Depends(get_settings),
    authorization: str | None = Header(default=None),
) -> None:
    token = settings.metrics_bearer_token
    if token is None:
        return
    if authorization != f"Bearer {token}":
        raise HTTPException(status_code=401, detail="metrics access denied")


@router.get("/metrics", dependencies=[Depends(_verify_metrics_access)])
async def prometheus_metrics() -> Response:
    return Response(
        content=metrics_payload(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
