"""Generic async repository base."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


class BaseRepository[ModelT: Base]:
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def get_by_id(self, entity_id: uuid.UUID) -> ModelT | None:
        return await self._session.get(self._model, entity_id)

    async def list_all(self) -> list[ModelT]:
        result = await self._session.scalars(select(self._model))
        return list(result.all())

    async def add(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        await self._session.flush()
        try:
            await self._session.refresh(
                entity,
                attribute_names=[column.name for column in entity.__table__.columns],
            )
        except InvalidRequestError:
            pass
        return entity

    async def save(self, entity: ModelT) -> ModelT:
        await self._session.flush()
        try:
            await self._session.refresh(
                entity,
                attribute_names=[column.name for column in entity.__table__.columns],
            )
        except InvalidRequestError:
            pass
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self._session.delete(entity)
        await self._session.flush()
