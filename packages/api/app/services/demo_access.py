"""Shared demo workspace read access helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.context import AuthContext
from app.db.models.organization import Organization


async def get_demo_organization_id(session: AsyncSession) -> uuid.UUID | None:
    result = await session.scalars(
        select(Organization.id).where(Organization.is_demo.is_(True)).limit(1),
    )
    return result.first()


async def readable_organization_ids(
    session: AsyncSession,
    auth: AuthContext,
) -> list[uuid.UUID]:
    ids = list(auth.organization_ids)
    demo_id = await get_demo_organization_id(session)
    if demo_id is not None and demo_id not in ids:
        ids.append(demo_id)
    return ids


def is_demo_organization(game_organization_id: uuid.UUID, demo_org_id: uuid.UUID | None) -> bool:
    return demo_org_id is not None and game_organization_id == demo_org_id
