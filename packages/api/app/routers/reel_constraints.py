"""Constraint validation endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.context import AuthContext
from app.auth.dependencies import get_auth_context
from app.reel_constraints.engine import ConstraintDocument, ConstraintValidationReport, run_constraint_engine
from app.reel_constraints.presets import BUILTIN_PRESETS

router = APIRouter(prefix="/reel-studio/constraints", tags=["reel-studio-constraints"])


class ValidateConstraintsRequest(BaseModel):
    reel_set: dict[str, Any] = Field(alias="reelSet")
    symbols: dict[str, Any]
    constraint_document: dict[str, Any] = Field(alias="constraintDocument")

    model_config = {"populate_by_name": True}


class SavePresetRequest(BaseModel):
    preset: dict[str, Any]


@router.post("/validate", response_model=ConstraintValidationReport)
def validate_constraints(
    body: ValidateConstraintsRequest,
    _auth: AuthContext = Depends(get_auth_context),
) -> ConstraintValidationReport:
    document = ConstraintDocument.model_validate(body.constraint_document)
    return run_constraint_engine(body.reel_set, body.symbols, document)


@router.get("/presets")
def list_constraint_presets(
    _auth: AuthContext = Depends(get_auth_context),
) -> list[dict[str, Any]]:
    return BUILTIN_PRESETS


@router.post("/presets")
def save_constraint_preset(
    body: SavePresetRequest,
    _auth: AuthContext = Depends(get_auth_context),
) -> dict[str, Any]:
    preset = body.preset
    if not preset.get("id") or not preset.get("document"):
        raise ValueError("Invalid preset payload")
    preset["builtIn"] = False
    return preset
