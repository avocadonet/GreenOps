from dataclasses import dataclass
from datetime import date
from uuid import UUID

from shared.enums import SensorType


@dataclass
class CreateSensorDTO:
    serial_number: str
    model: str
    calibration_date: date
    sensor_type: SensorType
    building_id: UUID | None
    unit_id: UUID | None
