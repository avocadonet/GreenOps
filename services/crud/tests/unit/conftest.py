from uuid import uuid4

import pytest
from domain.auth.dtos import CreateUserDto
from domain.auth.entities import User
from domain.enums import UserRole


@pytest.fixture
def create_user_dto() -> CreateUserDto:
    return CreateUserDto(
        email="email@email.com",
        hashed_password="hashed",
        org_id=uuid4(),
    )


@pytest.fixture
def created_user(create_user_dto: CreateUserDto) -> User:
    return User(
        user_id=uuid4(),
        org_id=create_user_dto.org_id,
        email=create_user_dto.email,
        hashed_password=create_user_dto.hashed_password,
        role=UserRole.VIEWER,
        is_active=True,
    )
