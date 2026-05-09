from uuid import UUID

from application.building.service import BuildingService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.users.entities import User
from fastapi import APIRouter, Depends, Query

from infrastructure.api.dependencies import get_current_user
from infrastructure.api.schemas import ErrorModel, PaginatedResponse

from . import mappers
from .schemas import BuildingResponse, CreateBuildingRequest, UpdateBuildingRequest

router = APIRouter(
    prefix="/buildings",
    route_class=DishkaRoute,
    tags=["buildings"],
)


@router.get(
    "",
    response_model=PaginatedResponse[BuildingResponse],
)
async def list_buildings(
    service: FromDishka[BuildingService],
    user: User = Depends(get_current_user),
    organization_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items = await service.list_all(user, organization_id, page, page_size)
    return PaginatedResponse(
        items=[mappers.entity_to_response(i) for i in items],
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=BuildingResponse,
    status_code=201,
)
async def create_building(
    body: CreateBuildingRequest,
    service: FromDishka[BuildingService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.create(user, mappers.create_request_to_dto(body))
    )


@router.get(
    "/{building_id}",
    response_model=BuildingResponse,
    responses={404: {"model": ErrorModel}},
)
async def read_building(
    building_id: UUID,
    service: FromDishka[BuildingService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.read(user, building_id))


@router.put(
    "/{building_id}",
    response_model=BuildingResponse,
    responses={404: {"model": ErrorModel}},
)
async def update_building(
    building_id: UUID,
    body: UpdateBuildingRequest,
    service: FromDishka[BuildingService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.update(user, mappers.update_request_to_dto(body, building_id))
    )


@router.delete(
    "/{building_id}",
    response_model=BuildingResponse,
    responses={404: {"model": ErrorModel}},
)
async def delete_building(
    building_id: UUID,
    service: FromDishka[BuildingService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.delete(user, building_id))
