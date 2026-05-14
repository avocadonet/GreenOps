from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class CreateMetricDTO:
    sensor_id: UUID
    value: float
    measurement_unit: str
    voltage: float
    current: float
    recorded_at: datetime
