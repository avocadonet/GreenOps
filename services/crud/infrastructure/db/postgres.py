from typing import Any

from application.transaction import TransactionsGateway
from crudx.sa.transaction import AsyncTransactionsDatabaseGateway
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

constraint_naming_conventions = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def get_engine(url: PostgresDsn, connect_args: dict[str, Any]) -> AsyncEngine:
    return create_async_engine(
        url.unicode_string(), pool_size=32, connect_args=connect_args
    )


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


class SqlalchemyTransactionsGateway(
    AsyncTransactionsDatabaseGateway, TransactionsGateway
):
    pass
