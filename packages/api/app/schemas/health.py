"""API response schemas for health checks."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(examples=["ok"])
    timestamp: str = Field(description="ISO 8601 UTC timestamp")


class ReadinessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(examples=["ready", "degraded"])
    timestamp: str
    checks: dict[str, str]
