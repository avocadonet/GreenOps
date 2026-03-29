from uuid import UUID

from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.unit.exceptions import UnitAlreadyExistsException, UnitNotFoundException
from domain.unit.repository import UnitRepository
from shared.db.unit import UnitModel
from shared.dtos.unit import CreateUnitDTO
from shared.entities.unit import Unit

from . import mappers


@provide(
    SqlalchemyConfig[CreateUnitDTO, Unit, UnitModel](
        create_mapper=mappers.unit__create_mapper,
        entity_mapper=mappers.unit__map_to_db,
        model_mapper=mappers.unit__map_from_db,
        model=UnitModel,
        not_found=lambda **kw: UnitNotFoundException(**kw),
        unique_constraint_failed=lambda **kw: UnitAlreadyExistsException(**kw),
    )
)
class UnitDatabaseRepository(
    UnitRepository,
    ErrorHandlingSqlAlchemyRepository[CreateUnitDTO, Unit, UnitModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=UnitModel, id_attr="unit_id"
        )

    @decorators.read
    async def read(self, unit_id: UUID) -> Unit: ...

    @decorators.create
    async def create(self, dto: CreateUnitDTO) -> Unit: ...

    @decorators.update
    async def update(self, unit: Unit) -> Unit: ...

    @decorators.delete
    async def delete(self, unit: Unit) -> Unit: ...
