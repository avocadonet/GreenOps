from uuid import uuid4

import pytest
from crudx.sa.gateway import AsyncSqlAlchemyGateway
from crudx.types import PageSpec
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from tests.conftest import User
from tests.sa.conftest import UserModel


@pytest.mark.asyncio
async def test_select_by_fields_first_happy_path(
    gateway: AsyncSqlAlchemyGateway, user: User
):
    saved = await gateway.select_by_fields_first(id=user.id, email=user.email)

    assert saved == user


@pytest.mark.asyncio
async def test_select_by_fields_first_wrong_params_value(
    gateway: AsyncSqlAlchemyGateway,
):
    wrong_user_id = uuid4()
    wrong_user_email = f"{wrong_user_id}@e.com"

    with pytest.raises(NoResultFound):
        await gateway.select_by_fields_first(id=wrong_user_id, email=wrong_user_email)


@pytest.mark.asyncio
async def test_select_by_fields_first_wrong_params_type(
    gateway: AsyncSqlAlchemyGateway,
):
    wrong_user_id = 42
    wrong_user_email = 42

    with pytest.raises(NoResultFound):
        await gateway.select_by_fields_first(id=wrong_user_id, email=wrong_user_email)


@pytest.mark.asyncio
async def test_select_by_fields_all_happy_path(
    gateway: AsyncSqlAlchemyGateway, user: User
):
    saved = await gateway.select_by_fields_all(id=user.id, email=user.email)

    assert saved == [user]


@pytest.mark.asyncio
async def test_select_by_fields_all_wrong_params_value(gateway: AsyncSqlAlchemyGateway):
    wrong_user_id = uuid4()
    wrong_user_email = f"{wrong_user_id}@e.com"
    assert (
        await gateway.select_by_fields_all(id=wrong_user_id, email=wrong_user_email)
        == []
    )


@pytest.mark.asyncio
async def test_select_by_fields_all_wrong_params_type(gateway: AsyncSqlAlchemyGateway):
    wrong_user_id = 42
    wrong_user_email = 42
    assert (
        await gateway.select_by_fields_all(id=wrong_user_id, email=wrong_user_email)
        == []
    )


@pytest.mark.asyncio
async def test_select_all_happy_path(gateway: AsyncSqlAlchemyGateway, user: User):
    dto = PageSpec(1, 1)
    saved = await gateway.select_all(dto)

    assert saved == [user]


@pytest.mark.asyncio
async def test_select_by_query_first_happy_path(
    gateway: AsyncSqlAlchemyGateway, user: UserModel
):
    stmt = select(UserModel).where(
        getattr(UserModel, "id") == user.id,
        getattr(UserModel, "is_active") == True,  # noqa
        getattr(UserModel, "email") == user.email,
    )

    saved = await gateway.select_by_query_first(stmt)
    assert saved == user


@pytest.mark.asyncio
async def test_select_by_query_all_happy_path(
    gateway: AsyncSqlAlchemyGateway, user: UserModel
):
    stmt = select(UserModel).where(
        getattr(UserModel, "id") == user.id,
        getattr(UserModel, "is_active") == True,  # noqa
        getattr(UserModel, "email") == user.email,
    )

    saved = await gateway.select_by_query_all(stmt)
    assert saved[0] == user
