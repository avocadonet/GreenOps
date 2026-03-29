from shared.dtos.average_load import CreateAverageLoadDTO
from shared.entities.average_load import AverageLoad
from sqlalchemy.ext.asyncio import AsyncSession

from . import mappers


class AverageLoadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dto: CreateAverageLoadDTO) -> AverageLoad:
        model = mappers.average_load__create_mapper(dto)
        self._session.add(model)
        await self._session.flush()
        return mappers.average_load__map_from_db(model)
