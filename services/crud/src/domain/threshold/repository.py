from abc import ABC, abstractmethod
from uuid import UUID

from shared.dtos.threshold import CreateThresholdDTO
from shared.entities.threshold import Threshold


class ThresholdRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateThresholdDTO) -> Threshold: ...

    @abstractmethod
    async def read(self, threshold_id: UUID) -> Threshold: ...

    @abstractmethod
    async def delete(self, threshold: Threshold) -> Threshold: ...
