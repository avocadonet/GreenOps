from dataclasses import dataclass
from datetime import date
from uuid import UUID

from shared.enums import SensorType


@dataclass
class Sensor:
    sensor_id: UUID
    serial_number: str
    model: str
    calibration_date: date
    sensor_type: SensorType
    building_id: UUID | None  # set when sensor_type == COMMON
    unit_id: UUID | None  # set when sensor_type == INDIVIDUAL
