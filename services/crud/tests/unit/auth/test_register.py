from unittest.mock import AsyncMock, Mock

import pytest
from application.auth.dtos import RegisterUserDto
from application.auth.services import AuthService


@pytest.mark.asyncio
async def test_auth_service_register_happy_path(register_user_dto: RegisterUserDto):
    security_gateway = Mock()
    tokens_gateway = AsyncMock()
    users_service = AsyncMock()
    auth_service = AuthService(security_gateway, tokens_gateway, users_service)

    await auth_service.register(register_user_dto)

    security_gateway.create_hashed_password.assert_called_once()
    users_service.create.assert_called_once()
