from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class PeakLoad:
    peak_id: UUID
    sensor_id: UUID
    max_value: float
    duration_seconds: float
    detected_at: datetime
