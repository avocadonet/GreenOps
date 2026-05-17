from enum import Enum


class UserNotificationSendToEnum(Enum):
    EMAIL = "EMAIL"
    TELEGRAM = "TELEGRAM"


class RoleEnum(Enum):
    SUPER_USER = "SUPER_USER"
    SUPER_OWNER = "SUPER_OWNER"
    SUPER_ADMIN = "SUPER_ADMIN"
    SUPER_REDACTOR = "SUPER_REDACTOR"
    ORGANIZATION_OWNER = "ORGANIZATION_OWNER"
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    REDACTOR = "REDACTOR"
    PUBLIC = "PUBLIC"


roles_priorities = [
    RoleEnum.SUPER_USER,
    RoleEnum.SUPER_OWNER,
    RoleEnum.SUPER_ADMIN,
    RoleEnum.SUPER_REDACTOR,
    RoleEnum.ORGANIZATION_OWNER,
    RoleEnum.OWNER,
    RoleEnum.ADMIN,
    RoleEnum.REDACTOR,
    RoleEnum.PUBLIC,
]

roles_delete_priorities = [
    RoleEnum.SUPER_USER,
    RoleEnum.SUPER_OWNER,
    RoleEnum.SUPER_ADMIN,
    RoleEnum.SUPER_REDACTOR,
    RoleEnum.ORGANIZATION_OWNER,
    RoleEnum.OWNER,
    RoleEnum.ADMIN,
    RoleEnum.REDACTOR,
    RoleEnum.PUBLIC,
]

roles_priorities_table = {role: i for i, role in enumerate(roles_priorities)}
roles_delete_priorities_table = {
    role: i for i, role in enumerate(roles_delete_priorities)
}
