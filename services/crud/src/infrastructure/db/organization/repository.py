from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.organization.exceptions import (
    OrganizationAlreadyExistsException,
    OrganizationNotFoundException,
)
from domain.organization.repository import OrganizationRepository
from shared.db.organization import OrganizationModel
from shared.dtos.organization import CreateOrganizationDTO
from shared.entities.organization import Organization

from . import mappers


@provide(
    SqlalchemyConfig[CreateOrganizationDTO, Organization, OrganizationModel](
        create_mapper=mappers.org__create_mapper,
        entity_mapper=mappers.org__map_to_db,
        model_mapper=mappers.org__map_from_db,
        model=OrganizationModel,
        not_found=lambda **kw: OrganizationNotFoundException(**kw),
        unique_constraint_failed=lambda **kw: OrganizationAlreadyExistsException(**kw),
    )
)
class OrganizationDatabaseRepository(
    OrganizationRepository,
    ErrorHandlingSqlAlchemyRepository[
        CreateOrganizationDTO, Organization, OrganizationModel
    ],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=OrganizationModel, id_attr="id"
        )

    @decorators.read_all
    async def list_all(self, page: int, page_size: int) -> list[Organization]:
        return select(OrganizationModel)

    @decorators.read
    async def read(self, id: int) -> Organization: ...

    @decorators.create
    async def create(self, dto: CreateOrganizationDTO) -> Organization: ...

    @decorators.update
    async def update(self, org: Organization) -> Organization: ...

    @decorators.delete
    async def delete(self, org: Organization) -> Organization: ...
