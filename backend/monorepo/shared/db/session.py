from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing_extensions import AsyncGenerator


def make_session_factory(database_url: str):
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"statement_cache_size": 0},
    )
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    return engine, session_factory


def make_get_db(session_factory):
    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    return get_db
