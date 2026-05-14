from datetime import datetime
from uuid import UUID

from adaptix.conversion import ConversionRetort
from crudx.sa.gateway import AsyncSqlAlchemyGateway
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.metric.repository import MetricRepository
from shared.db.metric import MetricModel
from shared.entities.metric import Metric

_retort = ConversionRetort()
_metric_from_db = _retort.get_converter(MetricModel, Metric)


class MetricDatabaseRepository(MetricRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=MetricModel, id_attr="metric_id"
        )

    async def list_by_sensor_in_range(
        self, sensor_id: UUID, start: datetime, end: datetime
    ) -> list[Metric]:
        stmt = select(MetricModel).where(
            MetricModel.sensor_id == sensor_id,
            MetricModel.recorded_at >= start,
            MetricModel.recorded_at < end,
        )
        models = await self.gateway.select_by_query_all(stmt)
        return [_metric_from_db(m) for m in models]
