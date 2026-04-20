import logging

from adaptix import Retort
from faststream.kafka import KafkaBroker

from shared.dtos.incident import IncidentCreatedEvent

logger = logging.getLogger(__name__)
_retort = Retort()


class KafkaEventPublisher:
    """Publishes domain events to Kafka topics via FastStream KafkaBroker."""

    def __init__(self, broker: KafkaBroker) -> None:
        self._broker = broker

    async def publish_incident(self, event: IncidentCreatedEvent) -> None:
        payload = _retort.dump(event)
        await self._broker.publish(payload, topic="incidents.created")
        logger.debug("Published incident %s to incidents.created", event.incident_id)
