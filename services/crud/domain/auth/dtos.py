from dataclasses import dataclass
from uuid import UUID

from domain.enums import UserRole


@dataclass
class ReadAllUsersDto:
    page: int
    page_size: int


@dataclass
class UpdateUserDto:
    user_id: UUID
    is_active: bool


@dataclass
class CreateUserDto:
    email: str
    hashed_password: str
    org_id: UUID
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
