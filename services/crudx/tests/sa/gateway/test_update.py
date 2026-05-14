from typing import Callable

import pytest
from crudx.sa.gateway import AsyncSqlAlchemyGateway
from sqlalchemy.exc import NoResultFound
from tests.conftest import User
from tests.sa.conftest import UserModel


@pytest.mark.asyncio
async def test_update_happy_path(gateway: AsyncSqlAlchemyGateway, user: UserModel):
    user.fullname = "new fullname"
    updated = await gateway.update(user)

    # assert isinstance(updated, UserModel)
    assert updated == user


@pytest.mark.asyncio
async def test_update_non_existent(
    gateway: AsyncSqlAlchemyGateway, make_user: Callable[[], User]
):
    new_user = make_user()
    new_user.fullname = "new fullname"

    with pytest.raises(NoResultFound):
        await gateway.update(new_user)
