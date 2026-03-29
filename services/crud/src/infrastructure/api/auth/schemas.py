from uuid import UUID

from pydantic import EmailStr

from domain.enums import UserRole
from infrastructure.api.schemas import CamelModel
from infrastructure.api.users.dtos import UserModel


class CreateUserModelDto(CamelModel):
    email: EmailStr
    password: str
    org_id: UUID
    role: UserRole = UserRole.VIEWER


class AuthenticateUserModelDto(CamelModel):
    email: EmailStr
    password: str


class UserWithTokenModelDto(CamelModel):
    access_token: str
    user: UserModel
