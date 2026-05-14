from datetime import datetime

from pydantic import BaseModel, field_validator

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


def _reject_super_role(role: RoleEnum) -> RoleEnum:
    if role.value.startswith("SUPER"):
        raise ValueError("SUPER_* roles cannot be assigned at the organization level")
    return role


class CreateRoleRequest(BaseModel):
    user_id: int
    organization_id: int
    role: RoleEnum

    @field_validator("role")
    @classmethod
    def role_not_super(cls, v: RoleEnum) -> RoleEnum:
        return _reject_super_role(v)


class UpdateRoleRequest(BaseModel):
    role: RoleEnum

    @field_validator("role")
    @classmethod
    def role_not_super(cls, v: RoleEnum) -> RoleEnum:
        return _reject_super_role(v)
