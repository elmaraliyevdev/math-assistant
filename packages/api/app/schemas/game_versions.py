"""Request and response schemas for game versions."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.games import ValidationFindingResponse


class CreateGameVersionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "canonicalJson": {"schemaVersion": "1.0.0"},
                    "engineVersion": "runtime-core@1.8.0",
                },
            ],
        },
    )

    canonical_json: dict[str, Any] = Field(alias="canonicalJson")
    engine_version: str = Field(alias="engineVersion")


class ValidationSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    passed: bool
    finding_count: int = Field(alias="findingCount")
    findings: list[ValidationFindingResponse] = Field(default_factory=list)


class CreateGameVersionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    version: int
    content_hash: str = Field(alias="contentHash")
    engine_version: str = Field(alias="engineVersion")
    validation_summary: ValidationSummaryResponse = Field(alias="validationSummary")


class GameVersionSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    version: int
    content_hash: str = Field(alias="contentHash")
    engine_version: str = Field(alias="engineVersion")
    created_at: datetime = Field(alias="createdAt")


class GameVersionDetailResponse(GameVersionSummaryResponse):
    canonical_json: dict[str, Any] = Field(alias="canonicalJson")
    validation_summary: ValidationSummaryResponse = Field(alias="validationSummary")
