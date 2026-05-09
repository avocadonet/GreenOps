from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.entities import UserOrganizationRole
from domain.users.enums import RoleEnum
from domain.users.repositories import UserOrganizationRolesRepository
from shared.db.user_organization_role import UserOrganizationRoleModel
from shared.exceptions import EntityNotFoundException


def _model_to_entity(m: UserOrganizationRoleModel) -> UserOrganizationRole:
    return UserOrganizationRole(
        organization_id=m.organization_id,
        user_id=m.user_id,
        role=RoleEnum(m.role),
    )


class UserOrganizationRolesDatabaseRepository(UserOrganizationRolesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, role: UserOrganizationRole) -> UserOrganizationRole:
        model = UserOrganizationRoleModel(
            user_id=role.user_id,
            organization_id=role.organization_id,
            role=role.role.value,
        )
        self._session.add(model)
        await self._session.flush()
        return role

    async def read(self, user_id: int, organization_id: int) -> UserOrganizationRole:
        result = await self._session.execute(
            select(UserOrganizationRoleModel).where(
                UserOrganizationRoleModel.user_id == user_id,
                UserOrganizationRoleModel.organization_id == organization_id,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("UserOrganizationRole")
        return _model_to_entity(model)

    async def update(self, role: UserOrganizationRole) -> UserOrganizationRole:
        result = await self._session.execute(
            select(UserOrganizationRoleModel).where(
                UserOrganizationRoleModel.user_id == role.user_id,
                UserOrganizationRoleModel.organization_id == role.organization_id,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise EntityNotFoundException("UserOrganizationRole")
        model.role = role.role.value
        await self._session.flush()
        return role

    async def delete(self, role: UserOrganizationRole) -> UserOrganizationRole:
        await self._session.execute(
            delete(UserOrganizationRoleModel).where(
                UserOrganizationRoleModel.user_id == role.user_id,
                UserOrganizationRoleModel.organization_id == role.organization_id,
            )
        )
        return role

    async def read_all(self, user_id: int) -> list[UserOrganizationRole]:
        result = await self._session.execute(
            select(UserOrganizationRoleModel).where(
                UserOrganizationRoleModel.user_id == user_id
            )
        )
        return [_model_to_entity(m) for m in result.scalars().all()]
