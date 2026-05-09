from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateUnitDTO:
    building_id: UUID
    unit_number: str
    floor: int
    owner_name: str
    organization_id: int | None = None


@dataclass
class UpdateUnitDTO:
    unit_id: UUID
    unit_number: str
    floor: int
    owner_name: str
