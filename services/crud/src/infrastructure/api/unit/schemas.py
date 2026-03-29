from uuid import UUID

from pydantic import BaseModel


class CreateUnitRequest(BaseModel):
    building_id: UUID
    unit_number: str
    floor: int
    owner_name: str


class UpdateUnitRequest(BaseModel):
    unit_number: str
    floor: int
    owner_name: str


class UnitResponse(BaseModel):
    unit_id: UUID
    building_id: UUID
    unit_number: str
    floor: int
    owner_name: str
