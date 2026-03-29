import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from application.energy_balance.service import EnergyBalanceService
from domain.energy_balance_calculator import EnergyBalanceCalculator
from shared.entities.building import Building
from shared.entities.metric import Metric
from shared.entities.sensor import Sensor
from shared.enums import BuildingType, SensorType


def _building() -> Building:
    return Building(
        building_id=uuid4(),
        address="Test St 1",
        building_type=BuildingType.RESIDENTIAL,
        total_area=1000.0,
    )


def _sensor(sensor_type: SensorType, building_id) -> Sensor:
    return Sensor(
        sensor_id=uuid4(),
        serial_number=f"SN-{uuid4()}",
        model="EM-100",
        calibration_date=datetime.now(tz=timezone.utc).date(),
        sensor_type=sensor_type,
        building_id=building_id,
        unit_id=None,
    )


def _metric(sensor_id, value: float) -> Metric:
    return Metric(
        metric_id=uuid4(),
        sensor_id=sensor_id,
        value=value,
        measurement_unit="kWh",
        voltage=220.0,
        current=1.0,
        recorded_at=datetime.now(tz=timezone.utc),
    )


class TestEnergyBalanceServiceRunDaily(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.buildings_repo = AsyncMock()
        self.sensors_repo = AsyncMock()
        self.metrics_repo = AsyncMock()
        self.balances_repo = AsyncMock()
        self.calculator = EnergyBalanceCalculator()

        self.service = EnergyBalanceService(
            buildings=self.buildings_repo,
            sensors=self.sensors_repo,
            metrics=self.metrics_repo,
            balances=self.balances_repo,
            calculator=self.calculator,
        )

    async def test_no_common_sensor_skips_building(self):
        building = _building()
        individual = _sensor(SensorType.INDIVIDUAL, building.building_id)
        self.buildings_repo.list_all.return_value = [building]
        self.sensors_repo.list_by_building.return_value = [individual]

        await self.service.run_daily()

        self.balances_repo.create.assert_not_awaited()

    async def test_loss_computed_and_persisted(self):
        building = _building()
        common = _sensor(SensorType.COMMON, building.building_id)
        unit_sensor = _sensor(SensorType.INDIVIDUAL, building.building_id)

        self.buildings_repo.list_all.return_value = [building]
        self.sensors_repo.list_by_building.return_value = [common, unit_sensor]
        self.metrics_repo.list_by_sensor_in_range.side_effect = [
            [_metric(common.sensor_id, 1000.0)],  # common meter
            [_metric(unit_sensor.sensor_id, 900.0)],  # unit meter
        ]

        await self.service.run_daily()

        self.balances_repo.create.assert_awaited_once()
        dto = self.balances_repo.create.call_args.args[0]
        self.assertAlmostEqual(dto.loss_kwh, 100.0)
        self.assertAlmostEqual(dto.loss_percent, 10.0)
        self.assertEqual(dto.building_id, building.building_id)

    async def test_failed_building_does_not_abort_others(self):
        b1, b2 = _building(), _building()
        self.buildings_repo.list_all.return_value = [b1, b2]
        # First building raises, second should still be processed
        self.sensors_repo.list_by_building.side_effect = [
            RuntimeError("db error"),
            [],
        ]

        await self.service.run_daily()  # must not raise

        # b2 was attempted (no common sensor → no create), b1 failed silently
        self.balances_repo.create.assert_not_awaited()
