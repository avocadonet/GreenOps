from shared.dtos.energy_balance import CreateEnergyBalanceDTO
from shared.entities.energy_balance import EnergyBalance
from sqlalchemy.ext.asyncio import AsyncSession

from . import mappers


class EnergyBalanceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dto: CreateEnergyBalanceDTO) -> EnergyBalance:
        model = mappers.energy_balance__create_mapper(dto)
        self._session.add(model)
        await self._session.flush()
        return mappers.energy_balance__map_from_db(model)
