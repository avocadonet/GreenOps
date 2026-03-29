from uuid import uuid4

import pytest
from application.users.services import UsersService
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException


@pytest.mark.asyncio
async def test_user_service_read_happy_path(
    created_user: User, users_service: UsersService
):
    saved = await users_service.read(created_user.user_id, created_user)

    assert saved == created_user


@pytest.mark.asyncio
async def test_user_service_read_without_permissions(
    created_user: User, users_service: UsersService
):
    wrong_user_id = uuid4()

    with pytest.raises(UserNotFoundException):
        await users_service.read(wrong_user_id, created_user)


@pytest.mark.asyncio
async def test_user_service_read_by_email_happy_path(
    created_user: User, users_service: UsersService
):
    saved = await users_service.read_by_email(created_user.email)

    assert saved == created_user


@pytest.mark.asyncio
async def test_user_service_read_by_email_wrong_email(
    created_user: User, users_service: UsersService
):
    wrong_email = "<EMAIL>"

    with pytest.raises(UserNotFoundException):
        await users_service.read_by_email(wrong_email)
