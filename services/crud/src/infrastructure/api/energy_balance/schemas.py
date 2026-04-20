from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EnergyBalanceResponse(BaseModel):
    balance_id: UUID
    building_id: UUID
    period_start: datetime
    period_end: datetime
    loss_kwh: float
    loss_percent: float
