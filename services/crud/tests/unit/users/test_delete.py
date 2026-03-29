from copy import copy
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
from application.transaction import TransactionsGateway
from application.users.services import UsersService
from domain.exceptions import EntityAccessDeniedException
from domain.auth.entities import User


@pytest.mark.asyncio
async def test_user_service_delete_happy_path(created_user: User):
    repo = AsyncMock()
    repo.read.return_value = created_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    await users_service.delete(created_user.user_id, created_user)

    tx.__aenter__.assert_awaited_once()
    tx.__aexit__.assert_awaited_once()
    repo.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_service_delete_without_permissions(created_user: User):
    user_without_perms = copy(created_user)
    user_without_perms.user_id = uuid4()

    repo = AsyncMock()
    repo.read.return_value = created_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    with pytest.raises(EntityAccessDeniedException):
        await users_service.delete(created_user.user_id, user_without_perms)

    tx.__aenter__.assert_awaited_once()
    tx.__aexit__.assert_awaited_once()
    repo.read.assert_awaited_once()
    repo.delete.assert_not_awaited()
