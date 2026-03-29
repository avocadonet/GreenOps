from copy import copy
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
from application.transaction import TransactionsGateway
from application.users.services import UsersService
from domain.exceptions import EntityAccessDeniedException
from domain.auth.dtos import UpdateUserDto
from domain.auth.entities import User


@pytest.mark.asyncio
async def test_user_service_update_happy_path(
    created_user: User, update_user_dto: UpdateUserDto
):
    updated = copy(created_user)
    updated.is_active = update_user_dto.is_active

    repo = AsyncMock()
    repo.read.return_value = created_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    await users_service.update(update_user_dto, created_user)

    tx.__aenter__.assert_awaited_once()
    tx.__aexit__.assert_awaited_once()
    repo.read.assert_awaited_once()
    repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_service_update_without_permissions(
    created_user: User, update_user_dto: UpdateUserDto
):
    user_without_perms = copy(created_user)
    user_without_perms.user_id = uuid4()

    repo = AsyncMock()
    repo.read.return_value = created_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    with pytest.raises(EntityAccessDeniedException):
        await users_service.update(update_user_dto, user_without_perms)

    tx.__aenter__.assert_awaited_once()
    tx.__aexit__.assert_awaited_once()
    repo.read.assert_awaited_once()
    repo.update.assert_not_awaited()
