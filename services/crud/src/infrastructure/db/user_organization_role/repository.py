from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.entities import UserOrganizationRole
from domain.users.exceptions import UserRoleAlreadyExistsError, UserRoleNotFoundError
from domain.users.repositories import UserOrganizationRolesRepository
from shared.db.user_organization_role import UserOrganizationRoleModel

from . import mappers


@provide(
    SqlalchemyConfig[
        UserOrganizationRole, UserOrganizationRole, UserOrganizationRoleModel
    ](
        create_mapper=mappers.to_model,
        entity_mapper=mappers.to_model,
        model_mapper=mappers.to_entity,
        model=UserOrganizationRoleModel,
        not_found=lambda **kw: UserRoleNotFoundError(),
        unique_constraint_failed=lambda **kw: UserRoleAlreadyExistsError(),
    )
)
class UserOrganizationRolesDatabaseRepository(
    UserOrganizationRolesRepository,
    ErrorHandlingSqlAlchemyRepository[
        UserOrganizationRole, UserOrganizationRole, UserOrganizationRoleModel
    ],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session,
            sa_model=UserOrganizationRoleModel,
            id_attr=("user_id", "organization_id"),
        )

    @decorators.create
    async def create(self, role: UserOrganizationRole) -> UserOrganizationRole: ...

    @decorators.read
    async def read(
        self, user_id: int, organization_id: int
    ) -> UserOrganizationRole: ...

    @decorators.read(raise_if_missing=False)
    async def read_or_none(
        self, user_id: int, organization_id: int
    ) -> UserOrganizationRole: ...

    @decorators.update
    async def update(self, role: UserOrganizationRole) -> UserOrganizationRole: ...

    @decorators.delete
    async def delete(self, role: UserOrganizationRole) -> UserOrganizationRole: ...

    @decorators.read_all
    async def read_all(
        self, user_id: int, page: int = 1, page_size: int = 100
    ) -> list[UserOrganizationRole]:
        return select(UserOrganizationRoleModel).where(
            UserOrganizationRoleModel.user_id == user_id
        )
