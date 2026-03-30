from uuid import UUID

from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.building.exceptions import (
    BuildingAlreadyExistsException,
    BuildingNotFoundException,
)
from domain.building.repository import BuildingRepository
from shared.db.building import BuildingModel
from shared.dtos.building import CreateBuildingDTO
from shared.entities.building import Building

from . import mappers


@provide(
    SqlalchemyConfig[CreateBuildingDTO, Building, BuildingModel](
        create_mapper=mappers.building__create_mapper,
        entity_mapper=mappers.building__map_to_db,
        model_mapper=mappers.building__map_from_db,
        model=BuildingModel,
        not_found=lambda **kw: BuildingNotFoundException(**kw),
        unique_constraint_failed=lambda **kw: BuildingAlreadyExistsException(**kw),
    )
)
class BuildingDatabaseRepository(
    BuildingRepository,
    ErrorHandlingSqlAlchemyRepository[CreateBuildingDTO, Building, BuildingModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=BuildingModel, id_attr="building_id"
        )

    async def list_all(self) -> list[Building]:
        models = await self.gateway.select_by_fields_all()
        return [self.config.model_mapper(m) for m in models]

    @decorators.read
    async def read(self, building_id: UUID) -> Building: ...

    @decorators.create
    async def create(self, dto: CreateBuildingDTO) -> Building: ...

    @decorators.update
    async def update(self, building: Building) -> Building: ...

    @decorators.delete
    async def delete(self, building: Building) -> Building: ...
