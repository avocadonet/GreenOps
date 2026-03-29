from abc import ABC, abstractmethod

from shared.dtos.peak_load import CreatePeakLoadDTO
from shared.entities.peak_load import PeakLoad


class PeakLoadRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreatePeakLoadDTO) -> PeakLoad: ...
