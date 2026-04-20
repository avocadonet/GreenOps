from uuid import UUID

from application.auth.enums import PermissionsEnum
from application.sensor.service import SensorService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from infrastructure.api.dependencies import require_permission
from infrastructure.api.schemas import ErrorModel

from . import mappers
from .schemas import CreateSensorRequest, SensorResponse, UpdateSensorRequest

router = APIRouter(
    prefix="/sensors",
    route_class=DishkaRoute,
    tags=["sensors"],
)


@router.post(
    "",
    response_model=SensorResponse,
    status_code=201,
    responses={422: {"model": ErrorModel}},
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_CREATE_SENSOR))],
)
async def create_sensor(
    body: CreateSensorRequest,
    service: FromDishka[SensorService],
):
    return mappers.entity_to_response(
        await service.create(mappers.create_request_to_dto(body))
    )


@router.get(
    "/{sensor_id}",
    response_model=SensorResponse,
    responses={404: {"model": ErrorModel}},
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_READ_SENSOR))],
)
async def read_sensor(
    sensor_id: UUID,
    service: FromDishka[SensorService],
):
    return mappers.entity_to_response(await service.read(sensor_id))


@router.put(
    "/{sensor_id}",
    response_model=SensorResponse,
    responses={404: {"model": ErrorModel}},
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_UPDATE_SENSOR))],
)
async def update_sensor(
    sensor_id: UUID,
    body: UpdateSensorRequest,
    service: FromDishka[SensorService],
):
    return mappers.entity_to_response(
        await service.update(
            sensor_id, body.serial_number, body.model, body.calibration_date
        )
    )


@router.delete(
    "/{sensor_id}",
    response_model=SensorResponse,
    responses={404: {"model": ErrorModel}},
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_DELETE_SENSOR))],
)
async def delete_sensor(
    sensor_id: UUID,
    service: FromDishka[SensorService],
):
    return mappers.entity_to_response(await service.delete(sensor_id))
