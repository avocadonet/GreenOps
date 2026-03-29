from abc import ABC, abstractmethod
from uuid import UUID

from shared.dtos.sensor import CreateSensorDTO
from shared.entities.sensor import Sensor


class SensorRepository(ABC):
    @abstractmethod
    async def create(self, dto: CreateSensorDTO) -> Sensor: ...

    @abstractmethod
    async def read(self, sensor_id: UUID) -> Sensor: ...

    @abstractmethod
    async def delete(self, sensor: Sensor) -> Sensor: ...
