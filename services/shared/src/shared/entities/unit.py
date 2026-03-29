from dataclasses import dataclass
from uuid import UUID


@dataclass
class Unit:
    unit_id: UUID
    building_id: UUID
    unit_number: str
    floor: int
    owner_name: str
