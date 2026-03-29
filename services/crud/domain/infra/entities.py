from dataclasses import dataclass
from uuid import UUID
from domain.enums import BuildingType, ThresholdType

@dataclass
class Building:
    build_id: UUID                 # <<MVP>> (было ID)
    org_id: UUID                   # Связь с владельцем!
    address: str
    building_type: BuildingType   
    total_area: float

@dataclass
class Unit:
    room_id: UUID                  # <<MVP>> (было ID)
    building_id: UUID
    room_number: str               # (было number)
    floor_level: int               # (было floor)

@dataclass
class Threshold:
    threshold_id: UUID             # (было ID)
    building_id: UUID
    threshold_type: ThresholdType  # <<MVP>>
    limit_value: float             # <<MVP>>
    
    def is_exceeded(self, current_value: float) -> bool:
        if self.threshold_type == ThresholdType.OVERLOAD:
            return current_value > self.limit_value
        elif self.threshold_type == ThresholdType.LEAKAGE:
            return current_value < self.limit_value
        return False
