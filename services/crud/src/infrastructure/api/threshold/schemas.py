from uuid import UUID

from pydantic import BaseModel

from shared.enums import TariffZone, ThresholdType


class CreateThresholdRequest(BaseModel):
    sensor_id: UUID
    limit_value: float
    threshold_type: ThresholdType
    tariff_zone: TariffZone


class ThresholdResponse(BaseModel):
    threshold_id: UUID
    sensor_id: UUID
    limit_value: float
    threshold_type: ThresholdType
    tariff_zone: TariffZone
