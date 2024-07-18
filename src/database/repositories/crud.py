from __future__ import annotations

from typing import Any, Generic, Mapping, Optional, Sequence, Type, TypeVar, cast

from sqlalchemy import (
    ColumnExpressionArgument,
    CursorResult,
    exists,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.base import Base

TypeModel = TypeVar("TypeModel", bound=Base)


class CRUDRepository(Generic[TypeModel]):
    __slots__ = (
        "model",
        "_session",
    )

    def __init__(self, model: Type[TypeModel], session: AsyncSession) -> None:
        self.model = model
        self._session = session

    async def create(self, **values: Any) -> Optional[TypeModel]:
        stmt = insert(self.model).values(**values).returning(self.model)

        return (await self._session.execute(stmt)).scalars().first()

    async def create_many(
        self, data: Sequence[Mapping[str, Any]]
    ) -> Sequence[TypeModel]:
        stmt = insert(self.model).returning(self.model)

        return (await self._session.scalars(stmt, data)).all()

    async def select(
        self, *clauses: ColumnExpressionArgument[bool]
    ) -> Optional[TypeModel]:
        stmt = select(self.model).where(*clauses)
        return (await self._session.execute(stmt)).scalars().first()

    async def select_many(
        self,
        *clauses: ColumnExpressionArgument[bool],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Sequence[TypeModel]:
        stmt = select(self.model).where(*clauses).offset(offset).limit(limit)
        return (await self._session.execute(stmt)).scalars().all()

    async def update(
        self, *clauses: ColumnExpressionArgument[bool], **values: Any
    ) -> Sequence[TypeModel]:
        stmt = update(self.model).where(*clauses).values(**values).returning(self.model)
        return (await self._session.execute(stmt)).scalars().all()

    async def update_many(self, data: Sequence[Mapping[str, Any]]) -> CursorResult[Any]:
        return await self._session.execute(update(self.model), data)

    async def delete(
        self, *clauses: ColumnExpressionArgument[bool]
    ) -> Sequence[TypeModel]:
        entities = await self.select_many(*clauses)

        if not entities:
            return []

        for entity in entities:
            await self._session.delete(entity)

        return entities

    async def exists(self, *clauses: ColumnExpressionArgument[bool]) -> bool:
        stmt = exists(select(self.model).where(*clauses)).select()

        return cast(bool, await self._session.scalar(stmt))

    async def count(self, *clauses: ColumnExpressionArgument[bool]) -> int:
        stmt = select(func.count()).where(*clauses).select_from(self.model)

        return cast(int, await self._session.scalar(stmt))

    def with_query_model(self, model: Type[TypeModel]) -> CRUDRepository[TypeModel]:
        return CRUDRepository(model, self._session)