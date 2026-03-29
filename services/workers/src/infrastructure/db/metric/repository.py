from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from domain.metric.repository import MetricRepository
from shared.db.metric import MetricModel
from shared.dtos.metric import CreateMetricDTO
from shared.entities.metric import Metric

from . import mappers


@provide(
    SqlalchemyConfig[CreateMetricDTO, Metric, MetricModel](
        create_mapper=mappers.metric__create_mapper,
        entity_mapper=mappers.metric__map_to_db,
        model_mapper=mappers.metric__map_from_db,
        model=MetricModel,
    )
)
class MetricDatabaseRepository(
    MetricRepository,
    ErrorHandlingSqlAlchemyRepository[CreateMetricDTO, Metric, MetricModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=MetricModel, id_attr="metric_id"
        )

    @decorators.create
    async def create(self, dto: CreateMetricDTO) -> Metric: ...
