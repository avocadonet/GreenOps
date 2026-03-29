from uuid import uuid4

import pytest
from domain.auth.dtos import UpdateUserDto
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException
from domain.auth.repositories import UsersRepository


@pytest.fixture(scope="function")
def update_user_dto(created_user: User) -> UpdateUserDto:
    return UpdateUserDto(user_id=created_user.user_id, is_active=False)


@pytest.mark.asyncio
async def test_user_repo_update_happy_path(
    created_user: User, update_user_dto: UpdateUserDto, repo: UsersRepository
):
    created_user.is_active = update_user_dto.is_active
    updated = await repo.update(created_user)

    assert updated.is_active == update_user_dto.is_active


@pytest.mark.asyncio
async def test_user_repo_update_wrong_user(
    created_user: User, update_user_dto: UpdateUserDto, repo: UsersRepository
):
    created_user.user_id = uuid4()
    created_user.is_active = update_user_dto.is_active

    with pytest.raises(UserNotFoundException):
        await repo.update(created_user)
