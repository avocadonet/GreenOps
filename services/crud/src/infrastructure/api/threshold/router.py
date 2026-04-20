from uuid import UUID

from application.auth.enums import PermissionsEnum
from application.threshold.service import ThresholdService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from infrastructure.api.dependencies import require_permission
from infrastructure.api.schemas import ErrorModel

from . import mappers
from .schemas import CreateThresholdRequest, ThresholdResponse, UpdateThresholdRequest

router = APIRouter(
    prefix="/thresholds",
    route_class=DishkaRoute,
    tags=["thresholds"],
)


@router.post(
    "",
    response_model=ThresholdResponse,
    status_code=201,
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_CREATE_THRESHOLD))],
)
async def create_threshold(
    body: CreateThresholdRequest,
    service: FromDishka[ThresholdService],
):
    return mappers.entity_to_response(
        await service.create(mappers.create_request_to_dto(body))
    )


@router.get(
    "/{threshold_id}",
    response_model=ThresholdResponse,
    responses={404: {"model": ErrorModel}},
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_READ_THRESHOLD))],
)
async def read_threshold(
    threshold_id: UUID,
    service: FromDishka[ThresholdService],
):
    return mappers.entity_to_response(await service.read(threshold_id))


@router.put(
    "/{threshold_id}",
    response_model=ThresholdResponse,
    responses={404: {"model": ErrorModel}},
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_UPDATE_THRESHOLD))],
)
async def update_threshold(
    threshold_id: UUID,
    body: UpdateThresholdRequest,
    service: FromDishka[ThresholdService],
):
    return mappers.entity_to_response(
        await service.update(threshold_id, body.limit_value)
    )


@router.delete(
    "/{threshold_id}",
    response_model=ThresholdResponse,
    responses={404: {"model": ErrorModel}},
    dependencies=[Depends(require_permission(PermissionsEnum.CAN_DELETE_THRESHOLD))],
)
async def delete_threshold(
    threshold_id: UUID,
    service: FromDishka[ThresholdService],
):
    return mappers.entity_to_response(await service.delete(threshold_id))
