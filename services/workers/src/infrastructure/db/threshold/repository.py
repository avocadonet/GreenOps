from uuid import UUID

from adaptix.conversion import ConversionRetort
from domain.threshold.repository import ThresholdReadRepository
from shared.db.threshold import ThresholdModel
from shared.entities.threshold import Threshold
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_retort = ConversionRetort()
_threshold_from_db = _retort.get_converter(ThresholdModel, Threshold)


class ThresholdReadDatabaseRepository(ThresholdReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_sensor(self, sensor_id: UUID) -> Threshold | None:
        result = await self._session.execute(
            select(ThresholdModel).where(ThresholdModel.sensor_id == sensor_id).limit(1)
        )
        model = result.scalar_one_or_none()
        return _threshold_from_db(model) if model is not None else None
