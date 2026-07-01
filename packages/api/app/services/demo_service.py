"""Demo workspace service."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.game import Game
from app.db.models.game_version import GameVersion
from app.db.models.organization_member import OrganizationRole
from app.db.repositories.game_repository import GameRepository
from app.db.repositories.game_version_repository import GameVersionRepository
from app.db.repositories.organization_member_repository import OrganizationMemberRepository
from app.db.repositories.organization_repository import OrganizationRepository
from app.db.repositories.simulation_repository import SimulationRepository
from app.exceptions.domain import DemoWorkspaceNotFoundError, ForbiddenError
from app.schemas.demo import DemoGameSummary, DemoOverviewResponse, DuplicateDemoResponse


@dataclass(frozen=True, slots=True)
class DemoService:
    organizations: OrganizationRepository
    games: GameRepository
    versions: GameVersionRepository
    simulations: SimulationRepository
    members: OrganizationMemberRepository

    @classmethod
    def from_session(cls, session: AsyncSession) -> DemoService:
        return cls(
            organizations=OrganizationRepository(session),
            games=GameRepository(session),
            versions=GameVersionRepository(session),
            simulations=SimulationRepository(session),
            members=OrganizationMemberRepository(session),
        )

    async def get_demo_organization(self):
        from app.db.models.organization import Organization

        result = await self.organizations._session.scalars(
            select(Organization).where(Organization.is_demo.is_(True)).limit(1),
        )
        return result.first()

    async def get_overview(self, auth: AuthContext) -> DemoOverviewResponse:
        demo_org = await self.get_demo_organization()
        if demo_org is None:
            return DemoOverviewResponse(configured=False)

        games = await self._list_games_for_org(demo_org.id)
        game_summaries: list[DemoGameSummary] = []
        total_versions = 0
        total_simulations = 0

        for game in games:
            version_count = await self._count_versions(game.id)
            simulation_count = await self._count_simulations_for_game(game.id)
            total_versions += version_count
            total_simulations += simulation_count
            game_summaries.append(
                DemoGameSummary(
                    id=game.id,
                    name=game.name,
                    version_count=version_count,
                    simulation_count=simulation_count,
                ),
            )

        return DemoOverviewResponse(
            organization_id=demo_org.id,
            organization_name=demo_org.name,
            game_count=len(games),
            version_count=total_versions,
            simulation_count=total_simulations,
            games=game_summaries,
        )

    async def duplicate_to_workspace(self, auth: AuthContext) -> DuplicateDemoResponse:
        demo_org = await self.get_demo_organization()
        if demo_org is None:
            raise DemoWorkspaceNotFoundError()

        target_org_id = self._resolve_target_org(auth)
        auth.require_role(target_org_id, OrganizationRole.DEVELOPER)

        demo_games = await self._list_games_for_org(demo_org.id)
        copied = 0

        for demo_game in demo_games:
            existing = await self.games.get_by_name_in_organization(
                name=demo_game.name,
                organization_id=target_org_id,
            )
            if existing is not None:
                continue

            new_game = Game(
                organization_id=target_org_id,
                name=demo_game.name,
                description=demo_game.description,
            )
            created_game = await self.games.add(new_game)

            demo_versions = await self.versions.list_by_game_id(demo_game.id)
            for demo_version in demo_versions:
                version = GameVersion(
                    game_id=created_game.id,
                    organization_id=target_org_id,
                    version=demo_version.version,
                    content_hash=demo_version.content_hash,
                    canonical_json=copy.deepcopy(demo_version.canonical_json),
                    engine_version=demo_version.engine_version,
                    validation_passed=demo_version.validation_passed,
                    validation_findings=copy.deepcopy(demo_version.validation_findings),
                )
                await self.versions.add(version)
            copied += 1

        return DuplicateDemoResponse(
            games_copied=copied,
            organization_id=target_org_id,
        )

    def _resolve_target_org(self, auth: AuthContext) -> uuid.UUID:
        if not auth.organization_ids:
            raise ForbiddenError(message="no organization available")
        return auth.organization_ids[0]

    async def _list_games_for_org(self, organization_id: uuid.UUID) -> list[Game]:
        result = await self.games._session.scalars(
            select(Game)
            .where(Game.organization_id == organization_id)
            .order_by(Game.name.asc()),
        )
        return list(result.all())

    async def _count_versions(self, game_id: uuid.UUID) -> int:
        result = await self.versions._session.scalar(
            select(func.count())
            .select_from(GameVersion)
            .where(GameVersion.game_id == game_id),
        )
        return int(result or 0)

    async def _count_simulations_for_game(self, game_id: uuid.UUID) -> int:
        from app.db.models.simulation import Simulation

        result = await self.simulations._session.scalar(
            select(func.count())
            .select_from(Simulation)
            .join(GameVersion, Simulation.game_version_id == GameVersion.id)
            .where(GameVersion.game_id == game_id),
        )
        return int(result or 0)

    def extended_organization_ids(self, auth: AuthContext) -> list[uuid.UUID]:
        """Include demo org for read access when listing games."""
        ids = list(auth.organization_ids)
        return ids
