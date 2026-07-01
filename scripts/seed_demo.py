#!/usr/bin/env python3
"""Seed the demo organization with example games and completed simulations."""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "packages" / "api"
sys.path.insert(0, str(API_ROOT))

from sqlalchemy import select  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db.models.game import Game  # noqa: E402
from app.db.models.game_version import GameVersion  # noqa: E402
from app.db.models.organization import Organization  # noqa: E402
from app.db.models.organization_member import OrganizationMember, OrganizationRole  # noqa: E402
from app.db.models.simulation import Simulation, SimulationStatus  # noqa: E402
from app.db.models.simulation_result import SimulationResult  # noqa: E402
from app.db.models.user import User  # noqa: E402
from app.db.session import create_engine, create_session_factory  # noqa: E402
from app.security.passwords import hash_password  # noqa: E402
from app.schemas.games import ValidateGameSuccessResponse  # noqa: E402
from app.services.validation_service import ValidationService  # noqa: E402

DEMO_GAMES = [
    "Classic Fruits",
    "Book of Riches",
    "Hold & Win Deluxe",
    "Aztec Adventure",
    "Treasure Spins",
]

FIXTURE_PATH = REPO_ROOT / "e2e" / "fixtures" / "game.canonical.json"


def _load_canonical() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def _mock_mathematics_report(rtp: float) -> dict:
    return {
        "rtp": {"observed": rtp, "target": 96.0},
        "volatility": {"index": 4.2, "label": "medium"},
        "hitFrequency": 0.284,
        "simulationIntelligence": {
            "summary": "Demo simulation intelligence snapshot.",
            "symbolContributions": [],
            "nearMisses": [],
        },
    }


async def seed() -> None:
    settings = get_settings()
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    validation = ValidationService.create()
    canonical = _load_canonical()

    async with session_factory() as session:
        existing = await session.scalars(
            select(Organization).where(Organization.slug == "demo"),
        )
        demo_org = existing.first()
        if demo_org is None:
            demo_org = Organization(
                name="MathStudio Demo",
                slug="demo",
                is_demo=True,
            )
            session.add(demo_org)
            await session.flush()

        demo_user = await session.scalars(
            select(User).where(User.email == "demo@mathstudio.app"),
        )
        user = demo_user.first()
        if user is None:
            user = User(
                email="demo@mathstudio.app",
                password_hash=hash_password("DemoStudio1!"),
                full_name="Demo User",
                is_active=True,
                email_verified=True,
            )
            session.add(user)
            await session.flush()

        membership = await session.scalars(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == demo_org.id,
                OrganizationMember.user_id == user.id,
            ),
        )
        if membership.first() is None:
            session.add(
                OrganizationMember(
                    organization_id=demo_org.id,
                    user_id=user.id,
                    role=OrganizationRole.OWNER,
                ),
            )

        for index, game_name in enumerate(DEMO_GAMES):
            existing_game = await session.scalars(
                select(Game).where(
                    Game.organization_id == demo_org.id,
                    Game.name == game_name,
                ),
            )
            game = existing_game.first()
            if game is None:
                game = Game(
                    organization_id=demo_org.id,
                    name=game_name,
                    description=f"Example demo game — {game_name}",
                )
                session.add(game)
                await session.flush()

            existing_version = await session.scalars(
                select(GameVersion).where(GameVersion.game_id == game.id),
            )
            version = existing_version.first()
            if version is None:
                game_json = json.loads(json.dumps(canonical))
                game_json["metadata"]["title"] = game_name
                result = validation.validate(
                    canonical_json=game_json,
                    engine_version="runtime-core@1.8.0",
                )
                if not isinstance(result, ValidateGameSuccessResponse):
                    print(f"Validation failed for {game_name}", file=sys.stderr)
                    continue
                version = GameVersion(
                    game_id=game.id,
                    organization_id=demo_org.id,
                    version=1,
                    content_hash=result.content_hash,
                    canonical_json=game_json,
                    engine_version=result.engine_version,
                    validation_passed=True,
                    validation_findings=[],
                )
                session.add(version)
                await session.flush()

            existing_sim = await session.scalars(
                select(Simulation).where(Simulation.game_version_id == version.id),
            )
            simulation = existing_sim.first()
            if simulation is None:
                rtp = 95.5 + (index * 0.15)
                simulation = Simulation(
                    game_version_id=version.id,
                    status=SimulationStatus.COMPLETED,
                    spin_count=100_000,
                    completed_spin_count=100_000,
                    bet_minor_units=100,
                    event_log_mode="none",
                    master_seed=f"demo-seed-{index}".encode().hex(),
                    cancel_requested=False,
                    created_by_user_id=user.id,
                    started_at=datetime.now(tz=UTC),
                    completed_at=datetime.now(tz=UTC),
                )
                session.add(simulation)
                await session.flush()

                total_bet = simulation.spin_count * simulation.bet_minor_units
                total_win = int(total_bet * (rtp / 100.0))
                session.add(
                    SimulationResult(
                        simulation_id=simulation.id,
                        total_bet_minor_units=total_bet,
                        total_win_minor_units=total_win,
                        uncapped_win_minor_units=total_win,
                        rtp=rtp,
                        volatility=4.2,
                        hit_frequency=0.284,
                        mathematics_report=_mock_mathematics_report(rtp),
                    ),
                )

        await session.commit()
        print(f"Demo organization ready: {demo_org.id} ({demo_org.name})")
        print(f"Demo user: demo@mathstudio.app / DemoStudio1!")


if __name__ == "__main__":
    asyncio.run(seed())
