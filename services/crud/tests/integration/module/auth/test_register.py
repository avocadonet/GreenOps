import pytest
from application.auth.dtos import RegisterUserDto
from application.auth.services import AuthService
from domain.auth.entities import User
from domain.auth.exceptions import UserAlreadyExistsException


@pytest.mark.asyncio
async def test_auth_service_register_happy_path(
    register_user_dto: RegisterUserDto, auth_service: AuthService
):
    user, token = await auth_service.register(register_user_dto)

    assert user.email == register_user_dto.email
    assert user.org_id == register_user_dto.org_id


@pytest.mark.asyncio
async def test_auth_service_register_already_exists(
    register_user_dto: RegisterUserDto, auth_service: AuthService, created_user: User
):
    with pytest.raises(UserAlreadyExistsException):
        await auth_service.register(register_user_dto)
