import logging

from adaptix import Retort
from faststream.nats import NatsBroker

from shared.dtos.incident import IncidentCreatedEvent

logger = logging.getLogger(__name__)
_retort = Retort()


class NatsEventPublisher:
    def __init__(self, broker: NatsBroker) -> None:
        self._broker = broker

    async def publish_incident(self, event: IncidentCreatedEvent) -> None:
        payload = _retort.dump(event)
        await self._broker.publish(payload, subject="incidents.created")
        logger.debug("Published incident %s to incidents.created", event.incident_id)
