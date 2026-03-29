from dataclasses import dataclass
from uuid import UUID

from shared.enums import TariffZone, ThresholdType


@dataclass
class CreateThresholdDTO:
    sensor_id: UUID
    limit_value: float
    threshold_type: ThresholdType
    tariff_zone: TariffZone
