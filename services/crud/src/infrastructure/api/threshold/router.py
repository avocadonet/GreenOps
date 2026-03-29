from uuid import UUID

from application.threshold.service import ThresholdService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from infrastructure.api.schemas import ErrorModel

from . import mappers
from .schemas import CreateThresholdRequest, ThresholdResponse

router = APIRouter(prefix="/thresholds", route_class=DishkaRoute, tags=["thresholds"])


@router.post("", response_model=ThresholdResponse, status_code=201)
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
)
async def read_threshold(
    threshold_id: UUID,
    service: FromDishka[ThresholdService],
):
    return mappers.entity_to_response(await service.read(threshold_id))


@router.delete(
    "/{threshold_id}",
    response_model=ThresholdResponse,
    responses={404: {"model": ErrorModel}},
)
async def delete_threshold(
    threshold_id: UUID,
    service: FromDishka[ThresholdService],
):
    return mappers.entity_to_response(await service.delete(threshold_id))
