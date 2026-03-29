from uuid import UUID

from application.transaction import TransactionsGateway
from domain.unit.repository import UnitRepository
from shared.dtos.unit import CreateUnitDTO, UpdateUnitDTO
from shared.entities.unit import Unit


class UnitService:
    def __init__(self, repository: UnitRepository, tx: TransactionsGateway) -> None:
        self._repository = repository
        self._tx = tx

    async def create(self, dto: CreateUnitDTO) -> Unit:
        return await self._repository.create(dto)

    async def read(self, unit_id: UUID) -> Unit:
        return await self._repository.read(unit_id)

    async def update(self, dto: UpdateUnitDTO) -> Unit:
        async with self._tx:
            unit = await self._repository.read(dto.unit_id)
            unit.unit_number = dto.unit_number
            unit.floor = dto.floor
            unit.owner_name = dto.owner_name
            return await self._repository.update(unit)

    async def delete(self, unit_id: UUID) -> Unit:
        async with self._tx:
            unit = await self._repository.read(unit_id)
            return await self._repository.delete(unit)
