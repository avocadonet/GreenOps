from uuid import UUID

from shared.dtos.building import CreateBuildingDTO, UpdateBuildingDTO
from shared.entities.building import Building

from .schemas import BuildingResponse, CreateBuildingRequest, UpdateBuildingRequest


def create_request_to_dto(request: CreateBuildingRequest) -> CreateBuildingDTO:
    return CreateBuildingDTO(
        address=request.address,
        building_type=request.building_type,
        total_area=request.total_area,
    )


def update_request_to_dto(request: UpdateBuildingRequest, building_id: UUID) -> UpdateBuildingDTO:
    return UpdateBuildingDTO(
        building_id=building_id,
        address=request.address,
        total_area=request.total_area,
    )


def entity_to_response(entity: Building) -> BuildingResponse:
    return BuildingResponse(
        building_id=entity.building_id,
        address=entity.address,
        building_type=entity.building_type,
        total_area=entity.total_area,
    )
