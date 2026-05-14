from datetime import datetime

from pydantic import BaseModel

from domain.users.enums import RoleEnum, UserNotificationSendToEnum


class UserResponse(BaseModel):
    id: int
    email: str
    fullname: str
    is_active: bool
    telegram_id: int | None = None
    created_at: datetime
    role: RoleEnum


class UpdateUserRequest(BaseModel):
    fullname: str | None = None
    telegram_id: int | None = None
    send_to_type: UserNotificationSendToEnum | None = None


class UserOrganizationRoleResponse(BaseModel):
    user_id: int
    organization_id: int
    role: RoleEnum


class CreateRoleRequest(BaseModel):
    user_id: int
    organization_id: int
    role: RoleEnum


class UpdateRoleRequest(BaseModel):
    role: RoleEnum
