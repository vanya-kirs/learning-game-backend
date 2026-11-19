from collections.abc import AsyncIterator
from functools import cache
from os import environ

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@cache
def session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(create_async_engine(environ["DATABASE_URL"]), expire_on_commit=False)



async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory()() as session:
        yield session
