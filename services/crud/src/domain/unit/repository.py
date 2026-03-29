from abc import ABC, abstractmethod
from uuid import UUID

from shared.dtos.unit import CreateUnitDTO, UpdateUnitDTO
from shared.entities.unit import Unit


class UnitRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateUnitDTO) -> Unit: ...

    @abstractmethod
    async def read(self, unit_id: UUID) -> Unit: ...

    @abstractmethod
    async def update(self, unit: Unit) -> Unit: ...

    @abstractmethod
    async def delete(self, unit: Unit) -> Unit: ...
