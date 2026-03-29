from unittest.mock import AsyncMock, Mock

import pytest
from application.auth.dtos import AuthenticateUserDto, RegisterUserDto
from application.auth.exceptions import InvalidCredentialsException
from application.auth.services import AuthService
from domain.auth.entities import User
from domain.auth.exceptions import UserNotFoundException


@pytest.fixture()
def authenticate_user_dto(register_user_dto: RegisterUserDto) -> AuthenticateUserDto:
    return AuthenticateUserDto(
        email=register_user_dto.email, password=register_user_dto.password
    )


@pytest.mark.asyncio
async def test_auth_service_authenticate_happy_path(
    authenticate_user_dto: AuthenticateUserDto, created_user: User
):
    security_gateway = Mock()
    tokens_gateway = AsyncMock()
    users_service = AsyncMock()
    users_service.read_by_email.return_value = created_user
    auth_service = AuthService(security_gateway, tokens_gateway, users_service)

    await auth_service.authenticate(authenticate_user_dto)

    security_gateway.verify_passwords.assert_called_once()
    users_service.read_by_email.assert_awaited_once()
    tokens_gateway.create_token_pair.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_service_authenticate_wrong_password(
    authenticate_user_dto: AuthenticateUserDto,
    created_user: User,
    register_user_dto: RegisterUserDto,
):
    security_gateway = Mock()
    security_gateway.verify_passwords.return_value = False
    tokens_gateway = AsyncMock()
    users_service = AsyncMock()
    users_service.read_by_email.return_value = created_user
    auth_service = AuthService(security_gateway, tokens_gateway, users_service)

    with pytest.raises(InvalidCredentialsException):
        await auth_service.authenticate(authenticate_user_dto)

    security_gateway.verify_passwords.assert_called_once()
    users_service.read_by_email.assert_awaited_once()
    tokens_gateway.create_token_pair.assert_not_awaited()


@pytest.mark.asyncio
async def test_auth_service_authenticate_wrong_email(
    register_user_dto: RegisterUserDto,
    authenticate_user_dto: AuthenticateUserDto,
):
    def mock_read_by_email(*_, **__):
        raise UserNotFoundException

    security_gateway = Mock()
    tokens_gateway = AsyncMock()
    users_service = AsyncMock()
    users_service.read_by_email.side_effect = mock_read_by_email
    auth_service = AuthService(security_gateway, tokens_gateway, users_service)

    with pytest.raises(InvalidCredentialsException):
        await auth_service.authenticate(authenticate_user_dto)

    security_gateway.verify_passwords.assert_not_called()
    users_service.read_by_email.assert_awaited_once()
    tokens_gateway.create_token_pair.assert_not_awaited()
