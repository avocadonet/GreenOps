from uuid import UUID

from application.sensor.service import SensorService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from infrastructure.api.schemas import ErrorModel

from . import mappers
from .schemas import CreateSensorRequest, SensorResponse

router = APIRouter(prefix="/sensors", route_class=DishkaRoute, tags=["sensors"])


@router.post(
    "",
    response_model=SensorResponse,
    status_code=201,
    responses={422: {"model": ErrorModel}},
)
async def create_sensor(
    body: CreateSensorRequest,
    service: FromDishka[SensorService],
):
    return mappers.entity_to_response(await service.create(mappers.create_request_to_dto(body)))


@router.get("/{sensor_id}", response_model=SensorResponse, responses={404: {"model": ErrorModel}})
async def read_sensor(
    sensor_id: UUID,
    service: FromDishka[SensorService],
):
    return mappers.entity_to_response(await service.read(sensor_id))


@router.delete("/{sensor_id}", response_model=SensorResponse, responses={404: {"model": ErrorModel}})
async def delete_sensor(
    sensor_id: UUID,
    service: FromDishka[SensorService],
):
    return mappers.entity_to_response(await service.delete(sensor_id))
