from dataclasses import dataclass
from uuid import UUID

from shared.enums import IncidentSeverity, IncidentStatus, IncidentType


@dataclass
class Incident:
    incident_id: UUID
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    threshold_id: UUID | None
    peak_load_id: UUID | None
