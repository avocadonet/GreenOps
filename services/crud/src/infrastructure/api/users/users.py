from typing import Annotated

from application.users.services import UsersService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.auth.entities import User
from fastapi import APIRouter, Depends

from ..auth.deps import get_user
from ..schemas import ErrorModel
from . import dtos, mappers

router = APIRouter(route_class=DishkaRoute)


@router.get("/me", response_model=dtos.UserModel)
async def get_me(actor: Annotated[User, Depends(get_user)]):
    return mappers.user__map_to_pydantic(actor)


@router.put(
    "/me", response_model=dtos.UserModel, responses={404: {"model": ErrorModel}}
)
async def update_me(
    dto: dtos.UpdateUserModelDto,
    actor: Annotated[User, Depends(get_user)],
    users: FromDishka[UsersService],
):
    return mappers.user__map_to_pydantic(
        await users.update(mappers.user__map_update_dto(dto, actor.user_id), actor)
    )


@router.delete(
    "/me", response_model=dtos.UserModel, responses={404: {"model": ErrorModel}}
)
async def delete_me(
    users: FromDishka[UsersService],
    actor: Annotated[User, Depends(get_user)],
):
    return mappers.user__map_to_pydantic(
        await users.delete(user_id=actor.user_id, actor=actor)
    )
