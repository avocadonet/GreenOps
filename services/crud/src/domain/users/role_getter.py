from .entities import User, UserOrganizationRole
from .enums import RoleEnum, roles_priorities_table
from .repositories import UserOrganizationRolesRepository


class RoleGetter:
    def __init__(
        self,
        roles_repository: UserOrganizationRolesRepository,
    ):
        self.__roles_repository = roles_repository

    async def all_roles(self, user: User) -> list[UserOrganizationRole]:
        return await self.__roles_repository.read_all(user.id)

    async def __call__(
        self, user: User, organization_id: int | None = None
    ) -> UserOrganizationRole:
        roles = await self.__roles_repository.read_all(user.id)
        current = UserOrganizationRole(
            organization_id=organization_id or 0,
            user_id=user.id,
            role=user.role,
        )
        for role in roles:
            if organization_id is None:
                current = min(
                    role, current, key=lambda x: roles_priorities_table[x.role]
                )
            elif (
                role.role.value.startswith("SUPER")
                or role.organization_id == organization_id
            ):
                current = min(
                    role, current, key=lambda x: roles_priorities_table[x.role]
                )
        return current
