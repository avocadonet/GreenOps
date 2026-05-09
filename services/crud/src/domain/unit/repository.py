from abc import ABC, abstractmethod
from uuid import UUID

from shared.dtos.unit import CreateUnitDTO, UpdateUnitDTO
from shared.entities.unit import Unit


class UnitRepository(ABC):
    @abstractmethod
    async def list_all(self, building_id: UUID | None, organization_id: int | None, page: int, page_size: int) -> list[Unit]: ...

    @abstractmethod
    async def create(self, dto: CreateUnitDTO) -> Unit: ...

    @abstractmethod
    async def read(self, unit_id: UUID) -> Unit: ...

    @abstractmethod
    async def update(self, unit: Unit) -> Unit: ...

    @abstractmethod
    async def delete(self, unit: Unit) -> Unit: ...
