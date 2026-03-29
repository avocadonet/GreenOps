from abc import ABC, abstractmethod
from uuid import UUID

from shared.entities.threshold import Threshold


class ThresholdReadRepository(ABC):
    """Read-only: workers never mutate thresholds, only the CRUD service does."""

    @abstractmethod
    async def read_by_sensor(self, sensor_id: UUID) -> Threshold | None: ...
