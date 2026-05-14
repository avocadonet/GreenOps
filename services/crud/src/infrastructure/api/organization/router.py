from application.organization.service import OrganizationService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.users.entities import User
from fastapi import APIRouter, Depends, Query

from infrastructure.api.dependencies import get_current_user
from infrastructure.api.schemas import ErrorModel, PaginatedResponse

from . import mappers
from .schemas import (
    CreateOrganizationRequest,
    OrganizationResponse,
    UpdateOrganizationRequest,
)

router = APIRouter(
    prefix="/organizations",
    route_class=DishkaRoute,
    tags=["organizations"],
)


@router.get(
    "",
    response_model=PaginatedResponse[OrganizationResponse],
)
async def list_organizations(
    service: FromDishka[OrganizationService],
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items = await service.list_all(user, page, page_size)
    return PaginatedResponse(
        items=[mappers.entity_to_response(i) for i in items],
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=201,
)
async def create_organization(
    body: CreateOrganizationRequest,
    service: FromDishka[OrganizationService],
    user: User = Depends(get_current_user),
):
    dto = mappers.create_request_to_dto(body, user.id)
    return mappers.entity_to_response(await service.create(user, dto))


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    responses={404: {"model": ErrorModel}},
)
async def read_organization(
    org_id: int,
    service: FromDishka[OrganizationService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.read(user, org_id))


@router.put(
    "/{org_id}",
    response_model=OrganizationResponse,
    responses={404: {"model": ErrorModel}},
)
async def update_organization(
    org_id: int,
    body: UpdateOrganizationRequest,
    service: FromDishka[OrganizationService],
    user: User = Depends(get_current_user),
):
    dto = mappers.update_request_to_dto(body, org_id)
    return mappers.entity_to_response(await service.update(user, dto))


@router.delete(
    "/{org_id}",
    response_model=OrganizationResponse,
    responses={404: {"model": ErrorModel}},
)
async def delete_organization(
    org_id: int,
    service: FromDishka[OrganizationService],
    user: User = Depends(get_current_user),
):
    return mappers.entity_to_response(await service.delete(user, org_id))
