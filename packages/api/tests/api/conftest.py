"""API integration test fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db.base import Base
from app.dependencies import get_db_session
from app.main import create_app
from app.security.guards import configure_security_guards
from tests.api.auth_helpers import register_and_auth


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


@pytest.fixture(autouse=True)
def _security_guards() -> None:
    configure_security_guards(
        Settings(
            database_url="sqlite+aiosqlite:///:memory:",
            jwt_secret_key="test-secret-key",
        ),
    )


@pytest.fixture
def api_client(db_engine: AsyncEngine) -> Iterator[TestClient]:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        simulation_worker_count=1,
        jwt_secret_key="test-secret-key",
    )
    app = create_app(settings=settings)
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    app.state.session_factory = session_factory

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def db_session_factory(db_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
def auth_context(api_client: TestClient) -> dict:
    return register_and_auth(api_client)


@pytest.fixture
def auth_headers(auth_context: dict) -> dict[str, str]:
    return auth_context["headers"]
