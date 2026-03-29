import logging

from adaptix import Retort
from dishka.integrations.faststream import FromDishka
from faststream.kafka import KafkaRouter

from application.telemetry.service import TelemetryService
from shared.dtos.metric import CreateMetricDTO

logger = logging.getLogger(__name__)
router = KafkaRouter()
_retort = Retort()


@router.subscriber("telemetry.raw")
async def on_telemetry_raw(
    message: dict,
    service: FromDishka[TelemetryService],
) -> None:
    dto = _retort.load(message, CreateMetricDTO)
    await service.process(dto)
    logger.debug("Processed metric for sensor %s", dto.sensor_id)
