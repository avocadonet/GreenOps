import logging

from adaptix import Retort
from dishka.integrations.faststream import FromDishka
from faststream.kafka import KafkaRouter

from shared.dtos.incident import IncidentCreatedEvent
from shared.dtos.metric import CreateMetricDTO
from telemetry import TelemetryService

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


@router.subscriber("incidents.created")
async def on_incident_created(message: dict) -> None:
    event = _retort.load(message, IncidentCreatedEvent)
    logger.info(
        "Incident received: id=%s type=%s severity=%s",
        event.incident_id,
        event.incident_type,
        event.severity,
    )
