import datetime as dt
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
from uuid import UUID

import pytest


class RoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class User:
    id: UUID
    email: str
    fullname: str
    is_active: bool
    created_at: field(default_factory=lambda: dt.datetime.now(dt.UTC))

    salt: str
    hashed_password: str
    role: RoleEnum

    def __eq__(self, other):
        return (
            self.id == getattr(other, "id", None)
            and self.email == getattr(other, "email", None)
            and self.fullname == getattr(other, "fullname", None)
            and self.is_active == getattr(other, "is_active", None)
            and self.salt == getattr(other, "salt", None)
            and self.hashed_password == getattr(other, "hashed_password", None)
            and self.role == getattr(other, "role", None)
        )


@pytest.fixture
def make_user() -> Callable[[], User]:
    def factory():
        user_id = uuid.uuid4()
        return User(
            id=user_id,
            email=f"{user_id}@ex.com",
            fullname=f"User {user_id}",
            is_active=True,
            created_at=dt.datetime(2024, 1, 1),
            salt="s",
            hashed_password="h",
            role=RoleEnum.USER,
        )

    return factory


@pytest.fixture
def user(make_user):
    return make_user()
