from typing import Callable

import pytest
from crudx.sa.gateway import AsyncSqlAlchemyGateway
from tests.conftest import User
from tests.sa.conftest import UserModel


@pytest.mark.asyncio
async def test_insert_one_happy_path(
    mappers, gateway: AsyncSqlAlchemyGateway, make_user: Callable[[], User]
):
    _, entity_mapper, _ = mappers
    entity = make_user()
    model = entity_mapper(entity)
    saved = await gateway.insert_one(model)

    # assert isinstance(saved, UserModel)
    assert entity == saved


@pytest.mark.asyncio
async def test_insert_one_already_exists(
    gateway: AsyncSqlAlchemyGateway, user: UserModel
):
    await gateway.insert_one(user)
