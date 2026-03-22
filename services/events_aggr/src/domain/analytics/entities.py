from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from domain.enums import CalculationPeriod

@dataclass
class EnergyBalance:
    balance_id: UUID
    building_id: UUID
    calc_period: CalculationPeriod  # <<MVP>> (Строгий Enum вместо period)
    loss_volume: float              # <<MVP>>
    calculated_at: datetime
    
    @property
    def is_critical_loss(self) -> bool:
        return self.loss_volume > 15.0

@dataclass
class AverageLoad:
    load_id: UUID
    building_id: UUID
    calc_period: CalculationPeriod 
    mean_value: float               # <<MVP>>
    calculated_at: datetime
