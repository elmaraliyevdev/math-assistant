"""Game version management service."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.game_version import GameVersion
from app.db.models.organization_member import OrganizationRole
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.exceptions.domain import (
    DuplicateGameVersionError,
    GameNotFoundError,
    GameVersionNotFoundError,
    ValidationFailedError,
)
from app.schemas.game_versions import (
    CreateGameVersionRequest,
    CreateGameVersionResponse,
    GameVersionDetailResponse,
    GameVersionSummaryResponse,
    ValidationSummaryResponse,
)
from app.schemas.games import ValidateGameFailureResponse, ValidationFindingResponse
from app.services.audit_service import AuditService
from app.services.validation_service import ValidationService


def _to_summary(version: GameVersion) -> GameVersionSummaryResponse:
    return GameVersionSummaryResponse(
        id=version.id,
        version=version.version,
        content_hash=version.content_hash,
        engine_version=version.engine_version,
        created_at=version.created_at,
    )


CERTIFICATION_NOTICE = (
    "All displayed metrics originate from certified backend calculations."
)


def _validation_summary_for(version: GameVersion) -> ValidationSummaryResponse:
    findings = [
        ValidationFindingResponse.model_validate(item)
        for item in version.validation_findings
    ]
    return ValidationSummaryResponse(
        passed=version.validation_passed,
        finding_count=len(findings),
        findings=findings,
    )


def _to_detail(version: GameVersion) -> GameVersionDetailResponse:
    return GameVersionDetailResponse(
        id=version.id,
        version=version.version,
        content_hash=version.content_hash,
        engine_version=version.engine_version,
        canonical_json=version.canonical_json,
        created_at=version.created_at,
        validation_summary=_validation_summary_for(version),
    )


@dataclass(frozen=True, slots=True)
class GameVersionService:
    games: GameRepository
    versions: GameVersionRepository
    validation_service: ValidationService

    @classmethod
    def from_session(
        cls,
        session: AsyncSession,
        validation_service: ValidationService,
    ) -> GameVersionService:
        return cls(
            games=GameRepository(session),
            versions=GameVersionRepository(session),
            validation_service=validation_service,
        )

    async def create_version(
        self,
        auth: AuthContext,
        game_id: uuid.UUID,
        body: CreateGameVersionRequest,
    ) -> CreateGameVersionResponse:
        game = await self._require_game(auth, game_id)
        auth.require_role(game.organization_id, OrganizationRole.DEVELOPER)

        result = self.validation_service.validate(
            canonical_json=body.canonical_json,
            engine_version=body.engine_version,
        )
        if isinstance(result, ValidateGameFailureResponse):
            raise ValidationFailedError(
                content_hash=result.content_hash,
                findings=[
                    finding.model_dump(by_alias=True)
                    for finding in result.report.findings
                ],
            )

        existing = await self.versions.get_by_content_hash(result.content_hash)
        if existing is not None:
            raise DuplicateGameVersionError(
                content_hash=result.content_hash,
                existing_version_id=str(existing.id),
            )

        findings_payload = [
            finding.model_dump(by_alias=True) for finding in result.report.findings
        ]
        next_version = await self.versions.get_max_version(game_id) + 1
        version = GameVersion(
            game_id=game_id,
            version=next_version,
            content_hash=result.content_hash,
            canonical_json=body.canonical_json,
            engine_version=result.engine_version,
            validation_passed=result.report.passed,
            validation_findings=findings_payload,
        )
        created = await self.versions.add(version)
        audit = AuditService.from_session(self.versions._session)
        await audit.record(
            action="game_version.create",
            entity_type="game_version",
            entity_id=created.id,
            user_id=auth.user.id,
            organization_id=game.organization_id,
            metadata={"gameId": str(game_id), "version": created.version},
        )
        return CreateGameVersionResponse(
            id=created.id,
            version=created.version,
            content_hash=created.content_hash,
            engine_version=created.engine_version,
            validation_summary=_validation_summary_for(created),
        )

    async def list_versions(
        self,
        auth: AuthContext,
        game_id: uuid.UUID,
    ) -> list[GameVersionSummaryResponse]:
        await self._require_game(auth, game_id)
        versions = await self.versions.list_by_game_id(game_id)
        return [_to_summary(version) for version in versions]

    async def get_version(
        self,
        auth: AuthContext,
        game_id: uuid.UUID,
        version_id: uuid.UUID,
    ) -> GameVersionDetailResponse:
        await self._require_game(auth, game_id)
        version = await self.versions.get_by_id_for_game(version_id, game_id)
        if version is None:
            raise GameVersionNotFoundError(
                game_id=str(game_id),
                version_id=str(version_id),
            )
        return _to_detail(version)

    async def _require_game(self, auth: AuthContext, game_id: uuid.UUID):
        game = await self.games.get_by_id_for_organizations(
            game_id,
            auth.organization_ids,
        )
        if game is None:
            raise GameNotFoundError(game_id=str(game_id))
        auth.require_membership(game.organization_id)
        return game
