from datetime import datetime
from uuid import UUID

from adaptix.conversion import ConversionRetort
from shared.db.metric import MetricModel
from shared.entities.metric import Metric
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_retort = ConversionRetort()
_metric_from_db = _retort.get_converter(MetricModel, Metric)


class MetricReadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_sensor_in_range(
        self, sensor_id: UUID, start: datetime, end: datetime
    ) -> list[Metric]:
        result = await self._session.execute(
            select(MetricModel).where(
                MetricModel.sensor_id == sensor_id,
                MetricModel.recorded_at >= start,
                MetricModel.recorded_at < end,
            )
        )
        return [_metric_from_db(row) for row in result.scalars()]
