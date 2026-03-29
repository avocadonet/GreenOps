from uuid import uuid4

import pytest
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException
from domain.auth.repositories import UsersRepository


@pytest.mark.asyncio
async def test_user_repo_delete_happy_path(
    created_user: User, repo: UsersRepository
):
    deleted = await repo.delete(created_user)

    assert deleted == created_user


@pytest.mark.asyncio
async def test_user_repo_delete_wrong_user(
    created_user: User, repo: UsersRepository
):
    created_user.user_id = uuid4()
    with pytest.raises(UserNotFoundException):
        await repo.delete(created_user)
