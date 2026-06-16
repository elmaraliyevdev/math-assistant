"""Request and response schemas for games and validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateGameRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Book of Fortune",
                    "description": (
                        "5x3 video slot with Free Spins and Hold & Win"
                    ),
                    "organizationId": "660e8400-e29b-41d4-a716-446655440000",
                },
            ],
        },
    )

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    organization_id: UUID = Field(alias="organizationId")


class UpdateGameRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [{"name": "Book of Fortune Deluxe"}],
        },
    )

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class GameResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    organization_id: UUID = Field(alias="organizationId")
    name: str
    description: str | None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class GameListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    items: list[GameResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class ValidateGameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    canonical_json: dict[str, Any] = Field(alias="canonicalJson")
    engine_version: str = Field(alias="engineVersion")


class ValidationFindingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    code: str
    severity: str
    message: str
    path: str
    suggestion: str | None = None


class ValidationReportMetadataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    validator_version: str = Field(alias="validatorVersion")
    schema_version: str = Field(alias="schemaVersion")


class ValidationReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    findings: list[ValidationFindingResponse] = Field(default_factory=list)
    metadata: ValidationReportMetadataResponse | None = None


class ValidateGameSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    valid: bool = True
    content_hash: str = Field(alias="contentHash")
    engine_version: str = Field(alias="engineVersion")
    report: ValidationReportResponse


class ValidateGameFailureResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    valid: bool = False
    content_hash: str = Field(alias="contentHash")
    report: ValidationReportResponse


class ReadyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    ready: bool
    engine_version: str = Field(alias="engineVersion")
