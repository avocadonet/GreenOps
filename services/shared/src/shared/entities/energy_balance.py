from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class EnergyBalance:
    balance_id: UUID
    building_id: UUID
    period_start: datetime
    period_end: datetime
    loss_kwh: float
    loss_percent: float
