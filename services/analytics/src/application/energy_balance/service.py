import logging
from datetime import datetime, timedelta, timezone

from domain.energy_balance_calculator import EnergyBalanceCalculator
from shared.dtos.energy_balance import CreateEnergyBalanceDTO
from shared.enums import SensorType

logger = logging.getLogger(__name__)


class EnergyBalanceService:
    def __init__(
        self,
        buildings,        # BuildingReadRepository
        sensors,          # SensorReadRepository
        metrics,          # MetricReadRepository
        balances,         # EnergyBalanceRepository
        calculator: EnergyBalanceCalculator,
    ) -> None:
        self._buildings = buildings
        self._sensors = sensors
        self._metrics = metrics
        self._balances = balances
        self._calculator = calculator

    async def run_daily(self) -> None:
        now = datetime.now(tz=timezone.utc)
        yesterday_start = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        yesterday_end = yesterday_start + timedelta(days=1)

        buildings = await self._buildings.list_all()
        for building in buildings:
            try:
                await self._compute_for_building(building, yesterday_start, yesterday_end)
            except Exception:
                logger.exception(
                    "Failed to compute EnergyBalance for building %s", building.building_id
                )

    async def _compute_for_building(self, building, period_start: datetime, period_end: datetime) -> None:
        sensors = await self._sensors.list_by_building(building.building_id)

        common_sensor = next(
            (s for s in sensors if s.sensor_type == SensorType.COMMON), None
        )
        if common_sensor is None:
            logger.debug("Building %s has no COMMON sensor — skipping", building.building_id)
            return

        common_metrics = await self._metrics.list_by_sensor_in_range(
            common_sensor.sensor_id, period_start, period_end
        )
        common_kwh = sum(m.value for m in common_metrics)

        individual_sensors = [s for s in sensors if s.sensor_type == SensorType.INDIVIDUAL]
        individual_sum = 0.0
        for sensor in individual_sensors:
            metrics = await self._metrics.list_by_sensor_in_range(
                sensor.sensor_id, period_start, period_end
            )
            individual_sum += sum(m.value for m in metrics)

        result = self._calculator.compute(
            common_kwh=common_kwh,
            individual_sum_kwh=individual_sum,
        )
        await self._balances.create(
            CreateEnergyBalanceDTO(
                building_id=building.building_id,
                period_start=period_start,
                period_end=period_end,
                loss_kwh=result.loss_kwh,
                loss_percent=result.loss_percent,
            )
        )
        logger.info(
            "EnergyBalance for building %s: loss=%.2f kWh (%.1f%%)",
            building.building_id,
            result.loss_kwh,
            result.loss_percent,
        )
