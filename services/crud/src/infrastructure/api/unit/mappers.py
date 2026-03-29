from uuid import UUID

from shared.dtos.unit import CreateUnitDTO, UpdateUnitDTO
from shared.entities.unit import Unit

from .schemas import CreateUnitRequest, UnitResponse, UpdateUnitRequest


def create_request_to_dto(request: CreateUnitRequest) -> CreateUnitDTO:
    return CreateUnitDTO(
        building_id=request.building_id,
        unit_number=request.unit_number,
        floor=request.floor,
        owner_name=request.owner_name,
    )


def update_request_to_dto(request: UpdateUnitRequest, unit_id: UUID) -> UpdateUnitDTO:
    return UpdateUnitDTO(
        unit_id=unit_id,
        unit_number=request.unit_number,
        floor=request.floor,
        owner_name=request.owner_name,
    )


def entity_to_response(entity: Unit) -> UnitResponse:
    return UnitResponse(
        unit_id=entity.unit_id,
        building_id=entity.building_id,
        unit_number=entity.unit_number,
        floor=entity.floor,
        owner_name=entity.owner_name,
    )
