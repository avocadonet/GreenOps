from uuid import UUID

from application.unit.service import UnitService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from infrastructure.api.schemas import ErrorModel

from . import mappers
from .schemas import CreateUnitRequest, UnitResponse, UpdateUnitRequest

router = APIRouter(prefix="/units", route_class=DishkaRoute, tags=["units"])


@router.post("", response_model=UnitResponse, status_code=201)
async def create_unit(
    body: CreateUnitRequest,
    service: FromDishka[UnitService],
):
    return mappers.entity_to_response(
        await service.create(mappers.create_request_to_dto(body))
    )


@router.get(
    "/{unit_id}", response_model=UnitResponse, responses={404: {"model": ErrorModel}}
)
async def read_unit(
    unit_id: UUID,
    service: FromDishka[UnitService],
):
    return mappers.entity_to_response(await service.read(unit_id))


@router.put(
    "/{unit_id}", response_model=UnitResponse, responses={404: {"model": ErrorModel}}
)
async def update_unit(
    unit_id: UUID,
    body: UpdateUnitRequest,
    service: FromDishka[UnitService],
):
    return mappers.entity_to_response(
        await service.update(mappers.update_request_to_dto(body, unit_id))
    )


@router.delete(
    "/{unit_id}", response_model=UnitResponse, responses={404: {"model": ErrorModel}}
)
async def delete_unit(
    unit_id: UUID,
    service: FromDishka[UnitService],
):
    return mappers.entity_to_response(await service.delete(unit_id))
