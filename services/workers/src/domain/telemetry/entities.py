from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from domain.enums import IncidentType

@dataclass(frozen=True)
class Metric:
    """Read-only событие из Kafka"""
    sensor_id: UUID
    building_id: UUID
    room_id: UUID                   # <<MVP>>
    value: float                    # <<MVP>>
    timestamp: datetime             # <<MVP>>

@dataclass
class PeakLoad:
    peak_id: UUID
    building_id: UUID
    max_value: float                # <<MVP>>
    timestamp: datetime             # <<MVP>>
    duration_seconds: int

@dataclass
class Incident:
    incident_id: UUID
    building_id: UUID
    incident_type: IncidentType     # <<MVP>> (было type)
    detected_at: datetime
    actual_value: float
    limit_value: float
    is_resolved: bool = False
