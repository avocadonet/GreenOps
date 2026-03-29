from dataclasses import dataclass
from uuid import UUID

from shared.enums import IncidentSeverity, IncidentType


@dataclass
class CreateIncidentDTO:
    incident_type: IncidentType
    severity: IncidentSeverity
    threshold_id: UUID | None
    peak_load_id: UUID | None


@dataclass
class IncidentCreatedEvent:
    """Published to incidents.created Kafka topic. Consumed by all services."""
    incident_id: UUID
    incident_type: IncidentType
    severity: IncidentSeverity
    threshold_id: UUID | None
    peak_load_id: UUID | None
