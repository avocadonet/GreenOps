from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.users.dtos import ReadAllUsersDto
from domain.users.entities import User
from fastapi import APIRouter, Depends, Query, Request

from application.users.services import UserRoleService, UserService
from infrastructure.api.dependencies import get_current_user
from infrastructure.api.schemas import ErrorModel, PaginatedResponse

from . import mappers
from .schemas import (
    CreateRoleRequest,
    UpdateRoleRequest,
    UpdateUserRequest,
    UserOrganizationRoleResponse,
    UserResponse,
)

router = APIRouter(prefix="/users", route_class=DishkaRoute, tags=["users"])

roles_router = APIRouter(
    prefix="/{user_id}/roles", route_class=DishkaRoute, tags=["user-roles"]
)


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    service: FromDishka[UserService],
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items = await service.list_all(
        ReadAllUsersDto(page=page, page_size=page_size), user
    )
    return PaginatedResponse(
        items=[mappers.user_to_response(u) for u in items],
        page=page,
        page_size=page_size,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return mappers.user_to_response(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UpdateUserRequest,
    service: FromDishka[UserService],
    user: User = Depends(get_current_user),
):
    dto = mappers.update_request_to_dto(body, user.id)
    return mappers.user_to_response(await service.update(dto, user))


@router.delete("/me", response_model=UserResponse)
async def delete_me(
    service: FromDishka[UserService],
    user: User = Depends(get_current_user),
):
    return mappers.user_to_response(await service.delete(user))


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"model": ErrorModel}},
)
async def get_user(
    user_id: int,
    service: FromDishka[UserService],
    user: User = Depends(get_current_user),
):
    return mappers.user_to_response(await service.get(user_id, user))


@roles_router.get("", response_model=list[UserOrganizationRoleResponse])
async def list_roles(
    user_id: int,
    service: FromDishka[UserRoleService],
    user: User = Depends(get_current_user),
):
    roles = await service.list_all(user_id)
    return [mappers.role_to_response(r) for r in roles]


@roles_router.get(
    "/{org_id}",
    response_model=UserOrganizationRoleResponse,
    responses={404: {"model": ErrorModel}},
)
async def get_role(
    user_id: int,
    org_id: int,
    service: FromDishka[UserRoleService],
    user: User = Depends(get_current_user),
):
    return mappers.role_to_response(await service.get(user_id, org_id))


@roles_router.post(
    "",
    response_model=UserOrganizationRoleResponse,
    status_code=201,
    responses={403: {"model": ErrorModel}},
)
async def create_role(
    user_id: int,
    body: CreateRoleRequest,
    service: FromDishka[UserRoleService],
    user: User = Depends(get_current_user),
):
    entity = mappers.create_role_request_to_entity(body)
    return mappers.role_to_response(await service.create(entity, user))


@roles_router.put(
    "/{org_id}",
    response_model=UserOrganizationRoleResponse,
    responses={403: {"model": ErrorModel}, 404: {"model": ErrorModel}},
)
async def update_role(
    user_id: int,
    org_id: int,
    body: UpdateRoleRequest,
    service: FromDishka[UserRoleService],
    user: User = Depends(get_current_user),
):
    entity = mappers.update_role_request_to_entity(body, user_id, org_id)
    return mappers.role_to_response(await service.update(entity, user))


@roles_router.delete(
    "/{org_id}",
    response_model=UserOrganizationRoleResponse,
    responses={403: {"model": ErrorModel}, 404: {"model": ErrorModel}},
)
async def delete_role(
    user_id: int,
    org_id: int,
    service: FromDishka[UserRoleService],
    user: User = Depends(get_current_user),
):
    dto = mappers.delete_role_to_dto(user_id, org_id)
    return mappers.role_to_response(await service.delete(dto, user))


router.include_router(roles_router)
