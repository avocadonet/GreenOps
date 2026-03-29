from dataclasses import dataclass
from uuid import UUID

from domain.enums import UserRole


@dataclass
class AuthenticateUserDto:
    email: str
    password: str


@dataclass
class RegisterUserDto:
    email: str
    password: str
    org_id: UUID
    role: UserRole = UserRole.VIEWER
