from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.base import SensorMapping
from shared.db.sensor import SensorModel


async def load_tuya_mappings(session: AsyncSession) -> list[SensorMapping]:
    result = await session.execute(
        select(SensorModel).where(
            SensorModel.provider == "tuya",
            SensorModel.external_id.is_not(None),
        )
    )
    rows = result.scalars().all()
    return [
        SensorMapping(external_id=row.external_id, sensor_id=row.sensor_id)
        for row in rows
    ]
