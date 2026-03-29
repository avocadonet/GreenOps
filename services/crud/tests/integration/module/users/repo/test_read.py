from uuid import uuid4

import pytest
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException
from domain.auth.repositories import UsersRepository


@pytest.mark.asyncio
async def test_user_repo_read_happy_path(created_user: User, repo: UsersRepository):
    saved = await repo.read(created_user.user_id)

    assert saved == created_user


@pytest.mark.asyncio
async def test_user_repo_read_not_found(repo: UsersRepository):
    wrong_user_id = uuid4()

    with pytest.raises(UserNotFoundException):
        await repo.read(wrong_user_id)


@pytest.mark.asyncio
async def test_user_repo_read_by_email_happy_path(
    created_user: User, repo: UsersRepository
):
    saved = await repo.read_by_email(created_user.email)

    assert saved == created_user


@pytest.mark.asyncio
async def test_user_repo_read_by_email_wrong_email(repo: UsersRepository):
    wrong_email = "<EMAIL>"

    with pytest.raises(UserNotFoundException):
        await repo.read_by_email(wrong_email)
