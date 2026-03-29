from uuid import uuid4

import pytest
from domain.auth.dtos import UpdateUserDto


@pytest.fixture
def update_user_dto(created_user) -> UpdateUserDto:
    return UpdateUserDto(user_id=created_user.user_id, is_active=False)
