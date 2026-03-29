from uuid import UUID

from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.threshold.exceptions import (
    ThresholdAlreadyExistsException,
    ThresholdNotFoundException,
)
from domain.threshold.repository import ThresholdRepository
from shared.db.threshold import ThresholdModel
from shared.dtos.threshold import CreateThresholdDTO
from shared.entities.threshold import Threshold

from . import mappers


@provide(
    SqlalchemyConfig[CreateThresholdDTO, Threshold, ThresholdModel](
        create_mapper=mappers.threshold__create_mapper,
        entity_mapper=mappers.threshold__map_to_db,
        model_mapper=mappers.threshold__map_from_db,
        model=ThresholdModel,
        not_found=lambda **kw: ThresholdNotFoundException(**kw),
        unique_constraint_failed=lambda **kw: ThresholdAlreadyExistsException(**kw),
    )
)
class ThresholdDatabaseRepository(
    ThresholdRepository,
    ErrorHandlingSqlAlchemyRepository[CreateThresholdDTO, Threshold, ThresholdModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=ThresholdModel, id_attr="threshold_id"
        )

    @decorators.read
    async def read(self, threshold_id: UUID) -> Threshold: ...

    @decorators.create
    async def create(self, dto: CreateThresholdDTO) -> Threshold: ...

    @decorators.delete
    async def delete(self, threshold: Threshold) -> Threshold: ...
