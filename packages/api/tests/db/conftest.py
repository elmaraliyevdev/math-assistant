"""Database test fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.auth.context import AuthContext
from app.db.base import Base
from app.db.models import (
    Game,
    GameVersion,
    Organization,
    OrganizationMember,
    OrganizationRole,
    Simulation,
    SimulationResult,
    User,
)
from app.db.repositories import (
    GameRepository,
    GameVersionRepository,
    OrganizationMemberRepository,
    OrganizationRepository,
    SimulationRepository,
    SimulationResultRepository,
    UserRepository,
)


@pytest_asyncio.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def session_factory(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
def game_repo(db_session: AsyncSession) -> GameRepository:
    return GameRepository(db_session)


@pytest.fixture
def game_version_repo(db_session: AsyncSession) -> GameVersionRepository:
    return GameVersionRepository(db_session)


@pytest.fixture
def simulation_repo(db_session: AsyncSession) -> SimulationRepository:
    return SimulationRepository(db_session)


@pytest.fixture
def simulation_result_repo(db_session: AsyncSession) -> SimulationResultRepository:
    return SimulationResultRepository(db_session)


@pytest.fixture
def organization_repo(db_session: AsyncSession) -> OrganizationRepository:
    return OrganizationRepository(db_session)


@pytest.fixture
def user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)


@pytest.fixture
def organization_member_repo(db_session: AsyncSession) -> OrganizationMemberRepository:
    return OrganizationMemberRepository(db_session)


@pytest.fixture
def sample_organization() -> Organization:
    return Organization(name="Test Organization", slug="test-organization")


@pytest.fixture
def sample_user() -> User:
    from app.security.passwords import hash_password

    return User(
        email="test@example.com",
        password_hash=hash_password("secure-password"),
        full_name="Test User",
        is_active=True,
    )


@pytest.fixture
def sample_game(sample_organization: Organization) -> Game:
    return Game(
        organization=sample_organization,
        name="Golden Base 5x3",
        description="Test game",
    )


@pytest.fixture
def sample_canonical_json() -> dict[str, str]:
    return {"schemaVersion": "1.0.0", "metadata": {"title": "Test"}}


@pytest.fixture
def sample_game_version(
    sample_game: Game,
    sample_canonical_json: dict[str, str],
) -> GameVersion:
    return GameVersion(
        game=sample_game,
        version=1,
        content_hash="a" * 64,
        canonical_json=sample_canonical_json,
        engine_version="runtime-core@1.8.0",
    )


@pytest.fixture
def sample_simulation(sample_game_version: GameVersion) -> Simulation:
    return Simulation(
        game_version=sample_game_version,
        spin_count=1000,
        completed_spin_count=0,
        bet_minor_units=100,
        event_log_mode="none",
    )


@pytest.fixture
def sample_simulation_result(sample_simulation: Simulation) -> SimulationResult:
    return SimulationResult(
        simulation=sample_simulation,
        total_bet_minor_units=100_000,
        total_win_minor_units=96_000,
        uncapped_win_minor_units=96_000,
        rtp=0.96,
        volatility=3.2,
        hit_frequency=0.28,
        mathematics_report={
            "rtp": {
                "rtp": 0.96,
                "uncappedRtp": 0.96,
                "totalBetMinorUnits": 100_000,
                "totalWinMinorUnits": 96_000,
                "uncappedWinMinorUnits": 96_000,
            },
            "hitFrequency": {
                "hitFrequency": 0.28,
                "winningSpinCount": 280,
                "losingSpinCount": 720,
            },
            "featureFrequencies": [],
            "jackpotFrequencies": [],
            "volatility": {
                "meanWinMinorUnits": 96.0,
                "variance": 100.0,
                "standardDeviation": 3.2,
                "coefficientOfVariation": 0.5,
            },
            "exposure": {
                "truncationRate": 0.0,
                "totalTruncatedMinorUnits": 0,
                "cappedRtp": 0.96,
                "uncappedRtp": 0.96,
                "rtpDifference": 0.0,
            },
            "confidenceInterval": {
                "lowerBound": 0.9,
                "upperBound": 1.0,
                "confidenceLevel": 0.95,
            },
            "winDistribution": {
                "totalSpins": 1000,
                "betMinorUnitsPerSpin": 100,
                "buckets": [],
            },
            "rtpDecomposition": {
                "totalRtp": 0.96,
                "categories": [],
            },
            "rtpValidation": {
                "targetRtp": 96.0,
                "actualRtp": 96.0,
                "difference": 0.0,
                "tolerance": 0.1,
                "withinTolerance": True,
            },
            "rtpDecompositionChart": {
                "BASE": 100.0,
                "FREE_SPINS": 0.0,
                "HOLD_AND_WIN": 0.0,
                "JACKPOT": 0.0,
                "totalRtp": 96.0,
            },
            "spinCount": 1000,
            "engineVersion": "runtime-core@1.8.0",
        },
    )


@pytest_asyncio.fixture
async def persisted_auth(
    organization_repo: OrganizationRepository,
    user_repo: UserRepository,
    organization_member_repo: OrganizationMemberRepository,
    sample_organization: Organization,
    sample_user: User,
) -> AuthContext:
    organization = await organization_repo.add(sample_organization)
    user = await user_repo.add(sample_user)
    await organization_member_repo.add(
        OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role=OrganizationRole.OWNER,
        ),
    )
    return AuthContext(
        user=user,
        memberships={organization.id: OrganizationRole.OWNER},
    )


@pytest.fixture
def auth_context(persisted_auth: AuthContext) -> AuthContext:
    return persisted_auth
