from uuid import UUID

from adaptix.conversion import ConversionRetort
from domain.average_load.repository import AverageLoadReadRepository
from shared.db.average_load import AverageLoadModel
from shared.entities.average_load import AverageLoad
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_retort = ConversionRetort()
_avg_load_from_db = _retort.get_converter(AverageLoadModel, AverageLoad)


class AverageLoadReadDatabaseRepository(AverageLoadReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_latest(self, sensor_id: UUID) -> AverageLoad | None:
        result = await self._session.execute(
            select(AverageLoadModel)
            .where(AverageLoadModel.sensor_id == sensor_id)
            .order_by(AverageLoadModel.calculated_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return _avg_load_from_db(model) if model is not None else None
