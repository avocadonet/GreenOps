from uuid import UUID

from application.transaction import TransactionsGateway
from domain.building.repository import BuildingRepository
from shared.dtos.building import CreateBuildingDTO, UpdateBuildingDTO
from shared.entities.building import Building


class BuildingService:
    def __init__(self, repository: BuildingRepository, tx: TransactionsGateway) -> None:
        self._repository = repository
        self._tx = tx

    async def create(self, dto: CreateBuildingDTO) -> Building:
        return await self._repository.create(dto)

    async def read(self, building_id: UUID) -> Building:
        return await self._repository.read(building_id)

    async def update(self, dto: UpdateBuildingDTO) -> Building:
        async with self._tx:
            building = await self._repository.read(dto.building_id)
            building.address = dto.address
            building.total_area = dto.total_area
            return await self._repository.update(building)

    async def delete(self, building_id: UUID) -> Building:
        async with self._tx:
            building = await self._repository.read(building_id)
            return await self._repository.delete(building)
