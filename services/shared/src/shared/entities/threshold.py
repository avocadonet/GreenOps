from dataclasses import dataclass
from uuid import UUID

from shared.enums import TariffZone, ThresholdType


@dataclass
class Threshold:
    threshold_id: UUID
    sensor_id: UUID
    limit_value: float
    threshold_type: ThresholdType
    tariff_zone: TariffZone
