import logging
from datetime import datetime, timedelta, timezone

from domain.average_load_calculator import AverageLoadCalculator
from shared.dtos.average_load import CreateAverageLoadDTO
from shared.enums import WindowSize

logger = logging.getLogger(__name__)


class AverageLoadService:
    def __init__(
        self,
        sensors,          # SensorReadRepository
        metrics,          # MetricReadRepository
        avg_loads,        # AverageLoadRepository
        calculator: AverageLoadCalculator,
    ) -> None:
        self._sensors = sensors
        self._metrics = metrics
        self._avg_loads = avg_loads
        self._calculator = calculator

    async def run_hourly(self) -> None:
        now = datetime.now(tz=timezone.utc)
        window_start = now - timedelta(hours=1)
        sensors = await self._sensors.list_all()
        for sensor in sensors:
            try:
                metrics = await self._metrics.list_by_sensor_in_range(
                    sensor_id=sensor.sensor_id,
                    start=window_start,
                    end=now,
                )
                result = self._calculator.compute([m.value for m in metrics])
                if result is None:
                    continue
                await self._avg_loads.create(
                    CreateAverageLoadDTO(
                        sensor_id=sensor.sensor_id,
                        window_size=WindowSize.HOUR,
                        mean_value=result.mean_value,
                        calculated_at=now,
                    )
                )
                logger.info("AverageLoad computed for sensor %s: %.3f", sensor.sensor_id, result.mean_value)
            except Exception:
                logger.exception("Failed to compute AverageLoad for sensor %s", sensor.sensor_id)
