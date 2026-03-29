from uuid import UUID

from pydantic import BaseModel

from shared.enums import BuildingType


class CreateBuildingRequest(BaseModel):
    address: str
    building_type: BuildingType
    total_area: float


class UpdateBuildingRequest(BaseModel):
    address: str
    total_area: float


class BuildingResponse(BaseModel):
    building_id: UUID
    address: str
    building_type: BuildingType
    total_area: float
