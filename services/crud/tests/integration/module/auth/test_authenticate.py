import pytest
from application.auth.dtos import AuthenticateUserDto, RegisterUserDto
from application.auth.exceptions import InvalidCredentialsException
from application.auth.services import AuthService
from domain.auth.entities import User


@pytest.fixture()
def authenticate_user_dto(register_user_dto: RegisterUserDto) -> AuthenticateUserDto:
    return AuthenticateUserDto(
        email=register_user_dto.email, password=register_user_dto.password
    )


@pytest.mark.asyncio
async def test_auth_service_authenticate_happy_path(
    authenticate_user_dto: AuthenticateUserDto,
    auth_service: AuthService,
    created_user: User,
):
    authenticated, _ = await auth_service.authenticate(authenticate_user_dto)

    assert authenticated == created_user


@pytest.mark.asyncio
async def test_auth_service_authenticate_wrong_password(
    authenticate_user_dto: AuthenticateUserDto,
    auth_service: AuthService,
    created_user: User,
):
    authenticate_user_dto.password = "<PASSWORD>"

    with pytest.raises(InvalidCredentialsException):
        await auth_service.authenticate(authenticate_user_dto)


@pytest.mark.asyncio
async def test_auth_service_authenticate_wrong_email(
    authenticate_user_dto: AuthenticateUserDto,
    auth_service: AuthService,
    created_user: User,
):
    authenticate_user_dto.email = "<EMAIL>"

    with pytest.raises(InvalidCredentialsException):
        await auth_service.authenticate(authenticate_user_dto)
