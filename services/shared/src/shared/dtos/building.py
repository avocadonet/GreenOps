from dataclasses import dataclass
from uuid import UUID

from shared.enums import BuildingType


@dataclass
class CreateBuildingDTO:
    address: str
    building_type: BuildingType
    total_area: float
    organization_id: int | None = None


@dataclass
class UpdateBuildingDTO:
    building_id: UUID
    address: str
    total_area: float
