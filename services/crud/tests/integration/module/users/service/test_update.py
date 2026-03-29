from copy import copy
from uuid import uuid4

import pytest
from application.users.services import UsersService
from domain.exceptions import EntityAccessDeniedException
from domain.auth.dtos import UpdateUserDto
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException


@pytest.fixture(scope="function")
def update_user_dto(created_user: User) -> UpdateUserDto:
    return UpdateUserDto(user_id=created_user.user_id, is_active=False)


@pytest.mark.asyncio
async def test_user_service_update_happy_path(
    created_user: User, users_service: UsersService, update_user_dto: UpdateUserDto
):
    updated = await users_service.update(update_user_dto, created_user)

    assert updated.is_active == update_user_dto.is_active


@pytest.mark.asyncio
async def test_user_service_update_wrong_user(
    created_user: User, users_service: UsersService, update_user_dto: UpdateUserDto
):
    update_user_dto = UpdateUserDto(user_id=uuid4(), is_active=False)

    with pytest.raises(UserNotFoundException):
        await users_service.update(update_user_dto, created_user)


@pytest.mark.asyncio
async def test_user_service_update_without_permissions(
    created_user: User, users_service: UsersService, update_user_dto: UpdateUserDto
):
    actor = copy(created_user)
    actor.user_id = uuid4()

    with pytest.raises(EntityAccessDeniedException):
        await users_service.update(update_user_dto, actor)
