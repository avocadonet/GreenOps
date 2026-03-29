import unittest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from application.sensor.service import SensorService
from domain.sensor.exceptions import SensorAttachmentException
from shared.dtos.sensor import CreateSensorDTO
from shared.enums import SensorType


class TestSensorServiceCreate(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = AsyncMock()
        self.tx = MagicMock()
        self.service = SensorService(repository=self.repo, tx=self.tx)
        self._dto_base = dict(
            serial_number="SN-001",
            model="EM-100",
            calibration_date=date.today(),
        )

    async def test_common_sensor_without_building_raises(self):
        dto = CreateSensorDTO(
            **self._dto_base,
            sensor_type=SensorType.COMMON,
            building_id=None,
            unit_id=None,
        )
        with self.assertRaises(SensorAttachmentException):
            await self.service.create(dto)
        self.repo.create.assert_not_awaited()

    async def test_individual_sensor_without_unit_raises(self):
        dto = CreateSensorDTO(
            **self._dto_base,
            sensor_type=SensorType.INDIVIDUAL,
            building_id=None,
            unit_id=None,
        )
        with self.assertRaises(SensorAttachmentException):
            await self.service.create(dto)

    async def test_dual_attachment_raises(self):
        dto = CreateSensorDTO(
            **self._dto_base,
            sensor_type=SensorType.COMMON,
            building_id=uuid4(),
            unit_id=uuid4(),
        )
        with self.assertRaises(SensorAttachmentException):
            await self.service.create(dto)

    async def test_valid_common_sensor_delegates_to_repo(self):
        dto = CreateSensorDTO(
            **self._dto_base,
            sensor_type=SensorType.COMMON,
            building_id=uuid4(),
            unit_id=None,
        )
        await self.service.create(dto)
        self.repo.create.assert_awaited_once_with(dto)

    async def test_valid_individual_sensor_delegates_to_repo(self):
        dto = CreateSensorDTO(
            **self._dto_base,
            sensor_type=SensorType.INDIVIDUAL,
            building_id=None,
            unit_id=uuid4(),
        )
        await self.service.create(dto)
        self.repo.create.assert_awaited_once_with(dto)
