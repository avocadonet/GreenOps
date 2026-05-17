import logging

from adaptix import Retort
from dishka.integrations.faststream import FromDishka, inject
from faststream.nats import NatsRouter
from faststream.nats.schemas import JStream

from shared.dtos.incident import IncidentCreatedEvent
from shared.dtos.metric import CreateMetricDTO
from telemetry import TelemetryService
import json

logger = logging.getLogger(__name__)
router = NatsRouter()
_retort = Retort()


@router.subscriber("telemetry.raw", stream=JStream(name="telemetry"))
async def on_telemetry_raw(
    message: dict,
    service: FromDishka[TelemetryService],
) -> None:
    dto = _retort.load(message, CreateMetricDTO)
    await service.process(dto)
    logger.debug("Processed metric for sensor %s", dto.sensor_id)


@router.subscriber("incidents.created", stream=JStream(name="incidents"))
async def on_incident_created(message: dict) -> None:
    event = _retort.load(message, IncidentCreatedEvent)
    logger.info(
        "Incident received: id=%s type=%s severity=%s",
        event.incident_id,
        event.incident_type,
        event.severity,
    )
