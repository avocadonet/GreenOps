from uuid import UUID

from application.sensor.service import SensorService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.users.entities import User
from fastapi import APIRouter, Depends, Query

from infrastructure.api.dependencies import get_current_user
from infrastructure.api.schemas import ErrorModel, PaginatedResponse

from . import mappers
from .schemas import CreateSensorRequest, SensorResponse, UpdateSensorRequest

router = APIRouter(
    prefix="/sensors",
    route_class=DishkaRoute,
    tags=["sensors"],
)


@router.get(
    "",
    response_model=PaginatedResponse[SensorResponse],
)
async def list_sensors(
    service: FromDishka[SensorService],
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
    response_model=SensorResponse,
    status_code=201,
    responses={422: {"model": ErrorModel}},
)
async def create_sensor(
    body: CreateSensorRequest,
    service: FromDishka[SensorService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.create(user, mappers.create_request_to_dto(body))
    )


@router.get(
    "/{sensor_id}",
    response_model=SensorResponse,
    responses={404: {"model": ErrorModel}},
)
async def read_sensor(
    sensor_id: UUID,
    service: FromDishka[SensorService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.read(user, sensor_id))


@router.put(
    "/{sensor_id}",
    response_model=SensorResponse,
    responses={404: {"model": ErrorModel}},
)
async def update_sensor(
    sensor_id: UUID,
    body: UpdateSensorRequest,
    service: FromDishka[SensorService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.update(user, sensor_id, body.serial_number, body.model, body.calibration_date)
    )


@router.delete(
    "/{sensor_id}",
    response_model=SensorResponse,
    responses={404: {"model": ErrorModel}},
)
async def delete_sensor(
    sensor_id: UUID,
    service: FromDishka[SensorService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.delete(user, sensor_id))
