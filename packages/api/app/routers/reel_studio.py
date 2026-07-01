"""Reel Studio helper endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.context import AuthContext
from app.auth.dependencies import get_auth_context
from app.reel_studio.merge import merge_reel_sets_into_canonical

router = APIRouter(prefix="/reel-studio", tags=["reel-studio"])


class MergeReelStudioRequest(BaseModel):
    canonical_json: dict[str, Any] = Field(alias="canonicalJson")
    reel_sets: dict[str, Any] = Field(alias="reelSets")

    model_config = {"populate_by_name": True}


class MergeReelStudioResponse(BaseModel):
    canonical_json: dict[str, Any] = Field(alias="canonicalJson")

    model_config = {"populate_by_name": True}


@router.post("/merge", response_model=MergeReelStudioResponse)
def merge_reel_studio(
    body: MergeReelStudioRequest,
    _auth: AuthContext = Depends(get_auth_context),
) -> MergeReelStudioResponse:
    return MergeReelStudioResponse(
        canonicalJson=merge_reel_sets_into_canonical(body.canonical_json, body.reel_sets),
    )
