from uuid import UUID

from domain.enums import UserRole
from infrastructure.api.schemas import CamelModel


class UpdateUserModelDto(CamelModel):
    is_active: bool


class UserModel(CamelModel):
    user_id: UUID
    org_id: UUID
    email: str
    role: UserRole
    is_active: bool
