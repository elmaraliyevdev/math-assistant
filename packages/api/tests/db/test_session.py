"""Session factory tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.base import Base
from app.db.session import create_engine, create_session_factory, get_session


@pytest.mark.asyncio
async def test_create_engine_with_custom_url() -> None:
    engine = create_engine(
        Settings(database_url="sqlite+aiosqlite:///:memory:"),
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_session_factory_and_get_session() -> None:
    engine = create_engine(Settings(database_url="sqlite+aiosqlite:///:memory:"))
    session_factory = create_session_factory(engine)

    sessions: list[AsyncSession] = []
    async for session in get_session(session_factory):
        sessions.append(session)
        assert isinstance(session, AsyncSession)
    assert len(sessions) == 1

    await engine.dispose()
