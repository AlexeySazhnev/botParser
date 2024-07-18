from __future__ import annotations

from typing import Union, Optional, Type
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.database.errors import CommitError, RollbackError
from src.database.core.connection import SessionFactoryType




class TransactionManager:

    __slots__ = (
        "session",
        "_transaction",
    )

    def __init__(self, session_or_factory: Union[AsyncSession, SessionFactoryType]) -> None:
        
        if isinstance(session_or_factory, async_sessionmaker):
            self.session = session_or_factory()
        else:
            self.session = session_or_factory
        
        self._transaction: Optional[AsyncSessionTransaction] = None

    async def __aenter__(self) -> TransactionManager:
        await self.make_transaction()
        return self
    
    async def __aexit__(
            self, 
            exc_type: Optional[Type[BaseException]], 
            exc_value: Optional[BaseException], 
            traceback: Optional[TracebackType]
    ) -> None:
        if self._transaction:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        
        await self.close_transaction()

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            raise CommitError from e
        
    async def rollback(self) -> None:
        try:
            await self.session.rollback()
        except SQLAlchemyError as e:
            raise RollbackError from e
        
    async def make_transaction(self) -> None:
        if not self.session.in_transaction() and self.session.is_active:
            self._transaction = await self.session.begin()

    async def close_transaction(self) -> None:
        if self.session.is_active:
            await self.session.close()
    
