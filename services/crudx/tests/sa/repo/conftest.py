from dataclasses import dataclass
from typing import Callable
from uuid import UUID

import pytest_asyncio
from crudx.sa import decorators as ad
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    SqlAlchemyRepository,
    provide,
)
from crudx.sa.utils import from_dto, from_query
from sqlalchemy import select
from tests.conftest import User
from tests.sa.conftest import UserModel


@pytest_asyncio.fixture
def repo(mappers, session):
    create_mapper, entity_mapper, model_mapper = mappers
    config = SqlalchemyConfig[None, User, UserModel](
        create_mapper=entity_mapper,
        entity_mapper=entity_mapper,
        model_mapper=model_mapper,
        model=UserModel,
    )

    @dataclass
    class UserReadDto:
        id: UUID
        email: str

    @provide(config=config)
    class TestRepo(ErrorHandlingSqlAlchemyRepository[None, User, UserModel]):
        def __init__(self, session_):
            self.gateway = AsyncSqlAlchemyGateway[UserModel](
                session_, sa_model=UserModel, id_attr=("id", "email")
            )

        @ad.create()
        async def create(self, entity: User) -> User: ...

        @ad.read()
        async def read(self, id: UUID, email: str) -> User: ...

        @ad.read
        async def read_from_dto(self, id: UUID, email: str) -> User:
            return from_dto(UserReadDto(id, email))

        @ad.read
        async def read_from_query(self, id: UUID, email: str) -> User:
            return from_query(select(UserModel).filter_by(id=id, email=email))

        @ad.read_all()
        async def read_all(self, id: UUID, email: str):
            return select(UserModel).filter_by(id=id, email=email)

        @ad.update
        async def update(self, entity: User): ...

        @ad.delete
        async def delete(self, entity: User): ...

        async def truncate(self): ...

    return TestRepo(session_=session)


@pytest_asyncio.fixture()
async def user(repo, make_user: Callable[[], User]) -> User:
    return await repo.create(make_user())
