from uuid import UUID

from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.sensor.exceptions import (
    SensorAlreadyExistsException,
    SensorNotFoundException,
)
from domain.sensor.repository import SensorRepository
from shared.db.sensor import SensorModel
from shared.dtos.sensor import CreateSensorDTO
from shared.entities.sensor import Sensor

from . import mappers


@provide(
    SqlalchemyConfig[CreateSensorDTO, Sensor, SensorModel](
        create_mapper=mappers.sensor__create_mapper,
        entity_mapper=mappers.sensor__map_to_db,
        model_mapper=mappers.sensor__map_from_db,
        model=SensorModel,
        not_found=lambda **kw: SensorNotFoundException(**kw),
        unique_constraint_failed=lambda **kw: SensorAlreadyExistsException(**kw),
    )
)
class SensorDatabaseRepository(
    SensorRepository,
    ErrorHandlingSqlAlchemyRepository[CreateSensorDTO, Sensor, SensorModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=SensorModel, id_attr="sensor_id"
        )

    @decorators.read_all
    async def list_all(self, organization_id: int | None, page: int, page_size: int) -> list[Sensor]:
        stmt = select(SensorModel)
        if organization_id is not None:
            stmt = stmt.where(SensorModel.organization_id == organization_id)
        return stmt

    @decorators.read_all
    async def list_by_building(self, building_id: UUID, page: int, page_size: int) -> list[Sensor]:
        return select(SensorModel).where(SensorModel.building_id == building_id)

    @decorators.read
    async def read(self, sensor_id: UUID) -> Sensor: ...

    @decorators.create
    async def create(self, dto: CreateSensorDTO) -> Sensor: ...

    @decorators.update
    async def update(self, sensor: Sensor) -> Sensor: ...

    @decorators.delete
    async def delete(self, sensor: Sensor) -> Sensor: ...
