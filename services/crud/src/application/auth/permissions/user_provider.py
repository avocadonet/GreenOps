from application.auth.enums import PermissionsEnum
from application.auth.permissions.provider import PermissionProvider
from application.auth.permissions.role_map import ROLE_PERMISSIONS
from domain.users.entities import User


class UserPermissionProvider(PermissionProvider):
    def __init__(self, user: User) -> None:
        self._user = user

    def __call__(self) -> set[PermissionsEnum]:
        return ROLE_PERMISSIONS.get(self._user.role, set())
