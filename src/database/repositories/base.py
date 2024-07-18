import abc
from typing import Generic, Type

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.crud import CRUDRepository, TypeModel



class BaseRepository(Generic[TypeModel]):

    __slots__ = (
        "_session",
        "_crud",
    )

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = CRUDRepository(self.model, session)

    @property
    @abc.abstractmethod
    def model(self) -> Type[TypeModel]:
        raise NotImplementedError("Please implement me!")
        