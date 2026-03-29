from typing import Callable

import pytest
import pytest_asyncio
from crudx.sa.gateway import AsyncSqlAlchemyGateway
from tests.conftest import User
from tests.sa.conftest import UserModel


@pytest.fixture
def gateway(session) -> AsyncSqlAlchemyGateway:
    return AsyncSqlAlchemyGateway(session, sa_model=UserModel, id_attr=("id", "email"))


@pytest_asyncio.fixture
async def user(
    mappers, gateway: AsyncSqlAlchemyGateway, make_user: Callable[[], User]
) -> UserModel:
    _, entity_mapper, _ = mappers
    entity = make_user()
    model = entity_mapper(entity)

    return await gateway.insert_one(model)


@pytest_asyncio.fixture
async def users_and_models(
    mappers, make_user: Callable[[], User]
) -> tuple[list[User], list[UserModel]]:
    _, entity_mapper, _ = mappers
    users = sorted((make_user() for _ in range(3)), key=lambda x: x.id)
    models = list(entity_mapper(entity) for entity in users)

    return users, models
