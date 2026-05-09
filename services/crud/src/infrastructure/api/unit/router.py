from uuid import UUID

from application.unit.service import UnitService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.users.entities import User
from fastapi import APIRouter, Depends, Query

from infrastructure.api.dependencies import get_current_user
from infrastructure.api.schemas import ErrorModel, PaginatedResponse

from . import mappers
from .schemas import CreateUnitRequest, UnitResponse, UpdateUnitRequest

router = APIRouter(
    prefix="/units",
    route_class=DishkaRoute,
    tags=["units"],
)


@router.get(
    "",
    response_model=PaginatedResponse[UnitResponse],
)
async def list_units(
    service: FromDishka[UnitService],
    user: User = Depends(get_current_user),
    building_id: UUID | None = Query(None),
    organization_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items = await service.list_all(user, building_id, organization_id, page, page_size)
    return PaginatedResponse(
        items=[mappers.entity_to_response(i) for i in items],
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=UnitResponse,
    status_code=201,
)
async def create_unit(
    body: CreateUnitRequest,
    service: FromDishka[UnitService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.create(user, mappers.create_request_to_dto(body))
    )


@router.get(
    "/{unit_id}",
    response_model=UnitResponse,
    responses={404: {"model": ErrorModel}},
)
async def read_unit(
    unit_id: UUID,
    service: FromDishka[UnitService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.read(user, unit_id))


@router.put(
    "/{unit_id}",
    response_model=UnitResponse,
    responses={404: {"model": ErrorModel}},
)
async def update_unit(
    unit_id: UUID,
    body: UpdateUnitRequest,
    service: FromDishka[UnitService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.update(user, mappers.update_request_to_dto(body, unit_id))
    )


@router.delete(
    "/{unit_id}",
    response_model=UnitResponse,
    responses={404: {"model": ErrorModel}},
)
async def delete_unit(
    unit_id: UUID,
    service: FromDishka[UnitService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.delete(user, unit_id))
