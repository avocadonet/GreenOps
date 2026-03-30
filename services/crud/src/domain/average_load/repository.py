from abc import ABC, abstractmethod

from shared.dtos.average_load import CreateAverageLoadDTO
from shared.entities.average_load import AverageLoad


class AverageLoadRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateAverageLoadDTO) -> AverageLoad: ...
