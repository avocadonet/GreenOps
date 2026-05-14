from domain.users.entities import User, UserOrganizationRole
from domain.users.enums import RoleEnum, roles_delete_priorities_table
from domain.users.exceptions import UserAccessDenied, UserRoleNotFoundError
from domain.users.repositories import UserOrganizationRolesRepository
from domain.users.role_getter import RoleGetter

from application.auth.enums import PermissionsEnum
from application.auth.permissions import PermissionBuilder
from application.transaction import TransactionsGateway
from application.users.dtos import DeleteUserRoleDto
from application.users.permissions.user import UserRolesPermissionProvider


class UserRoleService:
    def __init__(
        self,
        repository: UserOrganizationRolesRepository,
        tx: TransactionsGateway,
        role_getter: RoleGetter,
    ):
        self._repository = repository
        self._tx = tx
        self._role_getter = role_getter

    def _can_manage(self, role: UserOrganizationRole, actor_role: UserOrganizationRole) -> bool:
        return (
            role.role != RoleEnum.OWNER or actor_role.role == RoleEnum.SUPER_USER
        ) and roles_delete_priorities_table[actor_role.role] < roles_delete_priorities_table[role.role]

    async def get(self, user_id: int, organization_id: int) -> UserOrganizationRole:
        return await self._repository.read(user_id, organization_id)

    async def list_all(self, user_id: int) -> list[UserOrganizationRole]:
        return await self._repository.read_all(user_id)

    @staticmethod
    def _reject_super(role: UserOrganizationRole) -> None:
        if role.role.value.startswith("SUPER"):
            raise UserAccessDenied

    async def create(self, role: UserOrganizationRole, actor: User) -> UserOrganizationRole:
        self._reject_super(role)
        async with self._tx:
            actor_role = await self._role_getter(actor, role.organization_id)
            PermissionBuilder().providers(
                UserRolesPermissionProvider(role.organization_id, actor_role)
            ).add(PermissionsEnum.CAN_CREATE_ROLE).apply()
            if self._can_manage(role, actor_role):
                async with self._tx:
                    role_or_none = await self._repository.read_or_none(role.user_id, role.organization_id)
                    if role_or_none is not None:
                        return await self.update(role, actor)
                    return await self._repository.create(role)
            raise UserAccessDenied

    async def update(self, entity: UserOrganizationRole, actor: User) -> UserOrganizationRole:
        self._reject_super(entity)
        async with self._tx:
            actor_role = await self._role_getter(actor, entity.organization_id)
            PermissionBuilder().providers(
                UserRolesPermissionProvider(entity.organization_id, actor_role)
            ).add(PermissionsEnum.CAN_UPDATE_ROLE).apply()
            if self._can_manage(entity, actor_role):
                return await self._repository.update(entity)
            raise UserAccessDenied

    async def delete(self, dto: DeleteUserRoleDto, actor: User) -> UserOrganizationRole:
        async with self._tx:
            actor_role = await self._role_getter(actor, dto.organization_id)
            PermissionBuilder().providers(
                UserRolesPermissionProvider(dto.organization_id, actor_role)
            ).add(PermissionsEnum.CAN_DELETE_ROLE).apply()
            if role := await self._repository.read(dto.user_id, dto.organization_id):
                if roles_delete_priorities_table[actor_role.role] < roles_delete_priorities_table[role.role]:
                    return await self._repository.delete(role)
                raise UserAccessDenied
            raise UserRoleNotFoundError
