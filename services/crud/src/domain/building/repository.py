from abc import ABC, abstractmethod
from uuid import UUID

from shared.dtos.building import CreateBuildingDTO, UpdateBuildingDTO
from shared.entities.building import Building


class BuildingRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateBuildingDTO) -> Building: ...

    @abstractmethod
    async def read(self, building_id: UUID) -> Building: ...

    @abstractmethod
    async def update(self, building: Building) -> Building: ...

    @abstractmethod
    async def delete(self, building: Building) -> Building: ...
