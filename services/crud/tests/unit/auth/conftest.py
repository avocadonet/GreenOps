import pytest
from application.auth.dtos import RegisterUserDto
from uuid import uuid4


@pytest.fixture()
def register_user_dto() -> RegisterUserDto:
    return RegisterUserDto(email="email", password="password", org_id=uuid4())
