from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

SessionFactoryType = async_sessionmaker[AsyncSession]


def create_sa_engine(url: str, **kw: Any) -> AsyncEngine:
    return create_async_engine(url, **kw)


def create_sa_session_factory(engine: AsyncEngine) -> SessionFactoryType:
    return async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


def create_sa_session(session_factory: SessionFactoryType) -> AsyncSession:
    return session_factory()
