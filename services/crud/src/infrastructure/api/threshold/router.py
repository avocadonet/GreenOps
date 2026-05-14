from uuid import UUID

from application.threshold.service import ThresholdService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.users.entities import User
from fastapi import APIRouter, Depends, Query

from infrastructure.api.dependencies import get_current_user
from infrastructure.api.schemas import ErrorModel, PaginatedResponse

from . import mappers
from .schemas import CreateThresholdRequest, ThresholdResponse, UpdateThresholdRequest

router = APIRouter(
    prefix="/thresholds",
    route_class=DishkaRoute,
    tags=["thresholds"],
)


@router.get(
    "",
    response_model=PaginatedResponse[ThresholdResponse],
)
async def list_thresholds(
    service: FromDishka[ThresholdService],
    user: User = Depends(get_current_user),
    sensor_id: UUID | None = Query(None),
    organization_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items = await service.list_all(user, sensor_id, organization_id, page, page_size)
    return PaginatedResponse(
        items=[mappers.entity_to_response(i) for i in items],
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=ThresholdResponse,
    status_code=201,
)
async def create_threshold(
    body: CreateThresholdRequest,
    service: FromDishka[ThresholdService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.create(user, mappers.create_request_to_dto(body))
    )


@router.get(
    "/{threshold_id}",
    response_model=ThresholdResponse,
    responses={404: {"model": ErrorModel}},
)
async def read_threshold(
    threshold_id: UUID,
    service: FromDishka[ThresholdService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.read(user, threshold_id))


@router.put(
    "/{threshold_id}",
    response_model=ThresholdResponse,
    responses={404: {"model": ErrorModel}},
)
async def update_threshold(
    threshold_id: UUID,
    body: UpdateThresholdRequest,
    service: FromDishka[ThresholdService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(
        await service.update(user, threshold_id, body.limit_value)
    )


@router.delete(
    "/{threshold_id}",
    response_model=ThresholdResponse,
    responses={404: {"model": ErrorModel}},
)
async def delete_threshold(
    threshold_id: UUID,
    service: FromDishka[ThresholdService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.delete(user, threshold_id))
