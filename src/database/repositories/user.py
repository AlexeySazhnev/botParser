from typing import List, Optional, Type

from sqlalchemy import select
from typing_extensions import Unpack

from src.database.models import User
from src.database.repositories.base import BaseRepository
from src.database.types import CreateUserType, OrderByType, UpdateUserType


class UserRepository(BaseRepository[User]):
    __slots__ = ()

    @property
    def model(self) -> Type[User]:
        return User

    async def create(self, **data: Unpack[CreateUserType]) -> Optional[User]:
        return await self._crud.create(**data)

    async def get(self, user_id: int) -> Optional[User]:
        return await self._crud.select(self.model.id == user_id)

    async def get_many(
        self,
        order_by: OrderByType = "ASC",
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[User]:
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
        self, user_id: int, **data: Unpack[UpdateUserType]
    ) -> Optional[User]: 
        result = await self._crud.update(self.model.id == user_id, **data)

        return result[0] if result else None

    async def delete(self, user_id: int) -> Optional[User]:
        result = await self._crud.delete(self.model.id == user_id)

        return result[0] if result else None

    async def exists(self, user_id: int) -> bool:
        return await self._crud.exists(self.model.id == user_id)
