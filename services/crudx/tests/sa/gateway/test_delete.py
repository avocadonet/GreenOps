from copy import copy
from uuid import uuid4

import pytest
from crudx.sa.gateway import AsyncSqlAlchemyGateway
from sqlalchemy.exc import NoResultFound
from tests.sa.conftest import UserModel


@pytest.mark.asyncio
async def test_delete_happy_path(gateway: AsyncSqlAlchemyGateway, user: UserModel):
    result = await gateway.delete(user)

    assert user == result


@pytest.mark.asyncio
async def test_delete_non_existent(gateway: AsyncSqlAlchemyGateway, user: UserModel):
    user_copy = copy(user)
    user_copy.id = uuid4()

    with pytest.raises(NoResultFound):
        await gateway.delete(user_copy)
