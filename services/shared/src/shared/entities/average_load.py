from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from shared.enums import WindowSize


@dataclass
class AverageLoad:
    avg_load_id: UUID
    sensor_id: UUID
    window_size: WindowSize
    mean_value: float
    calculated_at: datetime
