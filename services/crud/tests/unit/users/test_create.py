from unittest.mock import AsyncMock

import pytest
from application.transaction import TransactionsGateway
from application.users.services import UsersService
from domain.auth.dtos import CreateUserDto
from domain.auth.entities import User


@pytest.mark.asyncio
async def test_user_service_create_happy_path(
    created_user: User, create_user_dto: CreateUserDto
):
    repo = AsyncMock()
    repo.create.return_value = created_user
    tx = AsyncMock(TransactionsGateway)
    users_service = UsersService(repo, tx=tx)  # type: ignore[arg-value]

    await users_service.create(create_user_dto)

    tx.__aenter__.assert_not_awaited()
    tx.__aexit__.assert_not_awaited()
    repo.create.assert_awaited_once()
