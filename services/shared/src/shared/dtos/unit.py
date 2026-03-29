from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateUnitDTO:
    building_id: UUID
    unit_number: str
    floor: int
    owner_name: str


@dataclass
class UpdateUnitDTO:
    unit_id: UUID
    unit_number: str
    floor: int
    owner_name: str
