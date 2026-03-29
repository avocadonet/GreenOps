from uuid import UUID

from application.building.service import BuildingService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from infrastructure.api.schemas import ErrorModel

from . import mappers
from .schemas import BuildingResponse, CreateBuildingRequest, UpdateBuildingRequest

router = APIRouter(prefix="/buildings", route_class=DishkaRoute, tags=["buildings"])


@router.post("", response_model=BuildingResponse, status_code=201)
async def create_building(
    body: CreateBuildingRequest,
    service: FromDishka[BuildingService],
):
    return mappers.entity_to_response(await service.create(mappers.create_request_to_dto(body)))


@router.get("/{building_id}", response_model=BuildingResponse, responses={404: {"model": ErrorModel}})
async def read_building(
    building_id: UUID,
    service: FromDishka[BuildingService],
):
    return mappers.entity_to_response(await service.read(building_id))


@router.put("/{building_id}", response_model=BuildingResponse, responses={404: {"model": ErrorModel}})
async def update_building(
    building_id: UUID,
    body: UpdateBuildingRequest,
    service: FromDishka[BuildingService],
):
    return mappers.entity_to_response(
        await service.update(mappers.update_request_to_dto(body, building_id))
    )


@router.delete("/{building_id}", response_model=BuildingResponse, responses={404: {"model": ErrorModel}})
async def delete_building(
    building_id: UUID,
    service: FromDishka[BuildingService],
):
    return mappers.entity_to_response(await service.delete(building_id))
