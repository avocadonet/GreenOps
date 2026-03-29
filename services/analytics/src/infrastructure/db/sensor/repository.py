from uuid import UUID

from adaptix.conversion import ConversionRetort
from shared.db.sensor import SensorModel
from shared.entities.sensor import Sensor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_retort = ConversionRetort()
_sensor_from_db = _retort.get_converter(SensorModel, Sensor)


class SensorReadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[Sensor]:
        result = await self._session.execute(select(SensorModel))
        return [_sensor_from_db(row) for row in result.scalars()]

    async def list_by_building(self, building_id: UUID) -> list[Sensor]:
        result = await self._session.execute(
            select(SensorModel).where(SensorModel.building_id == building_id)
        )
        return [_sensor_from_db(row) for row in result.scalars()]
