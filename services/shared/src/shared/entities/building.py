from dataclasses import dataclass
from uuid import UUID

from shared.enums import BuildingType


@dataclass
class Building:
    building_id: UUID
    address: str
    building_type: BuildingType
    total_area: float
