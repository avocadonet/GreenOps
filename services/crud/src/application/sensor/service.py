from uuid import UUID

from application.transaction import TransactionsGateway
from domain.sensor.exceptions import SensorAttachmentException
from domain.sensor.repository import SensorRepository
from shared.dtos.sensor import CreateSensorDTO
from shared.entities.sensor import Sensor
from shared.enums import SensorType


class SensorService:
    def __init__(self, repository: SensorRepository, tx: TransactionsGateway) -> None:
        self._repository = repository
        self._tx = tx

    async def create(self, dto: CreateSensorDTO) -> Sensor:
        self._validate_attachment(dto.sensor_type, dto.building_id, dto.unit_id)
        return await self._repository.create(dto)

    async def read(self, sensor_id: UUID) -> Sensor:
        return await self._repository.read(sensor_id)

    async def delete(self, sensor_id: UUID) -> Sensor:
        async with self._tx:
            sensor = await self._repository.read(sensor_id)
            return await self._repository.delete(sensor)

    @staticmethod
    def _validate_attachment(
        sensor_type: SensorType,
        building_id: UUID | None,
        unit_id: UUID | None,
    ) -> None:
        if building_id is not None and unit_id is not None:
            raise SensorAttachmentException(
                "Sensor cannot be attached to both a building and a unit"
            )
        if sensor_type == SensorType.COMMON and building_id is None:
            raise SensorAttachmentException("COMMON sensor requires building_id")
        if sensor_type == SensorType.INDIVIDUAL and unit_id is None:
            raise SensorAttachmentException("INDIVIDUAL sensor requires unit_id")
