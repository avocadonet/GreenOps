from uuid import uuid4

import pytest
from application.auth.dtos import RegisterUserDto
from application.users.services import UsersService
from domain.auth.dtos import CreateUserDto
from domain.auth.entities import User
from domain.auth.exceptions import UserAlreadyExistsException


@pytest.mark.asyncio
async def test_user_service_create_happy_path(
    users_service: UsersService, register_user_dto: RegisterUserDto
):
    create_user_dto = CreateUserDto(
        email=register_user_dto.email,
        hashed_password="hashed",
        org_id=register_user_dto.org_id,
    )

    created = await users_service.create(create_user_dto)

    assert created.email == create_user_dto.email
    assert created.org_id == create_user_dto.org_id
    assert created.hashed_password == create_user_dto.hashed_password


@pytest.mark.asyncio
async def test_user_service_create_already_exists(
    users_service: UsersService, created_user: User
):
    create_user_dto = CreateUserDto(
        email=created_user.email,
        hashed_password=created_user.hashed_password,
        org_id=created_user.org_id,
    )

    with pytest.raises(UserAlreadyExistsException):
        await users_service.create(create_user_dto)
