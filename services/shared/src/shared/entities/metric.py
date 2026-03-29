from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Metric:
    metric_id: UUID
    sensor_id: UUID
    value: float
    measurement_unit: (
        str  # "kWh"; renamed from spec's "unit" to avoid collision with Unit entity
    )
    voltage: float
    current: float
    recorded_at: datetime
