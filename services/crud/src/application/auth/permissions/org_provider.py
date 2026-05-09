from application.auth.enums import PermissionsEnum
from application.auth.permissions.provider import PermissionProvider
from application.auth.permissions.role_map import ROLE_PERMISSIONS
from domain.users.entities import UserOrganizationRole


class OrgPermissionProvider(PermissionProvider):
    def __init__(self, role: UserOrganizationRole) -> None:
        self._role = role

    def __call__(self) -> set[PermissionsEnum]:
        return ROLE_PERMISSIONS.get(self._role.role, set())
