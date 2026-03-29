from copy import copy
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
from application.transaction import TransactionsGateway
from application.users.services import UsersService
from domain.exceptions import EntityAccessDeniedException
from domain.auth.entities import User


@pytest.mark.asyncio
async def test_user_service_read_happy_path(created_user: User):
    repo = AsyncMock()
    repo.read.return_value = created_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    await users_service.read(created_user.user_id, created_user)

    tx.__aenter__.assert_not_awaited()
    tx.__aexit__.assert_not_awaited()
    repo.read.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_service_read_without_permissions(created_user: User):
    some_user = copy(created_user)
    some_user.user_id = uuid4()

    repo = AsyncMock()
    repo.read.return_value = some_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    with pytest.raises(EntityAccessDeniedException):
        await users_service.read(some_user.user_id, created_user)

    tx.__aenter__.assert_not_awaited()
    tx.__aexit__.assert_not_awaited()
    repo.read.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_service_read_by_email_happy_path(created_user: User):
    repo = AsyncMock()
    repo.read_by_email.return_value = created_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    await users_service.read_by_email(created_user.email)

    tx.__aenter__.assert_not_awaited()
    tx.__aexit__.assert_not_awaited()
    repo.read_by_email.assert_awaited_once()
