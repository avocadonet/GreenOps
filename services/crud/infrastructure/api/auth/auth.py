from typing import Annotated

from application.auth.services import AuthService
from application.auth.tokens.dtos import TokenInfoDto, TokenPairDto
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from domain.auth.entities import User
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from infrastructure.api.users.dtos import UserModel

from ..users.mappers import user__map_to_pydantic
from .deps import REFRESH_COOKIE, extract_refresh_token
from .mappers import map_authenticate_dto, map_create_dto
from .schemas import AuthenticateUserModelDto, CreateUserModelDto, UserWithTokenModelDto

router = APIRouter(route_class=DishkaRoute, tags=["Auth"])


def _make_response(user: User, tokens_pair: TokenPairDto):
    response = JSONResponse(
        content=UserWithTokenModelDto(
            user=user__map_to_pydantic(user),
            access_token=tokens_pair.access_token,
        ).model_dump(by_alias=True, mode="json"),
    )
    response.set_cookie(REFRESH_COOKIE, tokens_pair.refresh_token)
    return response


@router.post("/login", response_model=UserWithTokenModelDto)
async def login_user(dto: AuthenticateUserModelDto, auth: FromDishka[AuthService]):
    user, tokens_pair = await auth.authenticate(map_authenticate_dto(dto))
    return _make_response(user, tokens_pair)


@router.post("/register", response_model=UserWithTokenModelDto)
async def register_user(dto: CreateUserModelDto, auth: FromDishka[AuthService]):
    user, tokens_pair = await auth.register(map_create_dto(dto))
    return _make_response(user, tokens_pair)


@router.post("/refresh", response_model=UserWithTokenModelDto)
async def refresh_token(
    token_info: Annotated[TokenInfoDto, Depends(extract_refresh_token)],
    auth: FromDishka[AuthService],
):
    user, tokens_pair = await auth.authorize(token_info)
    return _make_response(user, tokens_pair)
