from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from shared.entities.metric import Metric


class MetricRepository(ABC):
    @abstractmethod
    async def list_by_sensor_in_range(
        self, sensor_id: UUID, start: datetime, end: datetime
    ) -> list[Metric]: ...
