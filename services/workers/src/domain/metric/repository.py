from abc import ABC, abstractmethod

from shared.dtos.metric import CreateMetricDTO
from shared.entities.metric import Metric


class MetricRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateMetricDTO) -> Metric: ...
