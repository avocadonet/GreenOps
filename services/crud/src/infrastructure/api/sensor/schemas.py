from datetime import date
from uuid import UUID

from pydantic import BaseModel

from shared.enums import SensorType


class CreateSensorRequest(BaseModel):
    serial_number: str
    model: str
    calibration_date: date
    sensor_type: SensorType
    building_id: UUID | None = None
    unit_id: UUID | None = None


class SensorResponse(BaseModel):
    sensor_id: UUID
    serial_number: str
    model: str
    calibration_date: date
    sensor_type: SensorType
    building_id: UUID | None
    unit_id: UUID | None
