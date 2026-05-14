from domain.users.entities import UserOrganizationRole
from domain.users.enums import RoleEnum

from application.auth.enums import PermissionsEnum
from application.auth.permissions import PermissionProvider


class UserRolesPermissionProvider(PermissionProvider):
    """Провайдер прав доступа для работы с ролями пользователей.

    Определяет набор разрешений для различных ролей в системе.
    Обеспечивает проверку прав при операциях с ролями пользователей
    в рамках организационной структуры.
    """

    __maximum_perms = {
        PermissionsEnum.CAN_CREATE_ROLE,
        PermissionsEnum.CAN_DELETE_ROLE,
        PermissionsEnum.CAN_READ_ROLE,
        PermissionsEnum.CAN_UPDATE_ROLE,
    }

    __perms: dict[RoleEnum, set[PermissionsEnum]] = {
        RoleEnum.SUPER_USER: __maximum_perms,
        RoleEnum.SUPER_OWNER: __maximum_perms,
        RoleEnum.SUPER_ADMIN: __maximum_perms,
        RoleEnum.SUPER_REDACTOR: __maximum_perms,
        RoleEnum.OWNER: __maximum_perms,
        RoleEnum.ADMIN: __maximum_perms,
        RoleEnum.REDACTOR: __maximum_perms,
        RoleEnum.PUBLIC: {PermissionsEnum.CAN_READ_ROLE},
    }

    def __init__(self, organization_id: int, user_role: UserOrganizationRole):
        """Инициализирует провайдер с проверкой прав для конкретной организации и роли."""

        self.permissions = self.__get_perms(organization_id, user_role)

    def __get_perms(
        self, organization_id: int, user_role: UserOrganizationRole
    ) -> set[PermissionsEnum]:
        """Определяет набор разрешений на основе роли пользователя и принадлежности к организации."""

        result = self.__perms.get(RoleEnum.PUBLIC).copy()
        if (
            user_role.role.value.startswith("SUPER")
            or user_role.organization_id == organization_id
        ):
            result |= self.__perms.get(user_role.role)
        return result

    def __call__(self) -> set[PermissionsEnum]:
        return self.permissions
