from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from application.auth.dtos import RegisterUserDto
from application.auth.exceptions import InvalidCredentialsException
from application.auth.services import AuthService
from application.auth.tokens.dtos import TokenInfoDto
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException


@pytest.fixture()
def token_info_dto(register_user_dto: RegisterUserDto) -> TokenInfoDto:
    return TokenInfoDto(
        subject=register_user_dto.email,
        user_id=uuid4(),
        expires_in=datetime.now() + timedelta(days=1),
    )


@pytest.mark.asyncio
async def test_auth_service_authorize_happy_path(
    token_info_dto: TokenInfoDto, created_user: User
):
    security_gateway = Mock()
    tokens_gateway = AsyncMock()
    users_service = AsyncMock()
    users_service.read_by_email.return_value = created_user
    auth_service = AuthService(security_gateway, tokens_gateway, users_service)

    await auth_service.authorize(token_info_dto)

    users_service.read_by_email.assert_awaited_once()
    tokens_gateway.create_token_pair.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_service_authorize_wrong_email(
    token_info_dto: TokenInfoDto, created_user: User
):
    def mock_read_by_email(*_, **__):
        raise UserNotFoundException

    security_gateway = Mock()
    tokens_gateway = AsyncMock()
    users_service = AsyncMock()
    users_service.read_by_email.side_effect = mock_read_by_email
    auth_service = AuthService(security_gateway, tokens_gateway, users_service)

    with pytest.raises(InvalidCredentialsException):
        await auth_service.authorize(token_info_dto)

    users_service.read_by_email.assert_awaited_once()
    tokens_gateway.create_token_pair.assert_not_awaited()
