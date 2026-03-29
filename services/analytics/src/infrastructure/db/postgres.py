from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


def get_engine(url: str) -> AsyncEngine:
    return create_async_engine(url, pool_size=3)


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False)
