import logging

from adaptix import Retort
from faststream.kafka import KafkaRouter

from shared.dtos.incident import IncidentCreatedEvent

logger = logging.getLogger(__name__)
router = KafkaRouter()
_retort = Retort()


@router.subscriber("incidents.created")
async def on_incident_created(message: dict) -> None:
    event = _retort.load(message, IncidentCreatedEvent)
    logger.info(
        "Incident received: id=%s type=%s severity=%s",
        event.incident_id,
        event.incident_type,
        event.severity,
    )
