from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.users.enums import RoleEnum, UserNotificationSendToEnum


@dataclass
class UserSettings:
    id: int
    user_id: int
    type: UserNotificationSendToEnum = UserNotificationSendToEnum.EMAIL
    calendar_uuid: UUID | None = None


@dataclass
class User:
    email: str
    fullname: str
    is_active: bool
    salt: str
    hashed_password: str

    id: int | None = None
    telegram_id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    settings: UserSettings | None = None
    role: RoleEnum = RoleEnum.PUBLIC


@dataclass
class UserOrganizationRole:
    organization_id: int
    user_id: int
    role: RoleEnum


@dataclass
class TelegramToken:
    id: UUID
    user_id: int
    is_used: bool = False
    created_at: datetime | None = None


@dataclass
class UserActivationToken:
    id: UUID
    user_id: int
    user: User
    is_used: bool = False
