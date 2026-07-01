"""Demo API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DemoGameSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: UUID
    name: str
    version_count: int = Field(alias="versionCount")
    simulation_count: int = Field(alias="simulationCount")


class DemoOverviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    configured: bool = True
    organization_id: UUID | None = Field(default=None, alias="organizationId")
    organization_name: str = Field(default="", alias="organizationName")
    game_count: int = Field(default=0, alias="gameCount")
    version_count: int = Field(default=0, alias="versionCount")
    simulation_count: int = Field(default=0, alias="simulationCount")
    games: list[DemoGameSummary] = Field(default_factory=list)


class DuplicateDemoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    games_copied: int = Field(alias="gamesCopied")
    organization_id: UUID = Field(alias="organizationId")
