from abc import ABC, abstractmethod
from uuid import UUID

from shared.dtos.threshold import CreateThresholdDTO
from shared.entities.threshold import Threshold


class ThresholdRepository(ABC):
    @abstractmethod
    async def list_all(
        self,
        sensor_id: UUID | None,
        organization_id: int | None,
        page: int,
        page_size: int,
    ) -> list[Threshold]: ...

    @abstractmethod
    async def create(self, dto: CreateThresholdDTO) -> Threshold: ...

    @abstractmethod
    async def read(self, threshold_id: UUID) -> Threshold: ...

    @abstractmethod
    async def update(self, threshold: Threshold) -> Threshold: ...

    @abstractmethod
    async def delete(self, threshold: Threshold) -> Threshold: ...
