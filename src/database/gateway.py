from __future__ import annotations

from types import TracebackType
from typing import Callable, Optional, Type

from src.database.core.connection import SessionFactoryType
from src.database.core.manager import TransactionManager
from src.database.repositories import  UserRepository, PhoneRepository


class DBGateway:
    __slots__ = ("manager",)

    def __init__(self, manager: TransactionManager) -> None:
        self.manager = manager

    async def __aenter__(self) -> DBGateway:
        await self.manager.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.manager.__aexit__(exc_type, exc_value, traceback)

    def user(self) -> UserRepository:
        return UserRepository(self.manager.session)
    
    def phone(self) -> PhoneRepository:
        return PhoneRepository(self.manager.session)

   

def create_gateway_lazy(
    session_factory: SessionFactoryType,
) -> Callable[[], DBGateway]:
    def create() -> DBGateway:
        return DBGateway(TransactionManager(session_factory()))

    return create
