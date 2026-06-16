"""AI Mathematics Assistant API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GroundedCitationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    label: str
    source: str
    path: str
    value: str | float | int | None = None


class AssistantSectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    title: str
    content: str


class SimulationRecommendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    target_rtp: float | None = Field(default=None, alias="targetRtp")


class SimulationCompareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_ids: list[UUID] = Field(alias="simulationIds", min_length=2, max_length=5)


class CalibrationRecommendationItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    severity: str
    category: str
    action: str
    expected_rtp_impact: str = Field(alias="expectedRtpImpact")


class SimulationAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    content: str
    sections: list[AssistantSectionResponse]
    citations: list[GroundedCitationResponse]


class SimulationRecommendResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_id: UUID = Field(alias="simulationId")
    target_rtp: float | None = Field(default=None, alias="targetRtp")
    content: str
    sections: list[AssistantSectionResponse]
    recommendations: list[CalibrationRecommendationItem]
    citations: list[GroundedCitationResponse]


class SimulationCompareAssistantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    simulation_ids: list[UUID] = Field(alias="simulationIds")
    content: str
    sections: list[AssistantSectionResponse]
    citations: list[GroundedCitationResponse]


class GameVersionExplainResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    game_version_id: UUID = Field(alias="gameVersionId")
    content: str
    sections: list[AssistantSectionResponse]
    citations: list[GroundedCitationResponse]
