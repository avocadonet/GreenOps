from copy import copy
from uuid import uuid4

import pytest
from application.users.services import UsersService
from domain.exceptions import EntityAccessDeniedException
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException


@pytest.mark.asyncio
async def test_user_service_delete_happy_path(
    created_user: User, users_service: UsersService
):
    deleted = await users_service.delete(created_user.user_id, created_user)

    assert deleted == created_user


@pytest.mark.asyncio
async def test_user_service_delete_wrong_user(
    created_user: User, users_service: UsersService
):
    wrong_user_id = uuid4()

    with pytest.raises(UserNotFoundException):
        await users_service.delete(wrong_user_id, created_user)


@pytest.mark.asyncio
async def test_user_service_delete_without_permissions(
    created_user: User, users_service: UsersService
):
    actor = copy(created_user)
    actor.user_id = uuid4()

    with pytest.raises(EntityAccessDeniedException):
        await users_service.delete(created_user.user_id, actor)
