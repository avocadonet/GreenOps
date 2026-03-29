from adaptix.conversion import ConversionRetort
from shared.db.building import BuildingModel
from shared.entities.building import Building
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_retort = ConversionRetort()
_building_from_db = _retort.get_converter(BuildingModel, Building)


class BuildingReadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[Building]:
        result = await self._session.execute(select(BuildingModel))
        return [_building_from_db(row) for row in result.scalars()]
