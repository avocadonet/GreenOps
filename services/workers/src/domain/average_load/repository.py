from abc import ABC, abstractmethod
from uuid import UUID

from shared.entities.average_load import AverageLoad


class AverageLoadReadRepository(ABC):
    @abstractmethod
    async def read_latest(self, sensor_id: UUID) -> AverageLoad | None: ...
