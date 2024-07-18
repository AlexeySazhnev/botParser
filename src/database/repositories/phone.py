from typing import List, Optional, Type

from sqlalchemy import select
from typing_extensions import Unpack

from src.database.models import Phone
from src.database.repositories.base import BaseRepository
from src.database.types import CreatePhoneType, OrderByType, UpdatePhoneType


class PhoneRepository(BaseRepository[Phone]):
    __slots__ = ()

    @property
    def model(self) -> Type[Phone]:
        return Phone

    async def create(self, **data: Unpack[CreatePhoneType]) -> Optional[Phone]:
        return await self._crud.create(**data)

    async def get(self, phone_id: int) -> Optional[Phone]:
        return await self._crud.select(self.model.id == phone_id)

    async def get_many(
        self,
        order_by: OrderByType = "ASC",
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Phone]:
        stmt = (
            select(self.model)
            .offset(offset)
            .limit(limit)
            .order_by(
                self.model.id.asc() if order_by == "ASC" else self.model.id.desc()
            )
        )
        result = (await self._session.execute(stmt)).scalars().all()

        return list(result)

    async def update(
        self, phone_url: str, **data: Unpack[UpdatePhoneType]
    ) -> Optional[Phone]:
        result = await self._crud.update(self.model.url == phone_url, **data)

        return result[0] if result else None

    async def delete(
        self,
        phone_id: Optional[int] = None,
    ) -> Optional[Phone]:
        result = await self._crud.delete(
            *([self.model.id == phone_id] if phone_id else [])
        )

        return result[0] if result else None

    async def exists(self, phone_url: str) -> bool:
        return await self._crud.exists(self.model.url == phone_url)
